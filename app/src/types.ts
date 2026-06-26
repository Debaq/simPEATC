// Espejo en TypeScript de los tipos serializados por el backend Rust (aep-core).

export interface Waveform {
  times_ms: number[];
  amplitudes_uv: number[];
}

export interface WavePeak {
  label: string;
  latency_ms: number;
  amplitude_uv: number;
}

export interface Recording {
  channels: Waveform[];
  detected: WavePeak[];
  fsp: number;
  accepted_sweeps: number;
  rejected_sweeps: number;
}

export interface OddballRecording {
  standard: Waveform;
  deviant: Waveform;
  difference: Waveform;
  detected: WavePeak[];
  fsp: number;
  accepted_sweeps: number;
  rejected_sweeps: number;
}

export interface AssrResult {
  carrier_hz: number;
  mod_freq_hz: number;
  f_ratio: number;
  snr_db: number;
  detected: boolean;
  n_epochs: number;
}

// Salida discriminada de `capture` / `run_case`.
export type SimOutput =
  | { kind: "transient"; data: Recording }
  | { kind: "oddball"; data: OddballRecording }
  | { kind: "assr"; data: AssrResult };

export interface CaseInfo {
  id: string;
  name: string;
  description: string;
  modality: string;
  ear: string;
}

// --- Clínico (G0: invariante verdad/ciego) ---

export type Modo = "practica" | "evaluacion" | "osce";

export interface VistaCiegaCaso {
  id: string;
  ear: string;
  age_years: number;
  sex: string;
  modo: Modo;
  nombre: string | null;
  descripcion: string | null;
}

export interface VerdadDto {
  caso_id: string;
  nombre: string;
  descripcion: string;
  lesiones: string[];
  verdad_picos: WavePeak[];
}

export interface EstadoSesion {
  modo: Modo;
  rol_docente: boolean;
  caso_cargado: boolean;
}

// Punto del audiograma: [frecuencia_hz, umbral_db | null].
export type AudiogramPoint = [number, number | null];

// Marca del alumno (G2): una onda etiquetada en (t, µV).
export interface Mark {
  label: string;
  t_ms: number;
  uv: number;
}

// Punto de la curva de calidad FSP (señal/ruido) vs promediaciones.
export interface FspPoint {
  sweeps: number;
  fsp: number;
}

// Curva ABR capturada en la pila clínica (apilado manual por arrastre).
export interface AbrCurve {
  id: string;
  ear: EarSide;
  intensity: number;
  wave: Waveform;
  gap: number; // offset vertical (µV) del apilado manual
  marks: Mark[]; // marcas ↓ de onda (I–V)
  fsp: FspPoint[]; // historial FSP de su captura
  replica?: Waveform; // segundo buffer A/B (reproducibilidad)
}

// Mensajes de captura progresiva (G3), por tauri::ipc::Channel.
export type CapMsg =
  | { event: "iniciada"; data: { objetivo: number; timesMs: number[] } }
  | {
      event: "refresco";
      data: {
        aceptados: number;
        rechazados: number;
        fsp: number;
        promedio: number[];
        replica: number[];
        epoca: number[];
      };
    }
  | { event: "finalizada"; data: { aceptados: number; rechazados: number } };

// --- Parametros de entrada ---

export type Modality = "ECochG" | "Abr" | "Mlr" | "Alr" | "P300" | "Mmn" | "Assr";
export type StimulusKind = "click" | "toneburst" | "ce_chirp" | "ls_chirp" | "nb_chirp";
export type EarSide = "Left" | "Right";
export type SexValue = "Male" | "Female";
export type ArousalState = "Awake" | "NaturalSleep" | "Sedated" | "Anesthetized";
export type Attention = "Active" | "Passive" | "Ignoring";
export type LesionSite = "Conductive" | "Cochlear" | "Retrocochlear" | "Neural" | "Central";
export type FreqProfile = "Flat" | "HighFrequency" | "LowFrequency" | "CookieBite";

export interface LesionParams {
  site: LesionSite;
  severity_db: number;
  profile: FreqProfile;
}

export interface SubjectParams {
  age_years: number;
  sex: SexValue;
  temperature_c: number;
  state: ArousalState;
  attention: Attention;
  lesion: LesionParams | null;
}

export type PolarityValue = "Rarefaction" | "Condensation" | "Alternating";
export type TransducerValue = "Insert" | "Supraaural" | "BoneConductor" | "FreeField";
export type RampValue = "Linear" | "Hanning" | "Blackman" | "Gaussian";
export type FilterType = "Butterworth" | "Bessel" | "Chebyshev";

// Ajustes del equipo (estímulo + adquisición); cada campo ausente deja el
// valor por defecto de la modalidad en el backend.
export interface EquipoParams {
  rate_hz?: number;
  polarity?: PolarityValue;
  transducer?: TransducerValue;
  hp_hz?: number;
  lp_hz?: number;
  notch_hz?: number;
  order?: number;
  filter_type?: FilterType;
  ramp?: RampValue;
  pre_ms?: number;
  post_ms?: number;
  artifact_reject_uv?: number;
  impedance_kohm?: number;
}

export interface SimParams {
  modality: Modality;
  ear: EarSide;
  stimulus?: StimulusKind;
  intensity_db: number;
  sweeps: number;
  freq_hz: number;
  carrier_hz: number;
  mod_freq_hz: number;
  equipo?: EquipoParams;
  subject: SubjectParams;
}
