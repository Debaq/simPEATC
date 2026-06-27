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
    AssrResult, CaptureSession, CaseCatalog, CaseDef, Ear, EvokedPotentialEngine, Lesion,
    LesionSite, OddballRecording, Recording, Subject,
};
use serde::{Deserialize, Serialize};

use crate::{build_protocol, build_subject, parse_ear, SimOutput, SimParams, SubjectParams};

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

/// La VERDAD de un oído: la **patología** (lesiones ya mapeadas a ese oído). Reside
/// en el backend; **NUNCA** se serializa al alumno. No deriva `Serialize`. El
/// sujeto (edad, estado…) son variables externas de la sesión que se combinan con
/// estas lesiones al capturar; la clave de respuesta depende del examen.
pub struct TruthSheet {
    pub caso_id: String,
    pub nombre: String,
    pub descripcion: String,
    /// Lesiones de la patología en este oído (oculto).
    pub lesions: Vec<Lesion>,
}

/// Estado autoritativo de la sesión (no cruza el IPC).
///
/// La verdad es **por oído**: cada slot (OD/OI) puede tener su propio caso, lo que
/// permite montar un paciente binaural con patologías asimétricas. La captura de
/// un oído usa la verdad de ese oído.
#[derive(Default)]
pub struct SesionInterna {
    pub modo: Modo,
    pub truth_right: Option<TruthSheet>,
    pub truth_left: Option<TruthSheet>,
    pub rol_docente: bool,
    /// Bandera de cancelación de la captura en curso (Stop).
    pub cancel: Arc<AtomicBool>,
}

impl SesionInterna {
    fn truth_for(&self, ear: Ear) -> Option<&TruthSheet> {
        match ear {
            Ear::Right => self.truth_right.as_ref(),
            Ear::Left => self.truth_left.as_ref(),
        }
    }
    fn set_truth(&mut self, ear: Ear, t: TruthSheet) {
        match ear {
            Ear::Right => self.truth_right = Some(t),
            Ear::Left => self.truth_left = Some(t),
        }
    }
    fn clear_truth(&mut self, ear: Ear) {
        match ear {
            Ear::Right => self.truth_right = None,
            Ear::Left => self.truth_left = None,
        }
    }
}

/// Estado gestionado por Tauri.
pub type AppState = Mutex<SesionInterna>;

/// Crea el estado inicial para `Builder::manage`.
pub fn new_state() -> AppState {
    Mutex::new(SesionInterna::default())
}

// --- DTOs hacia el frontend ---

/// Vista **ciega** de la patología cargada en un oído. Sin lesiones ni diagnóstico;
/// el nombre/descripción solo se incluyen en modo Práctica. Las variables del
/// sujeto (edad, sexo…) son de la sesión, no de aquí.
#[derive(Serialize)]
pub struct VistaCiegaCaso {
    pub id: String,
    pub ear: String,
    pub modo: Modo,
    pub nombre: Option<String>,
    pub descripcion: Option<String>,
}

/// Verdad de un oído: solo se entrega al rol docente desbloqueado. Describe la
/// fisiología (qué patología tiene el paciente); el detalle onda-a-onda lo da la
/// vista previa del editor según el examen.
#[derive(Serialize)]
pub struct VerdadDto {
    pub ear: String,
    pub caso_id: String,
    pub nombre: String,
    pub descripcion: String,
    pub lesiones: Vec<String>,
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

/// Arma el sujeto de una captura: variables externas de la sesión (`params.subject`)
/// + las lesiones de la patología del slot (`lesions`). Si el oído no tiene
/// patología, `lesions` va vacío → oído normal con las variables de la sesión.
fn subject_para_captura(params: &SimParams, ear: Ear, lesions: Vec<Lesion>) -> Subject {
    let mut s = build_subject(&params.subject, ear);
    s.lesions = lesions; // la patología manda; se ignora params.subject.lesion
    s
}

// --- Comandos ---

/// Guarda la **patología** del `def` en el slot `ear` y devuelve la **vista ciega**.
/// Las lesiones se aplican al oído del slot. Preserva el rol docente vigente (el
/// docente construye y ve la verdad en su modal; el relock/entrega es explícito).
fn cargar_def(
    def: &CaseDef,
    ear: Ear,
    modo: Modo,
    state: &tauri::State<'_, AppState>,
) -> Result<VistaCiegaCaso, String> {
    let truth = TruthSheet {
        caso_id: def.id.clone(),
        nombre: def.name.clone(),
        descripcion: def.description.clone(),
        lesions: def.lesions(ear),
    };

    let revela = modo.revela_verdad();
    let nombre = revela.then(|| def.name.clone());
    let descripcion = revela.then(|| def.description.clone());

    {
        let mut s = state.lock().unwrap();
        s.modo = modo;
        s.set_truth(ear, truth);
    }

    Ok(VistaCiegaCaso {
        id: def.id.clone(),
        ear: ear.label().to_string(),
        modo,
        nombre,
        descripcion,
    })
}

/// Carga un paciente del catálogo en el slot `ear` (oído del slot).
#[tauri::command]
pub fn cargar_caso(
    id: String,
    ear: String,
    modo: Modo,
    state: tauri::State<'_, AppState>,
) -> Result<VistaCiegaCaso, String> {
    let catalog = CaseCatalog::embedded();
    let case = catalog
        .get(&id)
        .ok_or_else(|| format!("caso desconocido: {id}"))?;
    cargar_def(case, parse_ear(&ear), modo, &state)
}

/// Carga un paciente **construido o importado** en el slot `ear`.
#[tauri::command]
pub fn cargar_caso_def(
    def: CaseDef,
    ear: String,
    modo: Modo,
    state: tauri::State<'_, AppState>,
) -> Result<VistaCiegaCaso, String> {
    if def.id.trim().is_empty() {
        return Err("el caso necesita un id".into());
    }
    cargar_def(&def, parse_ear(&ear), modo, &state)
}

/// Devuelve la **definición completa** de un caso del catálogo (con lesiones y
/// verdad) para cargarla en el editor. Solo con el rol docente desbloqueado,
/// porque revela el diagnóstico.
#[tauri::command]
pub fn obtener_caso_def(
    id: String,
    state: tauri::State<'_, AppState>,
) -> Result<CaseDef, String> {
    if !state.lock().unwrap().rol_docente {
        return Err("rol docente bloqueado".into());
    }
    let catalog = CaseCatalog::embedded();
    catalog
        .get(&id)
        .cloned()
        .ok_or_else(|| format!("caso desconocido: {id}"))
}

/// Vista previa del editor: simula un examen sobre el **paciente del `def`** en el
/// oído `ear`, sin tocar la sesión. Devuelve la respuesta esperada (ondas y
/// latencias) para que el creador vea reflejado qué sale a esa intensidad. Solo
/// con rol docente (revela la verdad).
#[tauri::command]
pub fn preview_caso(
    def: CaseDef,
    ear: String,
    params: SimParams,
    state: tauri::State<'_, AppState>,
) -> Result<SimOutput, String> {
    if !state.lock().unwrap().rol_docente {
        return Err("rol docente bloqueado".into());
    }
    let e = parse_ear(&ear);
    let subject = subject_para_captura(&params, e, def.lesions(e));
    let protocol = build_protocol(&params, e);
    let out = match params.modality.as_str() {
        "P300" | "Mmn" => {
            SimOutput::Oddball(EvokedPotentialEngine::simulate_oddball(&protocol, &subject))
        }
        "Assr" => SimOutput::Assr(EvokedPotentialEngine::simulate_assr(&protocol, &subject)),
        _ => SimOutput::Transient(EvokedPotentialEngine::simulate(&protocol, &subject)),
    };
    Ok(out)
}

/// Captura clínica: el alumno aporta la **config del equipo** (`params`); el
/// **paciente** sale de la verdad oculta (se ignora `params.subject`). El
/// resultado se proyecta ciego según el modo.
#[tauri::command]
pub fn capturar_clinico(
    params: SimParams,
    state: tauri::State<'_, AppState>,
) -> Result<Recording, String> {
    let ear = parse_ear(&params.ear);
    // No sostener el lock durante la simulación (CPU-bound): copiar y soltar.
    let (lesions, modo, docente) = {
        let s = state.lock().unwrap();
        // Slot vacío → sin lesiones (oído normal con las variables de la sesión).
        let lesions = s.truth_for(ear).map(|t| t.lesions.clone()).unwrap_or_default();
        (lesions, s.modo, s.rol_docente)
    };

    let subject = subject_para_captura(&params, ear, lesions);
    let protocol = build_protocol(&params, ear);
    let rec = EvokedPotentialEngine::simulate(&protocol, &subject);
    Ok(proyecta_recording(rec, modo, docente))
}

/// Toma las lesiones del slot + modo/rol del estado (helper de captura one-shot).
fn lesiones_y_modo(ear: Ear, state: &tauri::State<'_, AppState>) -> (Vec<Lesion>, Modo, bool) {
    let s = state.lock().unwrap();
    let lesions = s.truth_for(ear).map(|t| t.lesions.clone()).unwrap_or_default();
    (lesions, s.modo, s.rol_docente)
}

/// Captura clínica **oddball** (P300/MMN), one-shot. Proyecta ciego: en
/// Evaluación/OSCE quita la clave (P3b/MMN detectadas); las trazas se conservan.
#[tauri::command]
pub fn capturar_oddball_clinico(
    params: SimParams,
    state: tauri::State<'_, AppState>,
) -> Result<OddballRecording, String> {
    let ear = parse_ear(&params.ear);
    let (lesions, modo, docente) = lesiones_y_modo(ear, &state);
    let subject = subject_para_captura(&params, ear, lesions);
    let protocol = build_protocol(&params, ear);
    let rec = EvokedPotentialEngine::simulate_oddball(&protocol, &subject);
    if docente || modo.revela_verdad() {
        Ok(rec)
    } else {
        Ok(OddballRecording {
            detected: Vec::new(),
            ..rec
        })
    }
}

/// Captura clínica **ASSR** (estado estable), one-shot. La detección es la
/// medición objetiva (no una clave que marcar): se entrega íntegra en todos los modos.
#[tauri::command]
pub fn capturar_assr_clinico(
    params: SimParams,
    state: tauri::State<'_, AppState>,
) -> Result<AssrResult, String> {
    let ear = parse_ear(&params.ear);
    let (lesions, _modo, _docente) = lesiones_y_modo(ear, &state);
    let subject = subject_para_captura(&params, ear, lesions);
    let protocol = build_protocol(&params, ear);
    Ok(EvokedPotentialEngine::simulate_assr(&protocol, &subject))
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
    let ear = parse_ear(&params.ear);
    let (lesions, cancel) = {
        let mut s = state.lock().unwrap();
        // Slot vacío → sin lesiones (oído normal con las variables de la sesión).
        let lesions = s.truth_for(ear).map(|t| t.lesions.clone()).unwrap_or_default();
        let cancel = Arc::new(AtomicBool::new(false));
        s.cancel = cancel.clone();
        (lesions, cancel)
    };

    let subject = subject_para_captura(&params, ear, lesions);
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

/// Quita el caso de un oído (vacía ese slot).
#[tauri::command]
pub fn quitar_caso(ear: String, state: tauri::State<'_, AppState>) {
    state.lock().unwrap().clear_truth(parse_ear(&ear));
}

/// Construye el DTO de verdad de un oído.
fn verdad_dto(ear: Ear, t: &TruthSheet) -> VerdadDto {
    let lesiones = t
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
    VerdadDto {
        ear: ear.label().to_string(),
        caso_id: t.caso_id.clone(),
        nombre: t.nombre.clone(),
        descripcion: t.descripcion.clone(),
        lesiones,
    }
}

/// Devuelve la verdad de cada oído cargado **solo** si el rol docente está
/// desbloqueado (lista vacía si no hay casos).
#[tauri::command]
pub fn ver_verdad(state: tauri::State<'_, AppState>) -> Result<Vec<VerdadDto>, String> {
    let s = state.lock().unwrap();
    if !s.rol_docente {
        return Err("rol docente bloqueado".into());
    }
    let mut out = Vec::new();
    if let Some(t) = &s.truth_right {
        out.push(verdad_dto(Ear::Right, t));
    }
    if let Some(t) = &s.truth_left {
        out.push(verdad_dto(Ear::Left, t));
    }
    Ok(out)
}

/// Estado de sesión (no sensible) para la UI.
#[tauri::command]
pub fn estado_sesion(state: tauri::State<'_, AppState>) -> EstadoSesion {
    let s = state.lock().unwrap();
    EstadoSesion {
        modo: s.modo,
        rol_docente: s.rol_docente,
        caso_cargado: s.truth_right.is_some() || s.truth_left.is_some(),
    }
}

// --- G9: evaluación / scoring ---

/// Nombre canónico del sitio de lesión (igual que el `parse_site` del frontend).
fn site_str(s: LesionSite) -> &'static str {
    match s {
        LesionSite::Conductive => "Conductive",
        LesionSite::Cochlear => "Cochlear",
        LesionSite::Retrocochlear => "Retrocochlear",
        LesionSite::Neural => "Neural",
        LesionSite::Central => "Central",
        LesionSite::CentralConduction => "CentralConduction",
        LesionSite::Brainstem => "Brainstem",
        LesionSite::Cortical => "Cortical",
        LesionSite::Cognitive => "Cognitive",
    }
}

/// Diagnóstico del alumno para un oído: sitios de lesión elegidos (vacío = normal).
#[derive(Deserialize)]
pub struct DiagEar {
    pub ear: String,
    pub sitios: Vec<String>,
}

/// Una marca del alumno (onda etiquetada) con el contexto de su captura.
#[derive(Deserialize)]
pub struct MarcaDto {
    pub ear: String,
    pub modality: String,
    pub intensity_db: f64,
    pub label: String,
    pub t_ms: f64,
}

/// Entrega del alumno a evaluar.
#[derive(Deserialize)]
pub struct EntregaDto {
    /// Variables de sesión usadas (para recomputar la clave del marcado).
    pub sujeto: SubjectParams,
    pub diagnosticos: Vec<DiagEar>,
    pub marcas: Vec<MarcaDto>,
}

/// Resultado del diagnóstico de un oído.
#[derive(Serialize)]
pub struct DxResultado {
    pub ear: String,
    pub esperado: Vec<String>,
    pub respondido: Vec<String>,
    pub correcto: bool,
    pub parcial: bool,
}

/// Resumen del marcado de ondas.
#[derive(Serialize, Default)]
pub struct MarcasResumen {
    pub correctas: u32,
    pub incorrectas: u32,
    pub perdidas: u32,
}

/// Calificación completa devuelta al entregar.
#[derive(Serialize)]
pub struct Calificacion {
    pub puntaje: f64,
    pub dx_pct: f64,
    pub marcas_pct: f64,
    pub por_oido: Vec<DxResultado>,
    pub marcas: MarcasResumen,
    pub verdad: Vec<VerdadDto>,
}

/// Tolerancia de latencia (ms) para considerar una marca "correcta".
const TOL_MARCA_MS: f64 = 0.6;

fn ear_label(ear: Ear) -> &'static str {
    ear.label()
}

/// Califica la entrega del alumno contra la verdad oculta y la revela. Diagnóstico
/// por oído (sitios de lesión) + precisión del marcado de ondas. Puntaje 0-100.
#[tauri::command]
pub fn calificar(
    entrega: EntregaDto,
    state: tauri::State<'_, AppState>,
) -> Result<Calificacion, String> {
    // Copiar la verdad y soltar el lock antes de simular.
    let (truth_right, truth_left) = {
        let s = state.lock().unwrap();
        (
            s.truth_right.as_ref().map(|t| (t.lesions.clone(), t.nombre.clone(), t.descripcion.clone(), t.caso_id.clone())),
            s.truth_left.as_ref().map(|t| (t.lesions.clone(), t.nombre.clone(), t.descripcion.clone(), t.caso_id.clone())),
        )
    };

    // --- Diagnóstico por oído ---
    let mut por_oido = Vec::new();
    let mut dx_sum = 0.0;
    let mut dx_n = 0.0;
    for ear in [Ear::Right, Ear::Left] {
        let truth = match ear {
            Ear::Right => &truth_right,
            Ear::Left => &truth_left,
        };
        let Some((lesions, _, _, _)) = truth else { continue };
        dx_n += 1.0;
        let mut esperado: Vec<String> = lesions.iter().map(|l| site_str(l.site).to_string()).collect();
        esperado.sort();
        esperado.dedup();
        let resp = entrega
            .diagnosticos
            .iter()
            .find(|d| parse_ear(&d.ear) == ear)
            .map(|d| {
                let mut v = d.sitios.clone();
                v.sort();
                v.dedup();
                v
            })
            .unwrap_or_default();
        // Jaccard entre esperado y respondido (normal = ambos vacíos = 1.0).
        let inter = esperado.iter().filter(|s| resp.contains(s)).count() as f64;
        let union = {
            let mut u = esperado.clone();
            for r in &resp {
                if !u.contains(r) {
                    u.push(r.clone());
                }
            }
            u.len() as f64
        };
        let score = if union == 0.0 { 1.0 } else { inter / union };
        dx_sum += score;
        por_oido.push(DxResultado {
            ear: ear_label(ear).to_string(),
            esperado,
            respondido: resp,
            correcto: score >= 0.999,
            parcial: score > 0.0 && score < 0.999,
        });
    }
    let dx_pct = if dx_n > 0.0 { dx_sum / dx_n * 100.0 } else { 100.0 };

    // --- Marcado: recomputa la clave del motor por (oído, examen, intensidad) ---
    let mut resumen = MarcasResumen::default();
    let mut grupos: std::collections::HashMap<(String, String, i64), Vec<&MarcaDto>> =
        std::collections::HashMap::new();
    for m in &entrega.marcas {
        let key = (m.ear.clone(), m.modality.clone(), m.intensity_db.round() as i64);
        grupos.entry(key).or_default().push(m);
    }
    for ((ear_s, modality, intensity), marcas) in grupos {
        let ear = parse_ear(&ear_s);
        let lesions = match ear {
            Ear::Right => truth_right.as_ref(),
            Ear::Left => truth_left.as_ref(),
        }
        .map(|t| t.0.clone())
        .unwrap_or_default();

        let params = SimParams {
            modality: modality.clone(),
            ear: ear_s.clone(),
            stimulus: None,
            intensity_db: intensity as f64,
            sweeps: 2000,
            freq_hz: 2000.0,
            carrier_hz: 2000.0,
            mod_freq_hz: 80.0,
            equipo: None,
            subject: entrega.sujeto.clone(),
        };
        let subject = subject_para_captura(&params, ear, lesions);
        let protocol = build_protocol(&params, ear);
        let clave = EvokedPotentialEngine::simulate(&protocol, &subject).detected;

        let mut acertadas: std::collections::HashSet<&str> = std::collections::HashSet::new();
        for m in &marcas {
            match clave.iter().find(|p| p.label == m.label) {
                Some(p) if (p.latency_ms - m.t_ms).abs() <= TOL_MARCA_MS => {
                    resumen.correctas += 1;
                    acertadas.insert(p.label.as_str());
                }
                _ => resumen.incorrectas += 1,
            }
        }
        // Ondas reales no marcadas (o marcadas mal) = perdidas.
        for p in &clave {
            if !acertadas.contains(p.label.as_str()) {
                resumen.perdidas += 1;
            }
        }
    }
    let total_marcas = resumen.correctas + resumen.incorrectas + resumen.perdidas;
    let marcas_pct = if total_marcas == 0 {
        100.0
    } else {
        resumen.correctas as f64 / total_marcas as f64 * 100.0
    };

    // Puntaje: diagnóstico pesa más; el marcado solo si hubo marcas que evaluar.
    let puntaje = if total_marcas == 0 {
        dx_pct
    } else {
        dx_pct * 0.6 + marcas_pct * 0.4
    };

    // Revela la verdad (la evaluación terminó).
    let mut verdad = Vec::new();
    for (ear, truth) in [(Ear::Right, &truth_right), (Ear::Left, &truth_left)] {
        if let Some((lesions, nombre, descripcion, caso_id)) = truth {
            let lesiones = lesions
                .iter()
                .map(|l| format!("{:?} {} · {:.0} dB · {:?}", l.site, l.ear.label(), l.severity_db, l.freq_profile))
                .collect();
            verdad.push(VerdadDto {
                ear: ear.label().to_string(),
                caso_id: caso_id.clone(),
                nombre: nombre.clone(),
                descripcion: descripcion.clone(),
                lesiones,
            });
        }
    }

    Ok(Calificacion {
        puntaje,
        dx_pct,
        marcas_pct,
        por_oido,
        marcas: resumen,
        verdad,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use aep_core::WavePeak;

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
