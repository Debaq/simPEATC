// Evaluación (G9): el alumno emite su diagnóstico por oído y entrega. Muestra la
// calificación (diagnóstico + marcado) y revela la verdad. Solo en Evaluación/OSCE.

import { useState } from "react";
import type { Calificacion, DiagEar, EarSide, LesionSite } from "../types";
import Modal from "./Modal";
import { num } from "../lib/format";

const SITE_OPTS: { value: LesionSite; label: string }[] = [
  { value: "Conductive", label: "Conductiva" },
  { value: "Cochlear", label: "Coclear" },
  { value: "Retrocochlear", label: "Retrococlear" },
  { value: "Neural", label: "Neural" },
  { value: "CentralConduction", label: "Conducción central (EM)" },
  { value: "Brainstem", label: "Tronco / muerte encefálica" },
  { value: "Cortical", label: "Cortical (TPAC)" },
  { value: "Cognitive", label: "Cognitiva (P300)" },
];
const SITE_LABEL: Record<string, string> = Object.fromEntries(
  SITE_OPTS.map((o) => [o.value, o.label])
);
const EARS: EarSide[] = ["Right", "Left"];
const earTag = (e: string) => (e === "Right" || e === "OD" ? "OD" : "OI");

interface Props {
  onCalificar: (diagnosticos: DiagEar[]) => Promise<Calificacion>;
  onClose: () => void;
}

export default function AnswerModal({ onCalificar, onClose }: Props) {
  const [sel, setSel] = useState<Record<EarSide, Set<LesionSite>>>({
    Right: new Set(),
    Left: new Set(),
  });
  const [cal, setCal] = useState<Calificacion | null>(null);
  const [loading, setLoading] = useState(false);

  const toggle = (ear: EarSide, site: LesionSite) =>
    setSel((p) => {
      const s = new Set(p[ear]);
      s.has(site) ? s.delete(site) : s.add(site);
      return { ...p, [ear]: s };
    });

  async function entregar() {
    setLoading(true);
    try {
      const diagnosticos: DiagEar[] = EARS.map((ear) => ({
        ear: ear === "Right" ? "OD" : "OI",
        sitios: [...sel[ear]],
      }));
      setCal(await onCalificar(diagnosticos));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Modal title={cal ? "Resultado de la evaluación" : "Responder · diagnóstico"} onClose={onClose} width={680}>
      {cal ? (
        <Reporte cal={cal} />
      ) : (
        <>
          <p className="hint" style={{ marginBottom: 8 }}>
            Indica, por oído, el diagnóstico (sitio de lesión). Sin marcar = oído normal.
          </p>
          <div className="slot-row">
            {EARS.map((ear) => (
              <div key={ear} className={`slot slot-${earTag(ear).toLowerCase()}`}>
                <div className="slot-head">
                  <span className="slot-tag">{earTag(ear)}</span>
                  {sel[ear].size === 0 && <span className="hint">normal</span>}
                </div>
                <div className="chips" style={{ marginTop: 6 }}>
                  {SITE_OPTS.map((o) => (
                    <button
                      key={o.value}
                      className={`chip ${sel[ear].has(o.value) ? "active" : ""}`}
                      onClick={() => toggle(ear, o.value)}
                    >
                      {o.label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div className="editor-actions">
            <button className="primary" onClick={entregar} disabled={loading}>
              {loading ? "Calificando…" : "Entregar"}
            </button>
          </div>
        </>
      )}
    </Modal>
  );
}

function Reporte({ cal }: { cal: Calificacion }) {
  const color = cal.puntaje >= 70 ? "var(--accent)" : cal.puntaje >= 40 ? "#e0b85c" : "var(--danger)";
  const sites = (xs: string[]) => (xs.length ? xs.map((s) => SITE_LABEL[s] ?? s).join(", ") : "normal");
  return (
    <div>
      <div style={{ textAlign: "center", marginBottom: 10 }}>
        <div style={{ fontSize: 40, fontWeight: 800, color }}>{num(cal.puntaje, 0)}</div>
        <div className="hint">
          diagnóstico {num(cal.dx_pct, 0)}% · marcado {num(cal.marcas_pct, 0)}% · marcas {cal.marcas.correctas}✓ /{" "}
          {cal.marcas.incorrectas}✗ / {cal.marcas.perdidas} perdidas
        </div>
      </div>
      <table className="restab">
        <thead>
          <tr>
            <th>Oído</th>
            <th>Tu respuesta</th>
            <th>Correcto</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {cal.por_oido.map((d) => (
            <tr key={d.ear}>
              <td style={{ fontWeight: 700 }}>{earTag(d.ear)}</td>
              <td>{sites(d.respondido)}</td>
              <td>{sites(d.esperado)}</td>
              <td>
                <span className={`badge ${d.correcto ? "ok" : d.parcial ? "warn" : "bad"}`}>
                  {d.correcto ? "✓" : d.parcial ? "parcial" : "✗"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="verdad-box" style={{ marginTop: 10 }}>
        <span className="section-title" style={{ margin: 0 }}>
          Verdad
        </span>
        {cal.verdad.map((v) => (
          <p className="hint" key={v.ear} style={{ marginTop: 4 }}>
            <b>{earTag(v.ear)}</b> · {v.nombre} — {v.descripcion}
          </p>
        ))}
      </div>
    </div>
  );
}
