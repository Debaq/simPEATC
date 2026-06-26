//! Filtros IIR Butterworth implementados como cascada de biquads.
//!
//! Sin dependencias externas. Cada seccion de segundo orden usa los coeficientes
//! del "Audio EQ Cookbook" (Robert Bristow-Johnson) con el factor Q derivado de
//! la posicion de los polos Butterworth. Un Butterworth de orden N se construye
//! como N/2 secciones de 2º orden (mas una de 1º si N es impar). El pasa-banda
//! es un pasa-altos en cascada con un pasa-bajos; el notch es una seccion aparte.
//!
//! Estructura de cada biquad: Direct Form II Transposed (buena estabilidad
//! numerica con `f64`).

use crate::acquisition::Bandpass;
use std::f64::consts::{PI, TAU};

/// Seccion de segundo orden (biquad). `a0` ya esta normalizado a 1.
#[derive(Debug, Clone, Copy)]
pub struct Biquad {
    b0: f64,
    b1: f64,
    b2: f64,
    a1: f64,
    a2: f64,
    z1: f64,
    z2: f64,
}

impl Biquad {
    /// Construye normalizando por `a0`.
    fn new(b0: f64, b1: f64, b2: f64, a0: f64, a1: f64, a2: f64) -> Self {
        Self {
            b0: b0 / a0,
            b1: b1 / a0,
            b2: b2 / a0,
            a1: a1 / a0,
            a2: a2 / a0,
            z1: 0.0,
            z2: 0.0,
        }
    }

    /// Procesa una muestra (Direct Form II Transposed).
    #[inline]
    pub fn process(&mut self, x: f64) -> f64 {
        let y = self.b0 * x + self.z1;
        self.z1 = self.b1 * x - self.a1 * y + self.z2;
        self.z2 = self.b2 * x - self.a2 * y;
        y
    }

    /// Reinicia el estado interno.
    pub fn reset(&mut self) {
        self.z1 = 0.0;
        self.z2 = 0.0;
    }
}

/// Recorta la frecuencia de corte al rango valido `(0, Nyquist)`.
fn clamp_fc(fc: f64, fs: f64) -> f64 {
    let nyq = fs / 2.0;
    fc.clamp(1e-3, nyq * 0.999)
}

/// Biquad pasa-bajos RBJ con `Q` dado.
fn lowpass_biquad(fc: f64, fs: f64, q: f64) -> Biquad {
    let w0 = TAU * fc / fs;
    let (sin_w0, cos_w0) = w0.sin_cos();
    let alpha = sin_w0 / (2.0 * q);
    let b0 = (1.0 - cos_w0) / 2.0;
    let b1 = 1.0 - cos_w0;
    let b2 = (1.0 - cos_w0) / 2.0;
    let a0 = 1.0 + alpha;
    let a1 = -2.0 * cos_w0;
    let a2 = 1.0 - alpha;
    Biquad::new(b0, b1, b2, a0, a1, a2)
}

/// Biquad pasa-altos RBJ con `Q` dado.
fn highpass_biquad(fc: f64, fs: f64, q: f64) -> Biquad {
    let w0 = TAU * fc / fs;
    let (sin_w0, cos_w0) = w0.sin_cos();
    let alpha = sin_w0 / (2.0 * q);
    let b0 = (1.0 + cos_w0) / 2.0;
    let b1 = -(1.0 + cos_w0);
    let b2 = (1.0 + cos_w0) / 2.0;
    let a0 = 1.0 + alpha;
    let a1 = -2.0 * cos_w0;
    let a2 = 1.0 - alpha;
    Biquad::new(b0, b1, b2, a0, a1, a2)
}

/// Seccion pasa-bajos de primer orden (para Butterworth de orden impar).
fn lowpass_first_order(fc: f64, fs: f64) -> Biquad {
    let k = (PI * fc / fs).tan();
    let a0 = k + 1.0;
    Biquad::new(k, k, 0.0, a0, k - 1.0, 0.0)
}

/// Seccion pasa-altos de primer orden.
fn highpass_first_order(fc: f64, fs: f64) -> Biquad {
    let k = (PI * fc / fs).tan();
    let a0 = k + 1.0;
    Biquad::new(1.0, -1.0, 0.0, a0, k - 1.0, 0.0)
}

/// Biquad notch (banda eliminada) RBJ.
fn notch_biquad(f0: f64, fs: f64, q: f64) -> Biquad {
    let w0 = TAU * f0 / fs;
    let (sin_w0, cos_w0) = w0.sin_cos();
    let alpha = sin_w0 / (2.0 * q);
    let b0 = 1.0;
    let b1 = -2.0 * cos_w0;
    let b2 = 1.0;
    let a0 = 1.0 + alpha;
    let a1 = -2.0 * cos_w0;
    let a2 = 1.0 - alpha;
    Biquad::new(b0, b1, b2, a0, a1, a2)
}

/// Factores Q de las secciones de 2º orden de un Butterworth de orden `n`.
///
/// Para cada par de polos conjugados, `Q_k = 1 / (2·cos θ_k)`.
fn butterworth_qs(n: u8) -> Vec<f64> {
    let n = n.max(1) as usize;
    let pairs = n / 2;
    (0..pairs)
        .map(|k| {
            let theta = PI * (2 * k + 1) as f64 / (2.0 * n as f64);
            1.0 / (2.0 * theta.cos())
        })
        .collect()
}

/// Filtro IIR como cadena de biquads procesados en serie.
#[derive(Debug, Clone, Default)]
pub struct IirFilter {
    sections: Vec<Biquad>,
}

impl IirFilter {
    /// Filtro vacio (paso directo).
    pub fn identity() -> Self {
        Self {
            sections: Vec::new(),
        }
    }

    /// Anade las secciones de un Butterworth pasa-bajos de orden `order`.
    fn push_lowpass(&mut self, fc: f64, fs: f64, order: u8) {
        let fc = clamp_fc(fc, fs);
        for q in butterworth_qs(order) {
            self.sections.push(lowpass_biquad(fc, fs, q));
        }
        if order % 2 == 1 {
            self.sections.push(lowpass_first_order(fc, fs));
        }
    }

    /// Anade las secciones de un Butterworth pasa-altos de orden `order`.
    fn push_highpass(&mut self, fc: f64, fs: f64, order: u8) {
        let fc = clamp_fc(fc, fs);
        for q in butterworth_qs(order) {
            self.sections.push(highpass_biquad(fc, fs, q));
        }
        if order % 2 == 1 {
            self.sections.push(highpass_first_order(fc, fs));
        }
    }

    /// Butterworth pasa-bajos de orden `order` a `fc`/`fs`.
    pub fn butterworth_lowpass(fc: f64, fs: f64, order: u8) -> Self {
        let mut f = Self::identity();
        f.push_lowpass(fc, fs, order);
        f
    }

    /// Butterworth pasa-altos de orden `order` a `fc`/`fs`.
    pub fn butterworth_highpass(fc: f64, fs: f64, order: u8) -> Self {
        let mut f = Self::identity();
        f.push_highpass(fc, fs, order);
        f
    }

    /// Pasa-banda (HP `hp_hz` + LP `lp_hz`) + notch opcional, desde un `Bandpass`.
    pub fn from_bandpass(bp: &Bandpass, fs: f64) -> Self {
        let mut f = Self::identity();
        f.push_highpass(bp.hp_hz, fs, bp.order);
        f.push_lowpass(bp.lp_hz, fs, bp.order);
        if let Some(f0) = bp.notch_hz {
            // Q moderado: notch de red (50/60 Hz) suficientemente ancho para
            // asentar rapido sin tocar las frecuencias vecinas utiles.
            f.sections.push(notch_biquad(f0, fs, 8.0));
        }
        f
    }

    /// Procesa una muestra a traves de toda la cadena.
    #[inline]
    pub fn process_sample(&mut self, x: f64) -> f64 {
        self.sections.iter_mut().fold(x, |acc, s| s.process(acc))
    }

    /// Filtra un buffer in situ.
    pub fn process(&mut self, buf: &mut [f64]) {
        for x in buf.iter_mut() {
            *x = self.process_sample(*x);
        }
    }

    /// Reinicia el estado de todas las secciones.
    pub fn reset(&mut self) {
        for s in self.sections.iter_mut() {
            s.reset();
        }
    }

    /// Numero de secciones (biquads) de la cadena.
    pub fn n_sections(&self) -> usize {
        self.sections.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// RMS de la salida estacionaria al filtrar un seno de `freq` Hz.
    fn steady_rms(filter: &mut IirFilter, freq: f64, fs: f64) -> f64 {
        filter.reset();
        let n = 8192;
        let mut out = Vec::with_capacity(n);
        for i in 0..n {
            let t = i as f64 / fs;
            let x = (TAU * freq * t).sin();
            out.push(filter.process_sample(x));
        }
        // Descarta el transitorio inicial (primer cuarto).
        let tail = &out[n / 4..];
        let ms: f64 = tail.iter().map(|v| v * v).sum::<f64>() / tail.len() as f64;
        ms.sqrt()
    }

    #[test]
    fn lowpass_pasa_baja_atenua_alta() {
        let fs = 30_000.0;
        let mut f = IirFilter::butterworth_lowpass(1000.0, fs, 2);
        let pasa = steady_rms(&mut f, 200.0, fs); // muy por debajo
        let corta = steady_rms(&mut f, 8000.0, fs); // muy por encima
        // La banda de paso conserva ~0.707 RMS (amplitud 1), la de rechazo cae mucho.
        assert!(pasa > 0.6, "pasa-banda RMS {pasa}");
        assert!(corta < 0.05, "rechazo RMS {corta}");
    }

    #[test]
    fn highpass_atenua_baja_pasa_alta() {
        let fs = 30_000.0;
        let mut f = IirFilter::butterworth_highpass(300.0, fs, 2);
        let corta = steady_rms(&mut f, 20.0, fs);
        let pasa = steady_rms(&mut f, 3000.0, fs);
        assert!(pasa > 0.6, "pasa-banda RMS {pasa}");
        assert!(corta < 0.05, "rechazo RMS {corta}");
    }

    #[test]
    fn bandpass_pasa_dentro_atenua_fuera() {
        let fs = 30_000.0;
        let bp = Bandpass {
            hp_hz: 100.0,
            lp_hz: 3000.0,
            notch_hz: None,
            order: 2,
        };
        let mut f = IirFilter::from_bandpass(&bp, fs);
        let dentro = steady_rms(&mut f, 1000.0, fs);
        let bajo = steady_rms(&mut f, 10.0, fs);
        let alto = steady_rms(&mut f, 12000.0, fs);
        assert!(dentro > 0.5, "dentro {dentro}");
        assert!(bajo < 0.1, "bajo {bajo}");
        assert!(alto < 0.05, "alto {alto}");
    }

    #[test]
    fn orden_par_e_impar_construyen_secciones() {
        let fs = 30_000.0;
        assert_eq!(IirFilter::butterworth_lowpass(1000.0, fs, 2).n_sections(), 1);
        assert_eq!(IirFilter::butterworth_lowpass(1000.0, fs, 4).n_sections(), 2);
        // Orden impar: (n-1)/2 secciones de 2º + 1 de 1º.
        assert_eq!(IirFilter::butterworth_lowpass(1000.0, fs, 3).n_sections(), 2);
    }

    #[test]
    fn notch_elimina_su_frecuencia() {
        let fs = 30_000.0;
        let bp = Bandpass {
            hp_hz: 10.0,
            lp_hz: 5000.0,
            notch_hz: Some(50.0),
            order: 2,
        };
        let mut f = IirFilter::from_bandpass(&bp, fs);
        let en_notch = steady_rms(&mut f, 50.0, fs);
        let fuera = steady_rms(&mut f, 500.0, fs);
        assert!(en_notch < 0.2, "notch RMS {en_notch}");
        assert!(fuera > 0.5, "fuera RMS {fuera}");
    }
}
