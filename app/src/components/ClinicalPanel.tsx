import { useEffect, useRef, useState } from "react";
import { Channel } from "@tauri-apps/api/core";
import type {
  AbrCurve,
  CapMsg,
  CaseInfo,
  EarSide,
  FspPoint,
  Mark,
  Modo,
  SimParams,
  SubjectParams,
  VerdadDto,
  VistaCiegaCaso,
  Waveform,
} from "../types";
import {
  cargarCaso,
  detenerCaptura,
  docenteDesbloquear,
  docenteRelock,
  iniciarCapturaClinica,
  listCases,
  verVerdad,
} from "../api";
import AbrGraph from "../charts/AbrGraph";
import FspGraph from "../charts/FspGraph";
import EegMonitor from "../charts/EegMonitor";
import EquipmentPanel, { DEFAULT_EQUIPO } from "./EquipmentPanel";
import { ChipGroup } from "./widgets";
import { num } from "../lib/format";
import { loadDraft, saveDraft } from "../lib/draft";
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

const MODO_OPTS: { value: Modo; label: string }[] = [
  { value: "practica", label: "Práctica" },
  { value: "evaluacion", label: "Evaluación" },
  { value: "osce", label: "OSCE" },
];

export default function ClinicalPanel() {
  const draft = loadDraft();
  const [modo, setModo] = useState<Modo>(draft?.modo ?? "practica");
  const [cases, setCases] = useState<CaseInfo[]>([]);
  const [blind, setBlind] = useState<VistaCiegaCaso | null>(null);
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

  // Pila de curvas ABR (apilado manual) + marcado.
  const [curves, setCurves] = useState<AbrCurve[]>([]);
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
  const [verdad, setVerdad] = useState<VerdadDto | null>(null);

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

  async function load(c: CaseInfo) {
    setCurves([]);
    setActiveByEar({ Right: null, Left: null });
    setLiveMean(null);
    setLiveReplica(null);
    liveReplicaRef.current = null;
    setLiveEpoch(null);
    setLiveFsp([]);
    liveFspRef.current = [];
    setCapturingEar(null);
    try {
      setBlind(await cargarCaso(c.id, modo));
    } catch (e) {
      console.error(e);
    }
  }

  async function capturar() {
    if (!blind || capturing) return;
    setLiveEpoch(null);
    setLiveMean(null);
    setLiveReplica(null);
    liveReplicaRef.current = null;
    setProg({ aceptados: 0, objetivo: equipo.sweeps, fsp: 0, rechazados: 0 });
    setCapturing(true);
    const capEar = equipo.ear;
    const capInt = equipo.intensity_db;
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
            const sameEar = cs.filter((c) => c.ear === capEar).length;
            return [
              ...cs,
              {
                id,
                ear: capEar,
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
    if (ok) setVerdad(await verVerdad().catch(() => null));
  }
  async function relock() {
    await docenteRelock();
    setDocente(false);
    setVerdad(null);
  }

  function onGap(id: string, gap: number) {
    setCurves((cs) => cs.map((c) => (c.id === id ? { ...c, gap } : c)));
  }
  function onMark(id: string, mark: Mark) {
    setCurves((cs) =>
      cs.map((c) => (c.id === id ? { ...c, marks: upsertMark(c.marks, mark) } : c))
    );
  }

  // Columnas de la tabla: unión de ondas marcadas (soporta ABR+ALR+MMN juntas);
  // si aún no hay marcas, muestra el set activo como guía.
  const present = allWavesOrdered().filter((w) =>
    curves.some((c) => c.marks.some((m) => m.label === w))
  );
  const resultCols = present.length ? present : markSetWaves(markSetId);

  const fspFor = (ear: EarSide): FspPoint[] => {
    if (capturingEar === ear) return liveFsp;
    const ac = curves.find((c) => c.id === activeByEar[ear]);
    return ac ? ac.fsp : [];
  };

  return (
    <div className="clin">
      <aside className="clin-side">
        {/* Paciente (vista ciega) */}
        {blind ? (
          <div className="card" style={{ marginBottom: 8 }}>
            <p className="section-title">
              Paciente {blind.nombre ? `· ${blind.nombre}` : "(ciego)"}
            </p>
            <div className="hint">
              {blind.ear} · {num(blind.age_years, 0)} a · {blind.sex} · {blind.modo}
            </div>
          </div>
        ) : (
          <div className="card hint" style={{ marginBottom: 8 }}>
            El docente debe cargar un caso.
          </div>
        )}

        <EquipmentPanel params={equipo} onChange={setEquipo} />

        <div style={{ height: 8 }} />
        {capturing ? (
          <button className="primary" onClick={detener} style={{ background: "var(--danger)", color: "#1a0606" }}>
            Detener ({prog.aceptados}/{prog.objetivo})
          </button>
        ) : (
          <button className="primary" onClick={capturar} disabled={!blind}>
            Capturar
          </button>
        )}

        {/* Rol docente */}
        <div className="card" style={{ marginTop: 8 }}>
          <p className="section-title">Rol docente</p>
          {docente ? (
            <button className="mini" onClick={relock}>
              Bloquear
            </button>
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
        {/* Área DOCENTE: modo + caso + verdad (oculta al alumno) */}
        {docente && (
          <div className="card">
            <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
              <span className="section-title" style={{ margin: 0 }}>
                Docente · Modo
              </span>
              <ChipGroup<Modo> value={modo} options={MODO_OPTS} onChange={setModo} />
            </div>
            <div className="case-list" style={{ marginTop: 8, maxHeight: 130, overflowY: "auto" }}>
              {cases.map((c) => (
                <button
                  key={c.id}
                  className="case-item"
                  onClick={() => load(c)}
                  style={blind?.id === c.id ? { borderColor: "var(--accent)" } : undefined}
                >
                  <span className="cname">{c.name}</span>
                  <span className="cmeta"> · {c.modality} · {c.ear}</span>
                </button>
              ))}
            </div>
            {verdad && (
              <p className="hint" style={{ marginTop: 6 }}>
                Verdad: {verdad.descripcion} · Lesiones:{" "}
                {verdad.lesiones.length ? verdad.lesiones.join(" · ") : "ninguna"} · Clave:{" "}
                {verdad.verdad_picos.map((p) => `${p.label} ${num(p.latency_ms, 2)}`).join("  ") || "—"}
              </p>
            )}
          </div>
        )}

        {capturing && (
          <div className="hint" style={{ padding: "0 2px" }}>
            Promediando {prog.aceptados}/{prog.objetivo} · FSP {num(prog.fsp, 1)} · rechazadas{" "}
            {prog.rechazados}
          </div>
        )}

        {/* Fila superior: tabla de latencias (siempre visible) + EEG */}
        <div className="toprow">
          <div className="card results-card">
            <table className="restab">
              <thead>
                <tr>
                  <th>Oído</th>
                  <th>dB</th>
                  {resultCols.map((w) => (
                    <th key={w}>{w}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {curves.length === 0 ? (
                  <tr>
                    <td colSpan={resultCols.length + 2} className="restab-empty">
                      sin curvas — captura para ver latencias
                    </td>
                  </tr>
                ) : (
                  curves.map((c) => (
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
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          <EegMonitor wave={capturing ? liveEpoch : null} ear={equipo.ear} />
        </div>

        {/* Gráficos OD / OI */}
        <div className="abr-pair">
          {EARS.map((ear) => (
            <div className="abr-panel" key={ear}>
              <div style={{ flex: 1, minHeight: 0 }}>
                <AbrGraph
                  ear={ear}
                  curves={curves.filter((c) => c.ear === ear)}
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
      </main>
    </div>
  );
}
