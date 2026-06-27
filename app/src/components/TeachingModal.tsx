// Área docente (modal): pestañas Catálogo / Editor.
//
// Catálogo: buscador + filtro por modalidad, y DOS SLOTS (OD/OI). Se arrastra
// (o se asignan con botones →OD/→OI) las tarjetas de caso a los slots para montar
// un paciente, posiblemente binaural con patologías asimétricas. Slot vacío = oído
// normal por defecto.

import { useMemo, useState } from "react";
import type {
  CaseDef,
  CaseInfo,
  EarSide,
  Modo,
  SubjectParams,
  VerdadDto,
  VistaCiegaCaso,
} from "../types";
import { ChipGroup } from "./widgets";
import { importCaseFromFile } from "../lib/caseFile";
import CaseEditor from "./CaseEditor";
import SessionVarsPanel from "./SessionVarsPanel";
import Modal from "./Modal";

const MODO_OPTS: { value: Modo; label: string }[] = [
  { value: "practica", label: "Práctica" },
  { value: "evaluacion", label: "Evaluación" },
  { value: "osce", label: "OSCE" },
];

// Filtro por tipo de patología (se compara contra el resumen del paciente, que
// usa los nombres de sitio en inglés del motor).
const PATH_FILTER: { value: string; label: string }[] = [
  { value: "all", label: "Todas" },
  { value: "Normal", label: "Normal" },
  { value: "Conductive", label: "Conductiva" },
  { value: "Cochlear", label: "Coclear" },
  { value: "Retrocochlear", label: "Retrococlear" },
  { value: "Neural", label: "Neural" },
  { value: "CentralConduction", label: "Conducción central" },
  { value: "Brainstem", label: "Tronco" },
  { value: "Cortical", label: "Cortical" },
  { value: "Cognitive", label: "Cognitiva" },
];

const EARS: EarSide[] = ["Right", "Left"];

type Tab = "catalogo" | "editor";

interface Props {
  modo: Modo;
  setModo: (m: Modo) => void;
  cases: CaseInfo[];
  blindByEar: Record<EarSide, VistaCiegaCaso | null>;
  verdades: VerdadDto[];
  sessionVars: SubjectParams;
  onSessionVars: (s: SubjectParams) => void;
  editDef: CaseDef;
  onEditDef: (d: CaseDef) => void;
  onLoadDef: (d: CaseDef, ear: EarSide) => Promise<void>;
  onFetchDef: (id: string) => Promise<CaseDef | null>;
  onRemoveEar: (ear: EarSide) => Promise<void> | void;
  onClose: () => void;
}

export default function TeachingModal(props: Props) {
  const { modo, setModo, cases, blindByEar, verdades, editDef, onEditDef } = props;
  const [tab, setTab] = useState<Tab>("catalogo");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [pathFilter, setPathFilter] = useState<string>("all");
  const [dragEar, setDragEar] = useState<EarSide | null>(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return cases.filter((c) => {
      if (pathFilter !== "all") {
        const ok =
          pathFilter === "Normal" ? c.summary === "Normal" : c.summary.includes(pathFilter);
        if (!ok) return false;
      }
      if (!q) return true;
      return (
        c.name.toLowerCase().includes(q) ||
        c.description.toLowerCase().includes(q) ||
        c.id.toLowerCase().includes(q)
      );
    });
  }, [cases, query, pathFilter]);

  // Coloca un paciente del catálogo en el slot de un oído.
  async function placeCase(id: string, ear: EarSide) {
    setMsg(null);
    setLoading(true);
    try {
      const def = await props.onFetchDef(id);
      if (def) await props.onLoadDef(def, ear);
    } catch (e) {
      setMsg(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function editCatalog(id: string) {
    setMsg(null);
    const def = await props.onFetchDef(id).catch((e) => {
      setMsg(String(e));
      return null;
    });
    if (def) {
      onEditDef(def);
      setTab("editor");
    }
  }

  async function loadDef(def: CaseDef, ear: EarSide) {
    setLoading(true);
    setMsg(null);
    try {
      await props.onLoadDef(def, ear);
    } catch (e) {
      setMsg(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function doImport() {
    setMsg(null);
    try {
      const def = await importCaseFromFile();
      if (def) {
        onEditDef(def);
        setTab("editor");
        setMsg(`Importado: ${def.name}`);
      }
    } catch (e) {
      setMsg(`Error al importar: ${e}`);
    }
  }

  const verdadFor = (ear: EarSide) =>
    verdades.find((v) => (v.ear === "OD" ? "Right" : "Left") === ear);

  return (
    <Modal title="Área docente" onClose={props.onClose} width={820}>
      {/* Modo de sesión */}
      <div className="modal-row">
        <span className="section-title" style={{ margin: 0 }}>
          Modo
        </span>
        <ChipGroup<Modo> value={modo} options={MODO_OPTS} onChange={setModo} />
      </div>

      {/* Variables de sesión (las define el docente: el paciente/escenario) */}
      <SessionVarsPanel value={props.sessionVars} onChange={props.onSessionVars} />

      {/* Tabs */}
      <div className="tabbar">
        <button
          className={`tab ${tab === "catalogo" ? "active" : ""}`}
          onClick={() => setTab("catalogo")}
        >
          Catálogo
        </button>
        <button
          className={`tab ${tab === "editor" ? "active" : ""}`}
          onClick={() => setTab("editor")}
        >
          Editor
        </button>
        <div style={{ flex: 1 }} />
        <button className="mini" onClick={doImport}>
          ⤒ Importar JSON
        </button>
      </div>

      {msg && (
        <p className="hint" style={{ marginTop: 6 }}>
          {msg}
        </p>
      )}

      {tab === "catalogo" ? (
        <>
          {/* Slots OD / OI */}
          <div className="slot-row">
            {EARS.map((ear) => {
              const b = blindByEar[ear];
              const tag = ear === "Right" ? "OD" : "OI";
              const v = verdadFor(ear);
              return (
                <div
                  key={ear}
                  className={`slot slot-${tag.toLowerCase()} ${dragEar === ear ? "over" : ""}`}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setDragEar(ear);
                  }}
                  onDragLeave={() => setDragEar((d) => (d === ear ? null : d))}
                  onDrop={(e) => {
                    e.preventDefault();
                    setDragEar(null);
                    const id = e.dataTransfer.getData("text/plain");
                    if (id) placeCase(id, ear);
                  }}
                >
                  <div className="slot-head">
                    <span className="slot-tag">{tag}</span>
                    {b && (
                      <button
                        className="mini"
                        title="Quitar (vuelve a normal)"
                        onClick={() => props.onRemoveEar(ear)}
                      >
                        ✕
                      </button>
                    )}
                  </div>
                  {b ? (
                    <div className="slot-case">
                      <div className="cname">{v?.nombre ?? b.nombre ?? b.id}</div>
                      {v && <div className="cmeta">{v.lesiones.join(" · ") || "normal"}</div>}
                    </div>
                  ) : (
                    <div className="slot-empty">normal · arrastra una patología aquí</div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Buscador + filtro */}
          <div className="catalog-filters">
            <input
              type="text"
              className="search"
              placeholder="Buscar caso…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <select value={pathFilter} onChange={(e) => setPathFilter(e.target.value)}>
              {PATH_FILTER.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>

          {/* Lista de casos (arrastrables) */}
          <div className="case-list modal-cases">
            {filtered.length === 0 ? (
              <p className="hint">Sin casos para ese filtro.</p>
            ) : (
              filtered.map((c) => (
                <div
                  key={c.id}
                  className="case-item case-drag"
                  draggable
                  onDragStart={(e) => e.dataTransfer.setData("text/plain", c.id)}
                  title="Arrastra a un slot OD/OI"
                >
                  <span className="drag-grip">⠿</span>
                  <div className="case-info">
                    <span className="cname">{c.name}</span>
                    <span className="cmeta"> · {c.summary}</span>
                  </div>
                  <button className="mini" disabled={loading} onClick={() => placeCase(c.id, "Right")}>
                    →OD
                  </button>
                  <button className="mini" disabled={loading} onClick={() => placeCase(c.id, "Left")}>
                    →OI
                  </button>
                  <button className="mini" title="Editar copia" onClick={() => editCatalog(c.id)}>
                    ✎
                  </button>
                </div>
              ))
            )}
          </div>
        </>
      ) : (
        <CaseEditor value={editDef} onChange={onEditDef} onLoad={loadDef} loading={loading} />
      )}

      {/* Verdad por oído (solo docente) */}
      {verdades.length > 0 && (
        <div className="verdad-box">
          <span className="section-title" style={{ margin: 0 }}>
            Verdad cargada
          </span>
          {verdades.map((v) => (
            <p className="hint" key={v.ear} style={{ marginTop: 4 }}>
              <b>{v.ear}</b> · {v.nombre} — lesiones:{" "}
              {v.lesiones.length ? v.lesiones.join(" · ") : "ninguna"}
            </p>
          ))}
        </div>
      )}
    </Modal>
  );
}
