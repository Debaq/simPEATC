import ReactECharts from "echarts-for-react";
import type { EarSide, Waveform } from "../types";

/**
 * Monitor EEG: muestra la señal cruda en vivo (proxy: la época cruda de la
 * captura). TODO: el motor debe emitir el EEG continuo (ver memoria
 * pendientes-motor-monitores).
 */
export default function EegMonitor({ wave, ear }: { wave: Waveform | null; ear: EarSide }) {
  const color = ear === "Right" ? "#d62828" : "#1f6feb";
  const data = wave ? wave.times_ms.map((t, i) => [t, wave.amplitudes_uv[i]]) : [];

  const option = {
    backgroundColor: "#ffffff",
    animation: false,
    grid: { left: 6, right: 8, top: 6, bottom: 6 },
    xAxis: {
      type: "value",
      show: false,
      min: wave?.times_ms[0] ?? 0,
      max: wave?.times_ms[wave.times_ms.length - 1] ?? 1,
    },
    yAxis: { type: "value", scale: true, show: false },
    series: [
      {
        type: "line",
        data,
        showSymbol: false,
        silent: true,
        lineStyle: { color, width: 0.9 },
      },
    ],
  };

  return (
    <div className="eeg-card">
      <div className="eeg-head">EEG · {ear === "Right" ? "OD" : "OI"}</div>
      <div style={{ flex: 1, minHeight: 0 }}>
        {data.length ? (
          <ReactECharts option={option} style={{ height: "100%", width: "100%" }} notMerge />
        ) : (
          <div className="eeg-idle">sin captura</div>
        )}
      </div>
    </div>
  );
}
