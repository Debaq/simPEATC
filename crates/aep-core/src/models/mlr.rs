//! Modelo de respuesta de latencia media (MLR, Middle Latency Response).
//!
//! Componentes **Na, Pa, Nb, Pb** entre ~10 y 80 ms, generados en la via
//! talamocortical y la corteza auditiva primaria (MOTOR.md §2). A diferencia del
//! ABR (robusto), la MLR depende de:
//! - **Edad**: la **Pa madura tarde** (~10-12 años); en el lactante es pequena
//!   y variable.
//! - **Estado de alerta / sedacion**: el sueno, la sedacion y sobre todo la
//!   anestesia **atenuan** la respuesta cortical.

use super::ResponseModel;
use crate::acquisition::Acquisition;
use crate::component::Component;
use crate::lesion::LesionSite;
use crate::modulation::apply_intensity;
use crate::norms::NormTable;
use crate::protocol::Protocol;
use crate::subject::{ArousalState, Ear, Subject};
use crate::synth::NoiseProfile;

/// Modelo MLR parametrizado por su tabla normativa.
#[derive(Debug, Clone)]
pub struct MlrModel {
    norms: NormTable,
}

impl Default for MlrModel {
    fn default() -> Self {
        Self::new()
    }
}

impl MlrModel {
    /// Modelo con las normas MLR embebidas.
    pub fn new() -> Self {
        Self {
            norms: NormTable::embedded_mlr(),
        }
    }

    /// Modelo con una tabla normativa explicita.
    pub fn with_norms(norms: NormTable) -> Self {
        Self { norms }
    }
}

/// Factor de madurez de la Pa segun la edad (0.2 en el lactante → 1.0 en el
/// adulto). La Pa madura hacia los 10-12 años.
fn maturity_factor(years: f64) -> f64 {
    let m = (years / 10.0).clamp(0.0, 1.0);
    0.2 + 0.8 * m
}

/// Factor de atenuacion por estado de alerta / sedacion.
fn state_factor(state: ArousalState) -> f64 {
    match state {
        ArousalState::Awake => 1.0,
        ArousalState::NaturalSleep => 0.8,
        ArousalState::Sedated => 0.5,
        ArousalState::Anesthetized => 0.3,
    }
}

impl ResponseModel for MlrModel {
    fn components(&self, protocol: &Protocol, subject: &Subject) -> Vec<Component> {
        let stim = &protocol.stimulus;
        let ear = stim.ear;
        let freq = stim.kind.dominant_freq_hz();
        let level = stim.level.as_nhl();
        let delay = stim.transducer.acoustic_delay_ms();
        let years = subject.age.approx_years();

        // Umbral de entrada (conductiva/coclear) que reduce el nivel efectivo.
        let threshold = subject
            .lesions_on(ear)
            .filter(|l| matches!(l.site, LesionSite::Conductive | LesionSite::Cochlear))
            .map(|l| l.threshold_shift_at(freq))
            .fold(0.0, f64::max);
        let effective = level - threshold;

        let amp_factor = maturity_factor(years) * state_factor(subject.state);

        let mut comps = Vec::with_capacity(self.norms.waves.len());
        for w in &self.norms.waves {
            let mut c = Component::gaussian(
                w.label.clone(),
                w.latency_ms,
                w.amplitude_uv,
                w.width_ms,
                w.generator.clone(),
            );
            apply_intensity(&mut c, effective, effective, self.norms.reference_db_nhl);
            // Edad y estado modulan la amplitud cortical.
            c.amplitude_uv *= amp_factor;
            c.latency_ms += delay;
            if c.amplitude_uv.abs() > 1e-6 {
                comps.push(c);
            }
        }
        comps
    }

    fn recommended_acquisition(&self) -> Acquisition {
        Acquisition::mlr_default(Ear::Right)
    }

    fn background_noise(&self, _subject: &Subject) -> NoiseProfile {
        // El EEG cortical de fondo (banda baja) es mayor que en el ABR.
        NoiseProfile::new(1.2)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::subject::{Age, ArousalState};

    fn pa_amp(subject: &Subject) -> f64 {
        let model = MlrModel::new();
        model
            .components(&Protocol::mlr(Ear::Right), subject)
            .iter()
            .find(|c| c.label == "Pa")
            .unwrap()
            .amplitude_uv
            .abs()
    }

    #[test]
    fn adulto_tiene_las_cuatro_ondas() {
        let model = MlrModel::new();
        let comps = model.components(&Protocol::mlr(Ear::Right), &Subject::default());
        for label in ["Na", "Pa", "Nb", "Pb"] {
            assert!(comps.iter().any(|c| c.label == label), "falta {label}");
        }
    }

    #[test]
    fn pa_inmadura_en_el_nino() {
        let adulto = Subject::default();
        let nino = Subject {
            age: Age::Years { value: 3.0 },
            ..Default::default()
        };
        assert!(pa_amp(&nino) < pa_amp(&adulto), "nino vs adulto");
    }

    #[test]
    fn sedacion_y_anestesia_atenuan() {
        let despierto = Subject::default();
        let sedado = Subject {
            state: ArousalState::Sedated,
            ..Default::default()
        };
        let anestesiado = Subject {
            state: ArousalState::Anesthetized,
            ..Default::default()
        };
        assert!(pa_amp(&sedado) < pa_amp(&despierto));
        assert!(pa_amp(&anestesiado) < pa_amp(&sedado));
    }

    #[test]
    fn lactante_pa_muy_pequena() {
        let bebe = Subject {
            age: Age::Postnatal { days: 30 },
            ..Default::default()
        };
        let adulto = Subject::default();
        assert!(pa_amp(&bebe) < 0.5 * pa_amp(&adulto));
    }
}
