//! # aep-core
//!
//! Motor de simulacion de **Potenciales Evocados Auditivos** (AEP): desde la
//! electrococleografia (ECochG) hasta los potenciales cognitivos (P300/MMN) y
//! el ASSR, con una sola arquitectura. Independiente de la GUI.
//!
//! La idea central (MOTOR.md): toda la familia de AEP comparte la misma
//! estructura — estimulo → componentes neurales → modulacion por sujeto y
//! parametros → sintesis (senal + ruido) → cadena de adquisicion (filtro,
//! ventana, promediacion) → registro. Lo unico que cambia por modalidad es el
//! `ResponseModel`. La Capa 0 implementa el nucleo + el ABR.
//!
//! ```
//! use aep_core::{EvokedPotentialEngine, Protocol, Subject, Ear};
//!
//! let protocol = Protocol::abr_click(Ear::Right);
//! let subject = Subject::default();
//! let rec = EvokedPotentialEngine::simulate(&protocol, &subject);
//!
//! let curva = rec.primary().expect("hay un canal");
//! assert!(!curva.is_empty());
//! // La onda V se detecta en el registro.
//! assert!(rec.detected.iter().any(|w| w.label == "V"));
//! ```

pub mod acquisition;
pub mod assr;
pub mod audiometry;
pub mod cases;
pub mod component;
pub mod dsp;
pub mod engine;
pub mod lesion;
pub mod models;
pub mod modulation;
pub mod norms;
pub mod protocol;
pub mod rng;
pub mod stimulus;
pub mod subject;
pub mod synth;
pub mod units;
pub mod waveform;

// --- Re-exports de la API publica ---

pub use acquisition::{
    Acquisition, Bandpass, Channel, ElectrodeSite, Montage, TimeWindow,
};
pub use assr::{assr_audiogram, assr_threshold, detect_assr, AssrResult};
pub use audiometry::{
    estimate_audiogram, estimate_audiogram_chirp, estimate_audiogram_with, estimate_threshold,
    latency_intensity_curve,
};
pub use cases::{CaseCatalog, CaseDef};
pub use component::{Component, ComponentShape, WavePeak};
pub use engine::EvokedPotentialEngine;
pub use lesion::{FreqProfile, Lesion, LesionSite};
pub use models::{model_for, ResponseModel};
pub use modulation::{
    apply_age, apply_intensity, apply_polarity, apply_rate, apply_sex, apply_temperature,
    apply_tone_frequency,
};
pub use protocol::{Modality, Paradigm, Protocol};
pub use rng::Lcg;
pub use stimulus::{
    ChirpKind, Masking, NoiseBand, Polarity, RampWindow, SpeechToken, Stimulus, StimulusKind,
    Transducer,
};
pub use subject::{Age, ArousalState, Attention, Ear, Sex, Subject};
pub use synth::NoiseProfile;
pub use units::Level;
pub use waveform::{OddballRecording, Recording, Waveform};
