//! El protocolo: que se estimula, como se adquiere y bajo que paradigma.

use crate::acquisition::Acquisition;
use crate::stimulus::Stimulus;
use crate::subject::Ear;

/// Modalidad de potencial evocado. Selecciona el `ResponseModel` del motor.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Modality {
    /// Electrococleografia (0-5 ms).
    ECochG,
    /// ABR / PEATC (0-10/15 ms).
    Abr,
    /// Middle Latency Response (10-80 ms).
    Mlr,
    /// Auditory Late Response / CAEP (50-300 ms).
    Alr,
    /// P300 (cognitivo).
    P300,
    /// Mismatch Negativity (cognitivo preatencional).
    Mmn,
    /// Auditory Steady-State Response.
    Assr,
}

/// Paradigma de estimulacion.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Paradigm {
    /// Un estimulo repetido (ECochG…ALR).
    Transient,
    /// Oddball: estandar frecuente + desviante raro (P300/MMN).
    Oddball {
        /// Estimulo estandar (frecuente).
        standard: Stimulus,
        /// Estimulo desviante (raro).
        deviant: Stimulus,
        /// Probabilidad del desviante `[0, 1]`.
        deviant_prob: f64,
    },
    /// Estado estable: portadora modulada (ASSR).
    SteadyState {
        /// Frecuencia de modulacion (Hz).
        mod_freq_hz: f64,
    },
}

/// Protocolo completo.
#[derive(Debug, Clone, PartialEq)]
pub struct Protocol {
    /// Modalidad.
    pub modality: Modality,
    /// Estimulo.
    pub stimulus: Stimulus,
    /// Adquisicion.
    pub acquisition: Acquisition,
    /// Paradigma.
    pub paradigm: Paradigm,
}

impl Protocol {
    /// Protocolo ABR por click estandar para un oido.
    pub fn abr_click(ear: Ear) -> Self {
        Self {
            modality: Modality::Abr,
            stimulus: Stimulus::click_default(ear),
            acquisition: Acquisition::abr_default(ear),
            paradigm: Paradigm::Transient,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn abr_click_es_transitorio() {
        let p = Protocol::abr_click(Ear::Right);
        assert_eq!(p.modality, Modality::Abr);
        assert_eq!(p.paradigm, Paradigm::Transient);
    }
}
