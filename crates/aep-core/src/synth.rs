//! Sintesis de la senal cruda, sweep a sweep.
//!
//! Cada sweep = Σ componentes (la senal evocada, identica en cada repeticion) +
//! ruido EEG de fondo (independiente en cada sweep). El SNR **no se modela**:
//! emerge al promediar muchos sweeps, porque la senal se suma coherentemente y
//! el ruido cae ~√N (MOTOR.md §6, diseno desde cero).
//!
//! El ruido se genera de banda ancha; la cadena DSP (filtro IIR) lo colorea
//! despues, igual que en un equipo real.

use crate::acquisition::TimeWindow;
use crate::component::Component;
use crate::rng::Lcg;

/// Perfil de ruido EEG de fondo para una modalidad/sujeto.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct NoiseProfile {
    /// Amplitud RMS del ruido crudo (µV) antes de filtrar.
    pub rms_uv: f64,
}

impl NoiseProfile {
    /// Crea un perfil con el RMS dado.
    pub fn new(rms_uv: f64) -> Self {
        Self {
            rms_uv: rms_uv.max(0.0),
        }
    }
}

/// Eje temporal (ms) de la ventana, con `n` muestras.
pub fn time_axis(window: &TimeWindow, n: usize) -> Vec<f64> {
    (0..n).map(|i| window.time_at(i, n)).collect()
}

/// Senal evocada limpia (sin ruido) evaluada en cada instante de `times`.
pub fn clean_signal(components: &[Component], times: &[f64]) -> Vec<f64> {
    times
        .iter()
        .map(|&t| components.iter().map(|c| c.evaluate(t)).sum())
        .collect()
}

/// Genera **un** sweep: senal evocada + ruido EEG independiente.
///
/// `times` es el eje temporal precomputado (ms). `rng` debe sembrarse distinto
/// por sweep para que el ruido sea independiente entre repeticiones.
pub fn synth_sweep(
    components: &[Component],
    times: &[f64],
    noise: &NoiseProfile,
    rng: &mut Lcg,
) -> Vec<f64> {
    times
        .iter()
        .map(|&t| {
            let signal: f64 = components.iter().map(|c| c.evaluate(t)).sum();
            let n = rng.next_gaussian() * noise.rms_uv;
            signal + n
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::component::Component;

    fn comp_v() -> Component {
        Component::gaussian("V", 5.6, 0.5, 0.3, "coliculo inferior")
    }

    #[test]
    fn eje_temporal_cubre_ventana() {
        let w = TimeWindow {
            pre_ms: 1.0,
            post_ms: 11.0,
        };
        let t = time_axis(&w, 360);
        assert_eq!(t.len(), 360);
        assert!((t[0] - (-1.0)).abs() < 1e-9);
        assert!((t[359] - 11.0).abs() < 1e-9);
    }

    #[test]
    fn senal_limpia_tiene_pico_en_latencia() {
        let times = time_axis(
            &TimeWindow {
                pre_ms: 0.0,
                post_ms: 12.0,
            },
            480,
        );
        let s = clean_signal(&[comp_v()], &times);
        // El maximo debe caer cerca de 5.6 ms.
        let (idx, _) = s
            .iter()
            .enumerate()
            .max_by(|a, b| a.1.partial_cmp(b.1).unwrap())
            .unwrap();
        assert!((times[idx] - 5.6).abs() < 0.2);
    }

    #[test]
    fn sweeps_distinta_semilla_difieren_pero_promedian_a_la_senal() {
        let times = time_axis(
            &TimeWindow {
                pre_ms: 0.0,
                post_ms: 12.0,
            },
            480,
        );
        let noise = NoiseProfile::new(0.3);
        let comps = [comp_v()];

        // Promediar muchos sweeps: el ruido cae, emerge el pico.
        let n_sweeps = 4000;
        let mut acc = vec![0.0; times.len()];
        for k in 0..n_sweeps {
            let mut rng = Lcg::new(1000 + k as u64);
            let sweep = synth_sweep(&comps, &times, &noise, &mut rng);
            for (a, s) in acc.iter_mut().zip(sweep.iter()) {
                *a += s;
            }
        }
        for a in acc.iter_mut() {
            *a /= n_sweeps as f64;
        }
        let clean = clean_signal(&comps, &times);
        // El promedio debe parecerse a la senal limpia (error RMS pequeno).
        let err: f64 = acc
            .iter()
            .zip(clean.iter())
            .map(|(a, c)| (a - c) * (a - c))
            .sum::<f64>()
            / times.len() as f64;
        assert!(err.sqrt() < 0.02, "RMS error {}", err.sqrt());
    }
}
