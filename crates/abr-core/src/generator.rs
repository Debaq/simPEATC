//! Generador de curvas ABR.
//!
//! Modela la curva como suma de gaussianas centradas en las latencias de las
//! ondas I, III y V, contaminada con ruido. El sistema FSP (Factor Senal/Promedio)
//! controla la relacion senal/ruido segun el numero de promediaciones: pocas
//! promediaciones => predomina el ruido; muchas => emerge la curva objetivo.

use crate::params::StimParams;
use crate::waveform::{WavePeak, Waveform};

/// Ventana temporal del registro en ms.
pub const DURATION_MS: f64 = 12.0;
/// Intensidad de referencia para las latencias normativas (dB nHL).
const REF_DB: f64 = 75.0;
/// Desplazamiento de latencia por cada 10 dB de variacion (ms).
const SHIFT_PER_10DB: f64 = 0.3;
/// Ancho (sigma) de cada pico gaussiano en ms.
const PEAK_WIDTH_MS: f64 = 0.3;
/// Muestras por curva.
const SAMPLES: usize = 480;

/// Generador determinista de curvas ABR para unos parametros dados.
#[derive(Debug, Clone)]
pub struct AbrGenerator {
    params: StimParams,
}

impl AbrGenerator {
    /// Crea un generador para los parametros indicados.
    pub fn new(params: StimParams) -> Self {
        Self { params }
    }

    /// Picos esperados (I, III, V) ajustados por intensidad.
    ///
    /// A menor intensidad las latencias se retrasan `SHIFT_PER_10DB` ms cada 10 dB.
    pub fn peaks(&self) -> Vec<WavePeak> {
        let shift = (REF_DB - self.params.intensity_db) / 10.0 * SHIFT_PER_10DB;
        vec![
            WavePeak { label: "I", latency_ms: 1.6 + shift, amplitude_uv: 0.25 },
            WavePeak { label: "III", latency_ms: 3.7 + shift, amplitude_uv: 0.35 },
            WavePeak { label: "V", latency_ms: 5.6 + shift, amplitude_uv: 0.50 },
        ]
    }

    /// Relacion senal/ruido en [0, 1] segun las promediaciones.
    ///
    /// 0.0 = ruido puro, 1.0 = curva objetivo limpia. Usa la curva de ajuste
    /// `a * averages^b` heredada del simulador Python (a=0.52991151, b=0.52207181).
    pub fn snr(&self) -> f64 {
        let a = 0.529_911_51_f64;
        let b = 0.522_071_81_f64;
        let v = a * (self.params.averages.max(1) as f64).powf(b) / 30.0;
        v.clamp(0.0, 1.0)
    }

    /// Curva objetivo limpia evaluada en el instante `t` (ms).
    fn target(&self, t: f64) -> f64 {
        self.peaks()
            .iter()
            .map(|p| {
                let d = t - p.latency_ms;
                p.amplitude_uv * (-(d * d) / (2.0 * PEAK_WIDTH_MS * PEAK_WIDTH_MS)).exp()
            })
            .sum()
    }

    /// Genera la curva ABR para los parametros actuales.
    ///
    /// El resultado es determinista: los mismos parametros producen la misma curva.
    pub fn generate(&self) -> Waveform {
        let mut rng = Lcg::new(self.seed());
        let snr = self.snr();
        let mut times = Vec::with_capacity(SAMPLES);
        let mut amps = Vec::with_capacity(SAMPLES);
        for i in 0..SAMPLES {
            let t = DURATION_MS * i as f64 / (SAMPLES as f64 - 1.0);
            let noise = (rng.next_f64() - 0.5) * 0.5;
            let signal = self.target(t);
            times.push(t);
            amps.push(snr * signal + (1.0 - snr) * noise);
        }
        Waveform { times_ms: times, amplitudes_uv: amps }
    }

    /// Semilla determinista derivada de los parametros.
    fn seed(&self) -> u64 {
        let ear = match self.params.ear {
            crate::params::Ear::Left => 1u64,
            crate::params::Ear::Right => 2u64,
        };
        let i = (self.params.intensity_db * 10.0) as u64;
        ear.wrapping_mul(0x9E37_79B9)
            ^ i.wrapping_mul(0x85EB_CA77)
            ^ (self.params.averages as u64).wrapping_mul(0xC2B2_AE3D)
    }
}

/// Generador congruencial lineal minimo, sin dependencias externas.
struct Lcg {
    state: u64,
}

impl Lcg {
    fn new(seed: u64) -> Self {
        Self { state: seed ^ 0xDEAD_BEEF_CAFE_F00D }
    }

    fn next_u64(&mut self) -> u64 {
        // Constantes de Numerical Recipes.
        self.state = self
            .state
            .wrapping_mul(6364136223846793005)
            .wrapping_add(1442695040888963407);
        self.state
    }

    /// Siguiente flotante en [0, 1).
    fn next_f64(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 / (1u64 << 53) as f64
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::params::{Ear, StimParams};

    #[test]
    fn genera_muestras_en_ventana() {
        let g = AbrGenerator::new(StimParams::default());
        let w = g.generate();
        assert_eq!(w.len(), SAMPLES);
        assert!((w.times_ms[0] - 0.0).abs() < 1e-9);
        assert!((w.times_ms[w.len() - 1] - DURATION_MS).abs() < 1e-9);
    }

    #[test]
    fn es_determinista() {
        let p = StimParams::default();
        let a = AbrGenerator::new(p).generate();
        let b = AbrGenerator::new(p).generate();
        assert_eq!(a.amplitudes_uv, b.amplitudes_uv);
    }

    #[test]
    fn mas_promediaciones_sube_snr() {
        let pocas = AbrGenerator::new(StimParams { averages: 50, ..Default::default() });
        let muchas = AbrGenerator::new(StimParams { averages: 4000, ..Default::default() });
        assert!(muchas.snr() > pocas.snr());
    }

    #[test]
    fn menor_intensidad_retrasa_picos() {
        let alta = AbrGenerator::new(StimParams { intensity_db: 75.0, ..Default::default() });
        let baja = AbrGenerator::new(StimParams { intensity_db: 45.0, ..Default::default() });
        let v_alta = alta.peaks().iter().find(|p| p.label == "V").unwrap().latency_ms;
        let v_baja = baja.peaks().iter().find(|p| p.label == "V").unwrap().latency_ms;
        assert!(v_baja > v_alta);
    }

    #[test]
    fn oidos_distintos_dan_ruido_distinto() {
        let od = AbrGenerator::new(StimParams { ear: Ear::Right, averages: 1, ..Default::default() });
        let oi = AbrGenerator::new(StimParams { ear: Ear::Left, averages: 1, ..Default::default() });
        assert_ne!(od.generate().amplitudes_uv, oi.generate().amplitudes_uv);
    }
}
