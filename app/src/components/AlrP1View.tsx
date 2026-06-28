// Análisis ALR/CAEP: latencia de P1 vs EDAD (maduración cortical, biomarcador de
// Sharma). La P1 decae de ~300 ms al nacer a ~60 ms en el adulto; por encima de la
// banda normal sugiere retraso de maduración cortical (privación auditiva).
//
// Norma: ~300 ms (0 a), 7-8 a ~97, 11-12 a ~77, adulto ~60. Ajuste exponencial.

import ReactECharts from "echarts-for-react";
import type { AbrCurve, EarSide } from "../types";
import { num } from "../lib/format";

const EAR_COLOR: Record<EarSide, string> = { Right: "#d62828", Left: "#1f6feb" };

/** Latencia media normal de la P1 (ms) según la edad (años). */
function p1Media(age: number): number {
  return 60 + 240 * Math.exp(-age / 4.3);
}
/** Semiancho de la banda normal (más ancha en el niño pequeño). */
function p1Sd(age: number): number {
  return Math.max(15, 0.18 * p1Media(age));
}

export default function AlrP1View({ curves, age }: { curves: AbrCurve[]; age: number }) {
  // P1 marcada por el alumno en la curva ALR.
  const puntos = curves
    .map((c) => {
      const m = c.marks.find((d) => d.label === "P1");
      return m ? { ear: c.ear, lat: m.t_ms } : null;
    })
    .filter((x): x is { ear: EarSide; lat: number } => x !== null);

  const edades = Array.from({ length: 19 }, (_, i) => i); // 0..18
  const centros = edades.map((a) => [a, p1Media(a)]);

  const series: any[] = [
    {
      name: "Normal P1",
      type: "custom",
      data: centros,
      silent: true,
      z: 1,
      renderItem: (params: any, api: any) => {
        if (params.dataIndex !== 0) return;
        const pts: [number, number][] = [];
        for (const a of edades) pts.push(api.coord([a, p1Media(a) + p1Sd(a)]));
        for (let k = edades.length - 1; k >= 0; k--) {
          const a = edades[k];
          pts.push(api.coord([a, p1Media(a) - p1Sd(a)]));
        }
        return {
          type: "polygon",
          shape: { points: pts },
          style: { fill: "rgba(150,160,180,0.16)", stroke: "rgba(150,160,180,0.45)", lineWidth: 1 },
        };
      },
    },
    { name: "Media", type: "line", data: centros, lineStyle: { color: "#555a66", width: 1, type: "dashed" }, symbol: "none", silent: true, z: 2 },
  ];

  for (const ear of ["Right", "Left"] as EarSide[]) {
    const ps = puntos.filter((p) => p.ear === ear);
    if (!ps.length) continue;
    series.push({
      name: ear === "Right" ? "OD" : "OI",
      type: "scatter",
      data: ps.map((p) => [age, p.lat]),
      color: EAR_COLOR[ear],
      symbolSize: 12,
      z: 3,
    });
  }

  const option = {
    backgroundColor: "#ffffff",
    grid: { left: 52, right: 16, top: 26, bottom: 38 },
    legend: {
      top: 2,
      textStyle: { color: "#555a66", fontSize: 10 },
      itemHeight: 8,
      data: series.filter((s) => s.type === "scatter").map((s) => s.name),
    },
    tooltip: { trigger: "item" },
    xAxis: {
      type: "value",
      name: "Edad (años)",
      nameLocation: "middle",
      nameGap: 24,
      min: 0,
      max: 18,
      axisLine: { lineStyle: { color: "#b9bfca" } },
      splitLine: { lineStyle: { color: "#e8eaef" } },
    },
    yAxis: {
      type: "value",
      name: "Latencia P1 (ms)",
      nameLocation: "middle",
      nameGap: 38,
      min: 0,
      max: 320,
      axisLine: { lineStyle: { color: "#b9bfca" } },
      splitLine: { lineStyle: { color: "#e8eaef" } },
    },
    series,
  };

  const media = p1Media(age);
  const limite = media + p1Sd(age);
  const vers = puntos.map((p) => ({
    ear: p.ear === "Right" ? "OD" : "OI",
    lat: p.lat,
    tardia: p.lat > limite,
  }));

  return (
    <div>
      <div style={{ height: 320 }}>
        <ReactECharts option={option} style={{ height: "100%", width: "100%" }} notMerge />
      </div>
      <p className="hint" style={{ marginTop: 6 }}>
        A los {num(age, 0)} años: P1 normal {num(media, 0)} ms · límite {num(limite, 0)} ms.{" "}
        {vers.length === 0
          ? "Marca la P1 en la curva ALR (botón P1) para ubicarla aquí."
          : vers
              .map((v) => `${v.ear}: ${num(v.lat, 0)} ms ${v.tardia ? "⚠ retrasada (maduración)" : "✓ normal"}`)
              .join(" · ")}
      </p>
    </div>
  );
}
