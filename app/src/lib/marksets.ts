// Sets de marcas por modalidad: el select de la cabecera cambia los botones de
// onda según el tipo de potencial. Generaliza el marcado a todo el espectro.

export interface MarkSet {
  id: string;
  label: string;
  waves: string[];
}

export const MARK_SETS: MarkSet[] = [
  { id: "abr", label: "ABR", waves: ["I", "II", "III", "IV", "V", "VI", "VII"] },
  { id: "ecochg", label: "ECochG", waves: ["CM", "SP", "AP"] },
  { id: "vemp", label: "VEMP", waves: ["P13", "N23"] },
  { id: "mlr", label: "MLR", waves: ["Na", "Pa", "Nb", "Pb"] },
  { id: "alr", label: "ALR", waves: ["P1", "N1", "P2", "N2"] },
  { id: "p300", label: "P300", waves: ["N1", "P2", "P3a", "P3b"] },
  { id: "mmn", label: "MMN", waves: ["MMN"] },
];

export function markSetWaves(id: string): string[] {
  return (MARK_SETS.find((s) => s.id === id) ?? MARK_SETS[0]).waves;
}

/** Todas las ondas de todos los sets, en orden y sin duplicados (para tablas
 * multi-modalidad: ABR + ALR + MMN en el mismo examen). */
export function allWavesOrdered(): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const s of MARK_SETS) {
    for (const w of s.waves) {
      if (!seen.has(w)) {
        seen.add(w);
        out.push(w);
      }
    }
  }
  return out;
}
