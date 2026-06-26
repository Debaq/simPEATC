// Envoltorios tipados sobre los comandos Tauri del backend.

import { Channel, invoke } from "@tauri-apps/api/core";
import type {
  AudiogramPoint,
  CapMsg,
  CaseInfo,
  EstadoSesion,
  Modo,
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

/** Lista los casos clinicos del catalogo embebido. */
export function listCases(): Promise<CaseInfo[]> {
  return invoke<CaseInfo[]>("list_cases");
}

/** Ejecuta un caso del catalogo por su id. */
export function runCase(id: string): Promise<SimOutput> {
  return invoke<SimOutput>("run_case", { id });
}

// --- Clínico (G0: invariante verdad/ciego) ---

/** Carga un caso en modo dado; devuelve la vista CIEGA (sin verdad). */
export function cargarCaso(id: string, modo: Modo): Promise<VistaCiegaCaso> {
  return invoke<VistaCiegaCaso>("cargar_caso", { id, modo });
}

/** Captura clínica (instantánea): el alumno aporta el equipo; el paciente sale de la verdad oculta. */
export function capturarClinico(params: SimParams): Promise<Recording> {
  return invoke<Recording>("capturar_clinico", { params });
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

/** Verdad del caso: solo si el rol docente está desbloqueado (si no, rechaza). */
export function verVerdad(): Promise<VerdadDto> {
  return invoke<VerdadDto>("ver_verdad");
}

/** Estado de sesión (modo, rol, caso cargado). */
export function estadoSesion(): Promise<EstadoSesion> {
  return invoke<EstadoSesion>("estado_sesion");
}
