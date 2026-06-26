// Autosave del borrador de sesión (GUI.md §11): SOLO estado de UI no sensible
// (modo + configuración del equipo). NUNCA la verdad del paciente, que vive en
// el backend. Persistido en localStorage del webview.

import type { Modo, SimParams } from "../types";

const KEY = "simpeatc.draft.v1";

export interface Draft {
  modo: Modo;
  equipo: SimParams;
}

/** Lee el borrador guardado, o `null` si no hay / está corrupto. */
export function loadDraft(): Draft | null {
  try {
    const s = localStorage.getItem(KEY);
    return s ? (JSON.parse(s) as Draft) : null;
  } catch {
    return null;
  }
}

/** Persiste el borrador (sin verdad). */
export function saveDraft(d: Draft): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(d));
  } catch {
    // localStorage lleno/denegado: el autosave es best-effort.
  }
}
