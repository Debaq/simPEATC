// Análisis MLR: latencia-intensidad de la onda Pa (estimación de umbral, útil en
// graves). El alumno marca Pa a intensidades descendentes; la Pa se mantiene
// ~25-30 ms y DESAPARECE bajo umbral → la menor intensidad con Pa estima el umbral.
//
// Norma: Pa ~28 ms (adulto, 70 dB nHL), ~32 ms en niños; ±2 DE ≈ 6 ms.

import ReactECharts from "echarts-for-react";
import type { AbrCurve, EarSide } from "../types";
import { num } from "../lib/format";

const EAR_COLOR: Record<EarSide, string> = { Right: "#d62828", Left: "#1f6feb" };
const EARS: EarSide[] = ["Right", "Left"];
const PA_SD = 6;
const INTENSIDADES = [100, 90, 80, 70, 60, 50, 40, 30, 20];

/** Latencia central normal de la Pa (ms) según intensidad y edad. */
function paCentro(intensity: number, age: number): number {
  const base = 28 + (70 - intensity) * 0.05; // sube algo al bajar la intensidad
  const ageOff = age < 13 ? Math.min((13 - age) * 0.35, 5) : 0; // niño: Pa algo más tardía
  return base + ageOff;
}

export default function MlrPaView({ curves, age }: { curves: AbrCurve[]; age: number }) {
  const xs = [...INTENSIDADES].sort((a, b) => a - b);
  const centros = xs.map((i) => [i, paCentro(i, age)]);

  const series: any[] = [
    {
      name: "Normal Pa",
      type: "custom",
      data: centros,
      silent: true,
      z: 1,
      renderItem: (params: any, api: any) => {
        if (params.dataIndex !== 0) return;
        const pts: [number, number][] = [];
        for (const [x, c] of centros) pts.push(api.coord([x, c + PA_SD]));
        for (let k = centros.length - 1; k >= 0; k--) {
          const [x, c] = centros[k];
          pts.push(api.coord([x, c - PA_SD]));
        }
        return {
          type: "polygon",
          shape: { points: pts },
          style: { fill: "rgba(150,160,180,0.16)", stroke: "rgba(150,160,180,0.45)", lineWidth: 1 },
        };
      },
    },
  ];

  const umbrales: { ear: string; thr: number }[] = [];
  for (const ear of EARS) {
    const pts = curves
      .filter((c) => c.ear === ear)
      .map((c) => {
        const m = c.marks.find((x) => x.label === "Pa");
        return m ? ([c.intensity, m.t_ms] as [number, number]) : null;
      })
      .filter((p): p is [number, number] => p !== null)
      .sort((a, b) => a[0] - b[0]);
    if (!pts.length) continue;
    const tag = ear === "Right" ? "OD" : "OI";
    umbrales.push({ ear: tag, thr: Math.min(...pts.map((p) => p[0])) });
    series.push({
      name: tag,
      type: "line",
      data: pts,
      color: EAR_COLOR[ear],
      symbol: "circle",
      symbolSize: 8,
      lineStyle: { width: 2 },
      z: 3,
    });
  }

  const option = {
    backgroundColor: "#ffffff",
    grid: { left: 48, right: 16, top: 26, bottom: 38 },
    legend: {
      top: 2,
      textStyle: { color: "#555a66", fontSize: 10 },
      itemHeight: 8,
      data: series.filter((s) => s.type === "line").map((s) => s.name),
    },
    tooltip: { trigger: "item" },
    xAxis: {
      type: "value",
      name: "Intensidad (dB nHL)",
      nameLocation: "middle",
      nameGap: 24,
      min: 0,
      max: 110,
      axisLine: { lineStyle: { color: "#b9bfca" } },
      splitLine: { lineStyle: { color: "#e8eaef" } },
    },
    yAxis: {
      type: "value",
      name: "Latencia Pa (ms)",
      nameLocation: "middle",
      nameGap: 34,
      min: 0,
      max: 50,
      axisLine: { lineStyle: { color: "#b9bfca" } },
      splitLine: { lineStyle: { color: "#e8eaef" } },
    },
    series,
  };

  return (
    <div>
      <div style={{ height: 320 }}>
        <ReactECharts option={option} style={{ height: "100%", width: "100%" }} notMerge />
      </div>
      <p className="hint" style={{ marginTop: 6 }}>
        Marca la Pa a intensidades descendentes; la menor intensidad con Pa estima el umbral.{" "}
        {umbrales.length === 0
          ? "Aún sin Pa marcadas."
          : umbrales.map((u) => `${u.ear}: umbral ≈ ${num(u.thr, 0)} dB`).join(" · ")}
      </p>
    </div>
  );
}
