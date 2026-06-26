//! Curva muestreada y registro resultante de una simulacion.

use crate::component::WavePeak;

/// Curva: pares (tiempo en ms, amplitud en µV).
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Waveform {
    /// Eje temporal en milisegundos (relativo al estimulo).
    pub times_ms: Vec<f64>,
    /// Amplitud en microvoltios para cada instante.
    pub amplitudes_uv: Vec<f64>,
}

impl Waveform {
    /// Crea una curva a partir de ejes ya calculados.
    pub fn new(times_ms: Vec<f64>, amplitudes_uv: Vec<f64>) -> Self {
        debug_assert_eq!(times_ms.len(), amplitudes_uv.len());
        Self {
            times_ms,
            amplitudes_uv,
        }
    }

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

    /// Amplitud maxima absoluta (para escalado de graficos).
    pub fn max_abs_uv(&self) -> f64 {
        self.amplitudes_uv
            .iter()
            .fold(0.0_f64, |m, &a| m.max(a.abs()))
    }
}

/// Registro completo devuelto por el motor.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Recording {
    /// Una curva por canal del montaje.
    pub channels: Vec<Waveform>,
    /// Picos detectados sobre la curva promediada.
    pub detected: Vec<WavePeak>,
    /// Factor senal/promedio (F_sp) alcanzado.
    pub fsp: f64,
    /// Sweeps aceptados (promediados).
    pub accepted_sweeps: u32,
    /// Sweeps rechazados por artefacto.
    pub rejected_sweeps: u32,
}

impl Recording {
    /// Canal principal (primero del montaje), si existe.
    pub fn primary(&self) -> Option<&Waveform> {
        self.channels.first()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn longitud_y_vacio() {
        let w = Waveform::new(vec![0.0, 1.0], vec![0.1, -0.2]);
        assert_eq!(w.len(), 2);
        assert!(!w.is_empty());
        assert!(Waveform::default().is_empty());
    }

    #[test]
    fn max_abs() {
        let w = Waveform::new(vec![0.0, 1.0, 2.0], vec![0.1, -0.5, 0.3]);
        assert!((w.max_abs_uv() - 0.5).abs() < 1e-9);
    }
}
