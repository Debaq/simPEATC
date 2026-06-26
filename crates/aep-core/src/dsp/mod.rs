//! Cadena de adquisicion (DSP real).
//!
//! Reproduce lo que hace el equipo, muestra a muestra: filtro IIR Butterworth,
//! ventana/baseline, promediacion sweep-a-sweep con rechazo de artefactos y
//! calculo de F_sp. El filtrado y la promediacion son **reales** sobre las
//! muestras, no un efecto aproximado (MOTOR.md §6).

pub mod average;
pub mod fft;
pub mod filter;
pub mod fsp;

pub use average::Averager;
pub use fft::{fft_in_place, power_spectrum};
pub use filter::IirFilter;
pub use fsp::f_sp;
