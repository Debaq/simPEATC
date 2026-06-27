import { useEffect, useRef, useState } from "react";
import { Channel } from "@tauri-apps/api/core";
import type {
  AbrCurve,
  AssrCap,
  CapMsg,
  CaseDef,
  CaseInfo,
  EarSide,
  FspPoint,
  Mark,
  Modality,
  Modo,
  OddballCap,
  SimParams,
  SubjectParams,
  VerdadDto,
  VistaCiegaCaso,
  Waveform,
} from "../types";
import type { DiagEar } from "../types";
import {
  calificar,
  capturarAssrClinico,
  capturarOddballClinico,
  cargarCasoDef,
  detenerCaptura,
  docenteDesbloquear,
  docenteRelock,
  iniciarCapturaClinica,
  listCases,
  obtenerCasoDef,
  quitarCaso,
  verVerdad,
} from "../api";
import AbrGraph from "../charts/AbrGraph";
import FspGraph from "../charts/FspGraph";
import EegMonitor from "../charts/EegMonitor";
import LatencyIntensityChart from "../charts/LatencyIntensityChart";
import Modal from "./Modal";
import EquipmentPanel, { DEFAULT_EQUIPO } from "./EquipmentPanel";
import OddballView from "./OddballView";
import AssrView from "./AssrView";
import TeachingModal from "./TeachingModal";
import AnswerModal from "./AnswerModal";
import ReportModal from "./ReportModal";

// Familia de resultado según el examen: cada una tiene su vista.
type Family = "transient" | "oddball" | "assr";
function familyOf(m: Modality): Family {
  if (m === "P300" || m === "Mmn") return "oddball";
  if (m === "Assr") return "assr";
  return "transient";
}
import { num } from "../lib/format";
import { loadDraft, saveDraft } from "../lib/draft";
import { blankCase } from "../lib/caseFile";
import { upsertMark } from "../lib/marking";
import { allWavesOrdered, markSetWaves } from "../lib/marksets";

const EARS: EarSide[] = ["Right", "Left"];

const DUMMY_SUBJECT: SubjectParams = {
  age_years: 30,
  sex: "Female",
  temperature_c: 37,
  state: "Awake",
  attention: "Passive",
  lesion: null,
};

const DEFAULT_EQUIPO_PARAMS: SimParams = {
  modality: "Abr",
  ear: "Right",
  stimulus: "click",
  intensity_db: 80,
  sweeps: 2000,
  freq_hz: 2000,
  carrier_hz: 2000,
  mod_freq_hz: 80,
  equipo: DEFAULT_EQUIPO,
  subject: DUMMY_SUBJECT,
};

export default function ClinicalPanel() {
  const draft = loadDraft();
  const [modo, setModo] = useState<Modo>(draft?.modo ?? "practica");
  const [cases, setCases] = useState<CaseInfo[]>([]);
  // Caso cargado por oído (slots OD/OI): paciente binaural con patologías asimétricas.
  const [blindByEar, setBlindByEar] = useState<Record<EarSide, VistaCiegaCaso | null>>({
    Right: null,
    Left: null,
  });
  const [equipo, setEquipo] = useState<SimParams>(draft?.equipo ?? DEFAULT_EQUIPO_PARAMS);
  const [guardado, setGuardado] = useState(false);

  // Captura progresiva (G3).
  const [capturing, setCapturing] = useState(false);
  const [liveMean, setLiveMean] = useState<Waveform | null>(null);
  const [liveReplica, setLiveReplica] = useState<Waveform | null>(null);
  const [liveEpoch, setLiveEpoch] = useState<Waveform | null>(null);
  const liveReplicaRef = useRef<Waveform | null>(null);
  const [prog, setProg] = useState({ aceptados: 0, objetivo: 0, fsp: 0, rechazados: 0 });
  const timesRef = useRef<number[]>([]);
  const liveMeanRef = useRef<Waveform | null>(null);
  const fspRef = useRef(0);

  // FSP en vivo de la toma actual + oído que se captura; al terminar se guarda
  // en la curva, para que cada curva muestre su propia FSP al seleccionarla.
  const [liveFsp, setLiveFsp] = useState<FspPoint[]>([]);
  const [capturingEar, setCapturingEar] = useState<EarSide | null>(null);
  const liveFspRef = useRef<FspPoint[]>([]);

  // Resultados por familia (batería del paciente).
  const [curves, setCurves] = useState<AbrCurve[]>([]); // transitorios (ABR/ECochG/MLR/ALR)
  const [oddballs, setOddballs] = useState<OddballCap[]>([]); // P300/MMN
  const [assrs, setAssrs] = useState<AssrCap[]>([]); // ASSR
  // Curva activa POR OÍDO (binaural): se recuerda la última de cada lado.
  const [activeByEar, setActiveByEar] = useState<Record<EarSide, string | null>>({
    Right: null,
    Left: null,
  });
  const setActiveEar = (ear: EarSide, id: string) =>
    setActiveByEar((p) => ({ ...p, [ear]: id }));
  const [markSetId, setMarkSetId] = useState("abr");
  const idSeq = useRef(0);

  // Rol docente.
  const [pin, setPin] = useState("");
  const [docente, setDocente] = useState(false);
  const [verdades, setVerdades] = useState<VerdadDto[]>([]);

  // Área docente (modal): visibilidad + borrador del editor de casos.
  const [showTeach, setShowTeach] = useState(false);
  const [editDef, setEditDef] = useState<CaseDef>(blankCase());

  // Evaluación: panel de respuesta del alumno.
  const [showAnswer, setShowAnswer] = useState(false);

  // Gráfico latencia-intensidad (ABR).
  const [showLI, setShowLI] = useState(false);

  // Informe (lo redacta el estudiante).
  const [showReport, setShowReport] = useState(false);

  // Arma la entrega y la califica contra la verdad oculta del backend.
  function onCalificar(diagnosticos: DiagEar[]) {
    const marcas = curves.flatMap((c) =>
      c.marks.map((m) => ({
        ear: c.ear,
        modality: c.modality,
        intensity_db: c.intensity,
        label: m.label,
        t_ms: m.t_ms,
      }))
    );
    return calificar({ sujeto: equipo.subject, diagnosticos, marcas });
  }

  useEffect(() => {
    listCases().then(setCases).catch(console.error);
  }, []);

  // El set de marcas sigue al tipo de prueba seleccionado.
  useEffect(() => {
    const map: Record<string, string> = {
      Abr: "abr",
      ECochG: "ecochg",
      Mlr: "mlr",
      Alr: "alr",
      P300: "p300",
      Mmn: "mmn",
    };
    setMarkSetId(map[equipo.modality] ?? "abr");
  }, [equipo.modality]);

  useEffect(() => {
    const t = setTimeout(() => {
      saveDraft({ modo, equipo });
      setGuardado(true);
    }, 600);
    return () => clearTimeout(t);
  }, [modo, equipo]);

  // Limpia los resultados de UN oído (preserva el otro slot, binaural).
  function resetCapturaEar(ear: EarSide) {
    setCurves((cs) => cs.filter((c) => c.ear !== ear));
    setOddballs((o) => o.filter((c) => c.ear !== ear));
    setAssrs((a) => a.filter((c) => c.ear !== ear));
    setActiveByEar((p) => ({ ...p, [ear]: null }));
    if (capturingEar === ear) {
      setLiveMean(null);
      setLiveReplica(null);
      liveReplicaRef.current = null;
      setLiveEpoch(null);
      setLiveFsp([]);
      liveFspRef.current = [];
    }
  }

  // Tras cargar/quitar un caso, si el rol docente está abierto refresca la verdad.
  async function refrescarVerdad() {
    if (docente) setVerdades(await verVerdad().catch(() => []));
  }

  // Carga un paciente en el slot `ear`; preserva el otro oído (binaural).
  async function loadDef(def: CaseDef, ear: EarSide) {
    resetCapturaEar(ear);
    const vista = await cargarCasoDef(def, ear, modo);
    setBlindByEar((p) => ({ ...p, [ear]: vista }));
    await refrescarVerdad();
  }

  // Vacía el slot de un oído → vuelve a paciente normal por defecto en ese oído.
  async function removeEar(ear: EarSide) {
    await quitarCaso(ear).catch(() => {});
    setBlindByEar((p) => ({ ...p, [ear]: null }));
    resetCapturaEar(ear);
    await refrescarVerdad();
  }

  // Despacha la captura según la familia del examen activo.
  async function capturar() {
    if (capturing) return;
    const fam = familyOf(equipo.modality);
    if (fam === "oddball") return capturarOddball();
    if (fam === "assr") return capturarAssr();
    return capturarTransitorio();
  }

  // Oddball (P300/MMN): captura one-shot, se acumula por (oído, examen).
  async function capturarOddball() {
    setCapturing(true);
    try {
      const rec = await capturarOddballClinico(equipo);
      setOddballs((o) => [
        ...o,
        {
          id: `o${idSeq.current++}`,
          ear: equipo.ear,
          modality: equipo.modality,
          intensity: equipo.intensity_db,
          rec,
        },
      ]);
    } catch (e) {
      console.error(e);
    } finally {
      setCapturing(false);
    }
  }

  // ASSR: captura one-shot, se acumula por (oído, portadora).
  async function capturarAssr() {
    setCapturing(true);
    try {
      const result = await capturarAssrClinico(equipo);
      setAssrs((a) => [
        ...a,
        { id: `a${idSeq.current++}`, ear: equipo.ear, intensity: equipo.intensity_db, result },
      ]);
    } catch (e) {
      console.error(e);
    } finally {
      setCapturing(false);
    }
  }

  // Transitorio (ABR/ECochG/MLR/ALR): captura progresiva (promediación A/B).
  async function capturarTransitorio() {
    setLiveEpoch(null);
    setLiveMean(null);
    setLiveReplica(null);
    liveReplicaRef.current = null;
    setProg({ aceptados: 0, objetivo: equipo.sweeps, fsp: 0, rechazados: 0 });
    setCapturing(true);
    const capEar = equipo.ear;
    const capInt = equipo.intensity_db;
    const capMod = equipo.modality;
    setCapturingEar(capEar);
    liveFspRef.current = [];
    setLiveFsp([]);

    const channel = new Channel<CapMsg>();
    channel.onmessage = (msg) => {
      if (msg.event === "iniciada") {
        timesRef.current = msg.data.timesMs;
        setProg((p) => ({ ...p, objetivo: msg.data.objetivo }));
      } else if (msg.event === "refresco") {
        const t = timesRef.current;
        const mean: Waveform = { times_ms: t, amplitudes_uv: msg.data.promedio };
        const rep: Waveform = { times_ms: t, amplitudes_uv: msg.data.replica };
        liveMeanRef.current = mean;
        liveReplicaRef.current = rep;
        fspRef.current = msg.data.fsp;
        setLiveMean(mean);
        setLiveReplica(rep);
        setLiveEpoch({ times_ms: t, amplitudes_uv: msg.data.epoca });
        setProg((p) => ({
          aceptados: msg.data.aceptados,
          objetivo: p.objetivo,
          fsp: msg.data.fsp,
          rechazados: msg.data.rechazados,
        }));
        liveFspRef.current = [
          ...liveFspRef.current,
          { sweeps: msg.data.aceptados, fsp: msg.data.fsp },
        ];
        setLiveFsp(liveFspRef.current);
      } else if (msg.event === "finalizada") {
        const mean = liveMeanRef.current;
        if (mean && mean.amplitudes_uv.length > 0) {
          const id = `c${idSeq.current++}`;
          const fsp = liveFspRef.current;
          setCurves((cs) => {
            const sameEar = cs.filter((c) => c.ear === capEar && c.modality === capMod).length;
            return [
              ...cs,
              {
                id,
                ear: capEar,
                modality: capMod,
                intensity: capInt,
                wave: mean,
                gap: sameEar * 1.2,
                marks: [],
                fsp,
                replica: liveReplicaRef.current ?? undefined,
              },
            ];
          });
          setActiveEar(capEar, id);
        }
        setLiveEpoch(null);
        setLiveMean(null);
        setCapturing(false);
        setCapturingEar(null);
      }
    };

    try {
      // Semilla aleatoria por captura → ruido distinto cada toma.
      const salt = Math.floor(Math.random() * 1_000_000_000);
      await iniciarCapturaClinica(equipo, channel, salt);
    } catch (e) {
      console.error(e);
      setCapturing(false);
    }
  }

  async function detener() {
    await detenerCaptura().catch(() => {});
  }

  async function desbloquear() {
    const ok = await docenteDesbloquear(pin);
    setDocente(ok);
    if (ok) {
      setPin("");
      setShowTeach(true);
      setVerdades(await verVerdad().catch(() => []));
    }
  }
  async function relock() {
    await docenteRelock();
    setDocente(false);
    setVerdades([]);
    setShowTeach(false);
  }

  function onGap(id: string, gap: number) {
    setCurves((cs) => cs.map((c) => (c.id === id ? { ...c, gap } : c)));
  }
  function onMark(id: string, mark: Mark) {
    setCurves((cs) =>
      cs.map((c) => (c.id === id ? { ...c, marks: upsertMark(c.marks, mark) } : c))
    );
  }

  const fam = familyOf(equipo.modality);
  // Curvas transitorias del examen activo (ABR y MLR no se mezclan: distinta ventana).
  const transientCurves = curves.filter((c) => c.modality === equipo.modality);

  // Columnas de la tabla: ondas marcadas en el examen activo; si no hay, el set guía.
  const present = allWavesOrdered().filter((w) =>
    transientCurves.some((c) => c.marks.some((m) => m.label === w))
  );
  const resultCols = present.length ? present : markSetWaves(markSetId);

  // Intervalos interpico (ABR): aparecen cuando ambas ondas del par están marcadas.
  const IP_PAIRS: [string, string][] = [
    ["I", "III"],
    ["III", "V"],
    ["I", "V"],
  ];
  const ipShown = IP_PAIRS.filter(([a, b]) =>
    transientCurves.some(
      (c) => c.marks.some((m) => m.label === a) && c.marks.some((m) => m.label === b)
    )
  );
  const ipVal = (c: AbrCurve, a: string, b: string): number | null => {
    const ma = c.marks.find((m) => m.label === a);
    const mb = c.marks.find((m) => m.label === b);
    return ma && mb ? mb.t_ms - ma.t_ms : null;
  };

  const fspFor = (ear: EarSide): FspPoint[] => {
    if (capturingEar === ear) return liveFsp;
    const ac = transientCurves.find((c) => c.id === activeByEar[ear]);
    return ac ? ac.fsp : [];
  };

  return (
    <div className="clin">
      <aside className="clin-side">
        {/* Paciente: patología por oído (slot). Slot vacío = oído normal. */}
        <div className="card" style={{ marginBottom: 8 }}>
          <p className="section-title">
            Paciente · {modo} · {num(equipo.subject.age_years, 0)} a ·{" "}
            {equipo.subject.sex === "Male" ? "M" : "F"}
          </p>
          {EARS.map((ear) => {
            const b = blindByEar[ear];
            const tag = ear === "Right" ? "OD" : "OI";
            return (
              <div key={ear} className="hint" style={{ marginTop: 2 }}>
                <b style={{ color: ear === "Right" ? "#e8615f" : "#4aa3ff" }}>{tag}</b>:{" "}
                {b ? (
                  b.nombre ?? "(patología ciega)"
                ) : (
                  <span style={{ opacity: 0.7 }}>normal (sin patología)</span>
                )}
              </div>
            );
          })}
        </div>

        <EquipmentPanel params={equipo} onChange={setEquipo} />

        <div style={{ height: 8 }} />
        {capturing ? (
          <button className="primary" onClick={detener} style={{ background: "var(--danger)", color: "#1a0606" }}>
            Detener ({prog.aceptados}/{prog.objetivo})
          </button>
        ) : (
          <button className="primary" onClick={capturar}>
            Capturar
          </button>
        )}

        {modo !== "practica" && (
          <button className="mini" style={{ width: "100%", marginTop: 6 }} onClick={() => setShowAnswer(true)}>
            Responder y entregar
          </button>
        )}
        <button className="mini" style={{ width: "100%", marginTop: 6 }} onClick={() => setShowReport(true)}>
          Informe
        </button>{" "}

        {/* Rol docente */}
        <div className="card" style={{ marginTop: 8 }}>
          <p className="section-title">Rol docente</p>
          {docente ? (
            <div style={{ display: "flex", gap: 6 }}>
              <button className="mini" style={{ flex: 1 }} onClick={() => setShowTeach(true)}>
                Área docente
              </button>
              <button className="mini" onClick={relock} title="Bloquear y entregar al alumno">
                Bloquear
              </button>
            </div>
          ) : (
            <div style={{ display: "flex", gap: 6 }}>
              <input
                type="password"
                placeholder="PIN"
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                style={{
                  flex: 1,
                  padding: "4px 6px",
                  background: "var(--panel-2)",
                  color: "var(--text)",
                  border: "1px solid var(--border)",
                  borderRadius: 5,
                }}
              />
              <button className="mini" onClick={desbloquear}>
                Abrir
              </button>
            </div>
          )}
        </div>

        {guardado && (
          <p className="hint" style={{ marginTop: 6, textAlign: "center" }}>
            borrador guardado ✓
          </p>
        )}
      </aside>

      <main className="clin-main">
        {fam === "transient" && capturing && (
          <div className="hint" style={{ padding: "0 2px" }}>
            Promediando {prog.aceptados}/{prog.objetivo} · FSP {num(prog.fsp, 1)} · rechazadas{" "}
            {prog.rechazados}
          </div>
        )}
        {fam !== "transient" && capturing && (
          <div className="hint" style={{ padding: "0 2px" }}>Capturando {equipo.modality}…</div>
        )}

        {fam === "oddball" ? (
          <OddballView caps={oddballs.filter((c) => c.modality === equipo.modality)} />
        ) : fam === "assr" ? (
          <AssrView caps={assrs} />
        ) : (
          <>
            {/* Fila superior: tabla de latencias del examen activo + EEG */}
            <div className="toprow">
              <div className="card results-card">
                {equipo.modality === "Abr" && (
                  <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 4 }}>
                    <button
                      className="mini on"
                      onClick={() => setShowLI(true)}
                      title="Función latencia-intensidad de la onda V"
                    >
                      📈 Latencia / Intensidad
                    </button>
                  </div>
                )}
                <table className="restab">
                  <thead>
                    <tr>
                      <th>Oído</th>
                      <th>dB</th>
                      {resultCols.map((w) => (
                        <th key={w}>{w}</th>
                      ))}
                      {ipShown.map(([a, b]) => (
                        <th key={`ip${a}${b}`} style={{ color: "var(--accent)" }}>
                          {a}–{b}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {transientCurves.length === 0 ? (
                      <tr>
                        <td colSpan={resultCols.length + ipShown.length + 2} className="restab-empty">
                          sin curvas — captura {equipo.modality} para ver latencias
                        </td>
                      </tr>
                    ) : (
                      transientCurves.map((c) => (
                        <tr
                          key={c.id}
                          className={c.id === activeByEar[c.ear] ? "active" : ""}
                          onClick={() => setActiveEar(c.ear, c.id)}
                        >
                          <td style={{ color: c.ear === "Right" ? "#e8615f" : "#4aa3ff", fontWeight: 700 }}>
                            {c.ear === "Right" ? "OD" : "OI"}
                          </td>
                          <td>{num(c.intensity, 0)}</td>
                          {resultCols.map((w) => {
                            const m = c.marks.find((x) => x.label === w);
                            return <td key={w}>{m ? num(m.t_ms, 2) : "—"}</td>;
                          })}
                          {ipShown.map(([a, b]) => {
                            const v = ipVal(c, a, b);
                            return (
                              <td key={`ip${a}${b}`} style={{ color: "var(--accent)" }}>
                                {v != null ? num(v, 2) : "—"}
                              </td>
                            );
                          })}
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
              <EegMonitor wave={capturing ? liveEpoch : null} ear={equipo.ear} />
            </div>

            {/* Gráficos OD / OI del examen activo */}
            <div className="abr-pair">
              {EARS.map((ear) => (
                <div className="abr-panel" key={ear}>
                  <div style={{ flex: 1, minHeight: 0 }}>
                    <AbrGraph
                      ear={ear}
                      curves={transientCurves.filter((c) => c.ear === ear)}
                      activeId={activeByEar[ear]}
                      onActive={(id) => setActiveEar(ear, id)}
                      onGap={onGap}
                      onMark={onMark}
                      liveMean={capturing && equipo.ear === ear ? liveMean : null}
                      liveReplica={capturing && equipo.ear === ear ? liveReplica : null}
                      ghost={capturing && equipo.ear === ear ? liveEpoch : null}
                      preMs={equipo.equipo?.pre_ms ?? 1}
                      postMs={equipo.equipo?.post_ms ?? 10}
                      markSetId={markSetId}
                      onMarkSet={setMarkSetId}
                    />
                  </div>
                  <FspGraph data={fspFor(ear)} ear={ear} />
                </div>
              ))}
            </div>
          </>
        )}
      </main>

      {showTeach && docente && (
        <TeachingModal
          modo={modo}
          setModo={setModo}
          cases={cases}
          blindByEar={blindByEar}
          verdades={verdades}
          sessionVars={equipo.subject}
          onSessionVars={(s) => setEquipo({ ...equipo, subject: s })}
          editDef={editDef}
          onEditDef={setEditDef}
          onLoadDef={loadDef}
          onFetchDef={(id) => obtenerCasoDef(id)}
          onRemoveEar={removeEar}
          onClose={() => setShowTeach(false)}
        />
      )}

      {showAnswer && (
        <AnswerModal onCalificar={onCalificar} onClose={() => setShowAnswer(false)} />
      )}

      {showReport && (
        <ReportModal subject={equipo.subject} modo={modo} onClose={() => setShowReport(false)} />
      )}

      {showLI && (
        <Modal title="ABR · función latencia-intensidad" onClose={() => setShowLI(false)} width={620}>
          <div style={{ height: 360 }}>
            <LatencyIntensityChart
              curves={curves.filter((c) => c.modality === "Abr")}
              subject={equipo.subject}
              insert={(equipo.equipo?.transducer ?? "Insert") === "Insert"}
            />
          </div>
          <p className="hint" style={{ marginTop: 6 }}>
            Latencia de cada onda marcada vs. intensidad. La banda verde es la zona de normalidad
            de la onda V (sujeto normal de la misma edad/condición); las marcas fuera de ella
            sugieren patología.
          </p>
        </Modal>
      )}
    </div>
  );
}
