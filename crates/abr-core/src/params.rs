//! Parametros de estimulacion de un registro ABR.

/// Oido estimulado.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Ear {
    /// Oido izquierdo (OI).
    Left,
    /// Oido derecho (OD).
    Right,
}

impl Ear {
    /// Etiqueta clinica en espanol ("OD" / "OI").
    pub fn label(self) -> &'static str {
        match self {
            Ear::Left => "OI",
            Ear::Right => "OD",
        }
    }
}

/// Parametros de un barrido de estimulacion.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct StimParams {
    /// Oido estimulado.
    pub ear: Ear,
    /// Intensidad del estimulo en dB nHL.
    pub intensity_db: f64,
    /// Numero de promediaciones acumuladas.
    pub averages: u32,
}

impl Default for StimParams {
    fn default() -> Self {
        Self {
            ear: Ear::Right,
            intensity_db: 75.0,
            averages: 2000,
        }
    }
}
