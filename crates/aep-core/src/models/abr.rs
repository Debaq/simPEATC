//! Modelo de respuesta del ABR / PEATC por click.
//!
//! Construye las ondas I–VII desde la tabla normativa y les aplica las reglas
//! clinicas. El punto fino del ABR es como cada **sitio de lesion** altera la
//! respuesta de forma distinta:
//!
//! - **Conductiva**: atenua lo que llega a la coclea → alarga las latencias
//!   absolutas por igual, pero **preserva los intervalos interpico**.
//! - **Coclear**: eleva el umbral pero, por **reclutamiento**, a alta intensidad
//!   la latencia es casi normal; lo que cae es el margen sobre umbral (amplitud).
//! - **Retrococlear**: alarga selectivamente las ondas tardias → ↑ intervalo I–V.
//! - **Neural**: desincronia → atenua/cancela las ondas.
//!
//! Es el modelo que valida el nucleo y la modalidad estrella (MOTOR.md §12).

use super::ResponseModel;
use crate::acquisition::Acquisition;
use crate::component::Component;
use crate::lesion::{Lesion, LesionSite};
use crate::modulation::{
    apply_age, apply_intensity, apply_polarity, apply_rate, apply_sex, apply_temperature,
    apply_tone_frequency, TONE_FREQ_REF_HZ,
};
use crate::norms::AbrNorms;
use crate::protocol::Protocol;
use crate::stimulus::{ChirpKind, StimulusKind};
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

/// Umbrales efectivos separados por mecanismo, a una frecuencia dada.
struct Thresholds {
    /// Perdida conductiva (atenua antes de la coclea).
    conductive: f64,
    /// Perdida coclear (eleva umbral sensorial, con reclutamiento).
    cochlear: f64,
}

impl AbrModel {
    /// Modelo con las normas embebidas.
    pub fn new() -> Self {
        Self {
            norms: AbrNorms::embedded_abr(),
        }
    }

    /// Modelo con una tabla normativa explicita (p.ej. override del investigador).
    pub fn with_norms(norms: AbrNorms) -> Self {
        Self { norms }
    }

    /// Reparte el desplazamiento de umbral de las lesiones del oido segun su
    /// mecanismo. La conductiva es aditiva; la coclear toma el peor.
    fn thresholds(&self, lesions: &[&Lesion], freq_hz: f64) -> Thresholds {
        let mut conductive = 0.0;
        let mut cochlear = 0.0_f64;
        for l in lesions {
            let shift = l.threshold_shift_at(freq_hz);
            match l.site {
                LesionSite::Conductive => conductive += shift,
                LesionSite::Cochlear => cochlear = cochlear.max(shift),
                _ => {}
            }
        }
        Thresholds {
            conductive,
            cochlear,
        }
    }
}

/// Realce de amplitud del chirp por mejor sincronia.
///
/// La ventaja es mayor a intensidad baja/media (a alta intensidad el click ya
/// sincroniza bien). El LS-Chirp mantiene mas ventaja en todo el rango.
fn chirp_gain(kind: ChirpKind, level_nhl: f64) -> f64 {
    // 1.0 a 20 dB nHL → 0.0 a 80 dB nHL.
    let low_level_boost = 1.0 - ((level_nhl - 20.0) / 60.0).clamp(0.0, 1.0);
    match kind {
        ChirpKind::CeChirp | ChirpKind::NarrowBand { .. } => 1.15 + 0.35 * low_level_boost,
        ChirpKind::LsChirp => 1.25 + 0.35 * low_level_boost,
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
        "VI" => 1.1,
        "VII" => 1.2,
        _ => 0.5,
    }
}

/// Aplica el patron especifico del sitio de lesion que NO se reduce a un
/// desplazamiento de nivel (retrococlear y neural).
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
            // Conductiva y coclear: via umbral efectivo. Central: sin efecto en
            // el ABR de tronco (afecta componentes corticales, capas tardias).
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
        let delay = stim.transducer.acoustic_delay_ms();
        let years = subject.age.approx_years();
        let is_tone = matches!(stim.kind, StimulusKind::ToneBurst { .. });
        let chirp = match stim.kind {
            StimulusKind::Chirp { kind } => Some(kind),
            _ => None,
        };
        // El tone-burst y el NB-chirp son especificos en frecuencia.
        let freq_specific = is_tone || matches!(chirp, Some(ChirpKind::NarrowBand { .. }));
        let lesions: Vec<&Lesion> = subject.lesions_on(ear).collect();

        let th = self.thresholds(&lesions, freq);
        // Nivel que llega a la coclea tras la perdida conductiva.
        let level_at_cochlea = level_nhl - th.conductive;
        // Margen audible sobre el umbral total (determina la amplitud).
        let margin = level_at_cochlea - th.cochlear;
        // La latencia depende del nivel post-conductivo: la conductiva la alarga,
        // la coclear no (reclutamiento).
        let level_for_latency = level_at_cochlea;

        let mut comps = Vec::with_capacity(self.norms.waves.len());
        for w in &self.norms.waves {
            let mut c = Component::gaussian(
                w.label.clone(),
                w.latency_ms,
                w.amplitude_uv,
                w.width_ms,
                w.generator.clone(),
            );
            apply_intensity(&mut c, level_for_latency, margin, self.norms.reference_db_nhl);
            apply_temperature(&mut c, subject.temperature_c);
            apply_rate(&mut c, stim.rate_hz, self.norms.reference_rate_hz);
            apply_sex(&mut c, subject.sex);
            apply_age(&mut c, years);
            apply_polarity(&mut c, stim.polarity);
            if freq_specific {
                // Estimulo especifico en frecuencia (tone-burst o NB-chirp):
                // latencia/amplitud dependientes de la frecuencia.
                apply_tone_frequency(&mut c, freq, TONE_FREQ_REF_HZ);
            }
            if let Some(kind) = chirp {
                // El chirp compensa la dispersion coclear → mejor sincronia.
                c.amplitude_uv *= chirp_gain(kind, level_nhl);
            }
            c.latency_ms += delay;
            apply_lesion_pattern(&mut c, &lesions);
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
        // RMS crudo (banda ancha) del EEG/EMG de fondo de un adulto despierto.
        // Varias veces la señal evocada: un sweep aislado es grande y la onda
        // SOLO emerge al promediar (el ruido cae ~√N), quedando reconocible hacia
        // ~2000 sweeps. TODO: la tasa de emergencia (≈ este RMS o el SNR del caso)
        // debe ser una VARIABLE POR CASO editable en el área docente (como los
        // `fsp_puntos` del legacy): casos "buenos" emergen antes, los malos después.
        let mut rms = 1.7_f64;
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
    use crate::units::Level;

    fn interval(comps: &[Component], a: &str, b: &str) -> Option<f64> {
        let la = comps.iter().find(|c| c.label == a)?.latency_ms;
        let lb = comps.iter().find(|c| c.label == b)?.latency_ms;
        Some(lb - la)
    }

    fn cochlear(severity: f64) -> Lesion {
        Lesion {
            site: LesionSite::Cochlear,
            ear: Ear::Right,
            severity_db: severity,
            freq_profile: FreqProfile::Flat,
        }
    }

    fn conductive(severity: f64) -> Lesion {
        Lesion {
            site: LesionSite::Conductive,
            ear: Ear::Right,
            severity_db: severity,
            freq_profile: FreqProfile::Flat,
        }
    }

    #[test]
    fn normal_tiene_siete_ondas_y_v_en_rango() {
        let comps = AbrModel::new().components(&Protocol::abr_click(Ear::Right), &Subject::default());
        assert_eq!(comps.len(), 7); // I..VII
        let v = comps.iter().find(|c| c.label == "V").unwrap();
        assert!((v.latency_ms - 6.4).abs() < 0.7, "V = {} ms", v.latency_ms);
    }

    #[test]
    fn baja_intensidad_atenua_y_retrasa() {
        let model = AbrModel::new();
        let mut p = Protocol::abr_click(Ear::Right);
        let s = Subject::default();
        let alta = model.components(&p, &s);
        p.stimulus.level = Level::DbNhl(30.0);
        let baja = model.components(&p, &s);
        let v_alta = alta.iter().find(|c| c.label == "V").unwrap();
        let v_baja = baja.iter().find(|c| c.label == "V").unwrap();
        assert!(v_baja.latency_ms > v_alta.latency_ms);
        assert!(v_baja.amplitude_uv < v_alta.amplitude_uv);
    }

    #[test]
    fn conductiva_alarga_absolutas_preserva_intervalo() {
        let model = AbrModel::new();
        let p = Protocol::abr_click(Ear::Right);
        let sano = Subject::default();
        let mut enfermo = Subject::default();
        enfermo.lesions.push(conductive(35.0));
        let v_sano = model
            .components(&p, &sano)
            .iter()
            .find(|c| c.label == "V")
            .unwrap()
            .latency_ms;
        let comps_enf = model.components(&p, &enfermo);
        let v_enf = comps_enf.iter().find(|c| c.label == "V").unwrap().latency_ms;
        // Alarga la latencia absoluta...
        assert!(v_enf > v_sano);
        // ...pero el intervalo I–V se preserva.
        let iv_sano = interval(&model.components(&p, &sano), "I", "V").unwrap();
        let iv_enf = interval(&comps_enf, "I", "V").unwrap();
        assert!((iv_enf - iv_sano).abs() < 0.1, "sano={iv_sano} enfermo={iv_enf}");
    }

    #[test]
    fn coclear_reclutamiento_preserva_latencia_a_alta_intensidad() {
        let model = AbrModel::new();
        let p = Protocol::abr_click(Ear::Right);
        let sano = Subject::default();
        let mut coch = Subject::default();
        coch.lesions.push(cochlear(40.0));
        let v_sano = model
            .components(&p, &sano)
            .iter()
            .find(|c| c.label == "V")
            .unwrap()
            .latency_ms;
        let comps_c = model.components(&p, &coch);
        let v_coch = comps_c.iter().find(|c| c.label == "V").unwrap();
        // A 80 dB la latencia es casi normal (reclutamiento)...
        assert!((v_coch.latency_ms - v_sano).abs() < 0.1, "sano={v_sano} coclear={}", v_coch.latency_ms);
        // ...pero la amplitud cae respecto al sano.
        let amp_sano = model
            .components(&p, &sano)
            .iter()
            .find(|c| c.label == "V")
            .unwrap()
            .amplitude_uv;
        assert!(v_coch.amplitude_uv < amp_sano);
    }

    #[test]
    fn conductiva_vs_coclear_se_distinguen_en_latencia() {
        let model = AbrModel::new();
        let p = Protocol::abr_click(Ear::Right);
        let mut cond = Subject::default();
        cond.lesions.push(conductive(40.0));
        let mut coch = Subject::default();
        coch.lesions.push(cochlear(40.0));
        let v_cond = model
            .components(&p, &cond)
            .iter()
            .find(|c| c.label == "V")
            .unwrap()
            .latency_ms;
        let v_coch = model
            .components(&p, &coch)
            .iter()
            .find(|c| c.label == "V")
            .unwrap()
            .latency_ms;
        // Mismo umbral, distinto mecanismo: la conductiva alarga mas la latencia.
        assert!(v_cond > v_coch + 0.5, "conductiva={v_cond} coclear={v_coch}");
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
        let iv_sano = interval(&model.components(&p, &sano), "I", "V").unwrap();
        let iv_enf = interval(&model.components(&p, &enfermo), "I", "V").unwrap();
        assert!(iv_enf > iv_sano + 0.3, "sano={iv_sano} enfermo={iv_enf}");
    }

    #[test]
    fn toneburst_grave_mas_tardio_que_agudo() {
        let model = AbrModel::new();
        let s = Subject::default();
        let v = |f| {
            model
                .components(&Protocol::abr_toneburst(Ear::Right, f), &s)
                .iter()
                .find(|c| c.label == "V")
                .unwrap()
                .latency_ms
        };
        assert!(v(500.0) > v(4000.0), "500={} 4000={}", v(500.0), v(4000.0));
    }

    #[test]
    fn perdida_en_agudos_afecta_el_tono_agudo_no_el_grave() {
        let model = AbrModel::new();
        let mut s = Subject::default();
        s.lesions.push(Lesion {
            site: LesionSite::Cochlear,
            ear: Ear::Right,
            severity_db: 50.0,
            freq_profile: FreqProfile::HighFrequency,
        });
        let amp = |f| {
            model
                .components(&Protocol::abr_toneburst(Ear::Right, f), &s)
                .iter()
                .find(|c| c.label == "V")
                .map(|c| c.amplitude_uv.abs())
                .unwrap_or(0.0)
        };
        // El tono agudo (4 kHz) cae por la perdida; el grave (500 Hz) se respeta.
        assert!(amp(4000.0) < amp(500.0), "4000={} 500={}", amp(4000.0), amp(500.0));
    }

    #[test]
    fn chirp_da_mas_amplitud_que_click() {
        let model = AbrModel::new();
        let s = Subject::default();
        let v_click = model
            .components(&Protocol::abr_click(Ear::Right), &s)
            .iter()
            .find(|c| c.label == "V")
            .unwrap()
            .amplitude_uv;
        let mut p = Protocol::abr_click(Ear::Right);
        p.stimulus.kind = crate::stimulus::StimulusKind::Chirp {
            kind: crate::stimulus::ChirpKind::CeChirp,
        };
        let v_chirp = model
            .components(&p, &s)
            .iter()
            .find(|c| c.label == "V")
            .unwrap()
            .amplitude_uv;
        assert!(v_chirp > v_click, "chirp={v_chirp} click={v_click}");
    }

    #[test]
    fn ls_chirp_realza_mas_que_ce_chirp() {
        let model = AbrModel::new();
        let s = Subject::default();
        let v = |k| {
            model
                .components(&Protocol::abr_chirp(Ear::Right, k), &s)
                .iter()
                .find(|c| c.label == "V")
                .unwrap()
                .amplitude_uv
        };
        assert!(v(ChirpKind::LsChirp) > v(ChirpKind::CeChirp));
    }

    #[test]
    fn chirp_realza_mas_a_baja_intensidad() {
        let model = AbrModel::new();
        let s = Subject::default();
        let amp = |p: &Protocol| {
            model
                .components(p, &s)
                .iter()
                .find(|c| c.label == "V")
                .unwrap()
                .amplitude_uv
        };
        let ratio = |lvl| {
            let mut click = Protocol::abr_click(Ear::Right);
            click.stimulus.level = Level::DbNhl(lvl);
            let mut chirp = Protocol::abr_chirp(Ear::Right, ChirpKind::CeChirp);
            chirp.stimulus.level = Level::DbNhl(lvl);
            amp(&chirp) / amp(&click)
        };
        // El realce del chirp respecto al click es mayor a baja intensidad.
        assert!(ratio(30.0) > ratio(80.0), "30={} 80={}", ratio(30.0), ratio(80.0));
    }

    #[test]
    fn nbchirp_grave_mas_tardio_que_agudo() {
        let model = AbrModel::new();
        let s = Subject::default();
        let v = |f| {
            model
                .components(&Protocol::abr_nbchirp(Ear::Right, f), &s)
                .iter()
                .find(|c| c.label == "V")
                .unwrap()
                .latency_ms
        };
        assert!(v(500.0) > v(4000.0));
    }

    #[test]
    fn nbchirp_da_mas_amplitud_que_toneburst() {
        let model = AbrModel::new();
        let s = Subject::default();
        let amp = |p| {
            model
                .components(&p, &s)
                .iter()
                .find(|c| c.label == "V")
                .unwrap()
                .amplitude_uv
        };
        let tb = amp(Protocol::abr_toneburst(Ear::Right, 2000.0));
        let ch = amp(Protocol::abr_nbchirp(Ear::Right, 2000.0));
        assert!(ch > tb, "chirp={ch} tone={tb}");
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
        let max_amp = comps.iter().map(|c| c.amplitude_uv.abs()).fold(0.0, f64::max);
        assert!(max_amp < 0.1, "amplitud maxima {max_amp}");
    }
}
