//! Patologia parametrica.
//!
//! En vez de un catalogo cerrado de enfermedades, una lesion se describe por
//! *sitio* + *grado* + *perfil frecuencial*. El modelo de respuesta deriva de
//! ahi que componentes se alteran y como (MOTOR.md §3, §5.3). Encima se montan
//! presets clinicos (catalogo de casos) en capas posteriores.

use crate::subject::Ear;

/// Sitio anatomico de la lesion: define el *patron* de alteracion.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LesionSite {
    /// Conductiva (oido medio): desplaza umbral y alarga latencias absolutas;
    /// los intervalos interpico se mantienen normales.
    Conductive,
    /// Coclear (sensorial): reclutamiento; latencias casi normales a alta
    /// intensidad pese a umbral elevado.
    Cochlear,
    /// Retrococlear (VIII par): alarga intervalos I-V e I-III; afecta onda V.
    Retrocochlear,
    /// Neural (neuropatia/desincronia): AP/ABR ausentes o muy anomalos con
    /// microfonico coclear (CM) presente.
    Neural,
    /// Central (tronco/corteza): afecta componentes tardios segun el nivel.
    Central,
}

/// Perfil frecuencial de la perdida (forma del audiograma).
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum FreqProfile {
    /// Plano: misma perdida en todas las frecuencias.
    Flat,
    /// Caida en agudos (descendente).
    HighFrequency,
    /// Caida en graves (ascendente).
    LowFrequency,
    /// En cubeta (cookie-bite): peor en medias.
    CookieBite,
    /// Muesca (p.ej. trauma acustico a 4 kHz).
    Notch { center_hz: f64 },
}

impl FreqProfile {
    /// Factor `[0, 1]` de cuanto pesa la perdida a una frecuencia dada.
    ///
    /// 1.0 = perdida plena del `severity_db`; 0.0 = frecuencia respetada. Para
    /// estimulos de banda ancha (click) se usa la media (~`weight(2000)`).
    pub fn weight_at(self, freq_hz: f64) -> f64 {
        let f = freq_hz.max(1.0);
        match self {
            FreqProfile::Flat => 1.0,
            FreqProfile::HighFrequency => smoothstep(500.0, 4000.0, f),
            FreqProfile::LowFrequency => 1.0 - smoothstep(250.0, 2000.0, f),
            FreqProfile::CookieBite => {
                // Maximo alrededor de 1-2 kHz, menor en extremos.
                let center = 1500.0_f64;
                let oct = (f / center).log2().abs();
                (1.0 - smoothstep(0.0, 2.5, oct)).max(0.0)
            }
            FreqProfile::Notch { center_hz } => {
                let oct = (f / center_hz).log2().abs();
                (1.0 - smoothstep(0.0, 1.0, oct)).max(0.0)
            }
        }
    }
}

/// Una lesion concreta.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Lesion {
    /// Sitio anatomico.
    pub site: LesionSite,
    /// Oido afectado.
    pub ear: Ear,
    /// Grado: umbral anadido en dB.
    pub severity_db: f64,
    /// Perfil frecuencial.
    pub freq_profile: FreqProfile,
}

impl Lesion {
    /// Desplazamiento de umbral efectivo (dB) a una frecuencia dada.
    pub fn threshold_shift_at(&self, freq_hz: f64) -> f64 {
        self.severity_db * self.freq_profile.weight_at(freq_hz)
    }
}

/// Interpolacion suave de Hermite entre `edge0` y `edge1`, recortada a `[0, 1]`.
fn smoothstep(edge0: f64, edge1: f64, x: f64) -> f64 {
    if (edge1 - edge0).abs() < f64::EPSILON {
        return if x < edge0 { 0.0 } else { 1.0 };
    }
    let t = ((x - edge0) / (edge1 - edge0)).clamp(0.0, 1.0);
    t * t * (3.0 - 2.0 * t)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn perfil_plano_pesa_uno() {
        assert_eq!(FreqProfile::Flat.weight_at(500.0), 1.0);
        assert_eq!(FreqProfile::Flat.weight_at(4000.0), 1.0);
    }

    #[test]
    fn agudos_pesa_mas_en_alta_frecuencia() {
        let p = FreqProfile::HighFrequency;
        assert!(p.weight_at(4000.0) > p.weight_at(500.0));
    }

    #[test]
    fn graves_pesa_mas_en_baja_frecuencia() {
        let p = FreqProfile::LowFrequency;
        assert!(p.weight_at(250.0) > p.weight_at(4000.0));
    }

    #[test]
    fn notch_maximo_en_centro() {
        let p = FreqProfile::Notch { center_hz: 4000.0 };
        assert!(p.weight_at(4000.0) > p.weight_at(1000.0));
        assert!(p.weight_at(4000.0) > p.weight_at(8000.0));
    }

    #[test]
    fn threshold_shift_escala_con_severidad() {
        let l = Lesion {
            site: LesionSite::Cochlear,
            ear: Ear::Right,
            severity_db: 40.0,
            freq_profile: FreqProfile::Flat,
        };
        assert!((l.threshold_shift_at(2000.0) - 40.0).abs() < 1e-9);
    }
}
