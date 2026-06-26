//! F_sp (single-point): metrica objetiva de calidad del registro.
//!
//! Definicion de Elberling & Don (1984). Mide cuanto sobresale la forma de onda
//! promediada por encima del ruido residual:
//!
//! ```text
//!         M · Var_a
//! F_sp = ───────────
//!          Var_sp
//! ```
//!
//! - `M` = numero de sweeps promediados.
//! - `Var_a` = varianza de la curva promediada a lo largo de los puntos de la
//!   ventana (refleja senal + ruido residual).
//! - `Var_sp` = varianza, entre sweeps, del valor en un unico punto temporal
//!   fijo (estima el ruido de un barrido individual).
//!
//! Sin respuesta, la varianza del promedio es ≈ `Var_sp / M`, asi que
//! `F_sp ≈ 1`. Con respuesta presente, `Var_a` crece y `F_sp` sube; tambien
//! sube al promediar mas (mayor `M`). Umbral clinico habitual de deteccion:
//! `F_sp ≥ 3.1`.

/// Varianza muestral (divisor `n-1`). Devuelve 0 si hay menos de 2 datos.
fn sample_variance(xs: &[f64]) -> f64 {
    let n = xs.len();
    if n < 2 {
        return 0.0;
    }
    let mean = xs.iter().sum::<f64>() / n as f64;
    xs.iter().map(|x| (x - mean) * (x - mean)).sum::<f64>() / (n as f64 - 1.0)
}

/// Calcula F_sp a partir de la curva promediada y los valores del punto `sp`.
///
/// `average`: curva promediada (todos los puntos de la ventana).
/// `sp_samples`: valor del punto fijo en cada uno de los `M` sweeps aceptados.
pub fn f_sp(average: &[f64], sp_samples: &[f64]) -> f64 {
    let m = sp_samples.len();
    if m < 2 || average.len() < 2 {
        return 0.0;
    }
    let var_a = sample_variance(average);
    let var_sp = sample_variance(sp_samples);
    if var_sp <= f64::EPSILON {
        return 0.0;
    }
    m as f64 * var_a / var_sp
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::rng::Lcg;

    /// Promedia `m` sweeps de ruido + (opcional) una "respuesta" deterministica,
    /// y devuelve (curva promediada, valores del punto sp).
    fn simular(m: usize, n: usize, con_senal: bool) -> (Vec<f64>, Vec<f64>) {
        let mut sum = vec![0.0; n];
        let mut sp = Vec::with_capacity(m);
        let sp_idx = n / 2;
        // "Senal": una gaussiana centrada en el medio de la ventana.
        let signal = |i: usize| -> f64 {
            if !con_senal {
                return 0.0;
            }
            let d = i as f64 - n as f64 / 2.0;
            2.0 * (-(d * d) / (2.0 * 8.0 * 8.0)).exp()
        };
        for k in 0..m {
            let mut rng = Lcg::new(100 + k as u64);
            let mut sweep = vec![0.0; n];
            for (i, s) in sweep.iter_mut().enumerate() {
                *s = signal(i) + rng.next_gaussian();
            }
            for (acc, v) in sum.iter_mut().zip(sweep.iter()) {
                *acc += v;
            }
            sp.push(sweep[sp_idx]);
        }
        let avg: Vec<f64> = sum.iter().map(|s| s / m as f64).collect();
        (avg, sp)
    }

    #[test]
    fn sin_senal_fsp_cercano_a_uno() {
        let (avg, sp) = simular(2000, 256, false);
        let f = f_sp(&avg, &sp);
        // Estadisticamente ~1; toleramos un rango amplio.
        assert!(f > 0.3 && f < 3.0, "F_sp sin senal = {f}");
    }

    #[test]
    fn con_senal_fsp_mucho_mayor_que_sin_senal() {
        let (a1, s1) = simular(2000, 256, true);
        let (a0, s0) = simular(2000, 256, false);
        let f_con = f_sp(&a1, &s1);
        let f_sin = f_sp(&a0, &s0);
        assert!(f_con > 10.0 * f_sin.max(0.3), "con={f_con} sin={f_sin}");
        assert!(f_con > 3.1, "deberia superar umbral de deteccion: {f_con}");
    }

    #[test]
    fn fsp_sube_con_mas_sweeps() {
        let (a_pocos, s_pocos) = simular(200, 256, true);
        let (a_muchos, s_muchos) = simular(4000, 256, true);
        let f_pocos = f_sp(&a_pocos, &s_pocos);
        let f_muchos = f_sp(&a_muchos, &s_muchos);
        assert!(f_muchos > f_pocos, "pocos={f_pocos} muchos={f_muchos}");
    }
}
