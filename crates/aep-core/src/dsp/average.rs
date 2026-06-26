//! Promediacion sweep-a-sweep con rechazo de artefactos.
//!
//! El ruido cae ~√N de forma **real**: cada sweep aporta senal coherente +
//! ruido independiente, y la media acumulada reduce la varianza del ruido a
//! σ²/N. Los sweeps cuyo pico supera el umbral de rechazo se descartan y se
//! cuentan aparte. Se guarda ademas el valor de un punto fijo en cada sweep
//! aceptado para estimar F_sp (ver `fsp.rs`).

/// Acumulador de promediacion.
#[derive(Debug, Clone)]
pub struct Averager {
    sum: Vec<f64>,
    accepted: u32,
    rejected: u32,
    reject_uv: f64,
    sp_index: usize,
    sp_samples: Vec<f64>,
}

impl Averager {
    /// Crea un promediador para sweeps de longitud `n`.
    ///
    /// `reject_uv` es el umbral de rechazo (µV); `sp_index` el punto cuya
    /// evolucion se guarda para F_sp (por defecto, el centro de la ventana).
    pub fn new(n: usize, reject_uv: f64, sp_index: usize) -> Self {
        Self {
            sum: vec![0.0; n],
            accepted: 0,
            rejected: 0,
            reject_uv,
            sp_index: sp_index.min(n.saturating_sub(1)),
            sp_samples: Vec::new(),
        }
    }

    /// Anade un sweep. Devuelve `true` si se acepto, `false` si se rechazo.
    pub fn add(&mut self, sweep: &[f64]) -> bool {
        debug_assert_eq!(sweep.len(), self.sum.len());
        if sweep.iter().any(|v| v.abs() > self.reject_uv) {
            self.rejected += 1;
            return false;
        }
        for (s, x) in self.sum.iter_mut().zip(sweep.iter()) {
            *s += x;
        }
        self.sp_samples.push(sweep[self.sp_index]);
        self.accepted += 1;
        true
    }

    /// Curva promediada actual (vacia si no hay sweeps aceptados).
    pub fn mean(&self) -> Vec<f64> {
        if self.accepted == 0 {
            return vec![0.0; self.sum.len()];
        }
        let n = self.accepted as f64;
        self.sum.iter().map(|s| s / n).collect()
    }

    /// Sweeps aceptados.
    pub fn accepted(&self) -> u32 {
        self.accepted
    }

    /// Sweeps rechazados.
    pub fn rejected(&self) -> u32 {
        self.rejected
    }

    /// Valores del punto fijo (sp) en cada sweep aceptado.
    pub fn sp_samples(&self) -> &[f64] {
        &self.sp_samples
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::rng::Lcg;

    #[test]
    fn rechaza_sweeps_con_artefacto() {
        let mut avg = Averager::new(4, 10.0, 2);
        assert!(avg.add(&[1.0, -2.0, 3.0, 0.5]));
        assert!(!avg.add(&[1.0, 50.0, 3.0, 0.5])); // 50 > 10 → rechazado
        assert_eq!(avg.accepted(), 1);
        assert_eq!(avg.rejected(), 1);
    }

    #[test]
    fn promedio_de_constante_es_la_constante() {
        let mut avg = Averager::new(3, 100.0, 1);
        for _ in 0..10 {
            avg.add(&[2.0, 2.0, 2.0]);
        }
        let m = avg.mean();
        for v in m {
            assert!((v - 2.0).abs() < 1e-12);
        }
    }

    #[test]
    fn ruido_cae_como_raiz_de_n() {
        // Sweeps de puro ruido (sin senal): la desviacion del promedio debe
        // caer ~√N. Comparamos N=100 vs N=10000.
        let n = 256;
        let rms = 1.0;

        let promediar = |n_sweeps: u64| -> f64 {
            let mut avg = Averager::new(n, 1e9, n / 2);
            for k in 0..n_sweeps {
                let mut rng = Lcg::new(k + 1);
                let sweep: Vec<f64> = (0..n).map(|_| rng.next_gaussian() * rms).collect();
                avg.add(&sweep);
            }
            let m = avg.mean();
            // Desviacion estandar del promedio sobre la ventana.
            let mean = m.iter().sum::<f64>() / n as f64;
            (m.iter().map(|v| (v - mean) * (v - mean)).sum::<f64>() / n as f64).sqrt()
        };

        let s_100 = promediar(100);
        let s_10000 = promediar(10000);
        // 100x mas sweeps → ruido ~10x menor. Toleramos amplio margen estadistico.
        let ratio = s_100 / s_10000;
        assert!(ratio > 5.0 && ratio < 20.0, "ratio {ratio} (esperado ~10)");
    }
}
