// Informe clínico que REDACTA EL ESTUDIANTE. El encabezado (paciente, fecha) viene
// dado; los hallazgos, la impresión y las recomendaciones las escribe el alumno.
// Imprime a PDF (navegador) o exporta HTML con lo redactado.

import { useRef, useState } from "react";
import type { Modo, SubjectParams } from "../types";
import Modal from "./Modal";
import { num } from "../lib/format";

const STATE_LABEL: Record<string, string> = {
  Awake: "despierto", NaturalSleep: "sueño natural", Sedated: "sedado", Anesthetized: "anestesiado",
};

interface Secciones {
  motivo: string;
  hallazgosOD: string;
  hallazgosOI: string;
  impresion: string;
  recomendaciones: string;
}

const VACIO: Secciones = {
  motivo: "",
  hallazgosOD: "",
  hallazgosOI: "",
  impresion: "",
  recomendaciones: "",
};

interface Props {
  subject: SubjectParams;
  modo: Modo;
  onClose: () => void;
}

export default function ReportModal({ subject, modo, onClose }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [s, setS] = useState<Secciones>(VACIO);
  const fecha = new Date().toLocaleString("es-CL");
  const set = (k: keyof Secciones, v: string) => setS((p) => ({ ...p, [k]: v }));

  function exportarHtml() {
    const inner = ref.current?.innerHTML ?? "";
    const html = `<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Informe PEATC</title>
<style>body{font-family:system-ui,sans-serif;color:#111;background:#fff;max-width:760px;margin:24px auto;padding:0 16px}
h2{font-size:16px;margin:14px 0 4px;border-bottom:1px solid #ddd;padding-bottom:2px}
.muted{color:#666;font-size:12px}p{white-space:pre-wrap;line-height:1.4}</style>
</head><body>${inner}</body></html>`;
    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "informe_peatc.html";
    a.click();
    URL.revokeObjectURL(url);
  }

  const Seccion = ({ titulo, texto }: { titulo: string; texto: string }) => (
    <>
      <h2>{titulo}</h2>
      <p style={{ whiteSpace: "pre-wrap", minHeight: 18 }}>{texto || "—"}</p>
    </>
  );

  const Editor = ({ campo, label, rows = 3 }: { campo: keyof Secciones; label: string; rows?: number }) => (
    <div className="field no-print">
      <label>{label}</label>
      <textarea
        className="report-impresion"
        rows={rows}
        value={s[campo]}
        onChange={(e) => set(campo, e.target.value)}
      />
    </div>
  );

  return (
    <Modal title="Informe (lo redacta el estudiante)" onClose={onClose} width={760}>
      {/* Vista del informe (lo que se imprime/exporta) */}
      <div className="report-print" ref={ref}>
        <h2 style={{ marginTop: 0 }}>Informe de potenciales evocados auditivos</h2>
        <p className="muted">
          {fecha} · modo {modo} · paciente: {num(subject.age_years, 0)} años ·{" "}
          {subject.sex === "Male" ? "masculino" : "femenino"} ·{" "}
          {STATE_LABEL[subject.state] ?? subject.state} · {num(subject.temperature_c, 1)} °C
        </p>
        {s.motivo && <Seccion titulo="Motivo / contexto" texto={s.motivo} />}
        <Seccion titulo="Hallazgos — oído derecho (OD)" texto={s.hallazgosOD} />
        <Seccion titulo="Hallazgos — oído izquierdo (OI)" texto={s.hallazgosOI} />
        <Seccion titulo="Impresión diagnóstica" texto={s.impresion} />
        {s.recomendaciones && <Seccion titulo="Recomendaciones" texto={s.recomendaciones} />}
      </div>

      {/* Editor (no entra en el impreso) */}
      <div className="no-print" style={{ marginTop: 8 }}>
        <p className="hint" style={{ marginBottom: 6 }}>
          Redacta el informe a partir de tus registros y marcas. El encabezado con los datos del
          paciente ya está; tú escribes los hallazgos y la conclusión.
        </p>
        <Editor campo="motivo" label="Motivo / contexto (opcional)" rows={2} />
        <Editor campo="hallazgosOD" label="Hallazgos — OD" />
        <Editor campo="hallazgosOI" label="Hallazgos — OI" />
        <Editor campo="impresion" label="Impresión diagnóstica" />
        <Editor campo="recomendaciones" label="Recomendaciones (opcional)" rows={2} />
      </div>

      <div className="editor-actions no-print">
        <button className="mini" onClick={exportarHtml}>
          ⤓ Exportar HTML
        </button>
        <button className="primary" onClick={() => window.print()}>
          Imprimir / PDF
        </button>
      </div>
    </Modal>
  );
}
