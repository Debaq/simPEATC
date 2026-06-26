//! FFT radix-2 (Cooley-Tukey) iterativa, sin dependencias.
//!
//! Necesaria para el sub-motor ASSR (Capa 7), que trabaja en el dominio de la
//! frecuencia: detecta energia en la frecuencia de modulacion. La longitud debe
//! ser potencia de dos.

use std::f64::consts::PI;

/// FFT in situ (radix-2 decimacion en tiempo). `re`/`im` se sobreescriben con la
/// transformada. `re.len()` debe ser potencia de dos.
pub fn fft_in_place(re: &mut [f64], im: &mut [f64]) {
    let n = re.len();
    assert_eq!(n, im.len(), "re e im deben tener la misma longitud");
    assert!(n.is_power_of_two(), "la longitud debe ser potencia de dos");
    if n <= 1 {
        return;
    }

    // Permutacion por inversion de bits.
    let mut j = 0usize;
    for i in 1..n {
        let mut bit = n >> 1;
        while j & bit != 0 {
            j ^= bit;
            bit >>= 1;
        }
        j ^= bit;
        if i < j {
            re.swap(i, j);
            im.swap(i, j);
        }
    }

    // Mariposas por etapas de tamano `len`.
    let mut len = 2usize;
    while len <= n {
        let ang = -2.0 * PI / len as f64;
        let (wlen_re, wlen_im) = (ang.cos(), ang.sin());
        let half = len / 2;
        let mut base = 0usize;
        while base < n {
            let (mut w_re, mut w_im) = (1.0_f64, 0.0_f64);
            for k in 0..half {
                let a = base + k;
                let b = base + k + half;
                let v_re = re[b] * w_re - im[b] * w_im;
                let v_im = re[b] * w_im + im[b] * w_re;
                re[b] = re[a] - v_re;
                im[b] = im[a] - v_im;
                re[a] += v_re;
                im[a] += v_im;
                let nw_re = w_re * wlen_re - w_im * wlen_im;
                let nw_im = w_re * wlen_im + w_im * wlen_re;
                w_re = nw_re;
                w_im = nw_im;
            }
            base += len;
        }
        len <<= 1;
    }
}

/// Espectro de potencia (|X[k]|²) de una senal real, hasta Nyquist (`n/2` bins).
///
/// La senal se trunca o rellena con ceros a la mayor potencia de dos ≤ longitud
/// (si ya es potencia de dos, no cambia).
pub fn power_spectrum(signal: &[f64]) -> Vec<f64> {
    let n = signal.len().next_power_of_two();
    let n = if n > signal.len() { n >> 1 } else { n }.max(1);
    let mut re = vec![0.0; n];
    let mut im = vec![0.0; n];
    re.copy_from_slice(&signal[..n]);
    fft_in_place(&mut re, &mut im);
    (0..n / 2).map(|k| re[k] * re[k] + im[k] * im[k]).collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::f64::consts::TAU;

    #[test]
    fn seno_concentra_energia_en_su_bin() {
        let n = 1024;
        let bin = 40;
        let signal: Vec<f64> = (0..n)
            .map(|i| (TAU * bin as f64 * i as f64 / n as f64).sin())
            .collect();
        let p = power_spectrum(&signal);
        let (kmax, _) = p
            .iter()
            .enumerate()
            .max_by(|a, b| a.1.partial_cmp(b.1).unwrap())
            .unwrap();
        assert_eq!(kmax, bin, "pico espectral en el bin equivocado");
    }

    #[test]
    fn dc_va_al_bin_cero() {
        let signal = vec![2.0; 256];
        let p = power_spectrum(&signal);
        let (kmax, _) = p
            .iter()
            .enumerate()
            .max_by(|a, b| a.1.partial_cmp(b.1).unwrap())
            .unwrap();
        assert_eq!(kmax, 0);
    }

    #[test]
    fn es_determinista() {
        let signal: Vec<f64> = (0..512).map(|i| (i as f64 * 0.1).sin()).collect();
        assert_eq!(power_spectrum(&signal), power_spectrum(&signal));
    }

    #[test]
    fn impulso_da_espectro_plano() {
        let mut re = vec![0.0; 8];
        re[0] = 1.0;
        let mut im = vec![0.0; 8];
        fft_in_place(&mut re, &mut im);
        // La FFT de un impulso unitario es 1 en todos los bins.
        for (r, i) in re.iter().zip(im.iter()) {
            assert!((r - 1.0).abs() < 1e-9 && i.abs() < 1e-9);
        }
    }
}
