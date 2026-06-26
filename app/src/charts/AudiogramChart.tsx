import ReactECharts from "echarts-for-react";
import type { AudiogramPoint } from "../types";

/**
 * Audiograma estimado: frecuencia (log) vs umbral en dB con el eje invertido
 * (0 dB arriba, 100 dB abajo), como en la convencion clinica. Los puntos sin
 * respuesta (null) se dejan como hueco.
 */
export default function AudiogramChart({ data }: { data: AudiogramPoint[] }) {
  const pairs = data.map(([f, thr]) => [f, thr] as [number, number | null]);

  const option = {
    backgroundColor: "transparent",
    grid: { left: 56, right: 24, top: 24, bottom: 44 },
    tooltip: {
      trigger: "axis",
      valueFormatter: (v: number) =>
        v == null ? "sin respuesta" : `${v.toFixed(0)} dB`,
    },
    xAxis: {
      type: "log",
      name: "Frecuencia (Hz)",
      nameLocation: "middle",
      nameGap: 28,
      min: 250,
      max: 8000,
      axisLine: { lineStyle: { color: "#3a3f52" } },
      splitLine: { lineStyle: { color: "#20242f" } },
    },
    yAxis: {
      type: "value",
      name: "Umbral (dB nHL)",
      nameLocation: "middle",
      nameGap: 40,
      inverse: true,
      min: -10,
      max: 100,
      axisLine: { lineStyle: { color: "#3a3f52" } },
      splitLine: { lineStyle: { color: "#20242f" } },
    },
    series: [
      {
        type: "line",
        data: pairs,
        connectNulls: false,
        symbol: "circle",
        symbolSize: 9,
        lineStyle: { color: "#4aa3ff", width: 2 },
        itemStyle: { color: "#4aa3ff" },
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
