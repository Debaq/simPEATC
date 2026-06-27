// Vista de resultados oddball (P300/MMN): por oído, la última captura del examen
// activo (3 trazas), marcable y medible (ver OddballPanel).

import type { EarSide, Mark, OddballCap } from "../types";
import OddballPanel from "./OddballPanel";

const EARS: EarSide[] = ["Right", "Left"];

export default function OddballView({
  caps,
  onMark,
}: {
  caps: OddballCap[];
  onMark: (capId: string, mark: Mark) => void;
}) {
  const latestFor = (ear: EarSide) => caps.filter((c) => c.ear === ear).slice(-1)[0] ?? null;

  return (
    <div className="abr-pair">
      {EARS.map((ear) => {
        const cap = latestFor(ear);
        const tag = ear === "Right" ? "OD" : "OI";
        return (
          <div className="abr-panel" key={ear} style={{ border: "none" }}>
            {cap ? (
              <OddballPanel cap={cap} onMark={(m) => onMark(cap.id, m)} />
            ) : (
              <div className="restab-empty" style={{ padding: 20 }}>
                captura {tag} para ver las trazas
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
