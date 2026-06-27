// Análisis de ECochG: razón SP/AP (amplitud) por oído, con su zona de normalidad.
// Es el símil del L-I para la electrococleografía: el alumno marca SP y AP, y se
// calcula la razón; elevada → hidrops endolinfático (Ménière).
//
// Cortes clínicos: ≤ 0.35 normal · 0.40–0.49 aumentada · ≥ 0.50 anormal.

import type { AbrCurve, EarSide } from "../types";
import { num } from "../lib/format";

const EARS: EarSide[] = ["Right", "Left"];
const NORMAL = 0.4;
const ABNORMAL = 0.5;
const SCALE = 0.8; // tope de la barra visual

function veredicto(r: number): { txt: string; cls: string } {
  if (r >= ABNORMAL) return { txt: "elevada (hidrops)", cls: "bad" };
  if (r >= NORMAL) return { txt: "aumentada (límite)", cls: "warn" };
  return { txt: "normal", cls: "ok" };
}

export default function EcochgRatioView({ curves }: { curves: AbrCurve[] }) {
  // Por oído, la última captura ECochG con SP y AP marcadas.
  const filas = EARS.map((ear) => {
    const cs = curves.filter((c) => c.ear === ear);
    for (let i = cs.length - 1; i >= 0; i--) {
      const sp = cs[i].marks.find((m) => m.label === "SP");
      const ap = cs[i].marks.find((m) => m.label === "AP");
      if (sp && ap && Math.abs(ap.uv) > 1e-6) {
        return { ear, sp: sp.uv, ap: ap.uv, r: Math.abs(sp.uv) / Math.abs(ap.uv) };
      }
    }
    return { ear, sp: null, ap: null, r: null as number | null };
  });

  return (
    <div>
      {filas.map((f) => {
        const tag = f.ear === "Right" ? "OD" : "OI";
        const color = f.ear === "Right" ? "#e8615f" : "#4aa3ff";
        return (
          <div key={f.ear} className="card" style={{ marginBottom: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontWeight: 800, color }}>{tag}</span>
              {f.r == null ? (
                <span className="hint">marca SP y AP en la curva ECochG de este oído</span>
              ) : (
                <>
                  <span className="hint">
                    SP {num(f.sp!, 3)} µV · AP {num(f.ap!, 3)} µV
                  </span>
                  <span style={{ fontWeight: 800, fontSize: 18, marginLeft: "auto" }}>
                    SP/AP {num(f.r, 2)}
                  </span>
                  <span className={`badge ${veredicto(f.r).cls}`}>{veredicto(f.r).txt}</span>
                </>
              )}
            </div>
            {f.r != null && (
              <div className="spap-bar">
                <div
                  className="spap-mark"
                  style={{ left: `${Math.min(f.r / SCALE, 1) * 100}%` }}
                />
              </div>
            )}
          </div>
        );
      })}
      <p className="hint">
        Zona normal ≤ {NORMAL.toFixed(2)} (verde) · aumentada {NORMAL.toFixed(2)}–{(ABNORMAL - 0.01).toFixed(2)}{" "}
        (ámbar) · anormal ≥ {ABNORMAL.toFixed(2)} (rojo). La razón SP/AP elevada sugiere hidrops
        endolinfático (Ménière).
      </p>
    </div>
  );
}
