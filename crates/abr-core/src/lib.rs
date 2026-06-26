//! # abr-core
//!
//! Motor de simulacion de Potenciales Evocados Auditivos de Tronco Cerebral
//! (PEATC / ABR). Independiente de cualquier GUI: solo modela la senal.
//!
//! ```
//! use abr_core::{AbrGenerator, StimParams};
//!
//! let gen = AbrGenerator::new(StimParams::default());
//! let curva = gen.generate();
//! assert!(!curva.is_empty());
//! ```

pub mod generator;
pub mod params;
pub mod waveform;

pub use generator::{AbrGenerator, DURATION_MS};
pub use params::{Ear, StimParams};
pub use waveform::{WavePeak, Waveform};
