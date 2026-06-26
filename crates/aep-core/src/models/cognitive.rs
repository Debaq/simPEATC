//! Modelo de los potenciales cognitivos (P300 / MMN) — paradigma oddball.
//!
//! A diferencia de las demas modalidades, aqui hay **dos flujos** de estimulo:
//! un estandar frecuente y un desviante raro. El motor genera la respuesta a
//! cada uno y la **onda diferencia** (desviante − estandar), donde emergen:
//! - **MMN** (Mismatch Negativity): negatividad ~150-250 ms, **preatencional**
//!   (aparece aunque el sujeto no atienda); escala con la discriminabilidad
//!   estandar/desviante.
//! - **P3a**: positividad frontal ~250 ms (orientacion atencional involuntaria).
//! - **P3b**: positividad parietal ~300-400 ms que **requiere atencion activa**;
//!   crece con la rareza del desviante y decae con la edad (↑ latencia, ↓ amplitud).
//!
//! Comparte con la ALR la respuesta cortical obligatoria (P1/N1/P2), que se
//! cancela en la onda diferencia (MOTOR.md §11).

use crate::acquisition::Acquisition;
use crate::component::Component;
use crate::models::alr::AlrModel;
use crate::models::ResponseModel;
use crate::protocol::{Modality, Paradigm, Protocol};
use crate::stimulus::Stimulus;
use crate::subject::{Attention, Subject};

/// Modelo cognitivo para una modalidad oddball (P300 o MMN).
#[derive(Debug, Clone)]
pub struct CognitiveModel {
    modality: Modality,
    alr: AlrModel,
}

impl CognitiveModel {
    /// Crea el modelo para la modalidad dada (`P300` o `Mmn`).
    pub fn new(modality: Modality) -> Self {
        Self {
            modality,
            alr: AlrModel::new(),
        }
    }

    /// Respuesta cortical **obligatoria** (P1/N1/P2) a un estimulo dado.
    ///
    /// Es comun al estandar y al desviante, por eso se cancela en la diferencia.
    pub fn obligatory(&self, stimulus: &Stimulus, subject: &Subject) -> Vec<Component> {
        let proto = Protocol {
            modality: Modality::Alr,
            stimulus: *stimulus,
            acquisition: Acquisition::alr_default(stimulus.ear),
            paradigm: Paradigm::Transient,
        };
        self.alr.components(&proto, subject)
    }

    /// Componentes de la **onda diferencia** (MMN, y P3a/P3b en P300).
    pub fn difference(
        &self,
        standard: &Stimulus,
        deviant: &Stimulus,
        deviant_prob: f64,
        subject: &Subject,
    ) -> Vec<Component> {
        let discrim = discriminability(standard, deviant);
        let years = subject.age.approx_years();
        let mut comps = Vec::new();

        // MMN: preatencional (no depende de la atencion), escala con disparidad.
        comps.push(Component::gaussian(
            "MMN",
            180.0,
            -1.5 * discrim,
            20.0,
            "Corteza auditiva (deteccion preatencional de disparidad)",
        ));

        if matches!(self.modality, Modality::P300) {
            // P3a: orientacion atencional involuntaria (novelty/saliencia).
            comps.push(Component::gaussian(
                "P3a",
                260.0,
                0.8 * discrim,
                22.0,
                "Corteza frontal (orientacion atencional)",
            ));

            // P3b: requiere atencion activa; crece con la rareza y decae con edad.
            let rarity = (1.0 - deviant_prob).clamp(0.0, 1.0);
            let att = p3b_attention(subject.attention);
            let amp = 1.6 * discrim * rarity * att * p3b_age_amplitude(years);
            if amp > 1e-3 {
                comps.push(Component::gaussian(
                    "P3b",
                    320.0 + p3b_age_latency(years),
                    amp,
                    35.0,
                    "Corteza parietal (actualizacion de contexto)",
                ));
            }
        }
        comps
    }
}

/// Discriminabilidad estandar/desviante en `[0.05, 1]` (por frecuencia o nivel).
fn discriminability(standard: &Stimulus, deviant: &Stimulus) -> f64 {
    let df = (standard.kind.dominant_freq_hz() - deviant.kind.dominant_freq_hz()).abs();
    let freq_disc = (df / 1000.0).clamp(0.0, 1.0);
    let dl = (standard.level.as_nhl() - deviant.level.as_nhl()).abs();
    let level_disc = (dl / 30.0).clamp(0.0, 1.0);
    freq_disc.max(level_disc).clamp(0.05, 1.0)
}

/// Peso de la atencion sobre la P3b (sin atencion no hay P3b).
fn p3b_attention(attention: Attention) -> f64 {
    match attention {
        Attention::Active => 1.0,
        Attention::Passive => 0.2,
        Attention::Ignoring => 0.0,
    }
}

/// La latencia de la P3b aumenta ~1.5 ms/año por encima de los 25 años.
fn p3b_age_latency(years: f64) -> f64 {
    (years - 25.0).max(0.0) * 1.5
}

/// La amplitud de la P3b decae con la edad.
fn p3b_age_amplitude(years: f64) -> f64 {
    (1.0 - (years - 25.0).max(0.0) * 0.005).clamp(0.4, 1.0)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::subject::{Attention, Ear};

    fn p300() -> CognitiveModel {
        CognitiveModel::new(Modality::P300)
    }

    fn std_dev() -> (Stimulus, Stimulus) {
        (
            Stimulus::toneburst_default(Ear::Right, 1000.0),
            Stimulus::toneburst_default(Ear::Right, 2000.0),
        )
    }

    fn amp(comps: &[Component], label: &str) -> Option<f64> {
        comps.iter().find(|c| c.label == label).map(|c| c.amplitude_uv)
    }

    #[test]
    fn p3b_requiere_atencion_activa() {
        let (s, d) = std_dev();
        let activo = Subject {
            attention: Attention::Active,
            ..Default::default()
        };
        let ignorando = Subject {
            attention: Attention::Ignoring,
            ..Default::default()
        };
        assert!(amp(&p300().difference(&s, &d, 0.2, &activo), "P3b").is_some());
        assert!(amp(&p300().difference(&s, &d, 0.2, &ignorando), "P3b").is_none());
    }

    #[test]
    fn mmn_es_preatencional() {
        let (s, d) = std_dev();
        let ignorando = Subject {
            attention: Attention::Ignoring,
            ..Default::default()
        };
        // La MMN aparece aunque el sujeto ignore el estimulo.
        let mmn = amp(&p300().difference(&s, &d, 0.2, &ignorando), "MMN").unwrap();
        assert!(mmn < 0.0, "MMN deberia ser negativa: {mmn}");
    }

    #[test]
    fn mayor_disparidad_mayor_mmn() {
        let chico = (
            Stimulus::toneburst_default(Ear::Right, 1000.0),
            Stimulus::toneburst_default(Ear::Right, 1100.0),
        );
        let grande = std_dev();
        let s = Subject::default();
        let m_chico = amp(&p300().difference(&chico.0, &chico.1, 0.2, &s), "MMN")
            .unwrap()
            .abs();
        let m_grande = amp(&p300().difference(&grande.0, &grande.1, 0.2, &s), "MMN")
            .unwrap()
            .abs();
        assert!(m_grande > m_chico, "chico={m_chico} grande={m_grande}");
    }

    #[test]
    fn mas_raro_mayor_p3b() {
        let (s, d) = std_dev();
        let subj = Subject {
            attention: Attention::Active,
            ..Default::default()
        };
        let frecuente = amp(&p300().difference(&s, &d, 0.4, &subj), "P3b").unwrap();
        let raro = amp(&p300().difference(&s, &d, 0.1, &subj), "P3b").unwrap();
        assert!(raro > frecuente, "p=0.4 → {frecuente}, p=0.1 → {raro}");
    }

    #[test]
    fn mmn_modalidad_no_tiene_p3b() {
        let (s, d) = std_dev();
        let model = CognitiveModel::new(Modality::Mmn);
        let comps = model.difference(&s, &d, 0.2, &Subject::default());
        assert!(comps.iter().any(|c| c.label == "MMN"));
        assert!(comps.iter().all(|c| c.label != "P3b"));
    }

    #[test]
    fn p3b_mas_tardio_en_el_adulto_mayor() {
        let (s, d) = std_dev();
        let joven = Subject {
            attention: Attention::Active,
            ..Default::default()
        };
        let mayor = Subject {
            attention: Attention::Active,
            age: crate::subject::Age::Years { value: 70.0 },
            ..Default::default()
        };
        let lat = |subj| {
            p300()
                .difference(&s, &d, 0.2, subj)
                .into_iter()
                .find(|c| c.label == "P3b")
                .unwrap()
                .latency_ms
        };
        assert!(lat(&mayor) > lat(&joven));
    }
}
