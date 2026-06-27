// Análisis P300: latencia de la P3b frente a la EDAD, sobre la banda de
// normalidad por edad. Es el símil del L-I para los cognitivos: la P3b se alarga
// con la edad (~+1 ms/año, más rápido tras los 45); por encima de la banda
// (media + 2 DE) sugiere deterioro cognitivo / demencia.
//
// Norma (auditiva, adultos): joven ~305 ms, +2 DE ≈ 362; ancianos 60-64 ~337,
// 65-69 ~352, 70+ ~370. Fuentes en el chat.

import ReactECharts from "echarts-for-react";
import type { EarSide, OddballCap } from "../types";
import { num } from "../lib/format";

const EAR_COLOR: Record<EarSide, string> = { Right: "#e8615f", Left: "#4aa3ff" };
const SD2 = 58; // ±2 DE (ms)

/** Latencia media normal de la P3b según la edad (años). */
function p3bMedia(age: number): number {
  if (age <= 45) return 300 + Math.max(0, age - 25) * 0.6; // 25→300, 45→312
  return 312 + (age - 45) * 2.2; // 60→345, 70→367
}

export default function P300View({ caps, age }: { caps: OddballCap[]; age: number }) {
  // P3b medida por captura (de la onda diferencia detectada).
  const puntos = caps
    .map((c) => {
      const p = c.rec.detected.find((d) => d.label === "P3b");
      return p ? { ear: c.ear, lat: p.latency_ms } : null;
    })
    .filter((x): x is { ear: EarSide; lat: number } => x !== null);

  // Banda de normalidad (media ± 2 DE) a lo largo de la edad.
  const edades = Array.from({ length: 17 }, (_, i) => 10 + i * 5); // 10..90
  const centros = edades.map((a) => [a, p3bMedia(a)]);

  const series: any[] = [
    {
      name: "Normal P3b",
      type: "custom",
      data: centros,
      silent: true,
      z: 1,
      renderItem: (params: any, api: any) => {
        if (params.dataIndex !== 0) return;
        const pts: [number, number][] = [];
        for (const [x, c] of centros) pts.push(api.coord([x, c + SD2]));
        for (let k = centros.length - 1; k >= 0; k--) {
          const [x, c] = centros[k];
          pts.push(api.coord([x, c - SD2]));
        }
        return {
          type: "polygon",
          shape: { points: pts },
          style: { fill: "rgba(150,160,180,0.16)", stroke: "rgba(150,160,180,0.45)", lineWidth: 1 },
        };
      },
    },
    // Línea de la media.
    {
      name: "Media",
      type: "line",
      data: centros,
      lineStyle: { color: "#555a66", width: 1, type: "dashed" },
      symbol: "none",
      silent: true,
      z: 2,
    },
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
      max: 90,
      axisLine: { lineStyle: { color: "#b9bfca" } },
      splitLine: { lineStyle: { color: "#e8eaef" } },
    },
    yAxis: {
      type: "value",
      name: "Latencia P3b (ms)",
      nameLocation: "middle",
      nameGap: 38,
      min: 250,
      max: 500,
      axisLine: { lineStyle: { color: "#b9bfca" } },
      splitLine: { lineStyle: { color: "#e8eaef" } },
    },
    series,
  };

  const media = p3bMedia(age);
  const limite = media + SD2;
  const veredictos = puntos.map((p) => ({
    ear: p.ear === "Right" ? "OD" : "OI",
    lat: p.lat,
    prolongada: p.lat > limite,
  }));

  return (
    <div>
      <div style={{ height: 320 }}>
        <ReactECharts option={option} style={{ height: "100%", width: "100%" }} notMerge />
      </div>
      <p className="hint" style={{ marginTop: 6 }}>
        A los {num(age, 0)} años: media {num(media, 0)} ms · límite normal {num(limite, 0)} ms (media + 2 DE).{" "}
        {veredictos.length === 0
          ? "Captura P300 (con atención) para medir la P3b."
          : veredictos
              .map((v) => `${v.ear}: ${num(v.lat, 0)} ms ${v.prolongada ? "⚠ prolongada" : "✓ normal"}`)
              .join(" · ")}
      </p>
    </div>
  );
}
