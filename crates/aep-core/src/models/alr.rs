//! Modelo de respuesta auditiva tardia (ALR / CAEP).
//!
//! Complejo **P1-N1-P2-N2** entre ~50 y 250 ms, generado en la corteza auditiva
//! secundaria y de asociacion (MOTOR.md §2). Es la modalidad mas sensible al
//! estado del sujeto:
//! - **Estado de alerta**: necesita vigilia; el sueno y la sedacion la atenuan
//!   mucho mas que al ABR o la MLR.
//! - **Atencion**: atender al estimulo **realza la N1** (y la N2); ignorarlo la
//!   reduce. Este es el puente hacia los potenciales cognitivos (P300/MMN).

use super::ResponseModel;
use crate::acquisition::Acquisition;
use crate::component::Component;
use crate::lesion::LesionSite;
use crate::modulation::apply_intensity;
use crate::norms::NormTable;
use crate::protocol::Protocol;
use crate::subject::{ArousalState, Attention, Ear, Subject};
use crate::synth::NoiseProfile;

/// Modelo ALR/CAEP parametrizado por su tabla normativa.
#[derive(Debug, Clone)]
pub struct AlrModel {
    norms: NormTable,
}

impl Default for AlrModel {
    fn default() -> Self {
        Self::new()
    }
}

impl AlrModel {
    /// Modelo con las normas ALR embebidas.
    pub fn new() -> Self {
        Self {
            norms: NormTable::embedded_alr(),
        }
    }

    /// Modelo con una tabla normativa explicita.
    pub fn with_norms(norms: NormTable) -> Self {
        Self { norms }
    }
}

/// Atenuacion por estado de alerta (la ALR exige vigilia).
fn state_factor(state: ArousalState) -> f64 {
    match state {
        ArousalState::Awake => 1.0,
        ArousalState::NaturalSleep => 0.5,
        ArousalState::Sedated => 0.3,
        ArousalState::Anesthetized => 0.15,
    }
}

/// Realce de los componentes atencionales (N1/N2) por la atencion.
fn attention_factor(attention: Attention) -> f64 {
    match attention {
        Attention::Active => 1.3,
        Attention::Passive => 1.0,
        Attention::Ignoring => 0.85,
    }
}

impl ResponseModel for AlrModel {
    fn components(&self, protocol: &Protocol, subject: &Subject) -> Vec<Component> {
        let stim = &protocol.stimulus;
        let ear = stim.ear;
        let freq = stim.kind.dominant_freq_hz();
        let level = stim.level.as_nhl();
        let delay = stim.transducer.acoustic_delay_ms();

        let threshold = subject
            .lesions_on(ear)
            .filter(|l| matches!(l.site, LesionSite::Conductive | LesionSite::Cochlear))
            .map(|l| l.threshold_shift_at(freq))
            .fold(0.0, f64::max);
        let effective = level - threshold;

        let sf = state_factor(subject.state);
        let af = attention_factor(subject.attention);

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
            c.amplitude_uv *= sf;
            // La atencion realza los componentes negativos tardios (N1/N2).
            if c.label == "N1" || c.label == "N2" {
                c.amplitude_uv *= af;
            }
            c.latency_ms += delay;
            if c.amplitude_uv.abs() > 1e-6 {
                comps.push(c);
            }
        }
        comps
    }

    fn recommended_acquisition(&self) -> Acquisition {
        Acquisition::alr_default(Ear::Right)
    }

    fn background_noise(&self, _subject: &Subject) -> NoiseProfile {
        // EEG cortical de fondo grande en la banda lenta (1-30 Hz, ritmo alfa).
        NoiseProfile::new(2.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn n1_amp(subject: &Subject) -> f64 {
        AlrModel::new()
            .components(&Protocol::alr(Ear::Right), subject)
            .iter()
            .find(|c| c.label == "N1")
            .unwrap()
            .amplitude_uv
            .abs()
    }

    #[test]
    fn adulto_despierto_tiene_p1_n1_p2_n2() {
        let comps = AlrModel::new().components(&Protocol::alr(Ear::Right), &Subject::default());
        for label in ["P1", "N1", "P2", "N2"] {
            assert!(comps.iter().any(|c| c.label == label), "falta {label}");
        }
    }

    #[test]
    fn n1_es_negativa_y_la_mayor() {
        let comps = AlrModel::new().components(&Protocol::alr(Ear::Right), &Subject::default());
        let n1 = comps.iter().find(|c| c.label == "N1").unwrap();
        assert!(n1.amplitude_uv < 0.0);
        let max_abs = comps.iter().map(|c| c.amplitude_uv.abs()).fold(0.0, f64::max);
        assert!((n1.amplitude_uv.abs() - max_abs).abs() < 1e-9);
    }

    #[test]
    fn sueno_atenua_la_respuesta() {
        let despierto = Subject::default();
        let dormido = Subject {
            state: ArousalState::NaturalSleep,
            ..Default::default()
        };
        assert!(n1_amp(&dormido) < n1_amp(&despierto));
    }

    #[test]
    fn atencion_activa_realza_n1() {
        let pasivo = Subject {
            attention: Attention::Passive,
            ..Default::default()
        };
        let activo = Subject {
            attention: Attention::Active,
            ..Default::default()
        };
        let ignorando = Subject {
            attention: Attention::Ignoring,
            ..Default::default()
        };
        assert!(n1_amp(&activo) > n1_amp(&pasivo));
        assert!(n1_amp(&ignorando) < n1_amp(&pasivo));
    }
}
