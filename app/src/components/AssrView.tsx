// Vista de resultados ASSR (estado estable): tabla por (oído, portadora) con la
// detección objetiva (F, SNR) y el espectro de la última captura.

import { useState } from "react";
import type { AssrCap, EarSide } from "../types";
import SpectrumChart from "../charts/SpectrumChart";
import { num } from "../lib/format";

export default function AssrView({ caps }: { caps: AssrCap[] }) {
  const [sel, setSel] = useState<string | null>(null);
  const current = caps.find((c) => c.id === sel) ?? caps[caps.length - 1] ?? null;
  const earTag = (e: EarSide) => (e === "Right" ? "OD" : "OI");

  return (
    <div className="toprow">
      <div className="card results-card">
        <table className="restab">
          <thead>
            <tr>
              <th>Oído</th>
              <th>Portadora</th>
              <th>dB</th>
              <th>F</th>
              <th>SNR</th>
              <th>Resp.</th>
            </tr>
          </thead>
          <tbody>
            {caps.length === 0 ? (
              <tr>
                <td colSpan={6} className="restab-empty">
                  sin capturas — captura ASSR por frecuencia
                </td>
              </tr>
            ) : (
              caps.map((c) => (
                <tr
                  key={c.id}
                  className={c.id === current?.id ? "active" : ""}
                  onClick={() => setSel(c.id)}
                >
                  <td style={{ color: c.ear === "Right" ? "#e8615f" : "#4aa3ff", fontWeight: 700 }}>
                    {earTag(c.ear)}
                  </td>
                  <td>{num(c.result.carrier_hz, 0)} Hz</td>
                  <td>{num(c.intensity, 0)}</td>
                  <td>{num(c.result.f_ratio, 1)}</td>
                  <td>{num(c.result.snr_db, 1)}</td>
                  <td>
                    <span className={`badge ${c.result.detected ? "ok" : "bad"}`}>
                      {c.result.detected ? "sí" : "no"}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="card" style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column" }}>
        <p className="section-title">Espectro (F-test)</p>
        <div style={{ flex: 1, minHeight: 0 }}>
          {current ? (
            <SpectrumChart res={current.result} />
          ) : (
            <div className="restab-empty" style={{ padding: 20 }}>sin captura ASSR</div>
          )}
        </div>
      </div>
    </div>
  );
}
