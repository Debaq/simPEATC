// Gráfico latencia-intensidad (L-I) del ABR. Dibuja las MARCAS del alumno (onda V,
// y I/III si las marca) sobre un ÁREA ACHURADA de normalidad para que el evaluador
// vea visualmente si caen dentro o fuera. La banda es una NORMA CLÍNICA FIJA (no
// tiene nada que ver con el motor): tabla por intensidad, ajustada por grupo etario,
// sexo y transductor. Eje positivo/positivo (intensidad → ; latencia ↑).

import { useState } from "react";
import ReactECharts from "echarts-for-react";
import type { AbrCurve, EarSide, SexValue, SubjectParams } from "../types";

const EAR_COLOR: Record<EarSide, string> = { Right: "#e8615f", Left: "#4aa3ff" };
const EARS: EarSide[] = ["Right", "Left"];
const WAVES = ["I", "III", "V"];

// --- Norma clínica de la onda V (latencia, ms) ---
// Referencia: mujer adulta, supraaural, 80 dB nHL = 5.6 ms; pendiente 0.3 ms/10 dB;
// semiancho (±DE) 0.4 ms. Hombre +0.2; inserto +0.9; ajuste por grupo etario.
const V80_FEMALE = 5.6;
const SLOPE_PER_DB = 0.03; // 0.3 ms / 10 dB
const SD_MS = 0.4;
const SEX_OFFSET = { Female: 0, Male: 0.2 };
const TRANSDUCER_INSERT_MS = 0.9;
const AGE_OFFSET: Record<string, number> = { lactante: 0.8, nino: 0.1, adulto: 0, mayor: 0.25 };

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

/** Latencia normal central de la onda V para una intensidad y población dadas. */
function vCentro(intensity: number, grupo: string, sexo: SexValue, insert: boolean): number {
  return (
    V80_FEMALE +
    (80 - intensity) * SLOPE_PER_DB +
    SEX_OFFSET[sexo] +
    (AGE_OFFSET[grupo] ?? 0) +
    (insert ? TRANSDUCER_INSERT_MS : 0)
  );
}

const INTENSIDADES = [100, 90, 80, 70, 60, 50, 40, 30, 20];

export default function LatencyIntensityChart({
  curves,
  subject,
  insert,
}: {
  curves: AbrCurve[];
  subject: SubjectParams;
  insert: boolean;
}) {
  const [grupo, setGrupo] = useState(() => grupoDeEdad(subject.age_years));
  const [sexo, setSexo] = useState<SexValue>(subject.sex);

  const series: any[] = [];

  // Área achurada de normalidad de la onda V (debajo de las marcas).
  const xs = [...INTENSIDADES].sort((a, b) => a - b);
  const lower = xs.map((i) => [i, vCentro(i, grupo, sexo, insert) - SD_MS]);
  series.push({
    name: "_lo",
    type: "line",
    data: lower,
    stack: "bandaV",
    lineStyle: { opacity: 0 },
    symbol: "none",
    silent: true,
    z: 1,
  });
  series.push({
    name: "Normal V (±DE)",
    type: "line",
    data: xs.map((i) => [i, SD_MS * 2]),
    stack: "bandaV",
    lineStyle: { opacity: 0 },
    areaStyle: { color: "rgba(54, 179, 126, 0.18)" },
    symbol: "none",
    silent: true,
    z: 1,
  });

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
      data: series.filter((s) => s.name !== "_lo").map((s) => s.name),
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
        <span className="hint">{insert ? "inserto" : "supraaural"}</span>
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>
        <ReactECharts option={option} style={{ height: "100%", width: "100%" }} notMerge />
      </div>
    </div>
  );
}
