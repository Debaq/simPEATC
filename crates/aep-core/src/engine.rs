//! El motor: ejecuta la cadena de la §4 y devuelve un `Recording`.
//!
//! Separa la *verdad fisiologica* (componentes que produce el modelo) de la
//! *adquisicion* (lo que el equipo mide). El mismo paciente se ve distinto segun
//! como se configure el equipo, que es justo lo que se ensena.
//!
//! Pipeline por `simulate`:
//! 1. El `ResponseModel` da los componentes ya modulados + el ruido de fondo.
//! 2. Por cada sweep: sintesis (senal + ruido independiente) → artefacto
//!    ocasional → **rechazo** (sobre la senal cruda) → filtro IIR → correccion
//!    de linea base → acumulacion.
//! 3. Promediado → F_sp → deteccion de picos → `Recording`.

use crate::dsp::{f_sp, Averager, IirFilter};
use crate::models::{model_for, ResponseModel};
use crate::protocol::Protocol;
use crate::rng::Lcg;
use crate::subject::Subject;
use crate::synth::{self, NoiseProfile};
use crate::waveform::{Recording, Waveform};
use crate::component::{Component, ComponentShape, WavePeak};

/// Probabilidad de que un sweep traiga un artefacto (parpadeo/muscular).
const ARTIFACT_PROB: f64 = 0.03;
/// Media-ventana de busqueda de pico alrededor de la latencia esperada (ms).
const PEAK_SEARCH_MS: f64 = 0.7;

/// Motor de potenciales evocados.
pub struct EvokedPotentialEngine;

impl EvokedPotentialEngine {
    /// Simula un registro para un protocolo y un sujeto.
    ///
    /// Para modalidades aun no implementadas (Capas 2-7) devuelve un `Recording`
    /// vacio.
    pub fn simulate(protocol: &Protocol, subject: &Subject) -> Recording {
        match model_for(protocol.modality) {
            Some(model) => run_pipeline(&*model, protocol, subject),
            None => Recording::default(),
        }
    }
}

/// Ejecuta la cadena de adquisicion para un modelo concreto.
fn run_pipeline(model: &dyn ResponseModel, protocol: &Protocol, subject: &Subject) -> Recording {
    let acq = &protocol.acquisition;
    let comps = model.components(protocol, subject);

    // Ruido de fondo del modelo, elevado por la impedancia de electrodos.
    let mut noise = model.background_noise(subject);
    noise = NoiseProfile::new(noise.rms_uv * (1.0 + acq.impedance_kohm / 10.0));

    let n = acq.window.n_samples(acq.sample_rate_hz).max(2);
    let times = synth::time_axis(&acq.window, n);
    let sp_index = n / 2;

    // Filtro precomputado una vez; se clona+reinicia por sweep.
    let filter_template = IirFilter::from_bandpass(&acq.filter, acq.sample_rate_hz);

    // Averager sin rechazo propio: el rechazo se decide sobre la senal cruda.
    let mut avg = Averager::new(n, f64::INFINITY, sp_index);
    let mut rejected = 0u32;

    let target = acq.sweeps.max(1);
    let max_attempts = target.saturating_mul(2).max(target.saturating_add(100));
    let base_seed = seed(protocol, subject);

    let mut produced = 0u32;
    while avg.accepted() < target && produced < max_attempts {
        let mut rng = Lcg::new(base_seed ^ (produced as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15));
        produced += 1;

        let mut sweep = synth::synth_sweep(&comps, &times, &noise, &mut rng);
        inject_artifact(&mut sweep, &mut rng, acq.artifact_reject_uv);

        // Rechazo de artefactos sobre la senal CRUDA (pre-filtro), como el equipo.
        if sweep.iter().any(|v| v.abs() > acq.artifact_reject_uv) {
            rejected += 1;
            continue;
        }

        // Filtro IIR real, por sweep.
        let mut filt = filter_template.clone();
        filt.reset();
        filt.process(&mut sweep);
        // Correccion de linea base con el pre-estimulo.
        baseline_correct(&mut sweep, &times);

        avg.add(&sweep);
    }

    let mean = avg.mean();
    let fsp = f_sp(&mean, avg.sp_samples());
    let detected = detect_peaks(&comps, &times, &mean);
    let waveform = Waveform::new(times, mean);

    Recording {
        channels: vec![waveform],
        detected,
        fsp,
        accepted_sweeps: avg.accepted(),
        rejected_sweeps: rejected,
    }
}

/// Inyecta ocasionalmente un artefacto de gran amplitud (parpadeo/muscular).
fn inject_artifact(sweep: &mut [f64], rng: &mut Lcg, reject_uv: f64) {
    if rng.next_f64() < ARTIFACT_PROB {
        let sign = if rng.next_f64() < 0.5 { -1.0 } else { 1.0 };
        let amp = reject_uv * (1.5 + rng.next_f64());
        for v in sweep.iter_mut() {
            *v += sign * amp;
        }
    }
}

/// Resta la media del segmento pre-estimulo (t < 0) a todo el sweep.
fn baseline_correct(sweep: &mut [f64], times: &[f64]) {
    let mut sum = 0.0;
    let mut cnt = 0u32;
    for (&t, &v) in times.iter().zip(sweep.iter()) {
        if t < 0.0 {
            sum += v;
            cnt += 1;
        }
    }
    if cnt > 0 {
        let mean = sum / cnt as f64;
        for v in sweep.iter_mut() {
            *v -= mean;
        }
    }
}

/// Busca cada componente esperado como un maximo local cerca de su latencia.
///
/// La amplitud reportada es **absoluta desde la linea base** en el pico, no
/// pico-a-valle como en la medicion clinica; ademas el filtrado IIR forward
/// sesga las amplitudes absolutas. Por eso las latencias son fiables pero las
/// amplitudes (y razones como V/I) son aproximadas. Medicion pico-a-valle y
/// filtrado de fase cero quedan como refinamiento futuro.
fn detect_peaks(comps: &[Component], times: &[f64], mean: &[f64]) -> Vec<WavePeak> {
    comps
        .iter()
        // El microfonico es oscilatorio: no tiene un pico puntual que medir.
        .filter(|c| !matches!(c.shape, ComponentShape::Microphonic { .. }))
        .filter(|c| c.amplitude_uv.abs() > 1e-3)
        .filter_map(|c| {
            // Busca el maximo si la deflexion esperada es positiva (ondas ABR) o
            // el minimo si es negativa (AP/SP de la ECochG).
            let want_max = c.amplitude_uv >= 0.0;
            let lo = c.latency_ms - PEAK_SEARCH_MS;
            let hi = c.latency_ms + PEAK_SEARCH_MS;
            let mut best: Option<(usize, f64)> = None;
            for (i, &t) in times.iter().enumerate() {
                if t < lo || t > hi {
                    continue;
                }
                let v = mean[i];
                let better = match best {
                    None => true,
                    Some((_, bv)) => (want_max && v > bv) || (!want_max && v < bv),
                };
                if better {
                    best = Some((i, v));
                }
            }
            best.map(|(i, _)| WavePeak {
                label: c.label.clone(),
                latency_ms: times[i],
                amplitude_uv: mean[i],
            })
        })
        .collect()
}

/// Semilla determinista derivada del protocolo y el sujeto.
fn seed(protocol: &Protocol, subject: &Subject) -> u64 {
    let s = &protocol.stimulus;
    let ear = match s.ear {
        crate::subject::Ear::Left => 1u64,
        crate::subject::Ear::Right => 2u64,
    };
    let lvl = (s.level.as_nhl() * 10.0) as i64 as u64;
    let rate = (s.rate_hz * 10.0) as u64;
    let sweeps = protocol.acquisition.sweeps as u64;
    let temp = (subject.temperature_c * 10.0) as i64 as u64;
    let modal = protocol.modality as u64;

    ear.wrapping_mul(0x9E37_79B9)
        .wrapping_add(lvl.wrapping_mul(0x85EB_CA77))
        ^ rate.wrapping_mul(0xC2B2_AE3D)
        ^ sweeps.wrapping_mul(0x27D4_EB2F)
        ^ temp.wrapping_mul(0x1656_67B1)
        ^ modal.wrapping_mul(0x9E37_79B1)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::protocol::Protocol;
    use crate::subject::{Ear, Subject};
    use crate::units::Level;

    #[test]
    fn simula_y_detecta_onda_v() {
        let p = Protocol::abr_click(Ear::Right);
        let s = Subject::default();
        let rec = EvokedPotentialEngine::simulate(&p, &s);
        assert!(rec.primary().is_some());
        assert_eq!(rec.accepted_sweeps, p.acquisition.sweeps);
        // La onda V detectada cae cerca de ~6.5 ms (5.6 + retardo inserto).
        let v = rec.detected.iter().find(|w| w.label == "V").unwrap();
        assert!((v.latency_ms - 6.5).abs() < 0.6, "V detectada en {} ms", v.latency_ms);
    }

    #[test]
    fn es_determinista() {
        let p = Protocol::abr_click(Ear::Right);
        let s = Subject::default();
        let a = EvokedPotentialEngine::simulate(&p, &s);
        let b = EvokedPotentialEngine::simulate(&p, &s);
        assert_eq!(a.channels[0].amplitudes_uv, b.channels[0].amplitudes_uv);
        assert_eq!(a.fsp, b.fsp);
    }

    #[test]
    fn algunos_sweeps_se_rechazan() {
        let p = Protocol::abr_click(Ear::Right);
        let s = Subject::default();
        let rec = EvokedPotentialEngine::simulate(&p, &s);
        // Con ~3% de artefactos, deberia haber rechazos pero alcanzar el objetivo.
        assert!(rec.rejected_sweeps > 0);
        assert_eq!(rec.accepted_sweeps, p.acquisition.sweeps);
    }

    #[test]
    fn mas_sweeps_mejor_fsp() {
        let s = Subject::default();
        let mut pocos = Protocol::abr_click(Ear::Right);
        pocos.acquisition.sweeps = 100;
        let mut muchos = Protocol::abr_click(Ear::Right);
        muchos.acquisition.sweeps = 4000;
        let f_pocos = EvokedPotentialEngine::simulate(&pocos, &s).fsp;
        let f_muchos = EvokedPotentialEngine::simulate(&muchos, &s).fsp;
        assert!(f_muchos > f_pocos, "pocos={f_pocos} muchos={f_muchos}");
    }

    #[test]
    fn modalidad_no_implementada_devuelve_vacio() {
        let mut p = Protocol::abr_click(Ear::Right);
        p.modality = crate::protocol::Modality::Assr;
        let rec = EvokedPotentialEngine::simulate(&p, &Subject::default());
        assert!(rec.channels.is_empty());
    }

    #[test]
    fn cerca_del_umbral_la_v_es_la_mas_robusta() {
        // A intensidad muy baja, la onda V sobrevive cuando las demas casi no.
        let mut p = Protocol::abr_click(Ear::Right);
        p.stimulus.level = Level::DbNhl(20.0);
        let rec = EvokedPotentialEngine::simulate(&p, &Subject::default());
        assert!(rec.detected.iter().any(|w| w.label == "V"));
    }
}
