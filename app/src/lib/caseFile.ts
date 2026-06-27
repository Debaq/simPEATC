// Importar/exportar casos clínicos como JSON estructurado (formato CaseDef).
//
// El export usa un Blob + enlace de descarga; el import lee un archivo con
// FileReader. Sin plugins de Tauri: funciona en el webview. El JSON exportado es
// el mismo shape que `crates/aep-core/data/cases.json` (un caso suelto).

import type { CaseDef, CaseLesionDef, FreqProfile, LesionSite } from "../types";

const SITES: LesionSite[] = [
  "Conductive",
  "Cochlear",
  "Retrocochlear",
  "Neural",
  "Central",
  "CentralConduction",
  "Brainstem",
  "Cortical",
  "Cognitive",
];
const PROFILES: FreqProfile[] = ["Flat", "HighFrequency", "LowFrequency", "CookieBite"];

/** Patología en blanco para arrancar el editor. */
export function blankCase(): CaseDef {
  return {
    id: "",
    name: "",
    description: "",
    lesions: [],
  };
}

export function blankLesion(): CaseLesionDef {
  return { site: "Cochlear", severity_db: 40, profile: "Flat" };
}

/** Slug estable a partir del nombre (para el id del caso). */
export function slugify(s: string): string {
  return s
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 48);
}

function pick<T extends string>(v: unknown, allowed: T[], fallback: T): T {
  return typeof v === "string" && (allowed as string[]).includes(v) ? (v as T) : fallback;
}

function numOr(v: unknown, fallback: number): number {
  return typeof v === "number" && Number.isFinite(v) ? v : fallback;
}

/** Normaliza un objeto arbitrario (de un JSON importado) a un CaseDef válido.
 * Acepta tanto un caso suelto como un catálogo `{ cases: [...] }` (toma el 1.º). */
export function parseCaseJson(text: string): CaseDef {
  let raw: any;
  try {
    raw = JSON.parse(text);
  } catch {
    throw new Error("JSON inválido");
  }
  if (raw && Array.isArray(raw.cases)) raw = raw.cases[0];
  if (!raw || typeof raw !== "object") throw new Error("el archivo no contiene un caso");

  const lesions: CaseLesionDef[] = Array.isArray(raw.lesions)
    ? raw.lesions.map((l: any) => ({
        site: pick(l?.site, SITES, "Cochlear"),
        severity_db: numOr(l?.severity_db, 40),
        profile: pick(l?.profile, PROFILES, "Flat"),
      }))
    : [];

  return {
    id: typeof raw.id === "string" ? raw.id : slugify(raw.name ?? "") || "caso_importado",
    name: typeof raw.name === "string" ? raw.name : "Caso importado",
    description: typeof raw.description === "string" ? raw.description : "",
    lesions,
  };
}

/** Descarga el caso como archivo .json. */
export function downloadCase(def: CaseDef): void {
  const id = def.id || slugify(def.name) || "caso";
  const blob = new Blob([JSON.stringify(def, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `caso_${id}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

/** Abre el selector de archivos y devuelve el CaseDef leído (o null si se cancela). */
export function importCaseFromFile(): Promise<CaseDef | null> {
  return new Promise((resolve, reject) => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/json,.json";
    input.onchange = () => {
      const file = input.files?.[0];
      if (!file) return resolve(null);
      const reader = new FileReader();
      reader.onload = () => {
        try {
          resolve(parseCaseJson(String(reader.result)));
        } catch (e) {
          reject(e);
        }
      };
      reader.onerror = () => reject(new Error("no se pudo leer el archivo"));
      reader.readAsText(file);
    };
    input.click();
  });
}
