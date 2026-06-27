// Panel oddball (P300/MMN) de UNA captura, con marcado y medición: clic en la
// onda diferencia mueve el cursor (lee latencia y amplitud); los botones MMN/P3a/
// P3b colocan la marca en el cursor. Ventanas de referencia sombreadas.

import { useRef, useState } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsInstance } from "echarts-for-react";
import type { Mark, OddballCap, Waveform } from "../types";
import { ampAtTime } from "../lib/marking";
import { num } from "../lib/format";

const MARKBTNS = ["MMN", "P3a", "P3b"];
function toPairs(w: Waveform): [number, number][] {
  return w.times_ms.map((t, i) => [t, w.amplitudes_uv[i]]);
}

export default function OddballPanel({
  cap,
  onMark,
}: {
  cap: OddballCap;
  onMark: (m: Mark) => void;
}) {
  const [cursor, setCursor] = useState<number | null>(null);
  const instRef = useRef<EChartsInstance | null>(null);
  const tag = cap.ear === "Right" ? "OD" : "OI";
  const color = cap.ear === "Right" ? "#d62828" : "#1f6feb";
  const ampAt = cursor != null ? ampAtTime(cap.rec.difference, cursor) : 0;

  const option = {
    backgroundColor: "#ffffff",
    animation: false,
    grid: { left: 50, right: 16, top: 30, bottom: 34 },
    legend: { top: 2, textStyle: { color: "#555a66", fontSize: 10 }, data: ["Estándar", "Desviante", "Diferencia"] },
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "value",
      name: "Tiempo (ms)",
      nameLocation: "middle",
      nameGap: 22,
      axisLine: { lineStyle: { color: "#b9bfca" } },
      axisLabel: { color: "#555", fontSize: 9 },
      splitLine: { lineStyle: { color: "#e8eaef" } },
    },
    yAxis: {
      type: "value",
      name: "µV",
      nameGap: 28,
      axisLine: { lineStyle: { color: "#b9bfca" } },
      axisLabel: { color: "#555", fontSize: 9 },
      splitLine: { lineStyle: { color: "#e8eaef" } },
    },
    series: [
      { name: "Estándar", type: "line", data: toPairs(cap.rec.standard), showSymbol: false, lineStyle: { color: "#6b7384", width: 1.1 }, silent: true },
      { name: "Desviante", type: "line", data: toPairs(cap.rec.deviant), showSymbol: false, lineStyle: { color: "#1f6feb", width: 1.1 }, silent: true },
      {
        name: "Diferencia",
        type: "line",
        data: toPairs(cap.rec.difference),
        showSymbol: false,
        lineStyle: { color: "#ff8c4d", width: 2.4 },
        markArea: {
          silent: true,
          label: { color: "#9aa7b8", fontSize: 10, position: "insideTop" },
          itemStyle: { color: "rgba(150,160,180,0.12)" },
          data: [
            [{ name: "MMN", xAxis: 150 }, { xAxis: 250 }],
            [{ name: "P3b", xAxis: 280 }, { xAxis: 400 }],
          ],
        },
        markLine:
          cursor != null
            ? { silent: true, symbol: "none", lineStyle: { color: "#333", type: "solid" }, data: [{ xAxis: cursor }] }
            : undefined,
        markPoint: {
          symbol: "pin",
          symbolSize: 26,
          itemStyle: { color: "#36b37e" },
          label: { color: "#fff", fontSize: 9 },
          data: cap.marks.map((m) => ({ coord: [m.t_ms, m.uv], value: m.label })),
        },
      },
    ],
  };

  function onReady(inst: EChartsInstance) {
    instRef.current = inst;
    const zr = inst.getZr();
    zr.on("click", (e: { offsetX: number; offsetY: number }) => {
      const pt = [e.offsetX, e.offsetY];
      if (!inst.containPixel("grid", pt)) return;
      const [t] = inst.convertFromPixel("grid", pt) as [number, number];
      setCursor(t);
    });
  }

  return (
    <div className="abr-panel">
      <div className="abr-head">
        <span className="abr-ear" style={{ color }}>{tag}</span>
        <span className="abr-meas">
          {cursor != null
            ? `cursor ${num(cursor, 0)} ms · ${num(ampAt, 2)} µV`
            : "clic en la onda diferencia para medir"}
        </span>
        <span className="abr-tools">
          {MARKBTNS.map((w) => (
            <button
              key={w}
              className={`mini ${cap.marks.some((m) => m.label === w) ? "on" : ""}`}
              disabled={cursor == null}
              title={`Marcar ${w} en el cursor`}
              onClick={() => cursor != null && onMark({ label: w, t_ms: cursor, uv: ampAt })}
            >
              {w}
            </button>
          ))}
        </span>
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>
        <ReactECharts option={option} style={{ height: "100%", width: "100%" }} notMerge onChartReady={onReady} />
      </div>
    </div>
  );
}
