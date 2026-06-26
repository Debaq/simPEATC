//! Backend Tauri de simPEATC.
//!
//! Expone el motor `aep-core` al frontend web mediante comandos
//! `#[tauri::command]`. Cada comando construye un `Protocol` + `Subject` a partir
//! de parametros primitivos (JSON) y devuelve el resultado serializado.

use aep_core::{
    assr_audiogram, estimate_audiogram, estimate_audiogram_chirp, Age, ArousalState, Attention,
    AssrResult, CaseCatalog, ChirpKind, Ear, EvokedPotentialEngine, FreqProfile, Lesion, LesionSite,
    Level, OddballRecording, Paradigm, Polarity, Protocol, RampWindow, Recording, Sex,
    StimulusKind, Subject, Transducer,
};
use serde::{Deserialize, Serialize};

mod clinical;

// --- Parametros de entrada (JSON desde el frontend) ---

/// Lesion opcional del sujeto.
#[derive(Debug, Clone, Deserialize)]
pub struct LesionParams {
    /// "Conductive" | "Cochlear" | "Retrocochlear" | "Neural" | "Central".
    pub site: String,
    /// Grado: umbral anadido en dB.
    pub severity_db: f64,
    /// "Flat" | "HighFrequency" | "LowFrequency" | "CookieBite".
    pub profile: String,
}

/// Variables fisiologicas del sujeto.
#[derive(Debug, Clone, Deserialize)]
pub struct SubjectParams {
    /// Edad en anos.
    pub age_years: f64,
    /// "Male" | "Female".
    pub sex: String,
    /// Temperatura corporal (°C).
    pub temperature_c: f64,
    /// "Awake" | "NaturalSleep" | "Sedated" | "Anesthetized".
    pub state: String,
    /// "Active" | "Passive" | "Ignoring".
    pub attention: String,
    /// Lesion en el oido explorado (opcional).
    pub lesion: Option<LesionParams>,
}

/// Parametros completos de una captura.
#[derive(Debug, Clone, Deserialize)]
pub struct SimParams {
    /// "ECochG" | "Abr" | "Mlr" | "Alr" | "P300" | "Mmn" | "Assr".
    pub modality: String,
    /// "Left" | "Right".
    pub ear: String,
    /// Tipo de estimulo para ABR: "click" | "toneburst" | "ce_chirp" | "ls_chirp" | "nb_chirp".
    #[serde(default)]
    pub stimulus: Option<String>,
    /// Intensidad (dB nHL).
    pub intensity_db: f64,
    /// Promediaciones objetivo.
    pub sweeps: u32,
    /// Frecuencia del tone-burst / NB-chirp (Hz).
    #[serde(default = "default_freq")]
    pub freq_hz: f64,
    /// Portadora ASSR (Hz).
    #[serde(default = "default_carrier")]
    pub carrier_hz: f64,
    /// Frecuencia de modulacion ASSR (Hz).
    #[serde(default = "default_mod_freq")]
    pub mod_freq_hz: f64,
    /// Equipo (opcional): si falta, se usan los valores por defecto de la modalidad.
    #[serde(default)]
    pub equipo: Option<EquipoParams>,
    /// Sujeto.
    pub subject: SubjectParams,
}

/// Ajustes del equipo (estímulo + adquisición) que el alumno configura.
/// Todos opcionales: cada `None` deja el valor por defecto de la modalidad.
#[derive(Debug, Clone, Default, Deserialize)]
pub struct EquipoParams {
    /// Tasa de estimulación (estímulos/s).
    pub rate_hz: Option<f64>,
    /// "Rarefaction" | "Condensation" | "Alternating".
    pub polarity: Option<String>,
    /// "Insert" | "Supraaural" | "BoneConductor" | "FreeField".
    pub transducer: Option<String>,
    /// Pasa-altos del filtro (Hz).
    pub hp_hz: Option<f64>,
    /// Pasa-bajos del filtro (Hz).
    pub lp_hz: Option<f64>,
    /// Notch (Hz); `0` o ausente = desactivado.
    pub notch_hz: Option<f64>,
    /// Orden del filtro.
    pub order: Option<u8>,
    /// Tipo de filtro: "Butterworth" | "Bessel" | "Chebyshev".
    /// TODO: el motor solo implementa Butterworth; Bessel/Chebyshev quedan
    /// pendientes en `aep-core/src/dsp/filter.rs`. Por ahora se ignora.
    #[serde(default)]
    pub filter_type: Option<String>,
    /// Ventana de rampa del tone-burst: "Linear" | "Hanning" | "Blackman" | "Gaussian".
    pub ramp: Option<String>,
    /// Ventana: pre-estímulo (ms).
    pub pre_ms: Option<f64>,
    /// Ventana: post-estímulo (ms).
    pub post_ms: Option<f64>,
    /// Umbral de rechazo de artefactos (µV).
    pub artifact_reject_uv: Option<f64>,
    /// Impedancia de electrodos (kΩ): eleva el piso de ruido.
    pub impedance_kohm: Option<f64>,
}

fn default_freq() -> f64 {
    2000.0
}
fn default_carrier() -> f64 {
    2000.0
}
fn default_mod_freq() -> f64 {
    80.0
}

// --- Salida discriminada ---

/// Resultado de una captura, etiquetado por tipo para el frontend.
#[derive(Debug, Clone, Serialize)]
#[serde(tag = "kind", content = "data", rename_all = "snake_case")]
pub enum SimOutput {
    /// Registro transitorio (ECochG/ABR/MLR/ALR).
    Transient(Recording),
    /// Registro oddball (P300/MMN).
    Oddball(OddballRecording),
    /// Resultado espectral (ASSR).
    Assr(AssrResult),
}

/// Resumen de un caso del catalogo.
#[derive(Debug, Clone, Serialize)]
pub struct CaseInfo {
    /// Identificador estable.
    pub id: String,
    /// Nombre legible.
    pub name: String,
    /// Descripcion didactica.
    pub description: String,
    /// Modalidad ("Abr"/"ECochG"/...).
    pub modality: String,
    /// Oido explorado ("OD"/"OI").
    pub ear: String,
}

// --- Construccion de tipos del motor ---

pub(crate) fn parse_ear(s: &str) -> Ear {
    match s {
        "Left" | "OI" => Ear::Left,
        _ => Ear::Right,
    }
}

fn parse_sex(s: &str) -> Sex {
    match s {
        "Male" => Sex::Male,
        _ => Sex::Female,
    }
}

fn parse_state(s: &str) -> ArousalState {
    match s {
        "NaturalSleep" => ArousalState::NaturalSleep,
        "Sedated" => ArousalState::Sedated,
        "Anesthetized" => ArousalState::Anesthetized,
        _ => ArousalState::Awake,
    }
}

fn parse_attention(s: &str) -> Attention {
    match s {
        "Active" => Attention::Active,
        "Ignoring" => Attention::Ignoring,
        _ => Attention::Passive,
    }
}

fn parse_site(s: &str) -> LesionSite {
    match s {
        "Conductive" => LesionSite::Conductive,
        "Retrocochlear" => LesionSite::Retrocochlear,
        "Neural" => LesionSite::Neural,
        "Central" => LesionSite::Central,
        _ => LesionSite::Cochlear,
    }
}

fn parse_profile(s: &str) -> FreqProfile {
    match s {
        "HighFrequency" => FreqProfile::HighFrequency,
        "LowFrequency" => FreqProfile::LowFrequency,
        "CookieBite" => FreqProfile::CookieBite,
        _ => FreqProfile::Flat,
    }
}

fn build_subject(p: &SubjectParams, ear: Ear) -> Subject {
    let mut subject = Subject {
        age: Age::Years { value: p.age_years },
        sex: parse_sex(&p.sex),
        temperature_c: p.temperature_c,
        state: parse_state(&p.state),
        attention: parse_attention(&p.attention),
        lesions: Vec::new(),
    };
    if let Some(l) = &p.lesion {
        subject.lesions.push(Lesion {
            site: parse_site(&l.site),
            ear,
            severity_db: l.severity_db,
            freq_profile: parse_profile(&l.profile),
        });
    }
    subject
}

/// Construye el `Protocol` segun modalidad, estimulo e intensidad.
pub(crate) fn build_protocol(p: &SimParams, ear: Ear) -> Protocol {
    let mut proto = match p.modality.as_str() {
        "ECochG" => Protocol::ecochg(ear),
        "Mlr" => Protocol::mlr(ear),
        "Alr" => Protocol::alr(ear),
        "P300" => Protocol::p300(ear),
        "Mmn" => Protocol::mmn(ear),
        "Assr" => Protocol::assr(ear, p.carrier_hz, p.mod_freq_hz),
        // ABR (por defecto): el tipo de estimulo lo decide `stimulus`.
        _ => match p.stimulus.as_deref() {
            Some("toneburst") => Protocol::abr_toneburst(ear, p.freq_hz),
            Some("ce_chirp") => Protocol::abr_chirp(ear, ChirpKind::CeChirp),
            Some("ls_chirp") => Protocol::abr_chirp(ear, ChirpKind::LsChirp),
            Some("nb_chirp") => Protocol::abr_nbchirp(ear, p.freq_hz),
            _ => Protocol::abr_click(ear),
        },
    };

    proto.acquisition.sweeps = p.sweeps;
    let level = Level::DbNhl(p.intensity_db);

    // La intensidad aplica al estimulo principal y, en oddball, a ambos flujos.
    proto.stimulus.level = level;
    if let Paradigm::Oddball {
        standard, deviant, ..
    } = &mut proto.paradigm
    {
        standard.level = level;
        deviant.level = level;
    }

    // Ajustes de equipo del alumno (cada None deja el default de la modalidad).
    if let Some(eq) = &p.equipo {
        apply_equipo(&mut proto, eq);
    }

    proto
}

fn parse_polarity(s: &str) -> Polarity {
    match s {
        "Condensation" => Polarity::Condensation,
        "Alternating" => Polarity::Alternating,
        _ => Polarity::Rarefaction,
    }
}

fn parse_transducer(s: &str) -> Transducer {
    match s {
        "Supraaural" => Transducer::Supraaural,
        "BoneConductor" => Transducer::BoneConductor,
        "FreeField" => Transducer::FreeField,
        _ => Transducer::Insert,
    }
}

fn parse_ramp(s: &str) -> RampWindow {
    match s {
        "Linear" => RampWindow::Linear,
        "Blackman" => RampWindow::Blackman,
        "Gaussian" => RampWindow::Gaussian,
        _ => RampWindow::Hanning,
    }
}

/// Aplica los ajustes de equipo sobre el protocolo (estímulo + adquisición).
fn apply_equipo(proto: &mut Protocol, eq: &EquipoParams) {
    if let Some(r) = eq.rate_hz {
        proto.stimulus.rate_hz = r;
    }
    if let Some(p) = &eq.polarity {
        proto.stimulus.polarity = parse_polarity(p);
    }
    if let Some(t) = &eq.transducer {
        proto.stimulus.transducer = parse_transducer(t);
    }
    if let Some(r) = &eq.ramp {
        if let StimulusKind::ToneBurst { window, .. } = &mut proto.stimulus.kind {
            *window = parse_ramp(r);
        }
    }

    let acq = &mut proto.acquisition;
    if let Some(v) = eq.hp_hz {
        acq.filter.hp_hz = v;
    }
    if let Some(v) = eq.lp_hz {
        acq.filter.lp_hz = v;
    }
    if let Some(v) = eq.notch_hz {
        acq.filter.notch_hz = if v > 0.0 { Some(v) } else { None };
    }
    if let Some(v) = eq.order {
        acq.filter.order = v.clamp(1, 8);
    }
    if let Some(v) = eq.pre_ms {
        acq.window.pre_ms = v;
    }
    if let Some(v) = eq.post_ms {
        acq.window.post_ms = v;
    }
    if let Some(v) = eq.artifact_reject_uv {
        acq.artifact_reject_uv = v;
    }
    if let Some(v) = eq.impedance_kohm {
        acq.impedance_kohm = v.max(0.0);
    }
}

// --- Comandos ---

/// Captura un registro segun la modalidad. Despacha al sub-motor correcto.
#[tauri::command]
fn capture(params: SimParams) -> SimOutput {
    let ear = parse_ear(&params.ear);
    let subject = build_subject(&params.subject, ear);
    let protocol = build_protocol(&params, ear);

    match params.modality.as_str() {
        "P300" | "Mmn" => {
            SimOutput::Oddball(EvokedPotentialEngine::simulate_oddball(&protocol, &subject))
        }
        "Assr" => SimOutput::Assr(EvokedPotentialEngine::simulate_assr(&protocol, &subject)),
        _ => SimOutput::Transient(EvokedPotentialEngine::simulate(&protocol, &subject)),
    }
}

/// Audiograma estimado por frecuencia. `method`: "toneburst" | "nbchirp" | "assr".
#[tauri::command]
fn audiogram(
    ear: String,
    method: String,
    subject: SubjectParams,
    freqs: Vec<f64>,
    mod_freq_hz: Option<f64>,
) -> Vec<(f64, Option<f64>)> {
    let e = parse_ear(&ear);
    let subj = build_subject(&subject, e);
    let freqs = if freqs.is_empty() {
        vec![500.0, 1000.0, 2000.0, 4000.0]
    } else {
        freqs
    };
    match method.as_str() {
        "nbchirp" => estimate_audiogram_chirp(e, &subj, &freqs),
        "assr" => assr_audiogram(e, &subj, &freqs, mod_freq_hz.unwrap_or(80.0)),
        _ => estimate_audiogram(e, &subj, &freqs),
    }
}


/// Lista los casos clinicos del catalogo embebido.
#[tauri::command]
fn list_cases() -> Vec<CaseInfo> {
    let catalog = CaseCatalog::embedded();
    catalog
        .cases()
        .iter()
        .map(|c| CaseInfo {
            id: c.id.clone(),
            name: c.name.clone(),
            description: c.description.clone(),
            modality: c.modality.clone(),
            ear: c.ear().label().to_string(),
        })
        .collect()
}

/// Ejecuta un caso del catalogo (sujeto + protocolo predefinidos).
#[tauri::command]
fn run_case(id: String) -> Result<SimOutput, String> {
    let catalog = CaseCatalog::embedded();
    let case = catalog
        .get(&id)
        .ok_or_else(|| format!("caso desconocido: {id}"))?;
    let subject = case.subject();
    let protocol = case.protocol();

    let out = match protocol.modality {
        aep_core::Modality::P300 | aep_core::Modality::Mmn => {
            SimOutput::Oddball(EvokedPotentialEngine::simulate_oddball(&protocol, &subject))
        }
        aep_core::Modality::Assr => {
            SimOutput::Assr(EvokedPotentialEngine::simulate_assr(&protocol, &subject))
        }
        _ => SimOutput::Transient(EvokedPotentialEngine::simulate(&protocol, &subject)),
    };
    Ok(out)
}

/// Punto de entrada de la app Tauri.
pub fn run() {
    tauri::Builder::default()
        .manage(clinical::new_state())
        .invoke_handler(tauri::generate_handler![
            // Reutilizables (motor): catálogo + capturas/audiograma por modalidad
            capture,
            audiogram,
            list_cases,
            run_case,
            // Clínico (G0: invariante verdad/ciego)
            clinical::cargar_caso,
            clinical::capturar_clinico,
            clinical::iniciar_captura_clinica,
            clinical::detener_captura,
            clinical::docente_desbloquear,
            clinical::docente_relock,
            clinical::ver_verdad,
            clinical::estado_sesion,
        ])
        .run(tauri::generate_context!())
        .expect("error al arrancar la app Tauri de simPEATC");
}
