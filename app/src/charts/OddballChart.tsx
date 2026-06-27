import ReactECharts from "echarts-for-react";
import type { OddballRecording, Waveform } from "../types";

function toPairs(w: Waveform): [number, number][] {
  return w.times_ms.map((t, i) => [t, w.amplitudes_uv[i]]);
}

/** Estandar, desviante y onda diferencia superpuestas (P300/MMN). */
export default function OddballChart({ rec }: { rec: OddballRecording }) {
  const option = {
    backgroundColor: "#ffffff",
    grid: { left: 56, right: 18, top: 36, bottom: 40 },
    legend: {
      top: 4,
      textStyle: { color: "#555a66" },
      data: ["Estándar", "Desviante", "Diferencia"],
    },
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "value",
      name: "Tiempo (ms)",
      nameLocation: "middle",
      nameGap: 26,
      axisLine: { lineStyle: { color: "#b9bfca" } },
      splitLine: { lineStyle: { color: "#e8eaef" } },
    },
    yAxis: {
      type: "value",
      name: "Amplitud (µV)",
      nameLocation: "middle",
      nameGap: 40,
      axisLine: { lineStyle: { color: "#b9bfca" } },
      splitLine: { lineStyle: { color: "#e8eaef" } },
    },
    series: [
      {
        name: "Estándar",
        type: "line",
        data: toPairs(rec.standard),
        showSymbol: false,
        lineStyle: { color: "#6b7384", width: 1.2 },
      },
      {
        name: "Desviante",
        type: "line",
        data: toPairs(rec.deviant),
        showSymbol: false,
        lineStyle: { color: "#1f6feb", width: 1.2 },
      },
      {
        name: "Diferencia",
        type: "line",
        data: toPairs(rec.difference),
        showSymbol: false,
        lineStyle: { color: "#ff8c4d", width: 2.4 },
        // Ventanas de referencia (zona donde normalmente caen MMN y P3b). No es la
        // marca del paciente: el pico lo identifica el alumno.
        markArea: {
          silent: true,
          label: { color: "#555a66", fontSize: 10, position: "insideTop" },
          itemStyle: { color: "rgba(150,160,180,0.12)" },
          data: [
            [{ name: "MMN", xAxis: 150 }, { xAxis: 250 }],
            [{ name: "P3b", xAxis: 280 }, { xAxis: 400 }],
          ],
        },
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
