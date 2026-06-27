// Envoltorios tipados sobre los comandos Tauri del backend.

import { Channel, invoke } from "@tauri-apps/api/core";
import type {
  AssrResult,
  AudiogramPoint,
  Calificacion,
  CapMsg,
  CaseDef,
  CaseInfo,
  EntregaDto,
  EstadoSesion,
  Modo,
  OddballRecording,
  OddCapMsg,
  Recording,
  SimOutput,
  SimParams,
  SubjectParams,
  VerdadDto,
  VistaCiegaCaso,
} from "./types";

/** Captura un registro segun la modalidad seleccionada. */
export function capture(params: SimParams): Promise<SimOutput> {
  return invoke<SimOutput>("capture", { params });
}

/** Audiograma estimado por frecuencia. */
export function audiogram(args: {
  ear: string;
  method: "toneburst" | "nbchirp" | "assr";
  subject: SubjectParams;
  freqs: number[];
  modFreqHz?: number;
}): Promise<AudiogramPoint[]> {
  return invoke<AudiogramPoint[]>("audiogram", {
    ear: args.ear,
    method: args.method,
    subject: args.subject,
    freqs: args.freqs,
    modFreqHz: args.modFreqHz ?? null,
  });
}

/** Lista los pacientes del catalogo embebido. */
export function listCases(): Promise<CaseInfo[]> {
  return invoke<CaseInfo[]>("list_cases");
}

// --- Clínico (G0: invariante verdad/ciego) ---

/** Carga un paciente del catálogo en el slot `ear`; devuelve la vista CIEGA. */
export function cargarCaso(id: string, ear: string, modo: Modo): Promise<VistaCiegaCaso> {
  return invoke<VistaCiegaCaso>("cargar_caso", { id, ear, modo });
}

/** Carga un paciente construido/importado en el slot `ear`. */
export function cargarCasoDef(def: CaseDef, ear: string, modo: Modo): Promise<VistaCiegaCaso> {
  return invoke<VistaCiegaCaso>("cargar_caso_def", { def, ear, modo });
}

/** Definición completa de un paciente del catálogo (para editar). Requiere rol docente. */
export function obtenerCasoDef(id: string): Promise<CaseDef> {
  return invoke<CaseDef>("obtener_caso_def", { id });
}

/** Vista previa: simula un examen sobre el paciente del `def` en `ear`. Requiere rol docente. */
export function previewCaso(def: CaseDef, ear: string, params: SimParams): Promise<SimOutput> {
  return invoke<SimOutput>("preview_caso", { def, ear, params });
}

/** Captura clínica (instantánea): el alumno aporta el equipo; el paciente sale de la verdad oculta. */
export function capturarClinico(params: SimParams): Promise<Recording> {
  return invoke<Recording>("capturar_clinico", { params });
}

/** Captura clínica oddball (P300/MMN), one-shot. Proyectada ciega según el modo. */
export function capturarOddballClinico(params: SimParams): Promise<OddballRecording> {
  return invoke<OddballRecording>("capturar_oddball_clinico", { params });
}

/** Captura oddball progresiva (P300/MMN): emite estándar/desviante/diferencia por el Channel. */
export function iniciarCapturaOddballClinica(
  params: SimParams,
  channel: Channel<OddCapMsg>,
  salt: number
): Promise<void> {
  return invoke<void>("iniciar_captura_oddball_clinica", { params, channel, salt });
}

/** Captura clínica ASSR (estado estable), one-shot. */
export function capturarAssrClinico(params: SimParams): Promise<AssrResult> {
  return invoke<AssrResult>("capturar_assr_clinico", { params });
}

/** Captura progresiva (G3): emite promedio acumulado + época cruda por el Channel.
 * `salt` varía el ruido entre capturas (mismo paciente, otra toma). */
export function iniciarCapturaClinica(
  params: SimParams,
  channel: Channel<CapMsg>,
  salt: number
): Promise<void> {
  return invoke<void>("iniciar_captura_clinica", { params, channel, salt });
}

/** Detiene la captura progresiva en curso. */
export function detenerCaptura(): Promise<void> {
  return invoke<void>("detener_captura");
}

/** Desbloquea el rol docente con PIN. */
export function docenteDesbloquear(pin: string): Promise<boolean> {
  return invoke<boolean>("docente_desbloquear", { pin });
}

/** Vuelve a bloquear el rol docente. */
export function docenteRelock(): Promise<void> {
  return invoke<void>("docente_relock");
}

/** Quita el caso de un oído (vacía ese slot). */
export function quitarCaso(ear: string): Promise<void> {
  return invoke<void>("quitar_caso", { ear });
}

/** Verdad por oído: solo si el rol docente está desbloqueado (si no, rechaza). */
export function verVerdad(): Promise<VerdadDto[]> {
  return invoke<VerdadDto[]>("ver_verdad");
}

/** Estado de sesión (modo, rol, caso cargado). */
export function estadoSesion(): Promise<EstadoSesion> {
  return invoke<EstadoSesion>("estado_sesion");
}

/** Califica la entrega del alumno (diagnóstico + marcado) y revela la verdad. */
export function calificar(entrega: EntregaDto): Promise<Calificacion> {
  return invoke<Calificacion>("calificar", { entrega });
}
