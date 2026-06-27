// Panel de VARIABLES EXTERNAS de la sesión (las define el docente): edad, sexo,
// temperatura corporal, estado de alerta y atención. Se combinan con la patología
// del slot al capturar. Usa el mismo layout compacto que el equipo del alumno.

import type { ReactNode } from "react";
import type { ArousalState, Attention, SexValue, SubjectParams } from "../types";

const SEX_OPTS: { value: SexValue; label: string }[] = [
  { value: "Female", label: "Femenino" },
  { value: "Male", label: "Masculino" },
];
const STATE_OPTS: { value: ArousalState; label: string }[] = [
  { value: "Awake", label: "Despierto" },
  { value: "NaturalSleep", label: "Sueño natural" },
  { value: "Sedated", label: "Sedado" },
  { value: "Anesthetized", label: "Anestesiado" },
];
const ATTENTION_OPTS: { value: Attention; label: string }[] = [
  { value: "Passive", label: "Pasiva" },
  { value: "Active", label: "Activa" },
  { value: "Ignoring", label: "Ignorando" },
];

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="eqrow">
      <label>{label}</label>
      {children}
    </div>
  );
}

interface Props {
  value: SubjectParams;
  onChange: (s: SubjectParams) => void;
}

export default function SessionVarsPanel({ value, onChange }: Props) {
  const set = <K extends keyof SubjectParams>(key: K, v: SubjectParams[K]) =>
    onChange({ ...value, [key]: v });

  return (
    <div className="card eq">
      <p className="section-title">Variables de sesión</p>
      <Row label={`Edad: ${value.age_years} años`}>
        <span />
      </Row>
      <input
        className="eq-slider"
        type="range"
        min={0}
        max={90}
        step={1}
        value={value.age_years}
        onChange={(e) => set("age_years", parseFloat(e.target.value))}
      />
      <Row label="Sexo">
        <select value={value.sex} onChange={(e) => set("sex", e.target.value as SexValue)}>
          {SEX_OPTS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </Row>
      <Row label="Estado">
        <select value={value.state} onChange={(e) => set("state", e.target.value as ArousalState)}>
          {STATE_OPTS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </Row>
      <Row label="Atención">
        <select
          value={value.attention}
          onChange={(e) => set("attention", e.target.value as Attention)}
        >
          {ATTENTION_OPTS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </Row>
      <Row label={`Temperatura: ${value.temperature_c.toFixed(1)} °C`}>
        <span />
      </Row>
      <input
        className="eq-slider"
        type="range"
        min={34}
        max={40}
        step={0.1}
        value={value.temperature_c}
        onChange={(e) => set("temperature_c", parseFloat(e.target.value))}
      />
    </div>
  );
}
