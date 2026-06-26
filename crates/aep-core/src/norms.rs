//! Datos normativos: embebidos + override externo (MOTOR.md §9).
//!
//! Los valores por defecto se compilan en el binario via `include_str!`, asi
//! que el motor **siempre arranca**. Opcionalmente, un JSON externo editado por
//! el investigador (sin recompilar) los sobreescribe; si el override es invalido
//! se ignora con un aviso y se usa el embebido.

use serde::Deserialize;
use std::path::Path;

/// Valores normativos de una onda.
#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct WaveNorm {
    /// Etiqueta ("I", "III", "V"…).
    pub label: String,
    /// Latencia normativa (ms) a la intensidad/tasa de referencia.
    pub latency_ms: f64,
    /// Amplitud normativa (µV).
    pub amplitude_uv: f64,
    /// Ancho (sigma, ms).
    pub width_ms: f64,
    /// Generador anatomico (texto didactico).
    #[serde(default)]
    pub generator: String,
}

/// Tabla normativa del ABR.
#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct AbrNorms {
    /// Intensidad de referencia de las latencias (dB nHL).
    pub reference_db_nhl: f64,
    /// Tasa de estimulacion de referencia (Hz).
    pub reference_rate_hz: f64,
    /// Ondas normativas.
    pub waves: Vec<WaveNorm>,
}

/// JSON embebido en el binario.
const EMBEDDED_ABR: &str = include_str!("../data/norms_abr.json");

impl AbrNorms {
    /// Tabla embebida (siempre disponible). Panica solo si el JSON compilado es
    /// invalido, lo que seria un bug detectado por los tests.
    pub fn embedded() -> Self {
        serde_json::from_str(EMBEDDED_ABR).expect("norms_abr.json embebido invalido")
    }

    /// Validacion minima de esquema.
    pub fn is_valid(&self) -> bool {
        self.reference_db_nhl > 0.0
            && self.reference_rate_hz > 0.0
            && !self.waves.is_empty()
            && self
                .waves
                .iter()
                .all(|w| w.latency_ms > 0.0 && w.width_ms > 0.0 && !w.label.is_empty())
    }

    /// Carga con override opcional. Si `path` es `Some` y el archivo es valido,
    /// lo usa; en cualquier otro caso, el embebido (con aviso si fallo el parseo).
    pub fn load(path: Option<&Path>) -> Self {
        let Some(path) = path else {
            return Self::embedded();
        };
        match std::fs::read_to_string(path) {
            Ok(text) => match serde_json::from_str::<AbrNorms>(&text) {
                Ok(norms) if norms.is_valid() => norms,
                Ok(_) => {
                    eprintln!(
                        "aviso: override de normas '{}' no pasa la validacion; uso embebido",
                        path.display()
                    );
                    Self::embedded()
                }
                Err(e) => {
                    eprintln!(
                        "aviso: override de normas '{}' invalido ({e}); uso embebido",
                        path.display()
                    );
                    Self::embedded()
                }
            },
            Err(_) => Self::embedded(),
        }
    }

    /// Busca una onda por etiqueta.
    pub fn wave(&self, label: &str) -> Option<&WaveNorm> {
        self.waves.iter().find(|w| w.label == label)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn embebido_parsea_y_es_valido() {
        let n = AbrNorms::embedded();
        assert!(n.is_valid());
        assert_eq!(n.reference_db_nhl, 80.0);
        assert!(n.wave("I").is_some());
        assert!(n.wave("III").is_some());
        assert!(n.wave("V").is_some());
    }

    #[test]
    fn ondas_en_orden_de_latencia() {
        let n = AbrNorms::embedded();
        let i = n.wave("I").unwrap().latency_ms;
        let iii = n.wave("III").unwrap().latency_ms;
        let v = n.wave("V").unwrap().latency_ms;
        assert!(i < iii && iii < v);
    }

    #[test]
    fn load_sin_path_devuelve_embebido() {
        let n = AbrNorms::load(None);
        assert_eq!(n, AbrNorms::embedded());
    }

    #[test]
    fn load_con_path_inexistente_cae_a_embebido() {
        let n = AbrNorms::load(Some(Path::new("/no/existe/norms.json")));
        assert_eq!(n, AbrNorms::embedded());
    }
}
