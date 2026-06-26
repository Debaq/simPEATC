// Formato es-CL: coma decimal en todos los números visibles (i18n, GUI.md §2/§8).
// El backend siempre emite f64 crudos (punto decimal en JSON); la coma es-CL es
// responsabilidad del frontend al pintar.

const cache = new Map<number, Intl.NumberFormat>();

function fmt(digits: number): Intl.NumberFormat {
  let f = cache.get(digits);
  if (!f) {
    f = new Intl.NumberFormat("es-CL", {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    });
    cache.set(digits, f);
  }
  return f;
}

/** Número con `digits` decimales y coma es-CL. */
export function num(v: number, digits = 1): string {
  return fmt(digits).format(v);
}

/** Latencia en ms (2 decimales). */
export function lat(ms: number): string {
  return `${num(ms, 2)} ms`;
}

/** Amplitud en µV (2 decimales). */
export function amp(uv: number): string {
  return `${num(uv, 2)} µV`;
}

/** Impedancia en kΩ (1 decimal). */
export function ohm(k: number): string {
  return `${num(k, 1)} kΩ`;
}
