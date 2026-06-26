//! El estimulo acustico y sus parametros.

use crate::subject::Ear;
use crate::units::Level;

/// Ventana de envolvente para los tone-burst (rampa de subida/bajada).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RampWindow {
    /// Lineal.
    Linear,
    /// Hanning (coseno elevado).
    Hanning,
    /// Blackman.
    Blackman,
    /// Gaussiana.
    Gaussian,
}

/// Tipo de chirp (compensa la dispersion de la onda viajera coclear).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ChirpKind {
    /// CE-Chirp (banda ancha).
    CeChirp,
    /// LS-Chirp (Level-Specific).
    LsChirp,
}

/// Token de habla para potenciales cognitivos.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SpeechToken {
    /// Silaba /ba/.
    Ba,
    /// Silaba /da/.
    Da,
}

/// Banda del ruido (enmascaramiento).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NoiseBand {
    /// Ruido blanco.
    White,
    /// Banda estrecha centrada en una frecuencia.
    NarrowBand,
}

/// Naturaleza del estimulo.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum StimulusKind {
    /// Click de banda ancha (ABR clasico).
    Click {
        /// Duracion del pulso en microsegundos (tipico 100 µs).
        duration_us: f64,
    },
    /// Tone-burst especifico en frecuencia.
    ToneBurst {
        /// Frecuencia de la portadora (Hz).
        freq_hz: f64,
        /// Ciclos de subida.
        cycles_rise: u8,
        /// Ciclos de meseta.
        cycles_plateau: u8,
        /// Ciclos de bajada.
        cycles_fall: u8,
        /// Ventana de envolvente.
        window: RampWindow,
    },
    /// Chirp.
    Chirp {
        /// Variante.
        kind: ChirpKind,
    },
    /// Estimulo de habla (cognitivos).
    Speech {
        /// Token.
        token: SpeechToken,
    },
    /// Ruido (enmascaramiento).
    Noise {
        /// Banda.
        band: NoiseBand,
    },
}

impl StimulusKind {
    /// Frecuencia dominante del estimulo en Hz, para ponderar perfiles de
    /// perdida. El click (banda ancha) se trata como ~2-4 kHz efectivos.
    pub fn dominant_freq_hz(self) -> f64 {
        match self {
            StimulusKind::Click { .. } | StimulusKind::Chirp { .. } => 2828.0, // ~media geom. 2-4 kHz
            StimulusKind::ToneBurst { freq_hz, .. } => freq_hz,
            StimulusKind::Speech { .. } => 1000.0,
            StimulusKind::Noise { .. } => 2000.0,
        }
    }
}

/// Polaridad del estimulo.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Polarity {
    /// Rarefaccion.
    Rarefaction,
    /// Condensacion.
    Condensation,
    /// Alternante (cancela el microfonico coclear).
    Alternating,
}

/// Transductor de salida.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Transducer {
    /// Auricular de insercion (delay acustico ~0.9 ms).
    Insert,
    /// Supraaural (cascos).
    Supraaural,
    /// Vibrador oseo.
    BoneConductor,
    /// Campo libre (altavoz).
    FreeField,
}

impl Transducer {
    /// Retardo acustico introducido por el transductor (ms).
    ///
    /// Los insertos anaden el transito por el tubo (~0.9 ms); el resto ~0.
    pub fn acoustic_delay_ms(self) -> f64 {
        match self {
            Transducer::Insert => 0.9,
            _ => 0.0,
        }
    }
}

/// Enmascaramiento contralateral.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Masking {
    /// Nivel del ruido enmascarante.
    pub level: Level,
    /// Banda del ruido.
    pub band: NoiseBand,
}

/// Estimulo completo.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Stimulus {
    /// Tipo.
    pub kind: StimulusKind,
    /// Oido estimulado.
    pub ear: Ear,
    /// Polaridad.
    pub polarity: Polarity,
    /// Nivel.
    pub level: Level,
    /// Tasa de estimulacion (Hz), p.ej. 11.1, 27.7.
    pub rate_hz: f64,
    /// Transductor.
    pub transducer: Transducer,
    /// Enmascaramiento contralateral opcional.
    pub masking: Option<Masking>,
}

impl Stimulus {
    /// Click ABR estandar: 100 µs, rarefaccion, 80 dB nHL, 11.1/s, inserto.
    pub fn click_default(ear: Ear) -> Self {
        Self {
            kind: StimulusKind::Click { duration_us: 100.0 },
            ear,
            polarity: Polarity::Rarefaction,
            level: Level::DbNhl(80.0),
            rate_hz: 11.1,
            transducer: Transducer::Insert,
            masking: None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn click_default_es_80db_inserto() {
        let s = Stimulus::click_default(Ear::Right);
        assert_eq!(s.level.as_nhl(), 80.0);
        assert_eq!(s.transducer, Transducer::Insert);
        assert!((s.transducer.acoustic_delay_ms() - 0.9).abs() < 1e-9);
    }

    #[test]
    fn toneburst_frecuencia_dominante() {
        let k = StimulusKind::ToneBurst {
            freq_hz: 500.0,
            cycles_rise: 2,
            cycles_plateau: 1,
            cycles_fall: 2,
            window: RampWindow::Hanning,
        };
        assert_eq!(k.dominant_freq_hz(), 500.0);
    }
}
