//! Curva muestreada y registro resultante de una simulacion.

use crate::component::WavePeak;

/// Curva: pares (tiempo en ms, amplitud en µV).
#[derive(Debug, Clone, Default, PartialEq, serde::Serialize)]
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
#[derive(Debug, Clone, Default, PartialEq, serde::Serialize)]
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

    /// Pico detectado con una etiqueta dada.
    pub fn peak(&self, label: &str) -> Option<&WavePeak> {
        self.detected.iter().find(|w| w.label == label)
    }

    /// Intervalo interpico `b − a` (ms), si ambos picos existen.
    ///
    /// Tipicos en el ABR: `I–III`, `III–V`, `I–V`.
    pub fn interpeak(&self, a: &str, b: &str) -> Option<f64> {
        Some(self.peak(b)?.latency_ms - self.peak(a)?.latency_ms)
    }

    /// Razon de amplitudes onda V / onda I (ratio V/I), si ambas existen.
    ///
    /// Normalmente ≥ 1 en el adulto; un V/I bajo sugiere patologia retrococlear.
    pub fn v_i_ratio(&self) -> Option<f64> {
        let i = self.peak("I")?.amplitude_uv;
        let v = self.peak("V")?.amplitude_uv;
        if i.abs() < 1e-9 {
            return None;
        }
        Some(v / i)
    }

    /// Razon SP/AP de la ECochG (amplitudes absolutas), si ambos existen.
    ///
    /// Normal ≲ 0.4; elevada (> 0.4–0.5) sugiere hidrops endolinfatico (Ménière).
    pub fn sp_ap_ratio(&self) -> Option<f64> {
        let sp = self.peak("SP")?.amplitude_uv.abs();
        let ap = self.peak("AP")?.amplitude_uv.abs();
        if ap < 1e-9 {
            return None;
        }
        Some(sp / ap)
    }
}

/// Registro de un paradigma oddball (P300 / MMN).
///
/// Lleva las tres curvas que se ensenan: respuesta al **estandar** (frecuente),
/// al **desviante** (raro) y la **onda diferencia** (desviante − estandar),
/// donde emergen la MMN y la P300. `detected` lleva los picos medidos sobre la
/// onda diferencia.
#[derive(Debug, Clone, Default, PartialEq, serde::Serialize)]
pub struct OddballRecording {
    /// Respuesta promediada al estimulo estandar.
    pub standard: Waveform,
    /// Respuesta promediada al estimulo desviante.
    pub deviant: Waveform,
    /// Onda diferencia (desviante − estandar).
    pub difference: Waveform,
    /// Picos detectados sobre la onda diferencia (MMN, P3a, P3b).
    pub detected: Vec<WavePeak>,
    /// F_sp de la onda diferencia.
    pub fsp: f64,
    /// Sweeps aceptados del flujo desviante.
    pub accepted_sweeps: u32,
    /// Sweeps rechazados del flujo desviante.
    pub rejected_sweeps: u32,
}

impl OddballRecording {
    /// Pico detectado con una etiqueta dada (p.ej. "MMN", "P3b").
    pub fn peak(&self, label: &str) -> Option<&WavePeak> {
        self.detected.iter().find(|w| w.label == label)
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

    fn rec_con_picos() -> Recording {
        Recording {
            detected: vec![
                WavePeak { label: "I".into(), latency_ms: 1.5, amplitude_uv: 0.25 },
                WavePeak { label: "III".into(), latency_ms: 3.7, amplitude_uv: 0.30 },
                WavePeak { label: "V".into(), latency_ms: 5.6, amplitude_uv: 0.50 },
            ],
            ..Default::default()
        }
    }

    #[test]
    fn intervalos_interpico() {
        let r = rec_con_picos();
        assert!((r.interpeak("I", "V").unwrap() - 4.1).abs() < 1e-9);
        assert!((r.interpeak("I", "III").unwrap() - 2.2).abs() < 1e-9);
        assert!((r.interpeak("III", "V").unwrap() - 1.9).abs() < 1e-9);
        assert!(r.interpeak("I", "X").is_none());
    }

    #[test]
    fn ratio_v_i() {
        let r = rec_con_picos();
        assert!((r.v_i_ratio().unwrap() - 2.0).abs() < 1e-9);
    }
}
