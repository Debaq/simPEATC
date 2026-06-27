// Editor de un caso = PACIENTE (fisiología). No fija examen/oído/intensidad.
// Incluye una VISTA PREVIA: elige un examen + intensidad y muestra qué respuesta
// genera el motor sobre este paciente (qué ondas, a qué latencia), para que el
// creador vea reflejado el resultado. Carga el paciente en el slot OD u OI.

import { useState } from "react";
import type {
  CaseDef,
  CaseLesionDef,
  EarSide,
  FreqProfile,
  LesionSite,
  Modality,
  SimOutput,
  SimParams,
  SubjectParams,
} from "../types";
import { SelectField } from "./widgets";
import { previewCaso } from "../api";
import { blankLesion, downloadCase, slugify } from "../lib/caseFile";
import { num } from "../lib/format";

const SITE_OPTS = [
  { value: "Conductive", label: "Conductiva (oído medio)" },
  { value: "Cochlear", label: "Coclear (sensorial)" },
  { value: "Retrocochlear", label: "Retrococlear (VIII par)" },
  { value: "Neural", label: "Neural (neuropatía)" },
  { value: "CentralConduction", label: "Conducción central (EM)" },
  { value: "Brainstem", label: "Tronco / muerte encefálica" },
  { value: "Cortical", label: "Cortical (TPAC)" },
  { value: "Cognitive", label: "Cognitiva (P300)" },
] as const;
const PROFILE_OPTS = [
  { value: "Flat", label: "Plano" },
  { value: "HighFrequency", label: "Agudos" },
  { value: "LowFrequency", label: "Graves" },
  { value: "CookieBite", label: "En U (cookie-bite)" },
] as const;
const EXAM_OPTS = [
  { value: "Abr", label: "ABR" },
  { value: "ECochG", label: "ECochG" },
  { value: "Mlr", label: "MLR" },
  { value: "Alr", label: "ALR" },
  { value: "P300", label: "P300" },
  { value: "Mmn", label: "MMN" },
  { value: "Assr", label: "ASSR" },
] as const;
const EAR_OPTS = [
  { value: "Right", label: "OD" },
  { value: "Left", label: "OI" },
] as const;

const DUMMY_SUBJECT: SubjectParams = {
  age_years: 30,
  sex: "Female",
  temperature_c: 37,
  state: "Awake",
  attention: "Passive",
  lesion: null,
};

interface NumProps {
  label: string;
  value: number;
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
  onChange: (v: number) => void;
}
function NumField({ label, value, min, max, step = 1, unit, onChange }: NumProps) {
  return (
    <div className="field">
      <label>
        {label}
        {unit ? ` (${unit})` : ""}
      </label>
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(e) => onChange(parseFloat(e.target.value))}
      />
    </div>
  );
}

interface Props {
  value: CaseDef;
  onChange: (def: CaseDef) => void;
  onLoad: (def: CaseDef, ear: EarSide) => void;
  loading?: boolean;
}

export default function CaseEditor({ value, onChange, onLoad, loading }: Props) {
  const set = <K extends keyof CaseDef>(key: K, v: CaseDef[K]) =>
    onChange({ ...value, [key]: v });

  const setLesion = (i: number, l: CaseLesionDef) =>
    onChange({ ...value, lesions: value.lesions.map((x, j) => (j === i ? l : x)) });
  const addLesion = () => onChange({ ...value, lesions: [...value.lesions, blankLesion()] });
  const delLesion = (i: number) =>
    onChange({ ...value, lesions: value.lesions.filter((_, j) => j !== i) });

  const idShown = value.id || slugify(value.name);
  const withId = (): CaseDef => ({ ...value, id: idShown });

  // Vista previa.
  const [pvExam, setPvExam] = useState<Modality>("Abr");
  const [pvInt, setPvInt] = useState(80);
  const [pvEar, setPvEar] = useState<EarSide>("Right");
  const [preview, setPreview] = useState<SimOutput | null>(null);
  const [pvErr, setPvErr] = useState<string | null>(null);
  const [pvLoading, setPvLoading] = useState(false);

  async function runPreview() {
    setPvErr(null);
    setPvLoading(true);
    const params: SimParams = {
      modality: pvExam,
      ear: pvEar,
      intensity_db: pvInt,
      sweeps: 1000,
      freq_hz: 2000,
      carrier_hz: 2000,
      mod_freq_hz: 80,
      subject: DUMMY_SUBJECT,
    };
    try {
      setPreview(await previewCaso(withId(), pvEar, params));
    } catch (e) {
      setPvErr(String(e));
      setPreview(null);
    } finally {
      setPvLoading(false);
    }
  }

  return (
    <div className="case-editor">
      {/* Identidad */}
      <div className="field">
        <label>Nombre del paciente</label>
        <input
          type="text"
          value={value.name}
          placeholder="p. ej. Neurinoma del acústico"
          onChange={(e) => {
            const name = e.target.value;
            const autoId = value.id === "" || value.id === slugify(value.name);
            onChange({ ...value, name, id: autoId ? slugify(name) : value.id });
          }}
        />
      </div>
      <div className="field">
        <label>
          id <span className="hint">(slug estable; se usa en el archivo)</span>
        </label>
        <input
          type="text"
          value={value.id}
          placeholder={slugify(value.name) || "caso_id"}
          onChange={(e) => set("id", slugify(e.target.value))}
        />
      </div>
      <div className="field">
        <label>Descripción didáctica</label>
        <textarea
          rows={2}
          value={value.description}
          onChange={(e) => set("description", e.target.value)}
        />
      </div>

      <p className="hint" style={{ marginTop: 2 }}>
        La patología solo define las lesiones. Edad, sexo, estado y atención son
        variables de la sesión (se ajustan al montar el caso).
      </p>

      {/* Lesiones */}
      <div className="lesion-block">
        <div className="lesion-head">
          <span className="section-title" style={{ margin: 0 }}>
            Lesiones ({value.lesions.length})
          </span>
          <button className="mini" onClick={addLesion}>
            + Lesión
          </button>
        </div>
        {value.lesions.length === 0 ? (
          <p className="hint">Sin lesiones: paciente con audición normal.</p>
        ) : (
          value.lesions.map((l, i) => (
            <div className="lesion-row" key={i}>
              <SelectField<LesionSite>
                label="Sitio"
                value={l.site}
                options={SITE_OPTS as any}
                onChange={(v) => setLesion(i, { ...l, site: v })}
              />
              <NumField
                label="Severidad"
                unit="dB"
                value={l.severity_db}
                min={0}
                max={100}
                step={5}
                onChange={(v) => setLesion(i, { ...l, severity_db: v })}
              />
              <SelectField<FreqProfile>
                label="Perfil"
                value={l.profile}
                options={PROFILE_OPTS as any}
                onChange={(v) => setLesion(i, { ...l, profile: v })}
              />
              <button className="mini danger-btn" onClick={() => delLesion(i)} title="Quitar">
                ✕
              </button>
            </div>
          ))
        )}
      </div>

      {/* Vista previa del examen */}
      <div className="preview-block">
        <div className="lesion-head">
          <span className="section-title" style={{ margin: 0 }}>
            Vista previa — ¿qué sale?
          </span>
        </div>
        <div className="editor-grid">
          <SelectField<Modality>
            label="Examen"
            value={pvExam}
            options={EXAM_OPTS as any}
            onChange={setPvExam}
          />
          <NumField
            label="Intensidad"
            unit="dB"
            value={pvInt}
            min={0}
            max={120}
            step={5}
            onChange={setPvInt}
          />
          <SelectField<EarSide>
            label="Oído"
            value={pvEar}
            options={EAR_OPTS as any}
            onChange={setPvEar}
          />
          <div className="field" style={{ display: "flex", alignItems: "flex-end" }}>
            <button className="mini" onClick={runPreview} disabled={pvLoading}>
              {pvLoading ? "…" : "Previsualizar"}
            </button>
          </div>
        </div>
        <PreviewResult out={preview} err={pvErr} />
      </div>

      {/* Acciones */}
      <div className="editor-actions">
        <button className="mini" onClick={() => downloadCase(withId())}>
          ⤓ Exportar JSON
        </button>
        <button className="mini" disabled={loading} onClick={() => onLoad(withId(), "Right")}>
          Cargar en OD
        </button>
        <button className="mini" disabled={loading} onClick={() => onLoad(withId(), "Left")}>
          Cargar en OI
        </button>
      </div>
    </div>
  );
}

function PreviewResult({ out, err }: { out: SimOutput | null; err: string | null }) {
  if (err) return <p className="hint" style={{ color: "var(--danger)" }}>{err}</p>;
  if (!out) return <p className="hint">Elige examen e intensidad y pulsa Previsualizar.</p>;

  if (out.kind === "assr") {
    const d = out.data;
    return (
      <p className="hint">
        ASSR {d.carrier_hz} Hz / {d.mod_freq_hz} Hz · {d.detected ? "RESPUESTA presente" : "sin respuesta"} ·
        SNR {num(d.snr_db, 1)} dB · F {num(d.f_ratio, 1)}
      </p>
    );
  }
  const peaks = out.data.detected;
  if (!peaks.length) return <p className="hint">Sin ondas detectadas a esa intensidad (bajo umbral / desincronía).</p>;
  return (
    <table className="restab" style={{ marginTop: 4 }}>
      <thead>
        <tr>
          <th>Onda</th>
          <th>Latencia (ms)</th>
          <th>Amplitud (µV)</th>
        </tr>
      </thead>
      <tbody>
        {peaks.map((p) => (
          <tr key={p.label}>
            <td>{p.label}</td>
            <td>{num(p.latency_ms, 2)}</td>
            <td>{num(p.amplitude_uv, 3)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
