import ReactECharts from "echarts-for-react";
import type { EarSide, FspPoint } from "../types";
import { num } from "../lib/format";

// Umbral clínico de detección F_sp (Elberling & Don).
const FSP_THRESHOLD = 3.1;

/**
 * Sub-gráfico de calidad de la toma actual: F_sp (señal/ruido) vs promediaciones.
 * Sube con los sweeps; cruza el umbral (~3,1) cuando la respuesta es detectable.
 */
export default function FspGraph({ data, ear }: { data: FspPoint[]; ear: EarSide }) {
  const color = ear === "Right" ? "#d62828" : "#1f6feb";
  const last = data[data.length - 1];
  const maxFsp = data.reduce((m, p) => Math.max(m, p.fsp), FSP_THRESHOLD);

  const option = {
    backgroundColor: "#ffffff",
    animation: false,
    grid: { left: 30, right: 12, top: 6, bottom: 18 },
    xAxis: {
      type: "value",
      min: 0,
      axisLine: { lineStyle: { color: "#888" } },
      axisLabel: { color: "#555", fontSize: 9 },
      splitLine: { lineStyle: { color: "#eee" } },
    },
    yAxis: {
      type: "value",
      min: 0,
      max: Math.max(4, maxFsp * 1.1),
      axisLine: { lineStyle: { color: "#888" } },
      axisLabel: { color: "#555", fontSize: 9 },
      splitLine: { lineStyle: { color: "#eee" } },
    },
    series: [
      {
        type: "line",
        data: data.map((p) => [p.sweeps, p.fsp]),
        showSymbol: false,
        silent: true,
        lineStyle: { color, width: 1.6 },
        markLine: {
          symbol: "none",
          silent: true,
          label: { formatter: "umbral 3,1", color: "#999", fontSize: 9, position: "insideEndTop" },
          lineStyle: { color: "#c0392b", type: "dashed", opacity: 0.6 },
          data: [{ yAxis: FSP_THRESHOLD }],
        },
      },
    ],
  };

  return (
    <div className="fsp-wrap">
      <div className="fsp-head">
        <span style={{ color }}>{ear === "Right" ? "OD" : "OI"}</span> · FSP{" "}
        {last ? num(last.fsp, 1) : "—"} · {last ? last.sweeps : 0} sweeps
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>
        <ReactECharts option={option} style={{ height: "100%", width: "100%" }} notMerge />
      </div>
    </div>
  );
}
