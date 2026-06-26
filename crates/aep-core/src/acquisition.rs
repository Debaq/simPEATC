//! Cadena de adquisicion: lo que el *equipo* mide y como.
//!
//! Separado de la verdad fisiologica: un mismo paciente se ve distinto segun se
//! configure el equipo (MOTOR.md §4). Aqui viven la ventana de analisis, el
//! filtro, el montaje de electrodos y los parametros de promediacion.

use crate::subject::Ear;

/// Ventana temporal del registro, relativa al estimulo (t=0).
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct TimeWindow {
    /// Pre-estimulo (ms) usado como linea base. Positivo = ms antes de t=0.
    pub pre_ms: f64,
    /// Post-estimulo (ms): duracion analizada tras el estimulo.
    pub post_ms: f64,
}

impl TimeWindow {
    /// Duracion total de la ventana (pre + post) en ms.
    pub fn total_ms(self) -> f64 {
        self.pre_ms + self.post_ms
    }

    /// Numero de muestras a una tasa de muestreo dada.
    pub fn n_samples(self, sample_rate_hz: f64) -> usize {
        ((self.total_ms() / 1000.0) * sample_rate_hz).round() as usize
    }

    /// Tiempo (ms, relativo a t=0) de la muestra `i` de `n` totales.
    pub fn time_at(self, i: usize, n: usize) -> f64 {
        if n <= 1 {
            return -self.pre_ms;
        }
        -self.pre_ms + self.total_ms() * i as f64 / (n as f64 - 1.0)
    }
}

/// Filtro pasa-banda de adquisicion.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Bandpass {
    /// Frecuencia de corte pasa-altos (Hz).
    pub hp_hz: f64,
    /// Frecuencia de corte pasa-bajos (Hz).
    pub lp_hz: f64,
    /// Notch opcional (50/60 Hz).
    pub notch_hz: Option<f64>,
    /// Orden del Butterworth (por seccion HP y LP).
    pub order: u8,
}

/// Posicion de un electrodo (sistema 10-20 ampliado + sitios coclearas).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ElectrodeSite {
    /// Vertex.
    Cz,
    /// Frontal medio.
    Fz,
    /// Frontopolar medio (frente alta).
    Fpz,
    /// Mastoides del oido indicado.
    Mastoid(Ear),
    /// Lobulo de la oreja del oido indicado.
    Earlobe(Ear),
    /// Conducto auditivo externo (ECochG extratimpanica).
    EarCanal(Ear),
    /// Promontorio / transtimpanica (ECochG invasiva).
    Promontory(Ear),
    /// Nuca / 7a cervical.
    Nape,
}

/// Canal diferencial (no invasivo − invasivo/referencia).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Channel {
    /// Electrodo activo (no inversor).
    pub noninv: ElectrodeSite,
    /// Electrodo de referencia (inversor).
    pub inv: ElectrodeSite,
}

/// Montaje de electrodos.
#[derive(Debug, Clone, PartialEq)]
pub struct Montage {
    /// Canales registrados.
    pub channels: Vec<Channel>,
    /// Electrodo de tierra.
    pub ground: ElectrodeSite,
}

impl Montage {
    /// Montaje ABR ipsilateral clasico: Cz − mastoides del oido estimulado,
    /// tierra en Fpz.
    pub fn abr_ipsilateral(ear: Ear) -> Self {
        Self {
            channels: vec![Channel {
                noninv: ElectrodeSite::Cz,
                inv: ElectrodeSite::Mastoid(ear),
            }],
            ground: ElectrodeSite::Fpz,
        }
    }
}

/// Parametros completos de adquisicion.
#[derive(Debug, Clone, PartialEq)]
pub struct Acquisition {
    /// Ventana de analisis.
    pub window: TimeWindow,
    /// Filtro pasa-banda.
    pub filter: Bandpass,
    /// Promediaciones objetivo (sweeps aceptados).
    pub sweeps: u32,
    /// Umbral de rechazo de artefactos (µV); sweeps que lo superan se descartan.
    pub artifact_reject_uv: f64,
    /// Tasa de muestreo (Hz).
    pub sample_rate_hz: f64,
    /// Ganancia del amplificador.
    pub gain: f64,
    /// Montaje.
    pub montage: Montage,
    /// Impedancia de electrodos (kΩ); eleva el piso de ruido.
    pub impedance_kohm: f64,
}

impl Acquisition {
    /// Configuracion ABR por defecto: ventana 1 ms pre + 12 ms post, 100-3000 Hz
    /// orden 2, 2000 sweeps, rechazo a 25 µV, 30 kHz de muestreo.
    pub fn abr_default(ear: Ear) -> Self {
        Self {
            window: TimeWindow {
                pre_ms: 1.0,
                post_ms: 12.0,
            },
            filter: Bandpass {
                hp_hz: 100.0,
                lp_hz: 3000.0,
                notch_hz: None,
                order: 2,
            },
            sweeps: 2000,
            artifact_reject_uv: 25.0,
            sample_rate_hz: 30_000.0,
            gain: 100_000.0,
            montage: Montage::abr_ipsilateral(ear),
            impedance_kohm: 3.0,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ventana_total_y_muestras() {
        let w = TimeWindow {
            pre_ms: 1.0,
            post_ms: 9.0,
        };
        assert_eq!(w.total_ms(), 10.0);
        // 10 ms a 30 kHz = 300 muestras.
        assert_eq!(w.n_samples(30_000.0), 300);
    }

    #[test]
    fn primera_muestra_en_menos_pre() {
        let w = TimeWindow {
            pre_ms: 2.0,
            post_ms: 10.0,
        };
        assert!((w.time_at(0, 100) - (-2.0)).abs() < 1e-9);
        assert!((w.time_at(99, 100) - 10.0).abs() < 1e-9);
    }

    #[test]
    fn abr_default_filtra_100_3000() {
        let a = Acquisition::abr_default(Ear::Right);
        assert_eq!(a.filter.hp_hz, 100.0);
        assert_eq!(a.filter.lp_hz, 3000.0);
        assert_eq!(a.montage.channels.len(), 1);
    }
}
