//! Sub-motor ASSR (Auditory Steady-State Response) — dominio de frecuencia.
//!
//! El caso mas distinto del espectro (MOTOR.md §11): el estimulo es una
//! portadora **modulada en amplitud** a una frecuencia f<sub>mod</sub> (40 u
//! 80 Hz). La respuesta no son picos en el tiempo, sino **energia en
//! f<sub>mod</sub>**, que se detecta con FFT + un **test estadistico** (F-test:
//! energia en el bin de f<sub>mod</sub> frente al ruido de los bins vecinos).
//!
//! - **40 Hz**: respuesta **cortical**, grande en el adulto despierto, atenuada
//!   por el sueno/la sedacion.
//! - **80 Hz**: respuesta de **tronco**, mas pequena pero **robusta** al estado
//!   (de eleccion en el lactante dormido).
//!
//! La salida por frecuencia (presente/ausente) construye un **audiograma
//! objetivo** sin respuesta conductual del sujeto.

use crate::dsp::fft::power_spectrum;
use crate::lesion::LesionSite;
use crate::protocol::{Paradigm, Protocol};
use crate::rng::Lcg;
use crate::subject::{ArousalState, Ear, Subject};
use std::f64::consts::TAU;

/// Frecuencia de muestreo del sub-motor (Hz). Con `N` muestras, df = FS/N = 1 Hz,
/// asi que 40 y 80 Hz caen en bins enteros.
const FS: f64 = 1024.0;
/// Muestras por epoca (potencia de dos).
const N: usize = 1024;
/// Amplitud RMS del ruido EEG de fondo (µV).
const NOISE_RMS_UV: f64 = 1.0;
/// Umbral del F-test para declarar respuesta presente.
const F_CRIT: f64 = 4.0;

/// Resultado de una deteccion ASSR.
#[derive(Debug, Clone, PartialEq, serde::Serialize)]
pub struct AssrResult {
    /// Frecuencia portadora (Hz).
    pub carrier_hz: f64,
    /// Frecuencia de modulacion (Hz).
    pub mod_freq_hz: f64,
    /// Razon del F-test (energia en f_mod / ruido vecino).
    pub f_ratio: f64,
    /// Relacion senal/ruido en dB (10·log10 del F-ratio).
    pub snr_db: f64,
    /// `true` si la respuesta supera el umbral estadistico.
    pub detected: bool,
    /// Epocas promediadas.
    pub n_epochs: u32,
}

/// Frecuencia de modulacion del protocolo (40 Hz por defecto).
fn mod_freq_of(protocol: &Protocol) -> f64 {
    match protocol.paradigm {
        Paradigm::SteadyState { mod_freq_hz } => mod_freq_hz,
        _ => 40.0,
    }
}

/// Amplitud de la respuesta ASSR (µV) segun el margen audible a la portadora y
/// la frecuencia de modulacion / estado.
fn assr_amplitude(protocol: &Protocol, subject: &Subject) -> f64 {
    let stim = &protocol.stimulus;
    let carrier = stim.kind.dominant_freq_hz();
    let level = stim.level.as_nhl();
    let threshold = subject
        .lesions_on(stim.ear)
        .filter(|l| matches!(l.site, LesionSite::Conductive | LesionSite::Cochlear))
        .map(|l| l.threshold_shift_at(carrier))
        .fold(0.0, f64::max);
    let margin = level - threshold;
    if margin <= 0.0 {
        return 0.0;
    }
    let base = 0.10 * (margin / 60.0).clamp(0.0, 1.2);
    let mod_factor = if mod_freq_of(protocol) < 60.0 {
        // 40 Hz cortical: depende del estado de alerta.
        match subject.state {
            ArousalState::Awake => 1.0,
            ArousalState::NaturalSleep => 0.45,
            ArousalState::Sedated => 0.4,
            ArousalState::Anesthetized => 0.3,
        }
    } else {
        // 80 Hz de tronco: robusto al estado.
        0.8
    };
    base * mod_factor
}

/// Semilla determinista del sub-motor.
fn assr_seed(protocol: &Protocol, subject: &Subject) -> u64 {
    let stim = &protocol.stimulus;
    let c = (stim.kind.dominant_freq_hz() * 10.0) as u64;
    let l = (stim.level.as_nhl() * 10.0) as i64 as u64;
    let m = (mod_freq_of(protocol) * 10.0) as u64;
    let st = subject.state as u64;
    c.wrapping_mul(0x9E37_79B9)
        .wrapping_add(l.wrapping_mul(0x85EB_CA77))
        ^ m.wrapping_mul(0xC2B2_AE3D)
        ^ st.wrapping_mul(0x27D4_EB2F)
}

/// Promedia `acquisition.sweeps` epocas coherentes (respuesta + ruido) y
/// devuelve `(tiempos_ms, promedio)`.
pub fn averaged_epoch(protocol: &Protocol, subject: &Subject) -> (Vec<f64>, Vec<f64>) {
    let amp = assr_amplitude(protocol, subject);
    let mod_freq = mod_freq_of(protocol);
    let m = protocol.acquisition.sweeps.max(1);
    let base = assr_seed(protocol, subject);

    let mut avg = vec![0.0; N];
    for e in 0..m {
        let mut rng = Lcg::new(base ^ (e as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15));
        for (i, v) in avg.iter_mut().enumerate() {
            let t = i as f64 / FS;
            *v += amp * (TAU * mod_freq * t).sin() + rng.next_gaussian() * NOISE_RMS_UV;
        }
    }
    let inv = 1.0 / m as f64;
    for v in avg.iter_mut() {
        *v *= inv;
    }
    let times: Vec<f64> = (0..N).map(|i| i as f64 / FS * 1000.0).collect();
    (times, avg)
}

/// F-test: potencia en el bin `k` frente a la media de los bins de ruido
/// vecinos (excluyendo el bin de senal y sus fugas inmediatas).
fn f_test(power: &[f64], k: usize) -> f64 {
    let lo = k.saturating_sub(60).max(2);
    let hi = (k + 60).min(power.len().saturating_sub(1));
    let mut sum = 0.0;
    let mut cnt = 0u32;
    for (j, &p) in power.iter().enumerate().take(hi + 1).skip(lo) {
        if (j as i64 - k as i64).abs() <= 2 {
            continue; // excluye la senal y la fuga espectral
        }
        sum += p;
        cnt += 1;
    }
    if cnt == 0 {
        return 0.0;
    }
    let noise_mean = sum / cnt as f64;
    if noise_mean <= 0.0 {
        return 0.0;
    }
    power[k] / noise_mean
}

/// Detecta la respuesta ASSR de un protocolo de estado estable.
pub fn detect_assr(protocol: &Protocol, subject: &Subject) -> AssrResult {
    let carrier = protocol.stimulus.kind.dominant_freq_hz();
    let mod_freq = mod_freq_of(protocol);
    let (_, avg) = averaged_epoch(protocol, subject);
    let power = power_spectrum(&avg);
    let k = (mod_freq.round() as usize).min(power.len().saturating_sub(1));
    let f_ratio = f_test(&power, k);
    AssrResult {
        carrier_hz: carrier,
        mod_freq_hz: mod_freq,
        f_ratio,
        snr_db: 10.0 * f_ratio.max(1e-9).log10(),
        detected: f_ratio > F_CRIT,
        n_epochs: protocol.acquisition.sweeps.max(1),
    }
}

/// Umbral objetivo (dB nHL) para una portadora: menor intensidad con respuesta.
pub fn assr_threshold(ear: Ear, subject: &Subject, carrier_hz: f64, mod_freq_hz: f64) -> Option<f64> {
    let mut threshold = None;
    let mut level = 100.0_f64;
    while level >= 0.0 {
        let mut p = Protocol::assr(ear, carrier_hz, mod_freq_hz);
        p.stimulus.level = crate::units::Level::DbNhl(level);
        if detect_assr(&p, subject).detected {
            threshold = Some(level);
        } else if threshold.is_some() {
            break;
        }
        level -= 5.0;
    }
    threshold
}

/// Audiograma objetivo estimado por ASSR: `(portadora, umbral dB nHL)`.
pub fn assr_audiogram(
    ear: Ear,
    subject: &Subject,
    carriers: &[f64],
    mod_freq_hz: f64,
) -> Vec<(f64, Option<f64>)> {
    carriers
        .iter()
        .map(|&c| (c, assr_threshold(ear, subject, c, mod_freq_hz)))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::lesion::{FreqProfile, Lesion};
    use crate::units::Level;

    fn p_assr(carrier: f64, mod_freq: f64, level: f64) -> Protocol {
        let mut p = Protocol::assr(Ear::Right, carrier, mod_freq);
        p.stimulus.level = Level::DbNhl(level);
        p
    }

    #[test]
    fn respuesta_presente_sobre_umbral() {
        let r = detect_assr(&p_assr(2000.0, 80.0, 70.0), &Subject::default());
        assert!(r.detected, "F-ratio = {}", r.f_ratio);
    }

    #[test]
    fn sin_estimulo_audible_no_hay_respuesta() {
        // Perdida coclear profunda y plana → bajo umbral, sin respuesta.
        let mut s = Subject::default();
        s.lesions.push(Lesion {
            site: LesionSite::Cochlear,
            ear: Ear::Right,
            severity_db: 120.0,
            freq_profile: FreqProfile::Flat,
        });
        let r = detect_assr(&p_assr(2000.0, 80.0, 60.0), &s);
        assert!(!r.detected, "F-ratio = {}", r.f_ratio);
    }

    #[test]
    fn ochenta_hz_mas_robusto_que_cuarenta_en_sueno() {
        let dormido = Subject {
            state: ArousalState::NaturalSleep,
            ..Default::default()
        };
        let f40 = detect_assr(&p_assr(2000.0, 40.0, 60.0), &dormido).f_ratio;
        let f80 = detect_assr(&p_assr(2000.0, 80.0, 60.0), &dormido).f_ratio;
        assert!(f80 > f40, "40Hz={f40} 80Hz={f80}");
    }

    #[test]
    fn audiograma_objetivo_normal_es_bajo() {
        let audio = assr_audiogram(Ear::Right, &Subject::default(), &[500.0, 2000.0, 4000.0], 80.0);
        for (f, th) in audio {
            let th = th.unwrap_or_else(|| panic!("sin umbral en {f} Hz"));
            assert!(th <= 25.0, "freq {f} umbral {th}");
        }
    }

    #[test]
    fn perdida_en_agudos_eleva_umbral_objetivo_en_agudos() {
        let mut s = Subject::default();
        s.lesions.push(Lesion {
            site: LesionSite::Cochlear,
            ear: Ear::Right,
            severity_db: 55.0,
            freq_profile: FreqProfile::HighFrequency,
        });
        let audio = assr_audiogram(Ear::Right, &s, &[500.0, 4000.0], 80.0);
        let grave = audio.iter().find(|(f, _)| *f == 500.0).unwrap().1.unwrap();
        let agudo = audio.iter().find(|(f, _)| *f == 4000.0).unwrap().1.unwrap();
        assert!(agudo > grave + 20.0, "500={grave} 4000={agudo}");
    }

    #[test]
    fn es_determinista() {
        let a = detect_assr(&p_assr(2000.0, 80.0, 70.0), &Subject::default());
        let b = detect_assr(&p_assr(2000.0, 80.0, 70.0), &Subject::default());
        assert_eq!(a, b);
    }
}
