import ReactECharts from "echarts-for-react";
import type { OddballRecording, Waveform } from "../types";

function toPairs(w: Waveform): [number, number][] {
  return w.times_ms.map((t, i) => [t, w.amplitudes_uv[i]]);
}

/** Estandar, desviante y onda diferencia superpuestas (P300/MMN). */
export default function OddballChart({ rec }: { rec: OddballRecording }) {
  const option = {
    backgroundColor: "transparent",
    grid: { left: 56, right: 18, top: 36, bottom: 40 },
    legend: {
      top: 4,
      textStyle: { color: "#9aa0b4" },
      data: ["Estándar", "Desviante", "Diferencia"],
    },
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "value",
      name: "Tiempo (ms)",
      nameLocation: "middle",
      nameGap: 26,
      axisLine: { lineStyle: { color: "#3a3f52" } },
      splitLine: { lineStyle: { color: "#20242f" } },
    },
    yAxis: {
      type: "value",
      name: "Amplitud (µV)",
      nameLocation: "middle",
      nameGap: 40,
      axisLine: { lineStyle: { color: "#3a3f52" } },
      splitLine: { lineStyle: { color: "#20242f" } },
    },
    series: [
      {
        name: "Estándar",
        type: "line",
        data: toPairs(rec.standard),
        showSymbol: false,
        lineStyle: { color: "#8c96b3", width: 1.2 },
      },
      {
        name: "Desviante",
        type: "line",
        data: toPairs(rec.deviant),
        showSymbol: false,
        lineStyle: { color: "#59b3ff", width: 1.2 },
      },
      {
        name: "Diferencia",
        type: "line",
        data: toPairs(rec.difference),
        showSymbol: false,
        lineStyle: { color: "#ff8c4d", width: 2 },
        markLine: rec.detected.length
          ? {
              symbol: "none",
              label: {
                formatter: (p: { name: string }) => p.name,
                color: "#ffd23a",
                fontSize: 11,
              },
              lineStyle: { color: "#ffd23a", type: "dashed", opacity: 0.6 },
              data: rec.detected.map((pk) => ({ name: pk.label, xAxis: pk.latency_ms })),
            }
          : undefined,
      },
    ],
  };

  return (
    <ReactECharts
      option={option}
      style={{ height: "100%", width: "100%" }}
      notMerge
    />
  );
}
