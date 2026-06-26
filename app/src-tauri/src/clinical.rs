//! G0 — Sesión clínica e **invariante verdad/ciego**.
//!
//! La VERDAD del caso (paciente real, lesiones, clave de respuesta) vive en
//! `tauri::State` y **nunca se serializa hacia el alumno**. El alumno solo recibe
//! lo que el equipo *mediría* (`Recording`), y en Evaluación/OSCE sin la clave de
//! ondas detectadas (debe marcarlas él). El docente, tras desbloquear, sí ve la
//! verdad. Esta separación es el núcleo pedagógico y de integridad del simulador.

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use aep_core::{
    CaptureSession, CaseCatalog, EvokedPotentialEngine, Recording, Sex, Subject, WavePeak,
};
use serde::{Deserialize, Serialize};

use crate::{build_protocol, parse_ear, SimParams};

/// PIN del rol docente. Placeholder de G0: en una capa posterior se reemplaza por
/// un hash configurable (GUI.md §4.3).
const PIN_DOCENTE: &str = "1234";

/// Modo de funcionamiento fijado por el docente.
#[derive(Clone, Copy, PartialEq, Eq, Default, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Modo {
    /// Verdad visible, feedback inmediato, sugerencias activas.
    #[default]
    Practica,
    /// Caso anonimizado, verdad oculta, sin sugerencias.
    Evaluacion,
    /// Estaciones cronometradas, sin feedback.
    Osce,
}

impl Modo {
    /// `true` si en este modo el alumno puede ver la verdad/sugerencias.
    fn revela_verdad(self) -> bool {
        matches!(self, Modo::Practica)
    }
}

/// La VERDAD del caso. Reside en el backend; **NUNCA** se serializa al alumno.
/// No deriva `Serialize` a propósito.
pub struct TruthSheet {
    pub caso_id: String,
    pub nombre: String,
    pub descripcion: String,
    /// El paciente real, con sus lesiones (oculto).
    pub subject: Subject,
    /// Clave de respuesta: picos "verdaderos" medidos sobre el caso.
    pub verdad_picos: Vec<WavePeak>,
}

/// Estado autoritativo de la sesión (no cruza el IPC).
#[derive(Default)]
pub struct SesionInterna {
    pub modo: Modo,
    pub truth: Option<TruthSheet>,
    pub rol_docente: bool,
    /// Bandera de cancelación de la captura en curso (Stop).
    pub cancel: Arc<AtomicBool>,
}

/// Estado gestionado por Tauri.
pub type AppState = Mutex<SesionInterna>;

/// Crea el estado inicial para `Builder::manage`.
pub fn new_state() -> AppState {
    Mutex::new(SesionInterna::default())
}

// --- DTOs hacia el frontend ---

/// Vista **ciega** de un caso para el alumno. Sin lesiones ni diagnóstico; el
/// nombre/descripción solo se incluyen en modo Práctica.
#[derive(Serialize)]
pub struct VistaCiegaCaso {
    pub id: String,
    pub ear: String,
    pub age_years: f64,
    pub sex: String,
    pub modo: Modo,
    pub nombre: Option<String>,
    pub descripcion: Option<String>,
}

/// Verdad completa: solo se entrega al rol docente desbloqueado.
#[derive(Serialize)]
pub struct VerdadDto {
    pub caso_id: String,
    pub nombre: String,
    pub descripcion: String,
    pub lesiones: Vec<String>,
    pub verdad_picos: Vec<WavePeak>,
}

/// Estado de sesión visible (no sensible) para que el frontend sepa modo/rol.
#[derive(Serialize)]
pub struct EstadoSesion {
    pub modo: Modo,
    pub rol_docente: bool,
    pub caso_cargado: bool,
}

// --- Proyección ciega ---

/// Proyecta un `Recording` según el modo y el rol: en Evaluación/OSCE quita la
/// **clave de respuesta** (ondas detectadas); el alumno debe marcarlas él. En
/// Práctica (o rol docente) pasa íntegro.
pub fn proyecta_recording(rec: Recording, modo: Modo, docente: bool) -> Recording {
    if docente || modo.revela_verdad() {
        rec
    } else {
        Recording {
            detected: Vec::new(),
            ..rec
        }
    }
}

fn sex_label(sex: Sex) -> &'static str {
    match sex {
        Sex::Male => "Masculino",
        Sex::Female => "Femenino",
    }
}

// --- Comandos ---

/// Carga un caso del catálogo: precomputa y guarda la `TruthSheet` en el estado
/// y devuelve **solo la vista ciega**. Al cargar, relock del rol docente.
#[tauri::command]
pub fn cargar_caso(
    id: String,
    modo: Modo,
    state: tauri::State<'_, AppState>,
) -> Result<VistaCiegaCaso, String> {
    let catalog = CaseCatalog::embedded();
    let case = catalog
        .get(&id)
        .ok_or_else(|| format!("caso desconocido: {id}"))?;

    let subject = case.subject();
    let protocol = case.protocol();
    let rec = EvokedPotentialEngine::simulate(&protocol, &subject);

    let ear = case.ear();
    let age_years = subject.age.approx_years();
    let sex = sex_label(subject.sex).to_string();

    let truth = TruthSheet {
        caso_id: id.clone(),
        nombre: case.name.clone(),
        descripcion: case.description.clone(),
        subject,
        verdad_picos: rec.detected,
    };

    let revela = modo.revela_verdad();
    let nombre = revela.then(|| case.name.clone());
    let descripcion = revela.then(|| case.description.clone());

    {
        let mut s = state.lock().unwrap();
        s.modo = modo;
        s.rol_docente = false; // relock al cambiar de caso
        s.truth = Some(truth);
    }

    Ok(VistaCiegaCaso {
        id,
        ear: ear.label().to_string(),
        age_years,
        sex,
        modo,
        nombre,
        descripcion,
    })
}

/// Captura clínica: el alumno aporta la **config del equipo** (`params`); el
/// **paciente** sale de la verdad oculta (se ignora `params.subject`). El
/// resultado se proyecta ciego según el modo.
#[tauri::command]
pub fn capturar_clinico(
    params: SimParams,
    state: tauri::State<'_, AppState>,
) -> Result<Recording, String> {
    // No sostener el lock durante la simulación (CPU-bound): copiar y soltar.
    let (subject, modo, docente) = {
        let s = state.lock().unwrap();
        let truth = s.truth.as_ref().ok_or("no hay caso cargado")?;
        (truth.subject.clone(), s.modo, s.rol_docente)
    };

    let ear = parse_ear(&params.ear);
    let protocol = build_protocol(&params, ear);
    let rec = EvokedPotentialEngine::simulate(&protocol, &subject);
    Ok(proyecta_recording(rec, modo, docente))
}

// --- G3: captura progresiva (CaptureSession por Channel) ---

/// Mensaje de captura en vivo: promedio acumulado + última época cruda.
#[derive(Clone, Serialize)]
#[serde(
    tag = "event",
    content = "data",
    rename_all = "camelCase",
    rename_all_fields = "camelCase"
)]
pub enum CapMsg {
    /// Inicio: objetivo de sweeps y eje temporal (una sola vez).
    Iniciada { objetivo: u32, times_ms: Vec<f64> },
    /// Refresco: promedio combinado, réplica B y época cruda (decimados).
    Refresco {
        aceptados: u32,
        rechazados: u32,
        fsp: f64,
        /// Promedio combinado (A+B)/2.
        promedio: Vec<f64>,
        /// Réplica B (segundo buffer entrelazado), para juzgar reproducibilidad.
        replica: Vec<f64>,
        epoca: Vec<f64>,
    },
    /// Fin (objetivo alcanzado o detenido).
    Finalizada { aceptados: u32, rechazados: u32 },
}

/// Índices para decimar `n` muestras a como mucho `max` puntos.
fn decim_indices(n: usize, max: usize) -> Vec<usize> {
    if n <= max {
        return (0..n).collect();
    }
    let step = n as f64 / max as f64;
    (0..max).map(|i| ((i as f64) * step) as usize).collect()
}

fn pick(values: &[f64], idx: &[usize]) -> Vec<f64> {
    idx.iter().map(|&i| values.get(i).copied().unwrap_or(0.0)).collect()
}

/// Inicia una captura progresiva: un hilo avanza la `CaptureSession` y emite el
/// promedio acumulado + la época cruda por `channel`. El paciente sale de la
/// verdad oculta; el nº de refrescos se adapta a las promediaciones del examen.
#[tauri::command]
pub fn iniciar_captura_clinica(
    params: SimParams,
    channel: tauri::ipc::Channel<CapMsg>,
    salt: u64,
    state: tauri::State<'_, AppState>,
) -> Result<(), String> {
    let (subject, cancel) = {
        let mut s = state.lock().unwrap();
        let subject = s.truth.as_ref().ok_or("no hay caso cargado")?.subject.clone();
        let cancel = Arc::new(AtomicBool::new(false));
        s.cancel = cancel.clone();
        (subject, cancel)
    };

    let ear = parse_ear(&params.ear);
    let protocol = build_protocol(&params, ear);
    let target = protocol.acquisition.sweeps.max(2);
    let half = (target / 2).max(1);
    // Dos buffers entrelazados con ruido independiente (réplicas A/B). `salt`
    // varía el ruido entre capturas (la señal/ondas no cambian); fijarlo
    // reproduce la toma (para evaluación/OSCE).
    let mut a = CaptureSession::new_with_salt(&protocol, &subject, salt ^ 0xA17F)
        .ok_or("modalidad no soportada para captura progresiva")?;
    let mut b = CaptureSession::new_with_salt(&protocol, &subject, salt ^ 0xB23D)
        .ok_or("modalidad no soportada para captura progresiva")?;

    thread::spawn(move || {
        const MAX_PTS: usize = 600;
        let idx = decim_indices(a.times().len(), MAX_PTS);
        let objetivo = half * 2;
        let _ = channel.send(CapMsg::Iniciada {
            objetivo,
            times_ms: pick(a.times(), &idx),
        });

        let refresh_every = (objetivo / 120).max(1);
        let max_attempts = target.saturating_mul(3).max(target + 200);
        let mut attempts = 0u32;
        let mut last_emit = 0u32;
        while (a.accepted() < half || b.accepted() < half)
            && attempts < max_attempts
            && !cancel.load(Ordering::Relaxed)
        {
            if a.accepted() < half {
                a.step();
                attempts += 1;
            }
            if b.accepted() < half {
                b.step();
                attempts += 1;
            }
            let acc = a.accepted() + b.accepted();
            let done = a.accepted() >= half && b.accepted() >= half;
            if acc.saturating_sub(last_emit) >= refresh_every || done {
                last_emit = acc;
                let ma = a.mean();
                let mb = b.mean();
                let comb: Vec<f64> = ma.iter().zip(mb.iter()).map(|(x, y)| (x + y) * 0.5).collect();
                let _ = channel.send(CapMsg::Refresco {
                    aceptados: acc,
                    rechazados: a.rejected() + b.rejected(),
                    fsp: (a.fsp() + b.fsp()) * 0.5,
                    promedio: pick(&comb, &idx),
                    replica: pick(&mb, &idx),
                    epoca: pick(a.last_epoch(), &idx),
                });
                thread::sleep(Duration::from_millis(28));
            }
        }
        let _ = channel.send(CapMsg::Finalizada {
            aceptados: a.accepted() + b.accepted(),
            rechazados: a.rejected() + b.rejected(),
        });
    });
    Ok(())
}

/// Detiene la captura en curso (Stop).
#[tauri::command]
pub fn detener_captura(state: tauri::State<'_, AppState>) {
    state.lock().unwrap().cancel.store(true, Ordering::Relaxed);
}

/// Desbloquea el rol docente verificando el PIN. Devuelve si quedó desbloqueado.
#[tauri::command]
pub fn docente_desbloquear(pin: String, state: tauri::State<'_, AppState>) -> bool {
    let mut s = state.lock().unwrap();
    s.rol_docente = pin == PIN_DOCENTE;
    s.rol_docente
}

/// Vuelve a bloquear el rol docente (handoff al alumno).
#[tauri::command]
pub fn docente_relock(state: tauri::State<'_, AppState>) {
    state.lock().unwrap().rol_docente = false;
}

/// Devuelve la verdad del caso **solo** si el rol docente está desbloqueado.
#[tauri::command]
pub fn ver_verdad(state: tauri::State<'_, AppState>) -> Result<VerdadDto, String> {
    let s = state.lock().unwrap();
    if !s.rol_docente {
        return Err("rol docente bloqueado".into());
    }
    let t = s.truth.as_ref().ok_or("no hay caso cargado")?;
    let lesiones = t
        .subject
        .lesions
        .iter()
        .map(|l| {
            format!(
                "{:?} {} · {:.0} dB · {:?}",
                l.site,
                l.ear.label(),
                l.severity_db,
                l.freq_profile
            )
        })
        .collect();
    Ok(VerdadDto {
        caso_id: t.caso_id.clone(),
        nombre: t.nombre.clone(),
        descripcion: t.descripcion.clone(),
        lesiones,
        verdad_picos: t.verdad_picos.clone(),
    })
}

/// Estado de sesión (no sensible) para la UI.
#[tauri::command]
pub fn estado_sesion(state: tauri::State<'_, AppState>) -> EstadoSesion {
    let s = state.lock().unwrap();
    EstadoSesion {
        modo: s.modo,
        rol_docente: s.rol_docente,
        caso_cargado: s.truth.is_some(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn rec_con_clave() -> Recording {
        Recording {
            channels: Vec::new(),
            detected: vec![WavePeak {
                label: "SECRETO".into(),
                latency_ms: 5.6,
                amplitude_uv: 0.3,
            }],
            fsp: 7.0,
            accepted_sweeps: 2000,
            rejected_sweeps: 10,
        }
    }

    #[test]
    fn evaluacion_quita_la_clave() {
        let p = proyecta_recording(rec_con_clave(), Modo::Evaluacion, false);
        assert!(p.detected.is_empty(), "Eval no debe revelar las ondas");
        // El canal/FSP del equipo sí se conservan.
        assert_eq!(p.fsp, 7.0);
    }

    #[test]
    fn osce_quita_la_clave() {
        let p = proyecta_recording(rec_con_clave(), Modo::Osce, false);
        assert!(p.detected.is_empty());
    }

    #[test]
    fn practica_conserva_la_clave() {
        let p = proyecta_recording(rec_con_clave(), Modo::Practica, false);
        assert_eq!(p.detected.len(), 1);
    }

    #[test]
    fn docente_ve_la_clave_aun_en_evaluacion() {
        let p = proyecta_recording(rec_con_clave(), Modo::Evaluacion, true);
        assert_eq!(p.detected.len(), 1);
    }

    /// Invariante de lista blanca: el JSON que se enviaría al alumno en
    /// Evaluación NO contiene la clave de respuesta.
    #[test]
    fn el_json_al_alumno_no_filtra_la_clave() {
        let p = proyecta_recording(rec_con_clave(), Modo::Evaluacion, false);
        let json = serde_json::to_string(&p).unwrap();
        assert!(
            !json.contains("SECRETO"),
            "fuga de la clave de respuesta en el payload del alumno: {json}"
        );
    }

    #[test]
    fn vista_ciega_en_evaluacion_oculta_nombre_y_descripcion() {
        // Simula la lógica de cargar_caso para modo Evaluación.
        let revela = Modo::Evaluacion.revela_verdad();
        assert!(!revela);
        let nombre: Option<String> = revela.then(|| "Schwannoma vestibular".to_string());
        assert!(nombre.is_none(), "el nombre puede revelar el diagnóstico");
    }
}
