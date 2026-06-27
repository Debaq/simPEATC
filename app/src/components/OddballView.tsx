// Vista de resultados oddball (P300/MMN): por oído, la última captura del examen
// activo (3 trazas estándar/desviante/diferencia). Lista las ondas detectadas
// (P3b/MMN) cuando el modo las revela.

import type { EarSide, OddballCap } from "../types";
import OddballChart from "../charts/OddballChart";
import { num } from "../lib/format";

const EARS: EarSide[] = ["Right", "Left"];

export default function OddballView({ caps }: { caps: OddballCap[] }) {
  const latestFor = (ear: EarSide) =>
    caps.filter((c) => c.ear === ear).slice(-1)[0] ?? null;

  return (
    <div className="abr-pair">
      {EARS.map((ear) => {
        const cap = latestFor(ear);
        const tag = ear === "Right" ? "OD" : "OI";
        return (
          <div className="abr-panel" key={ear}>
            <div className="abr-head">
              <span className="abr-ear" style={{ color: ear === "Right" ? "#e8615f" : "#4aa3ff" }}>
                {tag}
              </span>
              {cap ? (
                <span className="abr-meas">
                  {cap.intensity} dB ·{" "}
                  {cap.rec.detected.length
                    ? cap.rec.detected.map((p) => `${p.label} ${num(p.latency_ms, 0)}ms`).join("  ")
                    : "marca P3b/MMN en la diferencia"}
                </span>
              ) : (
                <span className="abr-meas">sin captura</span>
              )}
            </div>
            <div style={{ flex: 1, minHeight: 0 }}>
              {cap ? (
                <OddballChart rec={cap.rec} />
              ) : (
                <div className="restab-empty" style={{ padding: 20 }}>
                  captura {tag} para ver las trazas
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
