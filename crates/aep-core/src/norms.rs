//! Datos normativos: embebidos + override externo (MOTOR.md §9).
//!
//! Los valores por defecto se compilan en el binario via `include_str!`, asi
//! que el motor **siempre arranca**. Opcionalmente, un JSON externo editado por
//! el investigador (sin recompilar) los sobreescribe; si el override es invalido
//! se ignora con un aviso y se usa el embebido.
//!
//! La misma estructura ([`NormTable`]) sirve para todas las modalidades
//! tabuladas por ondas (ABR, MLR, ALR…): cambia solo el JSON.

use serde::Deserialize;
use std::path::Path;

/// Valores normativos de una onda.
#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct WaveNorm {
    /// Etiqueta ("I", "V", "Pa"…).
    pub label: String,
    /// Latencia normativa (ms) a la intensidad/tasa de referencia.
    pub latency_ms: f64,
    /// Amplitud normativa (µV), con signo (polaridad de la deflexion).
    pub amplitude_uv: f64,
    /// Ancho (sigma, ms).
    pub width_ms: f64,
    /// Generador anatomico (texto didactico).
    #[serde(default)]
    pub generator: String,
}

/// Tabla normativa por ondas (independiente de la modalidad).
#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct NormTable {
    /// Intensidad de referencia de las latencias (dB nHL).
    pub reference_db_nhl: f64,
    /// Tasa de estimulacion de referencia (Hz).
    pub reference_rate_hz: f64,
    /// Ondas normativas.
    pub waves: Vec<WaveNorm>,
}

/// Alias historico: la tabla del ABR es una `NormTable`.
pub type AbrNorms = NormTable;

const EMBEDDED_ABR: &str = include_str!("../data/norms_abr.json");
const EMBEDDED_MLR: &str = include_str!("../data/norms_mlr.json");
const EMBEDDED_ALR: &str = include_str!("../data/norms_alr.json");

impl NormTable {
    /// Parsea una tabla desde texto JSON.
    pub fn from_json(text: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(text)
    }

    /// Tabla ABR embebida.
    pub fn embedded_abr() -> Self {
        Self::from_json(EMBEDDED_ABR).expect("norms_abr.json embebido invalido")
    }

    /// Tabla MLR embebida.
    pub fn embedded_mlr() -> Self {
        Self::from_json(EMBEDDED_MLR).expect("norms_mlr.json embebido invalido")
    }

    /// Tabla ALR/CAEP embebida.
    pub fn embedded_alr() -> Self {
        Self::from_json(EMBEDDED_ALR).expect("norms_alr.json embebido invalido")
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

    /// Carga la tabla ABR con override opcional. Si `path` es `Some` y el
    /// archivo es valido, lo usa; en cualquier otro caso, el embebido (con aviso
    /// si fallo el parseo).
    pub fn load_abr(path: Option<&Path>) -> Self {
        let Some(path) = path else {
            return Self::embedded_abr();
        };
        match std::fs::read_to_string(path) {
            Ok(text) => match Self::from_json(&text) {
                Ok(norms) if norms.is_valid() => norms,
                Ok(_) => {
                    eprintln!(
                        "aviso: override de normas '{}' no pasa la validacion; uso embebido",
                        path.display()
                    );
                    Self::embedded_abr()
                }
                Err(e) => {
                    eprintln!(
                        "aviso: override de normas '{}' invalido ({e}); uso embebido",
                        path.display()
                    );
                    Self::embedded_abr()
                }
            },
            Err(_) => Self::embedded_abr(),
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
    fn embebido_abr_parsea_y_es_valido() {
        let n = NormTable::embedded_abr();
        assert!(n.is_valid());
        assert_eq!(n.reference_db_nhl, 80.0);
        assert!(n.wave("I").is_some());
        assert!(n.wave("V").is_some());
    }

    #[test]
    fn embebido_mlr_parsea_y_es_valido() {
        let n = NormTable::embedded_mlr();
        assert!(n.is_valid());
        assert!(n.wave("Pa").is_some());
        assert!(n.wave("Nb").is_some());
        // Pa es la onda mas amplia y positiva.
        assert!(n.wave("Pa").unwrap().amplitude_uv > 0.0);
    }

    #[test]
    fn ondas_abr_en_orden_de_latencia() {
        let n = NormTable::embedded_abr();
        let i = n.wave("I").unwrap().latency_ms;
        let v = n.wave("V").unwrap().latency_ms;
        assert!(i < v);
    }

    #[test]
    fn load_sin_path_devuelve_embebido() {
        assert_eq!(NormTable::load_abr(None), NormTable::embedded_abr());
    }

    #[test]
    fn load_con_path_inexistente_cae_a_embebido() {
        let n = NormTable::load_abr(Some(Path::new("/no/existe/norms.json")));
        assert_eq!(n, NormTable::embedded_abr());
    }
}
