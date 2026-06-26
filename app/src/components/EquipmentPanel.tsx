import type {
  EarSide,
  EquipoParams,
  FilterType,
  Modality,
  PolarityValue,
  RampValue,
  SimParams,
  StimulusKind,
  TransducerValue,
} from "../types";
import { ChipGroup } from "./widgets";
import { num } from "../lib/format";

interface Props {
  params: SimParams;
  onChange: (p: SimParams) => void;
}

const STIM_OPTS: { value: StimulusKind; label: string }[] = [
  { value: "click", label: "Click" },
  { value: "toneburst", label: "Tone-burst" },
  { value: "ce_chirp", label: "CE-Chirp" },
  { value: "ls_chirp", label: "LS-Chirp" },
  { value: "nb_chirp", label: "NB-Chirp" },
];

// Estímulos válidos por prueba (los chirps son específicos del ABR).
const STIM_BY_MODALITY: Record<string, StimulusKind[]> = {
  Abr: ["click", "toneburst", "ce_chirp", "ls_chirp", "nb_chirp"],
  ECochG: ["click", "toneburst"],
  Mlr: ["click", "toneburst"],
  Alr: ["toneburst", "click"],
  P300: ["toneburst"],
  Mmn: ["toneburst"],
};
const POL_OPTS: { value: PolarityValue; label: string }[] = [
  { value: "Rarefaction", label: "Rarefacción" },
  { value: "Condensation", label: "Condensación" },
  { value: "Alternating", label: "Alternante" },
];
const TRANS_OPTS: { value: TransducerValue; label: string }[] = [
  { value: "Insert", label: "Inserción" },
  { value: "Supraaural", label: "Supraaural" },
  { value: "BoneConductor", label: "Óseo" },
];
const RAMP_OPTS: { value: RampValue; label: string }[] = [
  { value: "Linear", label: "Lineal" },
  { value: "Hanning", label: "Hanning" },
  { value: "Blackman", label: "Blackman" },
  { value: "Gaussian", label: "Gaussiana" },
];
// NOTA: el motor solo implementa Butterworth; Bessel/Chebyshev se listan pero
// por dentro usan Butterworth hasta implementarlas en aep-core/dsp/filter.rs.
const FILTER_TYPE_OPTS: { value: FilterType; label: string }[] = [
  { value: "Butterworth", label: "Butterworth" },
  { value: "Bessel", label: "Bessel" },
  { value: "Chebyshev", label: "Chebyshev" },
];
// Pendiente del filtro: dB/octava ↔ orden.
const SLOPE_OPTS: { value: number; label: string }[] = [
  { value: 1, label: "6 dB/oct" },
  { value: 2, label: "12 dB/oct" },
  { value: 4, label: "24 dB/oct" },
  { value: 8, label: "48 dB/oct" },
];

// Valores fijos estándar (de lista, no continuos).
// Tipos de prueba (todo menos estado estable / ASSR).
const TEST_OPTS: { value: Modality; label: string }[] = [
  { value: "Abr", label: "ABR" },
  { value: "ECochG", label: "ECochG" },
  { value: "Mlr", label: "MLR" },
  { value: "Alr", label: "ALR" },
  { value: "P300", label: "P300" },
  { value: "Mmn", label: "MMN" },
];

// Preset clínico por modalidad: estímulo, intensidad, promediaciones y equipo
// con sentido para esa prueba (todos los valores salen de las listas fijas).
interface ModalityPreset {
  stimulus: StimulusKind;
  intensity_db: number;
  sweeps: number;
  equipo: Partial<EquipoParams>;
}
const MODALITY_PRESETS: Record<string, ModalityPreset> = {
  Abr: {
    stimulus: "click",
    intensity_db: 80,
    sweeps: 2000,
    equipo: { rate_hz: 27.7, polarity: "Rarefaction", hp_hz: 100, lp_hz: 3000, pre_ms: 1, post_ms: 15, artifact_reject_uv: 25 },
  },
  ECochG: {
    stimulus: "click",
    intensity_db: 90,
    sweeps: 1500,
    equipo: { rate_hz: 11.1, polarity: "Alternating", hp_hz: 10, lp_hz: 1500, pre_ms: 1, post_ms: 10, artifact_reject_uv: 25 },
  },
  Mlr: {
    stimulus: "click",
    intensity_db: 70,
    sweeps: 1000,
    equipo: { rate_hz: 7.1, polarity: "Alternating", hp_hz: 10, lp_hz: 300, pre_ms: 0, post_ms: 80, artifact_reject_uv: 50 },
  },
  Alr: {
    stimulus: "toneburst",
    intensity_db: 60,
    sweeps: 200,
    equipo: { rate_hz: 1.1, polarity: "Alternating", hp_hz: 1, lp_hz: 30, pre_ms: 0, post_ms: 300, artifact_reject_uv: 50 },
  },
  P300: {
    stimulus: "toneburst",
    intensity_db: 70,
    sweeps: 300,
    equipo: { rate_hz: 1.1, polarity: "Alternating", hp_hz: 0.1, lp_hz: 30, pre_ms: 0, post_ms: 300, artifact_reject_uv: 50 },
  },
  Mmn: {
    stimulus: "toneburst",
    intensity_db: 70,
    sweeps: 300,
    equipo: { rate_hz: 1.1, polarity: "Alternating", hp_hz: 0.1, lp_hz: 30, pre_ms: 0, post_ms: 300, artifact_reject_uv: 50 },
  },
};

const FREQS = [500, 1000, 2000, 4000];
const RATES = [1.1, 3.1, 7.1, 11.1, 21.1, 27.7, 31.1, 51.1];
const HP_HZ = [0.1, 1, 3.3, 5, 10, 30, 100, 150, 300];
const LP_HZ = [30, 100, 300, 750, 1000, 1500, 3000, 5000];
const PRE_MS = [0, 1, 2];
const POST_MS = [10, 15, 20, 25, 80, 100, 300];
const REJECT_UV = [10, 15, 20, 25, 30, 40, 50];
const IMP_KOHM = [1, 2, 3, 5, 8, 12, 20];

export const DEFAULT_EQUIPO: EquipoParams = {
  rate_hz: 27.7,
  polarity: "Rarefaction",
  transducer: "Insert",
  hp_hz: 100,
  lp_hz: 3000,
  notch_hz: 0,
  order: 2,
  filter_type: "Butterworth",
  ramp: "Hanning",
  pre_ms: 1,
  post_ms: 10,
  artifact_reject_uv: 25,
  impedance_kohm: 3,
};

function impedanceState(k: number): { txt: string; cls: string } {
  if (k <= 5) return { txt: "OK", cls: "ok" };
  if (k <= 10) return { txt: "alta", cls: "warn" };
  return { txt: "fuera", cls: "bad" };
}

/** Fila compacta: etiqueta a la izquierda, control a la derecha. */
function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="eqrow">
      <label>{label}</label>
      {children}
    </div>
  );
}

function NumSelect({
  value,
  options,
  unit,
  onChange,
}: {
  value: number;
  options: number[];
  unit?: string;
  onChange: (v: number) => void;
}) {
  return (
    <select value={String(value)} onChange={(e) => onChange(parseFloat(e.target.value))}>
      {options.map((o) => (
        <option key={o} value={String(o)}>
          {num(o, o % 1 === 0 ? 0 : 1)}
          {unit ? ` ${unit}` : ""}
        </option>
      ))}
    </select>
  );
}

/**
 * Ventana de adquisición (menú izquierdo) compacta. Filtros y valores discretos
 * por **select** (valores fijos estándar). Sirve para todas las modalidades.
 */
export default function EquipmentPanel({ params, onChange }: Props) {
  const eq = { ...DEFAULT_EQUIPO, ...params.equipo };
  const patch = (p: Partial<SimParams>) => onChange({ ...params, ...p });
  const patchEq = (p: Partial<EquipoParams>) =>
    onChange({ ...params, equipo: { ...eq, ...p } });
  const usesFreq = params.stimulus === "toneburst" || params.stimulus === "nb_chirp";
  const imp = impedanceState(eq.impedance_kohm ?? 3);

  return (
    <>
      <div className="card eq">
        <Row label="Tipo de prueba">
          <select
            value={params.modality}
            onChange={(e) => {
              const m = e.target.value as Modality;
              const p = MODALITY_PRESETS[m];
              onChange({
                ...params,
                modality: m,
                stimulus: p.stimulus,
                intensity_db: p.intensity_db,
                sweeps: p.sweeps,
                equipo: { ...eq, ...p.equipo },
              });
            }}
          >
            {TEST_OPTS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </Row>
      </div>

      <div className="card eq">
        <p className="section-title">Estímulo</p>
        <Row label="Oído">
          <ChipGroup<EarSide>
            value={params.ear}
            options={[
              { value: "Right", label: "OD", className: "ear-od" },
              { value: "Left", label: "OI", className: "ear-oi" },
            ]}
            onChange={(v) => patch({ ear: v })}
          />
        </Row>
        <Row label="Estímulo">
          <select
            value={params.stimulus ?? "click"}
            onChange={(e) => patch({ stimulus: e.target.value as StimulusKind })}
          >
            {STIM_OPTS.filter((o) =>
              (STIM_BY_MODALITY[params.modality] ?? STIM_OPTS.map((s) => s.value)).includes(o.value)
            ).map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </Row>
        {usesFreq && (
          <Row label="Frecuencia">
            <NumSelect value={params.freq_hz} options={FREQS} unit="Hz" onChange={(v) => patch({ freq_hz: v })} />
          </Row>
        )}
        {params.stimulus === "toneburst" && (
          <Row label="Ventana (rampa)">
            <select
              value={eq.ramp}
              onChange={(e) => patchEq({ ramp: e.target.value as RampValue })}
            >
              {RAMP_OPTS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </Row>
        )}
        <Row label="Polaridad">
          <select
            value={eq.polarity}
            onChange={(e) => patchEq({ polarity: e.target.value as PolarityValue })}
          >
            {POL_OPTS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </Row>
        <Row label="Transductor">
          <select
            value={eq.transducer}
            onChange={(e) => patchEq({ transducer: e.target.value as TransducerValue })}
          >
            {TRANS_OPTS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </Row>
        <Row label="Tasa">
          <NumSelect value={eq.rate_hz ?? 27.7} options={RATES} unit="/s" onChange={(v) => patchEq({ rate_hz: v })} />
        </Row>
        <Row label={`Intensidad: ${num(params.intensity_db, 0)} dB`}>
          <span />
        </Row>
        <input
          className="eq-slider"
          type="range"
          min={0}
          max={100}
          step={5}
          value={params.intensity_db}
          onChange={(e) => patch({ intensity_db: parseFloat(e.target.value) })}
        />
      </div>

      <div className="card eq">
        <p className="section-title">Filtro</p>
        <Row label="Tipo">
          <select
            value={eq.filter_type ?? "Butterworth"}
            onChange={(e) => patchEq({ filter_type: e.target.value as FilterType })}
          >
            {FILTER_TYPE_OPTS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </Row>
        <Row label="Pendiente">
          <select
            value={String(eq.order ?? 2)}
            onChange={(e) => patchEq({ order: parseInt(e.target.value, 10) })}
          >
            {SLOPE_OPTS.map((o) => (
              <option key={o.value} value={String(o.value)}>
                {o.label}
              </option>
            ))}
          </select>
        </Row>
        <Row label="Pasa-altos">
          <NumSelect value={eq.hp_hz ?? 100} options={HP_HZ} unit="Hz" onChange={(v) => patchEq({ hp_hz: v })} />
        </Row>
        <Row label="Pasa-bajos">
          <NumSelect value={eq.lp_hz ?? 3000} options={LP_HZ} unit="Hz" onChange={(v) => patchEq({ lp_hz: v })} />
        </Row>
        <Row label="Notch 50 Hz">
          <input
            type="checkbox"
            checked={(eq.notch_hz ?? 0) > 0}
            onChange={(e) => patchEq({ notch_hz: e.target.checked ? 50 : 0 })}
          />
        </Row>
      </div>

      <div className="card eq">
        <p className="section-title">Ventana</p>
        <Row label="Pre-estímulo">
          <NumSelect value={eq.pre_ms ?? 1} options={PRE_MS} unit="ms" onChange={(v) => patchEq({ pre_ms: v })} />
        </Row>
        <Row label="Post-estímulo">
          <NumSelect value={eq.post_ms ?? 10} options={POST_MS} unit="ms" onChange={(v) => patchEq({ post_ms: v })} />
        </Row>
        <Row label="Rechazo artef.">
          <NumSelect value={eq.artifact_reject_uv ?? 25} options={REJECT_UV} unit="µV" onChange={(v) => patchEq({ artifact_reject_uv: v })} />
        </Row>
        <Row label={`Promediaciones: ${params.sweeps}`}>
          <span />
        </Row>
        <input
          className="eq-slider"
          type="range"
          min={50}
          max={4000}
          step={50}
          value={params.sweeps}
          onChange={(e) => patch({ sweeps: parseFloat(e.target.value) })}
        />
        <Row label="Impedancia">
          <span style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <NumSelect
              value={eq.impedance_kohm ?? 3}
              options={IMP_KOHM}
              unit="kΩ"
              onChange={(v) => patchEq({ impedance_kohm: v })}
            />
            <span className={`badge ${imp.cls}`}>{imp.txt}</span>
          </span>
        </Row>
      </div>
    </>
  );
}
