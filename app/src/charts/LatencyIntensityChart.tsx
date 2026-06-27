// Gráfico latencia-intensidad (L-I) del ABR. Dibuja las MARCAS del alumno (ondas
// I, III, V) sobre ÁREAS ACHURADAS de normalidad, para que el evaluador vea si
// caen dentro o fuera. Las bandas son NORMAS CLÍNICAS FIJAS (no tienen nada que
// ver con el motor): tabla por onda e intensidad, ajustable por grupo y sexo.
//
// Norma: inserto (ER-3C), 80 dB nHL, ±2 DE — datos de 73 normo-oyentes
// (PMC9595029). Mujer adulta = referencia; hombre algo mayor. Pendiente L-I
// ~0.3 ms/10 dB (las ondas se desplazan en paralelo, interpicos constantes).

import { useState } from "react";
import ReactECharts from "echarts-for-react";
import type { AbrCurve, EarSide, SexValue, SubjectParams } from "../types";

const EAR_COLOR: Record<EarSide, string> = { Right: "#e8615f", Left: "#4aa3ff" };
const EARS: EarSide[] = ["Right", "Left"];

// Norma por onda (mujer adulta, inserto, 80 dB nHL).
interface Norma {
  c80: number; // latencia central a 80 dB
  sd2: number; // ±2 DE (semiancho de la banda)
  sexM: number; // desfase del hombre (ms)
  ageK: number; // cuánto le pega la edad (las tardías maduran más tarde)
  minDb: number; // intensidad mínima a la que la onda suele estar presente
}
// Color neutro para todas las bandas (no compite con el color de oído de las
// marcas: OD rojo / OI azul). Cada banda se identifica con su etiqueta de onda.
const BAND_FILL = "rgba(150,160,180,0.16)";
const BAND_LINE = "rgba(150,160,180,0.45)";
const NORMA: Record<string, Norma> = {
  V: { c80: 5.6, sd2: 0.42, sexM: 0.15, ageK: 1.0, minDb: 20 },
  III: { c80: 3.7, sd2: 0.34, sexM: 0.08, ageK: 0.7, minDb: 40 },
  I: { c80: 1.55, sd2: 0.34, sexM: 0.0, ageK: 0.4, minDb: 60 },
};
const WAVES = ["I", "III", "V"];
const SLOPE_PER_DB = 0.03; // 0.3 ms / 10 dB
// Desfase por grupo etario a la onda V (escalado por ondas con ageK).
const AGE_V: Record<string, number> = { lactante: 0.8, nino: 0.1, adulto: 0, mayor: 0.25 };
const INTENSIDADES = [100, 90, 80, 70, 60, 50, 40, 30, 20];

const GRUPOS: { value: string; label: string }[] = [
  { value: "lactante", label: "Lactante" },
  { value: "nino", label: "Niño" },
  { value: "adulto", label: "Adulto" },
  { value: "mayor", label: "Adulto mayor" },
];
function grupoDeEdad(age: number): string {
  if (age < 2) return "lactante";
  if (age < 15) return "nino";
  if (age < 60) return "adulto";
  return "mayor";
}

function centro(wave: string, intensity: number, grupo: string, sexo: SexValue): number {
  const n = NORMA[wave];
  return (
    n.c80 +
    (80 - intensity) * SLOPE_PER_DB +
    (sexo === "Male" ? n.sexM : 0) +
    (AGE_V[grupo] ?? 0) * n.ageK
  );
}

export default function LatencyIntensityChart({
  curves,
  subject,
}: {
  curves: AbrCurve[];
  subject: SubjectParams;
}) {
  const [grupo, setGrupo] = useState(() => grupoDeEdad(subject.age_years));
  const [sexo, setSexo] = useState<SexValue>(subject.sex);

  const series: any[] = [];

  // Bandas de normalidad (polígonos custom; el apilado de áreas de ECharts no
  // funciona en un eje X de tipo value).
  for (const w of WAVES) {
    const n = NORMA[w];
    const xs = INTENSIDADES.filter((i) => i >= n.minDb).sort((a, b) => a - b);
    const centros = xs.map((i) => [i, centro(w, i, grupo, sexo)]);
    series.push({
      name: `Normal ${w}`,
      type: "custom",
      data: centros,
      silent: true,
      z: 1,
      renderItem: (params: any, api: any) => {
        if (params.dataIndex !== 0) return;
        const pts: [number, number][] = [];
        for (const [x, c] of centros) pts.push(api.coord([x, c + n.sd2]));
        for (let k = centros.length - 1; k >= 0; k--) {
          const [x, c] = centros[k];
          pts.push(api.coord([x, c - n.sd2]));
        }
        // Etiqueta de la onda a la izquierda (intensidad alta) de la banda.
        const [lx, lc] = centros[centros.length - 1];
        const label = api.coord([lx, lc]);
        return {
          type: "group",
          children: [
            { type: "polygon", shape: { points: pts }, style: { fill: BAND_FILL, stroke: BAND_LINE, lineWidth: 1 } },
            {
              type: "text",
              x: label[0] + 6,
              y: label[1],
              style: { text: w, fill: "#aeb4c6", fontSize: 11, fontWeight: "bold", verticalAlign: "middle" },
            },
          ],
        };
      },
    });
  }

  // Marcas del alumno por oído.
  for (const ear of EARS) {
    const ec = curves.filter((c) => c.ear === ear);
    for (const w of WAVES) {
      const pts = ec
        .map((c) => {
          const m = c.marks.find((x) => x.label === w);
          return m ? [c.intensity, m.t_ms] : null;
        })
        .filter((p): p is [number, number] => p !== null)
        .sort((a, b) => a[0] - b[0]);
      if (pts.length === 0) continue;
      const tag = ear === "Right" ? "OD" : "OI";
      series.push({
        name: `${tag} ${w}`,
        type: "line",
        data: pts,
        color: EAR_COLOR[ear],
        symbol: "circle",
        symbolSize: w === "V" ? 8 : 5,
        lineStyle: { width: w === "V" ? 2.5 : 1, type: w === "V" ? "solid" : "dashed" },
        z: 3,
      });
    }
  }

  const option = {
    backgroundColor: "transparent",
    grid: { left: 48, right: 16, top: 28, bottom: 38 },
    legend: {
      top: 2,
      textStyle: { color: "#9aa0b4", fontSize: 10 },
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
      axisLine: { lineStyle: { color: "#3a3f52" } },
      splitLine: { lineStyle: { color: "#20242f" } },
    },
    yAxis: {
      type: "value",
      name: "Latencia (ms)",
      nameLocation: "middle",
      nameGap: 32,
      min: 0,
      max: 12,
      axisLine: { lineStyle: { color: "#3a3f52" } },
      splitLine: { lineStyle: { color: "#20242f" } },
    },
    series,
  };

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 4 }}>
        <span className="hint">Normalidad:</span>
        <select className="li-sel" value={grupo} onChange={(e) => setGrupo(e.target.value)}>
          {GRUPOS.map((g) => (
            <option key={g.value} value={g.value}>
              {g.label}
            </option>
          ))}
        </select>
        <select className="li-sel" value={sexo} onChange={(e) => setSexo(e.target.value as SexValue)}>
          <option value="Female">Mujer</option>
          <option value="Male">Hombre</option>
        </select>
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>
        <ReactECharts option={option} style={{ height: "100%", width: "100%" }} notMerge />
      </div>
    </div>
  );
}
