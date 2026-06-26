//! Audiometria por ABR (MOTOR.md §12, Capa 3).
//!
//! Sobre el modelo de respuesta se construyen las herramientas clinicas:
//! - **Umbral** por frecuencia: la menor intensidad con onda V detectable.
//! - **Curva latencia-intensidad**: como se retrasa la onda V al bajar el nivel.
//! - **Audiograma estimado**: umbral por tone-burst en varias frecuencias.
//!
//! Trabaja sobre los **componentes** (verdad fisiologica, deterministas), no
//! sobre el registro ruidoso: el umbral estimado refleja el perfil de la lesion,
//! que es justo lo que el ABR estima en la clinica.

use crate::models::model_for;
use crate::protocol::Protocol;
use crate::subject::{Ear, Subject};
use crate::units::Level;

/// Amplitud minima de onda V considerada "detectable" (µV).
pub const DETECTABLE_UV: f64 = 0.04;

/// Amplitud absoluta de la onda V para un protocolo.
fn wave_v_amplitude(protocol: &Protocol, subject: &Subject) -> f64 {
    model_for(protocol.modality)
        .and_then(|m| {
            m.components(protocol, subject)
                .into_iter()
                .find(|c| c.label == "V")
                .map(|c| c.amplitude_uv.abs())
        })
        .unwrap_or(0.0)
}

/// Latencia de la onda V, si es detectable.
fn wave_v_latency(protocol: &Protocol, subject: &Subject) -> Option<f64> {
    let m = model_for(protocol.modality)?;
    let v = m
        .components(protocol, subject)
        .into_iter()
        .find(|c| c.label == "V")?;
    if v.amplitude_uv.abs() < DETECTABLE_UV {
        return None;
    }
    Some(v.latency_ms)
}

/// Estima el umbral (dB nHL) como la menor intensidad con onda V detectable.
///
/// Baja desde 100 dB en pasos de 5 dB. Devuelve `None` si no hay respuesta.
pub fn estimate_threshold(base: &Protocol, subject: &Subject) -> Option<f64> {
    let mut proto = base.clone();
    let mut threshold = None;
    let mut level = 100.0_f64;
    while level >= 0.0 {
        proto.stimulus.level = Level::DbNhl(level);
        if wave_v_amplitude(&proto, subject) >= DETECTABLE_UV {
            threshold = Some(level);
        } else if threshold.is_some() {
            // Ya cruzamos el umbral hacia abajo: no hace falta seguir.
            break;
        }
        level -= 5.0;
    }
    threshold
}

/// Curva latencia-intensidad: `(intensidad dB nHL, latencia V ms)` para los
/// niveles dados en que la onda V es detectable.
pub fn latency_intensity_curve(
    base: &Protocol,
    subject: &Subject,
    levels: &[f64],
) -> Vec<(f64, f64)> {
    let mut proto = base.clone();
    levels
        .iter()
        .filter_map(|&lvl| {
            proto.stimulus.level = Level::DbNhl(lvl);
            wave_v_latency(&proto, subject).map(|lat| (lvl, lat))
        })
        .collect()
}

/// Audiograma estimado con un constructor de protocolo por frecuencia.
///
/// Permite estimar el umbral con distintos estimulos especificos en frecuencia
/// (tone-burst o NB-chirp). El umbral es `None` donde no hay respuesta a ≤100 dB.
pub fn estimate_audiogram_with(
    ear: Ear,
    subject: &Subject,
    freqs: &[f64],
    make_protocol: impl Fn(Ear, f64) -> Protocol,
) -> Vec<(f64, Option<f64>)> {
    freqs
        .iter()
        .map(|&f| (f, estimate_threshold(&make_protocol(ear, f), subject)))
        .collect()
}

/// Audiograma estimado por ABR **tone-burst**.
pub fn estimate_audiogram(ear: Ear, subject: &Subject, freqs: &[f64]) -> Vec<(f64, Option<f64>)> {
    estimate_audiogram_with(ear, subject, freqs, Protocol::abr_toneburst)
}

/// Audiograma estimado por ABR **NB-chirp** (banda estrecha).
pub fn estimate_audiogram_chirp(
    ear: Ear,
    subject: &Subject,
    freqs: &[f64],
) -> Vec<(f64, Option<f64>)> {
    estimate_audiogram_with(ear, subject, freqs, Protocol::abr_nbchirp)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::lesion::{FreqProfile, Lesion, LesionSite};

    fn cochlear(severity: f64, profile: FreqProfile) -> Lesion {
        Lesion {
            site: LesionSite::Cochlear,
            ear: Ear::Right,
            severity_db: severity,
            freq_profile: profile,
        }
    }

    #[test]
    fn normal_umbral_bajo_en_todas_las_frecuencias() {
        let audio = estimate_audiogram(Ear::Right, &Subject::default(), &[500.0, 1000.0, 2000.0, 4000.0]);
        for (f, th) in audio {
            let th = th.unwrap_or_else(|| panic!("sin umbral en {f} Hz"));
            assert!(th <= 25.0, "freq {f} umbral {th}");
        }
    }

    #[test]
    fn perdida_en_agudos_da_audiograma_descendente() {
        let mut s = Subject::default();
        s.lesions.push(cochlear(55.0, FreqProfile::HighFrequency));
        let audio = estimate_audiogram(Ear::Right, &s, &[500.0, 4000.0]);
        let grave = audio.iter().find(|(f, _)| *f == 500.0).unwrap().1.unwrap();
        let agudo = audio.iter().find(|(f, _)| *f == 4000.0).unwrap().1.unwrap();
        assert!(agudo > grave + 20.0, "500={grave} 4000={agudo}");
    }

    #[test]
    fn latencia_cae_con_la_intensidad() {
        let base = Protocol::abr_click(Ear::Right);
        let curve = latency_intensity_curve(&base, &Subject::default(), &[40.0, 60.0, 80.0]);
        assert_eq!(curve.len(), 3);
        // A menor intensidad, mayor latencia.
        assert!(curve[0].1 > curve[2].1, "lat@40={} lat@80={}", curve[0].1, curve[2].1);
    }

    #[test]
    fn audiograma_por_chirp_tambien_desciende_en_agudos() {
        let mut s = Subject::default();
        s.lesions.push(cochlear(55.0, FreqProfile::HighFrequency));
        let audio = estimate_audiogram_chirp(Ear::Right, &s, &[500.0, 4000.0]);
        let grave = audio.iter().find(|(f, _)| *f == 500.0).unwrap().1.unwrap();
        let agudo = audio.iter().find(|(f, _)| *f == 4000.0).unwrap().1.unwrap();
        assert!(agudo > grave + 20.0, "500={grave} 4000={agudo}");
    }

    #[test]
    fn perdida_profunda_no_da_respuesta() {
        let mut s = Subject::default();
        s.lesions.push(cochlear(120.0, FreqProfile::Flat));
        let base = Protocol::abr_toneburst(Ear::Right, 2000.0);
        assert!(estimate_threshold(&base, &s).is_none());
    }

    #[test]
    fn umbral_sube_con_la_severidad() {
        let leve = {
            let mut s = Subject::default();
            s.lesions.push(cochlear(20.0, FreqProfile::Flat));
            estimate_threshold(&Protocol::abr_toneburst(Ear::Right, 2000.0), &s).unwrap()
        };
        let grave = {
            let mut s = Subject::default();
            s.lesions.push(cochlear(60.0, FreqProfile::Flat));
            estimate_threshold(&Protocol::abr_toneburst(Ear::Right, 2000.0), &s).unwrap()
        };
        assert!(grave > leve, "leve={leve} grave={grave}");
    }
}
