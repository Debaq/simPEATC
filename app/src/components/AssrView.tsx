// Vista de resultados ASSR = AUDIOGRAMA estimado. Por oído y frecuencia portadora,
// el umbral es la MENOR intensidad a la que hubo respuesta (detección). Se grafica
// como audiograma (frecuencia log, dB invertido) sobre la zona de audición normal.

import ReactECharts from "echarts-for-react";
import type { AssrCap, EarSide } from "../types";

const EAR_COLOR: Record<EarSide, string> = { Right: "#d62828", Left: "#1f6feb" };
const EARS: EarSide[] = ["Right", "Left"];

export default function AssrView({ caps }: { caps: AssrCap[] }) {
  // Frecuencias portadoras presentes.
  const freqs = [...new Set(caps.map((c) => Math.round(c.result.carrier_hz)))].sort((a, b) => a - b);

  // Umbral por (oído, frecuencia) = mínima intensidad con respuesta detectada.
  const umbral = (ear: EarSide, f: number): number | null => {
    const det = caps.filter(
      (c) => c.ear === ear && Math.round(c.result.carrier_hz) === f && c.result.detected
    );
    return det.length ? Math.min(...det.map((c) => c.intensity)) : null;
  };

  const series: any[] = EARS.map((ear) => ({
    name: ear === "Right" ? "OD" : "OI",
    type: "line",
    data: freqs.map((f) => [f, umbral(ear, f)]),
    connectNulls: false,
    symbol: ear === "Right" ? "circle" : "diamond",
    symbolSize: 11,
    lineStyle: { color: EAR_COLOR[ear], width: 2 },
    itemStyle: { color: EAR_COLOR[ear] },
  }));

  // Zona de audición normal (0–20 dB) sombreada.
  series.push({
    type: "line",
    data: [],
    silent: true,
    markArea: {
      silent: true,
      itemStyle: { color: "rgba(54,179,126,0.12)" },
      data: [[{ yAxis: -10 }, { yAxis: 20 }]],
    },
  });

  const option = {
    backgroundColor: "#ffffff",
    grid: { left: 56, right: 24, top: 28, bottom: 44 },
    legend: { top: 4, data: ["OD", "OI"], textStyle: { color: "#555a66", fontSize: 11 } },
    tooltip: {
      trigger: "item",
      valueFormatter: (v: number) => (v == null ? "sin respuesta" : `${v} dB`),
    },
    xAxis: {
      type: "log",
      name: "Frecuencia (Hz)",
      nameLocation: "middle",
      nameGap: 28,
      min: 250,
      max: 8000,
      axisLine: { lineStyle: { color: "#b9bfca" } },
      splitLine: { lineStyle: { color: "#e8eaef" } },
    },
    yAxis: {
      type: "value",
      name: "Umbral (dB HL)",
      nameLocation: "middle",
      nameGap: 40,
      inverse: true,
      min: -10,
      max: 110,
      interval: 20,
      axisLine: { lineStyle: { color: "#b9bfca" } },
      splitLine: { lineStyle: { color: "#e8eaef" } },
    },
    series,
  };

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div style={{ flex: 1, minHeight: 0 }}>
        <ReactECharts option={option} style={{ height: "100%", width: "100%" }} notMerge />
      </div>
      <p className="hint" style={{ padding: "2px 6px" }}>
        Audiograma por ASSR: captura cada frecuencia bajando la intensidad hasta que desaparece la
        respuesta; el umbral es la menor intensidad con respuesta. Zona verde = audición normal.
        {freqs.length === 0 && " — aún sin capturas."}
      </p>
    </div>
  );
}
