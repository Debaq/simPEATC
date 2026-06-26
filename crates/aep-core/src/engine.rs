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

use crate::acquisition::Acquisition;
use crate::assr::{self, AssrResult};
use crate::component::{Component, ComponentShape, WavePeak};
use crate::dsp::{f_sp, Averager, IirFilter};
use crate::models::cognitive::CognitiveModel;
use crate::models::{model_for, ResponseModel};
use crate::protocol::{Modality, Paradigm, Protocol};
use crate::rng::Lcg;
use crate::subject::Subject;
use crate::synth::{self, NoiseProfile};
use crate::waveform::{OddballRecording, Recording, Waveform};

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
        match protocol.modality {
            // Los cognitivos pasan por el flujo oddball; el canal es la diferencia.
            Modality::P300 | Modality::Mmn => {
                let odd = Self::simulate_oddball(protocol, subject);
                Recording {
                    channels: vec![odd.difference],
                    detected: odd.detected,
                    fsp: odd.fsp,
                    accepted_sweeps: odd.accepted_sweeps,
                    rejected_sweeps: odd.rejected_sweeps,
                }
            }
            // ASSR es de dominio de frecuencia; el canal lleva la epoca
            // promediada (vease tambien `simulate_assr`).
            Modality::Assr => {
                let (times, avg) = assr::averaged_epoch(protocol, subject);
                let res = assr::detect_assr(protocol, subject);
                Recording {
                    channels: vec![Waveform::new(times, avg)],
                    detected: Vec::new(),
                    fsp: res.f_ratio,
                    accepted_sweeps: res.n_epochs,
                    rejected_sweeps: 0,
                }
            }
            _ => match model_for(protocol.modality) {
                Some(model) => run_pipeline(&*model, protocol, subject),
                None => Recording::default(),
            },
        }
    }

    /// Detecta la respuesta ASSR (dominio de frecuencia): energia en la
    /// frecuencia de modulacion mediante FFT + F-test.
    pub fn simulate_assr(protocol: &Protocol, subject: &Subject) -> AssrResult {
        assr::detect_assr(protocol, subject)
    }

    /// Simula un paradigma oddball: promedia el flujo estandar y el desviante y
    /// calcula la onda diferencia (desviante − estandar).
    ///
    /// Devuelve un `OddballRecording` vacio si el protocolo no es oddball.
    pub fn simulate_oddball(protocol: &Protocol, subject: &Subject) -> OddballRecording {
        let Paradigm::Oddball {
            standard,
            deviant,
            deviant_prob,
        } = protocol.paradigm
        else {
            return OddballRecording::default();
        };

        let cog = CognitiveModel::new(protocol.modality);
        let acq = &protocol.acquisition;
        // Ruido cortical de fondo (banda lenta, grande), como en la ALR.
        let noise = impedance_noise(NoiseProfile::new(2.0), acq);

        let obligatory = cog.obligatory(&standard, subject);
        let diff_comps = cog.difference(&standard, &deviant, deviant_prob, subject);

        // Estandar: solo la respuesta obligatoria. Desviante: obligatoria + dif.
        let std_comps = obligatory.clone();
        let dev_comps: Vec<Component> = obligatory
            .into_iter()
            .chain(diff_comps.iter().cloned())
            .collect();

        let base = seed(protocol, subject);
        let std_resp = average_response(&std_comps, acq, &noise, base ^ 0x5101);
        let dev_resp = average_response(&dev_comps, acq, &noise, base ^ 0xD202);

        // Onda diferencia, punto a punto.
        let difference: Vec<f64> = dev_resp
            .mean
            .iter()
            .zip(std_resp.mean.iter())
            .map(|(d, s)| d - s)
            .collect();
        let detected = detect_peaks(&diff_comps, &dev_resp.times, &difference);
        let diff_times = dev_resp.times.clone();

        OddballRecording {
            standard: Waveform::new(std_resp.times, std_resp.mean),
            deviant: Waveform::new(dev_resp.times, dev_resp.mean),
            difference: Waveform::new(diff_times, difference),
            detected,
            fsp: dev_resp.fsp,
            accepted_sweeps: dev_resp.accepted,
            rejected_sweeps: dev_resp.rejected,
        }
    }
}

/// Ejecuta la cadena de adquisicion para un modelo concreto.
fn run_pipeline(model: &dyn ResponseModel, protocol: &Protocol, subject: &Subject) -> Recording {
    let acq = &protocol.acquisition;
    let comps = model.components(protocol, subject);
    let noise = impedance_noise(model.background_noise(subject), acq);
    let resp = average_response(&comps, acq, &noise, seed(protocol, subject));
    let detected = detect_peaks(&comps, &resp.times, &resp.mean);

    Recording {
        channels: vec![Waveform::new(resp.times, resp.mean)],
        detected,
        fsp: resp.fsp,
        accepted_sweeps: resp.accepted,
        rejected_sweeps: resp.rejected,
    }
}

/// Ruido de fondo elevado por la impedancia de electrodos.
pub(crate) fn impedance_noise(noise: NoiseProfile, acq: &Acquisition) -> NoiseProfile {
    NoiseProfile::new(noise.rms_uv * (1.0 + acq.impedance_kohm / 10.0))
}

/// Resultado de promediar un conjunto de componentes por la cadena de adquisicion.
pub(crate) struct AveragedResponse {
    pub times: Vec<f64>,
    pub mean: Vec<f64>,
    pub fsp: f64,
    pub accepted: u32,
    pub rejected: u32,
}

/// Promedia sweep a sweep (sintesis → artefacto → rechazo → filtro → baseline)
/// un conjunto de componentes. Es el nucleo reutilizable de la §4, compartido
/// por el flujo transitorio y por el oddball (dos flujos).
pub(crate) fn average_response(
    comps: &[Component],
    acq: &Acquisition,
    noise: &NoiseProfile,
    base_seed: u64,
) -> AveragedResponse {
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

    let mut produced = 0u32;
    while avg.accepted() < target && produced < max_attempts {
        let mut rng = Lcg::new(base_seed ^ (produced as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15));
        produced += 1;

        let mut sweep = synth::synth_sweep(comps, &times, noise, &mut rng);
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
    AveragedResponse {
        times,
        mean,
        fsp,
        accepted: avg.accepted(),
        rejected,
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
    // La ventana de busqueda debe cubrir al menos unas muestras de la rejilla:
    // a tasas de muestreo bajas (ALR/oddball) el paso temporal supera 0.7 ms.
    let grid_step = if times.len() > 1 {
        (times[1] - times[0]).abs()
    } else {
        PEAK_SEARCH_MS
    };
    let search = PEAK_SEARCH_MS.max(2.5 * grid_step);

    comps
        .iter()
        // El microfonico es oscilatorio: no tiene un pico puntual que medir.
        .filter(|c| !matches!(c.shape, ComponentShape::Microphonic { .. }))
        .filter(|c| c.amplitude_uv.abs() > 1e-3)
        .filter_map(|c| {
            // Busca el maximo si la deflexion esperada es positiva (ondas ABR) o
            // el minimo si es negativa (AP/SP de la ECochG).
            let want_max = c.amplitude_uv >= 0.0;
            let lo = c.latency_ms - search;
            let hi = c.latency_ms + search;
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
///
/// **No** depende de `acquisition.sweeps`: la semilla por-sweep se indexa con un
/// contador global de sweeps producidos, así el promedio acumulado de
/// `CaptureSession` tras N sweeps coincide exactamente con `simulate(N)` (G-core,
/// GUI.md §0.1).
fn seed(protocol: &Protocol, subject: &Subject) -> u64 {
    let s = &protocol.stimulus;
    let ear = match s.ear {
        crate::subject::Ear::Left => 1u64,
        crate::subject::Ear::Right => 2u64,
    };
    let lvl = (s.level.as_nhl() * 10.0) as i64 as u64;
    let rate = (s.rate_hz * 10.0) as u64;
    let temp = (subject.temperature_c * 10.0) as i64 as u64;
    let modal = protocol.modality as u64;

    ear.wrapping_mul(0x9E37_79B9)
        .wrapping_add(lvl.wrapping_mul(0x85EB_CA77))
        ^ rate.wrapping_mul(0xC2B2_AE3D)
        ^ temp.wrapping_mul(0x1656_67B1)
        ^ modal.wrapping_mul(0x9E37_79B1)
}

/// Sesión de captura progresiva: acumula sweeps de **a uno** y mantiene el
/// promedio en curso (G-core). Reusa el mismo pipeline que `average_response`,
/// así que tras aceptar N sweeps su promedio coincide **exactamente** con
/// `simulate(N)`. Sirve a la captura en vivo de la GUI (G3): cada `step` produce
/// una época cruda y actualiza el promedio acumulado.
///
/// Solo para modalidades transitorias (ABR/ECochG/MLR/ALR); oddball/ASSR no son
/// captura de promedio temporal.
pub struct CaptureSession {
    comps: Vec<Component>,
    noise: NoiseProfile,
    times: Vec<f64>,
    filter_template: IirFilter,
    artifact_reject_uv: f64,
    base_seed: u64,
    avg: Averager,
    produced: u32,
    rejected: u32,
    last_epoch: Vec<f64>,
}

impl CaptureSession {
    /// Crea una sesión para una modalidad transitoria; `None` para oddball/ASSR.
    pub fn new(protocol: &Protocol, subject: &Subject) -> Option<Self> {
        Self::new_with_salt(protocol, subject, 0)
    }

    /// Como `new`, pero mezcla `salt` en la semilla base para obtener un flujo de
    /// ruido **independiente** (réplicas A/B: misma señal, ruido distinto).
    pub fn new_with_salt(protocol: &Protocol, subject: &Subject, salt: u64) -> Option<Self> {
        if matches!(
            protocol.modality,
            Modality::P300 | Modality::Mmn | Modality::Assr
        ) {
            return None;
        }
        let model = model_for(protocol.modality)?;
        let acq = &protocol.acquisition;
        let comps = model.components(protocol, subject);
        let noise = impedance_noise(model.background_noise(subject), acq);
        let n = acq.window.n_samples(acq.sample_rate_hz).max(2);
        let times = synth::time_axis(&acq.window, n);
        let sp_index = n / 2;
        Some(Self {
            comps,
            noise,
            times,
            filter_template: IirFilter::from_bandpass(&acq.filter, acq.sample_rate_hz),
            artifact_reject_uv: acq.artifact_reject_uv,
            base_seed: seed(protocol, subject) ^ salt.wrapping_mul(0x9E37_79B9_7F4A_7C15),
            avg: Averager::new(n, f64::INFINITY, sp_index),
            produced: 0,
            rejected: 0,
            last_epoch: vec![0.0; n],
        })
    }

    /// Eje temporal (ms) de la ventana.
    pub fn times(&self) -> &[f64] {
        &self.times
    }
    /// Sweeps aceptados (promediados) hasta ahora.
    pub fn accepted(&self) -> u32 {
        self.avg.accepted()
    }
    /// Sweeps rechazados por artefacto hasta ahora.
    pub fn rejected(&self) -> u32 {
        self.rejected
    }
    /// Promedio acumulado (µV).
    pub fn mean(&self) -> Vec<f64> {
        self.avg.mean()
    }
    /// F_sp del promedio actual.
    pub fn fsp(&self) -> f64 {
        f_sp(&self.avg.mean(), self.avg.sp_samples())
    }
    /// Última época cruda aceptada (sweep filtrado + baseline).
    pub fn last_epoch(&self) -> &[f64] {
        &self.last_epoch
    }

    /// Produce el siguiente sweep (síntesis → artefacto → rechazo → filtro →
    /// baseline → acumulación). Devuelve `true` si fue aceptado. Cuerpo idéntico
    /// al bucle de `average_response`, paso a paso.
    pub fn step(&mut self) -> bool {
        let mut rng = Lcg::new(
            self.base_seed ^ (self.produced as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15),
        );
        self.produced += 1;
        let mut sweep = synth::synth_sweep(&self.comps, &self.times, &self.noise, &mut rng);
        inject_artifact(&mut sweep, &mut rng, self.artifact_reject_uv);
        if sweep.iter().any(|v| v.abs() > self.artifact_reject_uv) {
            self.rejected += 1;
            return false;
        }
        let mut filt = self.filter_template.clone();
        filt.reset();
        filt.process(&mut sweep);
        baseline_correct(&mut sweep, &self.times);
        self.avg.add(&sweep);
        self.last_epoch = sweep;
        true
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::protocol::Protocol;
    use crate::subject::{Attention, Ear, Subject};
    use crate::units::Level;

    #[test]
    fn captura_acumulada_igual_a_simulate() {
        // El promedio de CaptureSession tras N aceptados == simulate(N) (G-core).
        let mut p = Protocol::abr_click(Ear::Right);
        p.acquisition.sweeps = 200;
        let s = Subject::default();
        let full = EvokedPotentialEngine::simulate(&p, &s);

        let mut cap = CaptureSession::new(&p, &s).expect("ABR es transitoria");
        let mut guard = 0;
        while cap.accepted() < 200 && guard < 10_000 {
            cap.step();
            guard += 1;
        }
        assert_eq!(cap.accepted(), 200);
        assert_eq!(cap.mean(), full.channels[0].amplitudes_uv);
        assert_eq!(cap.rejected(), full.rejected_sweeps);
    }

    #[test]
    fn captura_oddball_es_none() {
        let p = Protocol::p300(Ear::Right);
        assert!(CaptureSession::new(&p, &Subject::default()).is_none());
    }

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
    fn assr_por_simulate_devuelve_la_epoca_promediada() {
        // Todas las modalidades estan implementadas; el ASSR por `simulate`
        // entrega la epoca promediada como canal (la deteccion va por
        // `simulate_assr`).
        let p = Protocol::assr_default(Ear::Right);
        let rec = EvokedPotentialEngine::simulate(&p, &Subject::default());
        assert!(!rec.channels.is_empty());
        assert!(rec.detected.is_empty());
    }

    #[test]
    fn oddball_detecta_p3b_y_mmn_con_atencion() {
        let p = Protocol::p300(Ear::Right);
        let subj = Subject {
            attention: Attention::Active,
            ..Default::default()
        };
        let odd = EvokedPotentialEngine::simulate_oddball(&p, &subj);
        assert!(odd.peak("MMN").is_some(), "falta MMN");
        assert!(odd.peak("P3b").is_some(), "falta P3b");
        // Las tres curvas tienen la misma longitud.
        assert_eq!(odd.standard.len(), odd.difference.len());
        assert_eq!(odd.deviant.len(), odd.difference.len());
    }

    #[test]
    fn oddball_sin_atencion_mantiene_mmn_pero_no_p3b() {
        let p = Protocol::p300(Ear::Right);
        let subj = Subject {
            attention: Attention::Ignoring,
            ..Default::default()
        };
        let odd = EvokedPotentialEngine::simulate_oddball(&p, &subj);
        assert!(odd.peak("MMN").is_some(), "la MMN es preatencional");
        assert!(odd.peak("P3b").is_none(), "la P3b necesita atencion");
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
