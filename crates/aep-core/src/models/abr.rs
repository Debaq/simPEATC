//! Modelo de respuesta del ABR / PEATC por click.
//!
//! Construye las ondas I–V desde la tabla normativa y les aplica las reglas
//! clinicas (intensidad efectiva sobre umbral, temperatura, tasa, retardo del
//! transductor y patron de lesion). Es el modelo que valida el nucleo de la
//! Capa 0 (MOTOR.md §12).

use super::ResponseModel;
use crate::acquisition::Acquisition;
use crate::component::Component;
use crate::lesion::{Lesion, LesionSite};
use crate::modulation::{apply_intensity, apply_rate, apply_temperature};
use crate::norms::AbrNorms;
use crate::protocol::Protocol;
use crate::subject::{ArousalState, Ear, Subject};
use crate::synth::NoiseProfile;

/// Modelo ABR parametrizado por su tabla normativa.
#[derive(Debug, Clone)]
pub struct AbrModel {
    norms: AbrNorms,
}

impl Default for AbrModel {
    fn default() -> Self {
        Self::new()
    }
}

impl AbrModel {
    /// Modelo con las normas embebidas.
    pub fn new() -> Self {
        Self {
            norms: AbrNorms::embedded(),
        }
    }

    /// Modelo con una tabla normativa explicita (p.ej. override del investigador).
    pub fn with_norms(norms: AbrNorms) -> Self {
        Self { norms }
    }

    /// Desplazamiento de umbral (dB) por las lesiones del oido a la frecuencia
    /// dominante del estimulo. Capa 0: domina el peor desplazamiento.
    fn threshold_shift(&self, subject: &Subject, ear: Ear, freq_hz: f64) -> f64 {
        subject
            .lesions_on(ear)
            .map(|l| l.threshold_shift_at(freq_hz))
            .fold(0.0, f64::max)
    }
}

/// Factor de retraso retrococlear por onda (la onda V se retrasa mas que la I).
fn retrocochlear_factor(label: &str) -> f64 {
    match label {
        "I" => 0.0,
        "II" => 0.2,
        "III" => 0.4,
        "IV" => 0.7,
        "V" => 1.0,
        _ => 0.5,
    }
}

/// Aplica el patron especifico del sitio de lesion a un componente.
///
/// La conductiva y la coclear actuan ya via el umbral efectivo (alargan
/// latencias absolutas / reducen el nivel efectivo). Aqui se anaden los patrones
/// que NO se reducen a un simple desplazamiento de nivel:
/// - Retrococlear: alarga selectivamente las ondas tardias (↑ intervalo I–V).
/// - Neural: atenua/cancela las ondas (desincronia).
fn apply_lesion_pattern(c: &mut Component, lesions: &[&Lesion]) {
    for l in lesions {
        match l.site {
            LesionSite::Retrocochlear => {
                c.latency_ms += l.severity_db / 40.0 * 0.8 * retrocochlear_factor(&c.label);
            }
            LesionSite::Neural => {
                let keep = (1.0 - l.severity_db / 60.0).clamp(0.0, 1.0);
                c.amplitude_uv *= keep;
            }
            // Conductiva, coclear y central: cubiertas por el umbral efectivo
            // (o sin efecto relevante para el ABR en Capa 0).
            _ => {}
        }
    }
}

impl ResponseModel for AbrModel {
    fn components(&self, protocol: &Protocol, subject: &Subject) -> Vec<Component> {
        let stim = &protocol.stimulus;
        let ear = stim.ear;
        let freq = stim.kind.dominant_freq_hz();
        let level_nhl = stim.level.as_nhl();
        let threshold = self.threshold_shift(subject, ear, freq);
        let effective = level_nhl - threshold;
        let delay = stim.transducer.acoustic_delay_ms();
        let lesions: Vec<&Lesion> = subject.lesions_on(ear).collect();

        let mut comps = Vec::with_capacity(self.norms.waves.len());
        for w in &self.norms.waves {
            let mut c = Component::gaussian(
                w.label.clone(),
                w.latency_ms,
                w.amplitude_uv,
                w.width_ms,
                w.generator.clone(),
            );
            apply_intensity(&mut c, effective, self.norms.reference_db_nhl);
            apply_temperature(&mut c, subject.temperature_c);
            apply_rate(&mut c, stim.rate_hz, self.norms.reference_rate_hz);
            c.latency_ms += delay;
            apply_lesion_pattern(&mut c, &lesions);
            // Solo conservar ondas con amplitud apreciable.
            if c.amplitude_uv.abs() > 1e-6 {
                comps.push(c);
            }
        }
        comps
    }

    fn recommended_acquisition(&self) -> Acquisition {
        Acquisition::abr_default(Ear::Right)
    }

    fn background_noise(&self, subject: &Subject) -> NoiseProfile {
        // RMS crudo base (banda ancha) de un adulto despierto.
        let mut rms = 0.35_f64;
        rms *= match subject.state {
            ArousalState::Awake => 1.0,
            ArousalState::NaturalSleep => 0.85,
            ArousalState::Sedated => 0.7,
            ArousalState::Anesthetized => 0.6,
        };
        // El lactante tiene mas ruido EEG de fondo.
        if subject.age.approx_years() < 1.0 {
            rms *= 1.3;
        }
        NoiseProfile::new(rms)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::lesion::FreqProfile;
    use crate::protocol::Protocol;
    use crate::subject::Subject;

    fn intervalo_iv(comps: &[Component]) -> Option<f64> {
        let i = comps.iter().find(|c| c.label == "I")?.latency_ms;
        let v = comps.iter().find(|c| c.label == "V")?.latency_ms;
        Some(v - i)
    }

    #[test]
    fn normal_produce_ondas_en_rango() {
        let model = AbrModel::new();
        let p = Protocol::abr_click(Ear::Right);
        let s = Subject::default();
        let comps = model.components(&p, &s);
        // Onda V presente y en rango normativo (~5.6 ms + retardo inserto 0.9).
        let v = comps.iter().find(|c| c.label == "V").unwrap();
        assert!((v.latency_ms - 6.5).abs() < 0.6, "V = {} ms", v.latency_ms);
    }

    #[test]
    fn baja_intensidad_atenua_y_retrasa() {
        let model = AbrModel::new();
        let mut p = Protocol::abr_click(Ear::Right);
        let s = Subject::default();
        let alta = model.components(&p, &s);
        p.stimulus.level = crate::units::Level::DbNhl(30.0);
        let baja = model.components(&p, &s);
        let v_alta = alta.iter().find(|c| c.label == "V").unwrap();
        let v_baja = baja.iter().find(|c| c.label == "V").unwrap();
        assert!(v_baja.latency_ms > v_alta.latency_ms);
        assert!(v_baja.amplitude_uv < v_alta.amplitude_uv);
    }

    #[test]
    fn retrococlear_alarga_intervalo_i_v() {
        let model = AbrModel::new();
        let p = Protocol::abr_click(Ear::Right);
        let sano = Subject::default();
        let mut enfermo = Subject::default();
        enfermo.lesions.push(Lesion {
            site: LesionSite::Retrocochlear,
            ear: Ear::Right,
            severity_db: 40.0,
            freq_profile: FreqProfile::Flat,
        });
        let iv_sano = intervalo_iv(&model.components(&p, &sano)).unwrap();
        let iv_enf = intervalo_iv(&model.components(&p, &enfermo)).unwrap();
        assert!(iv_enf > iv_sano + 0.3, "sano={iv_sano} enfermo={iv_enf}");
    }

    #[test]
    fn neuropatia_atenua_las_ondas() {
        let model = AbrModel::new();
        let p = Protocol::abr_click(Ear::Right);
        let mut s = Subject::default();
        s.lesions.push(Lesion {
            site: LesionSite::Neural,
            ear: Ear::Right,
            severity_db: 55.0,
            freq_profile: FreqProfile::Flat,
        });
        let comps = model.components(&p, &s);
        // Las ondas quedan muy atenuadas (o ausentes).
        let max_amp = comps.iter().map(|c| c.amplitude_uv.abs()).fold(0.0, f64::max);
        assert!(max_amp < 0.1, "amplitud maxima {max_amp}");
    }

    #[test]
    fn conductiva_preserva_intervalo_i_v() {
        let model = AbrModel::new();
        let p = Protocol::abr_click(Ear::Right);
        let sano = Subject::default();
        let mut enfermo = Subject::default();
        enfermo.lesions.push(Lesion {
            site: LesionSite::Conductive,
            ear: Ear::Right,
            severity_db: 30.0,
            freq_profile: FreqProfile::Flat,
        });
        let iv_sano = intervalo_iv(&model.components(&p, &sano)).unwrap();
        let iv_enf = intervalo_iv(&model.components(&p, &enfermo)).unwrap();
        // La conductiva alarga absolutas pero respeta el intervalo interpico.
        assert!((iv_enf - iv_sano).abs() < 0.15, "sano={iv_sano} enfermo={iv_enf}");
    }
}
