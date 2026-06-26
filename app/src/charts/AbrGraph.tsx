import { useEffect, useRef, useState } from "react";
import ReactECharts from "echarts-for-react";
import type { EChartsInstance } from "echarts-for-react";
import type { AbrCurve, EarSide, Mark, Waveform } from "../types";
import { num } from "../lib/format";
import { ampAtTime } from "../lib/marking";
import { MARK_SETS, markSetWaves } from "../lib/marksets";

interface Props {
  ear: EarSide;
  /** Curvas de este oído (apiladas por su `gap`). */
  curves: AbrCurve[];
  activeId: string | null;
  onActive: (id: string) => void;
  /** Arrastre del label dB → nuevo offset vertical. */
  onGap: (id: string, gap: number) => void;
  /** Marca ↓ de onda colocada en el cursor A sobre una curva. */
  onMark: (id: string, mark: Mark) => void;
  /** Captura en vivo en este oído (promedio + réplica B + época cruda). */
  liveMean?: Waveform | null;
  liveReplica?: Waveform | null;
  ghost?: Waveform | null;
  /** Ventana de adquisición (ms): define el eje temporal del gráfico. */
  preMs?: number;
  postMs?: number;
  /** Set de marcas activo (modalidad) y su cambio. */
  markSetId: string;
  onMarkSet: (id: string) => void;
}

const EAR_COLOR: Record<EarSide, { active: string; dim: string }> = {
  Right: { active: "#d62828", dim: "#e89a9a" },
  Left: { active: "#1f6feb", dim: "#9bbcf0" },
};

/** Paso de grid "bonito" (1/2/5/10·×10ⁿ) para ~`target` divisiones en `range`. */
function niceStep(range: number, target: number): number {
  if (range <= 0) return 1;
  const raw = range / target;
  const pow = Math.pow(10, Math.floor(Math.log10(raw)));
  const norm = raw / pow;
  const step = norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10;
  return step * pow;
}

/**
 * Gráfico clínico ABR (estilo legacy): fondo blanco, apilado manual por arrastre
 * del label dB, cursores verticales A/A′ que miden amplitud y latencia, marcas ↓
 * de onda sobre la curva activa, escala Y ajustable. Eje Y sin valores absolutos.
 */
export default function AbrGraph({
  ear,
  curves,
  activeId,
  onActive,
  onGap,
  onMark,
  liveMean,
  liveReplica,
  ghost,
  preMs = 1,
  postMs = 10,
  markSetId,
  onMarkSet,
}: Props) {
  const T_MIN = -preMs;
  const T_MAX = postMs;
  const waves = markSetWaves(markSetId);
  const boxRef = useRef<HTMLDivElement>(null);
  const instRef = useRef<EChartsInstance | null>(null);
  const [ready, setReady] = useState(false);
  const [, setTick] = useState(0);
  const [yScale, setYScale] = useState(6); // rango total µV (−3..3)
  const [cur, setCur] = useState({ a: 2, b: 6 });
  const drag = useRef<null | { kind: "gap"; id: string } | { kind: "cur"; which: "a" | "b" }>(null);
  const col = EAR_COLOR[ear];

  useEffect(() => {
    const el = boxRef.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(() => setTick((t) => t + 1));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Selección de curva activa por clic en su serie.
  useEffect(() => {
    const inst = instRef.current;
    if (!ready || !inst) return;
    const zr = inst.getZr();
    const handler = (e: { offsetX: number; offsetY: number }) => {
      // Curva más cercana al clic (en píxeles).
      const pt = [e.offsetX, e.offsetY];
      if (!inst.containPixel("grid", pt)) return;
      const [t, v] = inst.convertFromPixel("grid", pt) as [number, number];
      let best: string | null = null;
      let bd = Infinity;
      for (const c of curves) {
        const y = ampAtTime(c.wave, t) + c.gap;
        const d = Math.abs(y - v);
        if (d < bd) {
          bd = d;
          best = c.id;
        }
      }
      if (best) onActive(best);
    };
    zr.on("click", handler);
    return () => zr.off("click", handler);
  }, [ready, curves, onActive]);

  const series: object[] = [];
  if (ghost) {
    series.push({
      type: "line",
      data: ghost.times_ms.map((t, i) => [t, ghost.amplitudes_uv[i]]),
      showSymbol: false,
      silent: true,
      lineStyle: { color: "#b8bcc8", width: 0.8 },
      z: 1,
    });
  }
  if (liveReplica) {
    series.push({
      type: "line",
      data: liveReplica.times_ms.map((t, i) => [t, liveReplica.amplitudes_uv[i]]),
      showSymbol: false,
      silent: true,
      lineStyle: { color: col.active, width: 1.1, type: "dashed", opacity: 0.7 },
      z: 2,
    });
  }
  if (liveMean) {
    series.push({
      type: "line",
      data: liveMean.times_ms.map((t, i) => [t, liveMean.amplitudes_uv[i]]),
      showSymbol: false,
      silent: true,
      lineStyle: { color: col.active, width: 1.8 },
      z: 3,
    });
  }
  for (const c of curves) {
    const active = c.id === activeId;
    // Réplica B (segundo buffer): línea punteada del mismo color.
    if (c.replica) {
      series.push({
        type: "line",
        data: c.replica.times_ms.map((t, i) => [t, c.replica!.amplitudes_uv[i] + c.gap]),
        showSymbol: false,
        silent: true,
        lineStyle: {
          color: active ? col.active : col.dim,
          width: 0.9,
          type: "dashed",
          opacity: 0.7,
        },
        z: active ? 4 : 1,
      });
    }
    series.push({
      type: "line",
      data: c.wave.times_ms.map((t, i) => [t, c.wave.amplitudes_uv[i] + c.gap]),
      showSymbol: false,
      silent: true,
      lineStyle: { color: active ? col.active : col.dim, width: active ? 1.8 : 1.1 },
      z: active ? 5 : 2,
    });
  }

  const xStep = niceStep(T_MAX - T_MIN, 12);
  const yStep = niceStep(yScale, 6);
  const option = {
    backgroundColor: "#ffffff",
    animation: false,
    grid: { left: 8, right: 34, top: 8, bottom: 24 },
    xAxis: {
      type: "value",
      min: T_MIN,
      max: T_MAX,
      interval: xStep,
      axisLine: { lineStyle: { color: "#888" } },
      axisLabel: {
        color: "#555",
        fontSize: 9,
        formatter: (v: number) => num(v, v % 1 === 0 ? 0 : 1),
      },
      splitLine: { lineStyle: { color: "#e6e6e6" } },
    },
    yAxis: {
      type: "value",
      min: -yScale / 2,
      max: yScale / 2,
      interval: yStep,
      axisLabel: { show: false },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: "#eee" } },
    },
    series,
  };

  function onReady(inst: EChartsInstance) {
    instRef.current = inst;
    setReady(true);
    setTick((t) => t + 1);
  }

  const inst = instRef.current;
  const toPx = (t: number, uv: number): [number, number] | null =>
    inst ? (inst.convertToPixel("grid", [t, uv]) as [number, number]) : null;

  function pointer(clientX: number, clientY: number): { t: number; v: number } | null {
    const box = boxRef.current;
    if (!inst || !box) return null;
    const r = box.getBoundingClientRect();
    const res = inst.convertFromPixel("grid", [clientX - r.left, clientY - r.top]) as
      | [number, number]
      | undefined;
    return res ? { t: res[0], v: res[1] } : null;
  }

  function onMove(e: React.PointerEvent) {
    const d = drag.current;
    if (!d) return;
    const p = pointer(e.clientX, e.clientY);
    if (!p) return;
    if (d.kind === "gap") {
      onGap(d.id, p.v);
    } else {
      const t = Math.max(T_MIN, Math.min(T_MAX, p.t));
      setCur((c) => ({ ...c, [d.which]: t }));
    }
  }
  function endDrag() {
    drag.current = null;
  }

  // Medición A/A′ sobre la curva activa.
  const active = curves.find((c) => c.id === activeId) ?? null;
  const ampA = active ? ampAtTime(active.wave, cur.a) : 0;
  const ampB = active ? ampAtTime(active.wave, cur.b) : 0;
  const ampAB = Math.abs(ampA - ampB);
  const latAB = Math.abs(cur.a - cur.b);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {/* Cabecera compacta: oído + medición + escala */}
      <div className="abr-head">
        <span className="abr-ear" style={{ color: col.active }}>
          {ear === "Right" ? "OD" : "OI"}
        </span>
        <span className="abr-meas">
          A-A′ amp {num(ampAB, 2)} µV · lat {num(latAB, 2)} ms
        </span>
        <span className="abr-tools">
          <select
            className="mini abr-set"
            value={markSetId}
            onChange={(e) => onMarkSet(e.target.value)}
            title="Set de marcas"
          >
            {MARK_SETS.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
          {waves.map((w) => {
            const on = !!active && active.marks.some((m) => m.label === w);
            return (
              <button
                key={w}
                className={`mini ${on ? "on" : ""}`}
                disabled={!active}
                title={`Marcar ${w} en cursor A`}
                onClick={() =>
                  active &&
                  onMark(active.id, { label: w, t_ms: cur.a, uv: ampAtTime(active.wave, cur.a) })
                }
              >
                {w}
              </button>
            );
          })}
          <span className="abr-sep" />
          <button className="mini" title="menos amplitud" onClick={() => setYScale((s) => Math.min(s * 2, 48))}>
            −
          </button>
          <button className="mini" title="más amplitud" onClick={() => setYScale((s) => Math.max(s / 2, 1.5))}>
            +
          </button>
        </span>
      </div>

      <div ref={boxRef} className="abr-plot" onPointerMove={onMove} onPointerUp={endDrag}>
        <ReactECharts
          option={option}
          style={{ height: "100%", width: "100%" }}
          notMerge
          onChartReady={onReady}
        />

        {/* Cursores verticales A / A′ */}
        {inst &&
          (["a", "b"] as const).map((w) => {
            const x = toPx(cur[w], 0)?.[0];
            if (x == null) return null;
            return (
              <div key={w} className="abr-cursor" style={{ left: x }}>
                <div
                  className="abr-cursor-grip"
                  onPointerDown={(e) => {
                    e.stopPropagation();
                    (e.target as HTMLElement).setPointerCapture(e.pointerId);
                    drag.current = { kind: "cur", which: w };
                  }}
                >
                  {w === "a" ? "A" : "A′"}
                </div>
              </div>
            );
          })}

        {/* Etiquetas dB arrastrables (apilado manual) */}
        {inst &&
          curves.map((c) => {
            const px = toPx(T_MAX - 0.4, c.gap);
            if (!px) return null;
            const active = c.id === activeId;
            return (
              <div
                key={c.id}
                className={`abr-dblabel ${active ? "active" : ""}`}
                style={{ left: px[0], top: px[1], borderColor: active ? col.active : col.dim }}
                onPointerDown={(e) => {
                  e.stopPropagation();
                  (e.target as HTMLElement).setPointerCapture(e.pointerId);
                  drag.current = { kind: "gap", id: c.id };
                  onActive(c.id);
                }}
              >
                {num(c.intensity, 0)} dB
              </div>
            );
          })}

        {/* Marcas ↓ de todas las curvas */}
        {inst &&
          curves.flatMap((c) =>
            c.marks.map((m) => {
              const px = toPx(m.t_ms, m.uv + c.gap);
              if (!px) return null;
              return (
                <div
                  key={`${c.id}_${m.label}`}
                  className="abr-mark"
                  style={{ left: px[0], top: px[1] }}
                >
                  ↓<span className="abr-mark-lbl">{m.label}</span>
                </div>
              );
            })
          )}
      </div>
    </div>
  );
}
