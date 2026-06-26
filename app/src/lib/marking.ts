// G2 — marcado de picos: snap al extremo local y medidas derivadas.
// MVP frontend (el alumno tiene las muestras); el plan prevé moverlo a Rust
// (`ajustar_pico`) como autoridad en una capa posterior.

import type { Waveform } from "../types";
import type { Mark } from "../types";

/**
 * Ajusta un tiempo clicado al **máximo local** de la curva en una ventana
 * (±`halfMs`). Para el ABR las ondas son deflexiones positivas; el refinamiento
 * pico-a-valle y los componentes negativos (AP/SP) llegan después.
 */
export function snapToPeak(wave: Waveform, tMs: number, halfMs = 0.6): { t_ms: number; uv: number } {
  let bestI = -1;
  let bestV = -Infinity;
  for (let i = 0; i < wave.times_ms.length; i++) {
    if (Math.abs(wave.times_ms[i] - tMs) > halfMs) continue;
    if (wave.amplitudes_uv[i] > bestV) {
      bestV = wave.amplitudes_uv[i];
      bestI = i;
    }
  }
  if (bestI < 0) return { t_ms: tMs, uv: 0 };
  return { t_ms: wave.times_ms[bestI], uv: wave.amplitudes_uv[bestI] };
}

/** Índice de la muestra más cercana a `tMs`. */
function nearestIndex(wave: Waveform, tMs: number): number {
  let best = 0;
  let bd = Infinity;
  for (let i = 0; i < wave.times_ms.length; i++) {
    const d = Math.abs(wave.times_ms[i] - tMs);
    if (d < bd) {
      bd = d;
      best = i;
    }
  }
  return best;
}

/** Amplitud (µV) de la curva en el tiempo `tMs` (muestra más cercana). */
export function ampAtTime(wave: Waveform, tMs: number): number {
  if (wave.times_ms.length === 0) return 0;
  return wave.amplitudes_uv[nearestIndex(wave, tMs)];
}

/** Valle (mínimo local) inmediatamente posterior al pico, dentro de `maxMs`. */
export function troughAfter(
  wave: Waveform,
  peakT: number,
  maxMs = 1.5
): { t_ms: number; uv: number } | null {
  let bestI = -1;
  let bestV = Infinity;
  for (let i = 0; i < wave.times_ms.length; i++) {
    const t = wave.times_ms[i];
    if (t <= peakT || t > peakT + maxMs) continue;
    if (wave.amplitudes_uv[i] < bestV) {
      bestV = wave.amplitudes_uv[i];
      bestI = i;
    }
  }
  if (bestI < 0) return null;
  return { t_ms: wave.times_ms[bestI], uv: wave.amplitudes_uv[bestI] };
}

/** Amplitud **pico-a-valle** de una onda: pico − valle siguiente (µV), o `null`. */
export function pvAmplitude(wave: Waveform, peakT: number, peakUv: number): number | null {
  const tr = troughAfter(wave, peakT);
  if (!tr) return null;
  return peakUv - tr.uv;
}

/** Inserta o **mueve** la marca de una onda (una por etiqueta). */
export function upsertMark(marks: Mark[], m: Mark): Mark[] {
  const rest = marks.filter((x) => x.label !== m.label);
  return [...rest, m].sort((a, b) => a.t_ms - b.t_ms);
}

/** Intervalo interpico `b − a` (ms), o `null` si falta alguna. */
export function interpeak(marks: Mark[], a: string, b: string): number | null {
  const pa = marks.find((m) => m.label === a);
  const pb = marks.find((m) => m.label === b);
  if (!pa || !pb) return null;
  return pb.t_ms - pa.t_ms;
}

/** Razón de amplitudes `b/a`, o `null` si falta alguna o `a≈0`. */
export function ampRatio(marks: Mark[], a: string, b: string): number | null {
  const pa = marks.find((m) => m.label === a);
  const pb = marks.find((m) => m.label === b);
  if (!pa || !pb || Math.abs(pa.uv) < 1e-9) return null;
  return pb.uv / pa.uv;
}
