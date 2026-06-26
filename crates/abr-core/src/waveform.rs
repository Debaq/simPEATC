//! Representacion de una curva ABR muestreada.

/// Curva ABR: pares (tiempo en ms, amplitud en uV).
#[derive(Debug, Clone, Default)]
pub struct Waveform {
    /// Eje temporal en milisegundos.
    pub times_ms: Vec<f64>,
    /// Amplitud en microvoltios para cada instante.
    pub amplitudes_uv: Vec<f64>,
}

impl Waveform {
    /// Numero de muestras.
    pub fn len(&self) -> usize {
        self.times_ms.len()
    }

    /// `true` si la curva no tiene muestras.
    pub fn is_empty(&self) -> bool {
        self.times_ms.is_empty()
    }

    /// Itera sobre pares (tiempo_ms, amplitud_uv).
    pub fn points(&self) -> impl Iterator<Item = (f64, f64)> + '_ {
        self.times_ms
            .iter()
            .copied()
            .zip(self.amplitudes_uv.iter().copied())
    }
}

/// Pico identificable de una onda ABR (I, III, V, ...).
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct WavePeak {
    /// Etiqueta de la onda (p. ej. "I", "III", "V").
    pub label: &'static str,
    /// Latencia absoluta del pico en ms.
    pub latency_ms: f64,
    /// Amplitud del pico en uV.
    pub amplitude_uv: f64,
}
