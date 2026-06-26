//! Unidades fuertemente tipadas.
//!
//! El objetivo es no confundir referencias de decibelios entre si (dB nHL vs
//! dB SPL vs dB peSPL). El nivel de estimulo se modela con [`Level`], que lleva
//! la referencia en el propio tipo. Las conversiones entre referencias dependen
//! del estimulo (espectro), el transductor y la frecuencia; en esta capa se usan
//! offsets *nominales* de banda ancha (click) marcados como provisionales hasta
//! la validacion clinica (ver MOTOR.md §15.2).

/// Nivel de un estimulo, etiquetado con su referencia de decibelios.
///
/// - `DbNhl`: dB nHL (normal Hearing Level), referencia clinica habitual del ABR.
/// - `DbSpl`: dB SPL (Sound Pressure Level), referencia fisica.
/// - `DbHl`: dB HL (Hearing Level audiometrico).
/// - `DbPeSpl`: dB peSPL (peak-equivalent SPL), usado con clicks/transitorios.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Level {
    /// dB nHL.
    DbNhl(f64),
    /// dB SPL.
    DbSpl(f64),
    /// dB HL.
    DbHl(f64),
    /// dB peSPL.
    DbPeSpl(f64),
}

/// Offset nominal click insert peSPL→nHL (dB). Provisional; revisar §15.2.
const PESPL_TO_NHL: f64 = 35.5;
/// Offset nominal banda ancha SPL→nHL (dB). Provisional; revisar §15.2.
const SPL_TO_NHL: f64 = 30.0;

impl Level {
    /// Valor numerico crudo en dB, sin convertir de referencia.
    pub fn value(self) -> f64 {
        match self {
            Level::DbNhl(v) | Level::DbSpl(v) | Level::DbHl(v) | Level::DbPeSpl(v) => v,
        }
    }

    /// Nivel efectivo en **dB nHL**.
    ///
    /// Conversion nominal de banda ancha (click). Los offsets son provisionales
    /// y dependen en realidad de estimulo/transductor/frecuencia (§15.2). El
    /// motor de Capa 0 trabaja internamente en dB nHL.
    pub fn as_nhl(self) -> f64 {
        match self {
            Level::DbNhl(v) => v,
            Level::DbHl(v) => v, // ≈ para banda ancha
            Level::DbPeSpl(v) => v - PESPL_TO_NHL,
            Level::DbSpl(v) => v - SPL_TO_NHL,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn nhl_es_identidad() {
        assert_eq!(Level::DbNhl(70.0).as_nhl(), 70.0);
    }

    #[test]
    fn pespl_resta_offset_click() {
        assert!((Level::DbPeSpl(105.5).as_nhl() - 70.0).abs() < 1e-9);
    }

    #[test]
    fn value_devuelve_crudo() {
        assert_eq!(Level::DbSpl(90.0).value(), 90.0);
    }
}
