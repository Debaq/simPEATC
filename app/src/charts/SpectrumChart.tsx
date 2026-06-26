import ReactECharts from "echarts-for-react";
import type { AssrResult } from "../types";

// Umbral del F-test (F_CRIT = 4.0 en el motor) expresado en dB SNR.
const SNR_THRESHOLD_DB = 10 * Math.log10(4.0);

/** Energia detectada en la frecuencia de modulacion frente al umbral del F-test. */
export default function SpectrumChart({ res }: { res: AssrResult }) {
  const color = res.detected ? "#36b37e" : "#e07070";
  const option = {
    backgroundColor: "transparent",
    grid: { left: 56, right: 18, top: 30, bottom: 40 },
    tooltip: {
      trigger: "axis",
      valueFormatter: (v: number) => (typeof v === "number" ? `${v.toFixed(2)} dB` : v),
    },
    xAxis: {
      type: "category",
      data: [`${res.mod_freq_hz.toFixed(0)} Hz (f_mod)`],
      axisLine: { lineStyle: { color: "#3a3f52" } },
    },
    yAxis: {
      type: "value",
      name: "SNR (dB)",
      nameLocation: "middle",
      nameGap: 40,
      axisLine: { lineStyle: { color: "#3a3f52" } },
      splitLine: { lineStyle: { color: "#20242f" } },
    },
    series: [
      {
        type: "bar",
        barWidth: "38%",
        data: [res.snr_db],
        itemStyle: { color, borderRadius: [4, 4, 0, 0] },
        markLine: {
          symbol: "none",
          label: {
            formatter: `umbral ${SNR_THRESHOLD_DB.toFixed(1)} dB`,
            color: "#ffd23a",
            fontSize: 11,
          },
          lineStyle: { color: "#ffd23a", type: "dashed" },
          data: [{ yAxis: SNR_THRESHOLD_DB }],
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
