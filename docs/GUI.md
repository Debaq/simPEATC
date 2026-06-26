# Plan de Implementación de la GUI de simPEATC (Tauri) — FINAL

> Plan de diseño de la **interfaz clínica** de `simPEATC` (backend **Rust + Tauri 2**, frontend **web: React + Vite + TypeScript**).
> Alcance: una estación de examen de potenciales evocados auditivos de **formato clínico**, donde el **docente** configura un "paciente real conectado" y el **estudiante** configura el equipo, captura, marca/mueve picos, interpreta y redacta un informe, en modos **Práctica / Evaluación / OSCE**.
> Estado: **diseño revisado** tras dos auditorías adversariales (heredada del plan iced v2 y la del re‑plataformado a Tauri, ya **grounded contra el código real** de `aep-core`). El motor (`aep-core`, Capas 0–7) está completo en lo nuclear; este documento define la arquitectura objetivo de la GUI sobre Tauri, **los huecos clínicos del core que condicionan los objetivos docentes** (re‑dimensionados según el código real) y el roadmap por capas (G0..G9) con una capa de núcleo intercalada (G‑core).
> Estilo y rigor: hermano de `docs/MOTOR.md`.

---

> ### ⚙️ Adaptación de stack del frontend (decisión del proyecto) — GOBIERNA TODO EL DOCUMENTO
>
> El plan fue redactado originalmente con **Svelte 5 + uPlot**. **Decisión vigente: el frontend es React + Vite + TypeScript con ECharts.** Esta nota tiene **precedencia** sobre cualquier mención posterior del stack en el documento. Léase, en todo el texto:
>
> | Donde el doc dice… | Léase / impleméntese como… |
> |---|---|
> | **Svelte 5**, runes `$state`/`$derived` | **React 18** + hooks (`useState`/`useMemo`/`useReducer`), Context para estado global |
> | Stores `*.svelte.ts` | módulos de estado React: **Context + reducer** o store ligero (Zustand) en `src/stores/*.ts` |
> | `App.svelte`, `screens/*.svelte`, componentes `.svelte` | `App.tsx`, `screens/*.tsx`, componentes `.tsx` |
> | `main.ts` (bootstrap Svelte) | `main.tsx` (`ReactDOM.createRoot`) |
> | **uPlot** (Canvas2D) para las trazas | **ECharts** (`echarts-for-react`, render Canvas) |
> | `u.setData()` en cada snapshot | `chartRef.getEchartsInstance().setOption({series:[{data}]}, {lazyUpdate:true})` |
> | `u.valToPos`/`u.posToVal` (el "Plano") | `echartsInstance.convertToPixel` / `convertFromPixel` (mismo rol data↔pixel) |
> | overlay DOM/SVG arrastrable sobre uPlot | overlay DOM absoluto sobre el `<canvas>` de ECharts **o** componentes `graphic` arrastrables de ECharts (`draggable:true`); evaluar ambos en G2 |
> | `cursor.sync` entre dos uPlot (split OD/OI) | `echarts.connect([odChart, oiChart])` para sincronizar cursor/zoom |
> | bands de uPlot (bandas normativas) | `markArea` de ECharts |
> | pnpm | **npm** (ya en uso) |
> | Paraglide/typesafe‑i18n | `react-i18next` (o catálogo propio) |
>
> **Riesgo de stack reevaluado:** ECharts cuesta más CPU/RAM que uPlot en captura en vivo (§5). Mitigación: en `Parcial` del `Channel` **decimar al ancho en píxeles** (~500–1000 pts), `setOption` con `lazyUpdate`/`notMerge:false` y `silent:true`, y coalescing en `requestAnimationFrame`. Validar en **G0‑spike** que ECharts sostiene ~20–30 fps de captura en WebKitGTK (Linux). Si no rinde, el plan deja uPlot como alternativa documentada.
>
> Todo lo demás del documento (arquitectura Tauri, invariante verdad/ciego, roles/modos, scoring, gaps del core, roadmap G0–G9) es **agnóstico del framework** y aplica tal cual.

---

## 0. Cambios de esta revisión (iced v2 → Tauri → grounding contra el código)

El plan v2 (iced) pasó auditoría adversarial; el re‑plataformado a Tauri pasó una segunda. **Decisión del proyecto: se reemplaza la GUI iced por Tauri** (backend Rust + frontend web), para lograr una interfaz más visual y de formato clínico, sin fricción frente a un equipo comercial, aprovechando que el equipo está cómodo con JS/TS. **~70 % del v2 es agnóstico de la tecnología y se reutiliza tal cual**; este documento sólo reescribe lo que depende del medio **y corrige las afirmaciones que no se sostenían contra el código fuente**.

**Se reutiliza sin cambios de fondo** (sólo traduciendo nombres iced→web): visión/alcance (§1), principios (§2, salvo "Elm estricto"), cobertura de modalidades (§6), modelo del paciente/autoría docente (§7), modos Práctica/Evaluación/OSCE (§8), motor de scoring/rúbrica (§9, ahora explícitamente *en el backend Rust*), roles/persistencia/integridad (§11), GAPS de `aep-core` (§12, **re‑dimensionados**), y los riesgos clínicos de §14.

**Se reescribe para Tauri:**

1. **Arquitectura (§3).** Ya no `iced::application` (Elm estricto) sino **Tauri 2**: backend Rust con `#[tauri::command]` + **eventos/`Channel`**, frontend reactivo (Svelte 5 runes), estado partido **autoridad‑en‑Rust / UI‑en‑frontend**, tipado TS end‑to‑end con **tauri‑specta**.
2. **Modelo de datos (§4).** Dominio Rust serializable que cruza el IPC + estado del frontend en TS + **lista explícita de comandos y eventos/`Channel`**. Se **reevalúa** la regla "cero `Serialize` en el core" (ver §0.1 y §4).
3. **Gráfico clínico (§5).** Ya no `canvas::Program` de iced, sino **uPlot (Canvas2D)** para las trazas + **capa overlay DOM/SVG** para marcadores **arrastrables**; captura progresiva por **`tauri::ipc::Channel`** con **decimado al ancho en píxeles** como única palanca real de throughput.
4. **Informe/PDF (§10).** En web es trivial: **PNG hi‑res (`canvas.toDataURL`) como ruta primaria** + `pdfmake`/jsPDF para la maqueta. Se **descarta `printpdf`** y el redibujo vectorial Rust del plan iced.
5. **Roadmap (§13).** **G0 = andamiaje Tauri + frontend + IPC tipado + invariante verdad/ciego + i18n + autosave**, precedido de un **G0‑spike desechable** para los dos *unknowns* reales de Tauri. La lógica de capas, dependencias y "Hecho cuando" se conservan.
6. **Riesgos (§14).** Desaparecen los de iced. Aparecen los de Tauri **con las imprecisiones corregidas** (f32 no abarata JSON; no existe whitelist por ventana vía `AppManifest::commands`; pdfmake‑SVG es frágil; CSP estricta rompe `data:` de fuentes/canvas).

### 0.1 Correcciones de *grounding* contra el código real (bloqueantes, no cosméticas)

La segunda auditoría verificó el árbol `crates/aep-core/src`. Estas afirmaciones del plan Tauri v1 eran **falsas o mal dimensionadas** y se corrigen aquí:

- **GAP #2 (Serialize) estaba subestimado.** `aep-core` **NO** deriva `Serialize` en **ningún** tipo del dominio que cruza el IPC (`grep Serialize` ⇒ 0). Solo hay `Deserialize` manual en `cases.rs` y `norms.rs`. Además `CaseDef` usa **`String`** para `modality`/`ear` y `lesions` es privado. El prerequisito IPC es **bastante más trabajo** del que sugería el texto (ver §12.C #2 y §0.2).
- **GAP #12 estaba mal alcanzado.** **`Lesion.ear` YA EXISTE** (`lesion.rs:74`, tipo `Ear`). Lo que colapsa el oído es **`CaseDef::subject()`** (`cases.rs:147`), que sobreescribe `ear` con `self.ear()` para todas las lesiones, más el esquema **mono‑oído/mono‑modalidad/mono‑intensidad** de `CaseDef`. El trabajo se concentra en el **esquema de `CaseDef` + lista de órdenes**, no en "añadir `ear` a `Lesion`".
- **GAP #1 / G‑core estaba mal dimensionado, con un subtotal oculto.** El **sembrado por‑sweep YA EXISTE** (`engine.rs:189`: `Lcg::new(base_seed ^ produced.wrapping_mul(...))`). El arreglo real tiene **dos partes**: (a) quitar `sweeps` del *seed base* (`engine.rs:311` y `318` lo mezclan); (b) **lo difícil, antes omitido:** el bucle de rechazo usa un contador `produced` con `max_attempts` derivado de `target` (`engine.rs:184‑189`); para que `CaptureSession::step(n)` dé **exactamente** la misma curva que `simulate(N)`, **el contador `produced` debe persistir GLOBAL entre `step()`** y la semilla por‑sweep indexarse por ese contador global. Si cada `step` reinicia `produced`, los snapshots no igualarán a `simulate(N)`. **Este es el núcleo del "Hecho cuando" de G‑core.**

### 0.2 Decisión revisada sobre DTOs (boilerplate)

El plan v1 prohibía `Serialize` en `aep-core` para mantenerlo "puro", forzando ~15 DTOs espejo. Pero **`aep-core` ya depende de `serde`** (en `Cargo.toml`, hoy para `Deserialize`). **Decisión revisada:** se **deriva `Serialize` directamente en el dominio del core** (los tipos crudos), y la **ceguera se logra con funciones de proyección** (`fn vista_alumno(&Recording, Modo) -> RecordingDto`) en lugar de DTOs espejo completos. Se reservan DTOs/newtypes finos **solo donde** hay (i) **stripping** (proyección ciega) o (ii) necesidad de **`specta::Type`** para tipar TS. Esto reduce el boilerplate ~a la mitad sin debilitar el invariante: la frontera ciega sigue siendo **una función de proyección revisada y testeada**, no un `derive` arrastrado por error (ver §4 y el test de lista blanca en §11.B).

Y se mantienen las correcciones clínicas del v2: fidelidad como bloqueo de alcance (§12.A); presencia por `DETECTABLE_UV` (no `Recording.detected`); V/I y SP/AP desde marcas P‑V del alumno (no `v_i_ratio`/`sp_ap_ratio`); tolerancia de umbral ≥ 1 paso; D5 sobre `ActionLog`; bandas normativas con **peso 0 por defecto** ("referencia no validada") hasta tener SD revisadas; versionado/reproducibilidad; i18n es‑CL y accesibilidad desde G0.

---

## 1. Visión y alcance de la GUI

La GUI convierte el motor `aep-core` en una **estación de trabajo clínica simulada** indistinguible —en flujo— de un equipo comercial (Interacoustics Eclipse, Natus Bio‑logic, GSI Audera, IHS SmartEP). Dos actores:

- **Docente (autor):** define el *paciente* (un `Subject` + una o más "órdenes"/modalidades) componiendo la **causa** (sitio, grado y perfil de lesión, edad, temperatura, estado, atención). No dibuja curvas: declara la fisiología y el motor la deriva de forma determinista. Fija la *plantilla de equipo ideal* y la *rúbrica*. Controla el **modo** de funcionamiento.
- **Estudiante (examinador):** realiza el examen completo — chequea impedancias, configura estímulo/adquisición, **captura** (curva emergiendo en vivo), hace **réplica A/B**, **marca y mueve** los picos (mouse + teclas + táctil), construye la **serie de intensidades** y la **curva latencia‑intensidad**, **interpreta** y redacta el **informe**.

**Principio rector (anti‑fricción):** el estudiante no debe sentir diferencia con un equipo real. Se replican literalmente las convenciones (OD rojo / OI azul **con redundancia no‑cromática**, ondas romanas I–V, dB nHL con unidad visible, stacking por intensidad descendente, banda normativa al marcar, F<sub>sp</sub>/ruido residual en vivo, réplicas superpuestas, pantalla dividida OD/OI, **expandir/comprimir base de tiempos y µV/div, readout numérico bajo el cursor**). En Tauri esto es **más fácil de lograr visualmente**: la estética clínica vive en HTML/CSS y el gráfico en una librería web rápida.

**Alcance clínico — declaración explícita (ver §12.A).** Tres objetivos docentes centrales dependen de huecos del motor. Para cada uno se decide **implementar el gap** o **recortar el objetivo del alcance**:
- **Enmascaramiento clínico** — requiere efecto fisiológico de `Masking` (cross‑hearing, curva fantasma contralateral). Sin él, solo se chequea un combo.
- **Diferencial conductivo vs sensorineural por vía aérea/ósea** — requiere gap aire‑hueso por transductor. Sin él, la conducción ósea no evita la lesión conductiva.
- **Asimetría interaural / paciente multi‑orden** — requiere `CaseDef` multi‑oído/multi‑modalidad con lesiones por oído independientes.

Si alguno **no** se implementa, se elimina su criterio de la rúbrica y su sección del informe, y se documenta la limitación. No se evalúa contra fisiología que no se simula.

**Modos del docente** (no cambian la arquitectura, solo ramas de `view`/comandos):
- **Práctica / Libre:** verdad visible (solo rol docente), feedback inmediato, `Suggest` activo, sin cronómetro.
- **Evaluación:** caso anonimizado, verdad **que no cruza el IPC al alumno**, `Suggest` off, flujo obligatorio, feedback diferido y puntuado.
- **OSCE:** estaciones cronometradas en secuencia, sin feedback, sellado + HMAC y export por estudiante/estación, **variante por `seed_salt`**.

**Fuera de alcance de la GUI (vive en `aep-core`):** la verdad fisiológica (`model_for`/`Component`/`generator`), el DSP, la modulación clínica y los normativos. La GUI **consume** el motor; no reimplementa fisiología.

---

## 2. Principios de diseño

1. **Anti‑fricción clínica.** Cada control de la UI mapea 1:1 a un campo de `Protocol`/`Stimulus`/`Acquisition`/`Subject`. Los nombres, colores y etiquetas son los del dominio clínico, no los del struct Rust ni del DTO.
2. **Separación verdad‑fisiológica vs adquisición como núcleo pedagógico — y como invariante de seguridad reforzado por Tauri.** El estudiante **solo** ve `Recording`/`OddballRecording`/`AssrResult` (lo que el equipo *mediría*). La "verdad" (componentes, lesiones, diagnóstico, umbral real) vive en una `TruthSheet` que **reside en `tauri::State` del backend y nunca se serializa hacia el webview del alumno**, legible solo por el rol Docente (server‑side) y por el motor de scoring (Rust). **Invariante (testeado desde G0, como LISTA BLANCA estructural):** en Evaluación/OSCE, **todo payload del flujo del alumno se valida campo a campo** contra una lista blanca; el test falla si aparece *cualquier* campo de `TruthSheet` (`latencias_verdaderas`, `presentes`, `umbral_verdadero`, `curva_li_verdadera`, `lesiones`, `diagnostico`) o un `detected` no vacío. A diferencia de iced, no es "stripear un campo de un struct en memoria compartida": **el dato no cruza la frontera del proceso**. Que el mismo paciente "se vea distinto" según la configuración del equipo **es** la lección. *(Nota honesta: la verdad fisiológica vive en la `amplitudes_uv` de la waveform; el alumno puede correr su propia detección —es la lección—. El invariante protege contra fuga de la `TruthSheet` derivada, no contra que el alumno mida la señal que sí debe recibir.)*
3. **Reuso total de `aep-core`.** La GUI no duplica simulación, DSP ni normativos. Toda medición se apoya en la API pública (vía comandos Rust que envuelven el core). Los huecos se cubren **en el core** (§12), no parcheando en el frontend. **Excepción explícita:** V/I y SP/AP del informe/score se calculan desde las **marcas P‑V del alumno** (no con `v_i_ratio`/`sp_ap_ratio`, que miden amplitud absoluta desde línea base); el cálculo derivado vive en el frontend para readout y en Rust para el score con peso.
4. **Determinismo controlado.** Mismo caso + misma configuración + mismo `seed_salt` ⇒ misma curva. El `seed_salt` (por estudiante/intento, **guardado en `state` del backend y NUNCA serializado al alumno**, §11.B) habilita **variación de ruido en OSCE** y recompute de notas; sin salt, OSCE reproducible para auditoría docente. **Para recomputar la curva exacta hay que sellar también el conteo de parada** (`produced`/`accepted` al momento del Stop del alumno), no solo el `Protocol` (§11.B).
5. **No destructivo.** Re‑marcar, re‑filtrar, sumar/restar y comparar capturas guardadas sin recapturar. El marcado del alumno vive en el store del frontend, separado del `Recording`.
6. **Peso de evaluación alineado con lo que el motor mide bien.** Latencias e interpicos pesan alto (robustos). Amplitudes, V/I y SP/AP pesan bajo o cualitativo (limitación conocida: amplitud desde línea base, filtro IIR de fase no nula). Umbral del alumno se gradúa con tolerancia **≥ 1 paso (5–10 dB)**, nunca exacta. **Bandas normativas: peso 0 por defecto** hasta validación de SD (§9, §14).
7. **Modelo Tauri: comandos + eventos, frontera de proceso como límite de confianza** (reemplaza "Elm estricto"). El **backend Rust es la única fuente de verdad** de todo lo evaluable y sensible; el **frontend es una proyección reactiva** de estado no sensible. El frontend invoca `#[tauri::command]` (request/response) y recibe streaming por `tauri::ipc::Channel`; el backend emite eventos de ciclo de vida con `emit`. **Regla de oro de integridad:** si un dato es evaluable o sensible, su autoridad vive en `tauri::State` y no se serializa al alumno.
8. **i18n y accesibilidad de primera clase.** Toda string visible pasa por una capa de i18n del frontend con `Locale` (es‑CL por defecto: **coma decimal**, formato de fecha local; OD/OI con opción R/L). El backend emite **siempre números crudos `f64` y claves/enums estables**, nunca strings pre‑formateados (el JSON usa punto decimal; la coma es‑CL es responsabilidad del frontend al pintar). Codificación nunca **solo** por color: redundancia por etiqueta, forma y patrón de línea. Marcado operable por mouse, **teclado completo (Tab entre picos)** y **táctil** (Pointer Events).
9. **Reproducibilidad auditable.** Todo artefacto evaluable sella **versión de motor + versión de normativos + hash del caso + `seed_salt` + conteo de parada**, para recomputar la nota idéntica aunque cambien normas o casos. El artefacto firmado/verificable es el **JSON** del informe; el PDF es la vista humana. **Compatibilidad de esquema:** los DTOs sellados llevan un `schema_version`; ver §11.B para la política de migración.

---

## 3. Arquitectura de la GUI en Tauri 2

Aplicación de escritorio **Tauri 2.x** (fijar el último parche 2.x): proceso **backend Rust** (el "src‑tauri") que posee la verdad y el motor, y un **webview** que renderiza una SPA estática (sin SSR) servida por Vite. La comunicación es por **IPC tipado** (comandos + eventos + `Channel`).

**Por qué Tauri 2.x (no 1.x):** (1) modelo de seguridad por *capabilities/permissions* que refuerza la separación verdad/ciego por ventana; (2) `tauri::ipc::Channel<T>` para la captura progresiva en **streaming ordenado** de alto throughput (no existe en v1); (3) raw IPC (`tauri::ipc::Request`/`Response` + `ArrayBuffer`) para arreglos grandes de muestras sin pagar JSON; (4) **tauri‑specta v2** (requiere Tauri 2 + Specta 2) para tipado TS end‑to‑end de **comandos y eventos**. **Riesgo de borde a validar en G0‑spike:** tipar `Channel<T>` como **parámetro** de comando vía tauri‑specta es el punto más áspero de specta v2.

### 3.1 Workspace y crates

- **`aep-core`**: se le **añade `derive(Serialize)`** en el dominio (ya depende de `serde`). Sigue **sin** dependencias de GUI ni de `specta`. La ceguera se hace por **proyección** en `simpeatc-tauri`, no por ausencia de `Serialize` (§0.2).
- **NUEVO crate `crates/simpeatc-tauri`** (layout src‑tauri) en el workspace, depende de `aep-core`. Es el backend de la app.
- **`crates/simpeatc-gui`** (iced) se **archiva** (se saca de `members` o se marca legacy).
- **Frontend** Vite (TS) en `/src` de la raíz del repo. `@tauri-apps/api` **exactamente en la misma versión** que el crate `tauri`.

```
simPEATC/
├── Cargo.toml                  # workspace: aep-core, simpeatc-tauri
├── crates/
│   ├── aep-core/               # + derive(Serialize) en dominio; SIN specta/GUI
│   └── simpeatc-tauri/         # "src-tauri": backend Tauri
│       ├── Cargo.toml          # tauri, aep-core, serde/serde_json, hmac, sha2,
│       │                       #   specta, tauri-specta; [build-deps] tauri-build
│       ├── build.rs            # tauri_build::build()
│       ├── tauri.conf.json     # devUrl, frontendDist, CSP, bundle, ventanas
│       ├── capabilities/       # *.json scopeados por LABEL de ventana
│       ├── icons/
│       └── src/
│           ├── main.rs         # arranque, Builder, invoke_handler, setup(manage)
│           ├── lib.rs          # run(): wiring de comandos/eventos/estado
│           ├── commands.rs     # #[tauri::command] (ver §4.3)
│           ├── events.rs       # MensajeCaptura (Channel), eventos de ciclo de vida
│           ├── state.rs        # AppState (Mutex<SesionInterna>): verdad, seed_salt,
│           │                   #   rol docente, capturas en curso, hmac_key, OSCE
│           ├── proj.rs         # PROYECCIÓN ciega (Recording -> RecordingDto) + specta
│           ├── dto.rs          # DTOs finos SOLO donde hay stripping/specta::Type
│           ├── truth.rs        # TruthSheet (NUNCA se serializa al alumno)
│           ├── scoring.rs      # rúbrica/scoring contra TruthSheet (Rust)
│           ├── sesion.rs       # sellado + HMAC + cronómetro OSCE monótono
│           ├── captura.rs      # CaptureSession + hilo + cancelación
│           └── strip.rs        # lista blanca de proyección + tests invariante
├── src/                        # FRONTEND (Vite + Svelte 5 + TS)  (ver §3.3)
├── package.json                # pnpm; @tauri-apps/api, svelte, vite, uplot, pdfmake
└── vite.config.ts
```

### 3.2 Backend Rust (autoridad)

- **Arranque:** `Builder::default().setup(|app| { app.manage(AppState::default()); Ok(()) }).invoke_handler(tauri::generate_handler![...]).run(...)`. Con tauri‑specta se usa `collect_commands!`/`collect_events!` para emitir `bindings.ts`.
- **Estado en `tauri::State`** (ver §4.2): la verdad, el `seed_salt`, el `CaseDef`, el rol docente desbloqueado, los flags de captura, la clave HMAC y el cronómetro OSCE monótono. Inyección por parámetro `state: tauri::State<'_, AppState>`; **nunca** viaja por IPC.
- **No congelar el runtime:** el DSP (`simulate`/`CaptureSession`) es CPU‑bound ⇒ se ejecuta en `tauri::async_runtime::spawn_blocking` o un hilo dedicado, **nunca** en el handler async. El comando retorna de inmediato (p.ej. el `capture_id`) y el hilo sigue emitiendo por el `Channel`. **La matriz ASSR freq×intensidad (N FFTs) también va a `spawn_blocking`** (§6, §14).
- **Regla del Mutex:** `std::sync::Mutex` para estado en memoria; **nunca** sostener el `MutexGuard` a través de un `.await` (lock → copiar/clonar lo necesario → drop → recién await/spawn). Cuidado con el envenenamiento por panic.
- **Proyección ciega:** ningún comando del flujo del alumno serializa el dominio crudo con verdad; las **funciones de proyección** (`proj.rs`) producen los DTOs ciegos aplicando el stripping de `detected` **antes** de retornar en Evaluación/OSCE. La proyección está cubierta por el test de lista blanca (§11.B).

### 3.3 Frontend (proyección reactiva)

**React 18 + Vite + TypeScript**, SPA estática (sin SSR). Reactividad por hooks (`useState`/`useMemo`/`useReducer`) + Context para estado global; la tabla de métricas se recalcula sola al arrastrar un marcador vía `useMemo` sobre el store de marcado. Theming clínico con CSS variables. El gráfico usa **ECharts** (`echarts-for-react`) para las trazas, con una **capa de interacción** (overlay DOM o `graphic` arrastrable de ECharts) para el drag de picos; ver §5.

```
src/
├── main.tsx                # bootstrap React (ReactDOM.createRoot)
├── App.tsx                 # shell + router de pantalla (estado, sin SSR)
├── lib/
│   ├── ipc/                # ÚNICO módulo que importa @tauri-apps/api
│   │   ├── commands.ts     #   wrappers de invoke (usa bindings.ts generado)
│   │   ├── channel.ts      #   Channel<MensajeCaptura> de captura progresiva
│   │   └── events.ts       #   listen() de ciclo de vida (autosave, OSCE tick)
│   ├── types/              # bindings.ts GENERADO por tauri-specta (versionado)
│   ├── i18n/               # catálogos es-CL (react-i18next o catálogo propio)
│   ├── format/             # formatNum/formatLat/formatAmp + parseNumEsCl (coma)
│   └── plot/               # gráfico clínico (§5)
│       ├── chart.ts        #   builder de `option` ECharts + escalas + markArea
│       ├── plano.ts        #   transform data<->pixel (convertToPixel/convertFromPixel) + offset stacking
│       ├── overlay.ts      #   marcadores ARRASTRABLES (overlay DOM / graphic ECharts)
│       └── stacking.ts     #   offset_y MANUAL (pre-suma datos; resta en hit-test)
├── stores/                 # estado UI (no sensible): Context + reducer o Zustand
│   ├── examen.ts               # config equipo, capturas visibles
│   ├── vista.ts                # zoom/pan/base de tiempos/µV-div
│   ├── marcado.ts              # PeakMarks del alumno (mientras edita)
│   ├── cursores.ts             # readout/medición
│   ├── sesion.ts               # progreso, borrador (sin verdad)
│   ├── rolModo.ts              # rol/modo (visibilidad; la compuerta real es Rust)
│   └── locale.ts               # idioma, OD/OI vs R/L
├── components/             # PanelEquipo, PanelImpedancia, BarraMetricasLive,
│   └── ...                 #   TablaPicos, ReadoutCursor, LeyendaCurvas, ...
└── screens/                # Inicio, Catalogo, ConfigPaciente, Examen,
                            #   Audiometria, Informe, Revision  (*.tsx)
```

**Reglas del frontend:**
- **Gateway IPC único:** ningún componente llama `invoke`/`listen`/`Channel` directamente; todo pasa por `src/lib/ipc`. Centraliza el contrato y permite **mockear el IPC** (`@tauri-apps/api/mocks`) en tests sin backend real.
- **Pantallas** (mapean §6/§8/§9): Inicio (selector rol/modo), Catalogo (ficha ciega), ConfigPaciente (docente), Examen (estación principal), Audiometria, Informe, Revision (rúbrica docente). Router por estado de pantalla (o `react-router` en modo memoria/hash); **nada de SSR ni navegación de archivos**.

### 3.4 Tipado TS end‑to‑end (sin drift)

- **tauri‑specta v2** como fuente única de verdad: `#[specta::specta]` en cada comando, `collect_commands!`/`collect_events!`, exporter que emite `src/lib/types/bindings.ts` con **comandos y eventos/Channels tipados**.
- **No** se mete `specta::Type` dentro de `aep-core` (lo ensucia). `aep-core` solo gana `Serialize`. Los **DTOs finos** de `simpeatc-tauri/dto.rs` derivan `Serialize + specta::Type` **solo donde** hace falta tipar o stripear; lo demás cruza como el tipo crudo serializado vía proyección.
- **Convenciones serde:** `#[serde(rename_all = "camelCase")]`; enums con `tag`/`content` para *discriminated unions* limpias (`DatosCaptura → Transitorio | Oddball | Assr`).
- `bindings.ts` se **commitea** y un check de CI falla si quedó desactualizado (regenerar + `git diff --exit-code`).

---

## 4. Modelo de datos: lo que cruza el IPC, el estado del backend y el del frontend

Tres capas: **(A) lo que cruza la frontera** (dominio crudo `Serialize` + DTOs finos donde hay stripping), **(B) estado autoritativo en Rust** (no cruza), **(C) estado de UI en el frontend** (TS). Más la **lista de comandos y eventos**.

### 4.1 Lo que cruza el IPC (Rust → TS)

`aep-core` ahora deriva `Serialize` en el dominio. La ceguera se logra por **proyección** (`proj.rs`); los DTOs finos existen **solo** donde hay stripping/`specta::Type`.

```rust
// proj.rs — proyección ciega: NO arrastra TruthSheet. Stripping de `detected` server-side.
#[derive(Serialize, specta::Type)] #[serde(rename_all = "camelCase")]
pub struct RecordingDto {              // detected VACÍO en Eval/OSCE (proyección)
    pub channels: Vec<WaveformDto>,    // Waveform{times_ms, amplitudes_uv} del core
    pub detected: Vec<WavePeakDto>,    // [] salvo Práctica con Suggest
    pub fsp: f64, pub rejected_sweeps: u32,
}
// times_ms se manda UNA sola vez (al consolidar / en Iniciada del Channel);
// los snapshots de captura solo llevan `muestras` (ver §4.4).

#[derive(Serialize, specta::Type)] #[serde(tag = "tipo", content = "datos",
    rename_all = "camelCase")]
pub enum DatosCapturaDto {
    Transitorio(RecordingDto),
    Oddball(OddballRecordingDto),      // 3 trazas: standard/deviant/difference
    Assr { result: AssrResultDto, espectro: Vec<f64>, binFmod: usize }, // gap #7
}

#[derive(Serialize, specta::Type)] #[serde(rename_all = "camelCase")]
pub struct CasoResumenDto { id: String, demografia: DemografiaDto, motivo: String }
                                       // CIEGO: sin lesiones/diagnóstico/name docente
#[derive(Serialize, specta::Type)]
pub struct VistaCiegaCaso { resumen: CasoResumenDto } // SIN seed_salt (queda backend-only)

#[derive(Serialize, specta::Type)]     // resultado de scoring (corre en Rust)
pub struct ResultadoRubrica { /* por_dimension, global, items, version_motor,
                                 version_normas, hash_caso, schema_version */ }
```

```rust
// Hacia Rust (TS → comandos): config del alumno y marcas. NUNCA verdad.
#[derive(Deserialize, specta::Type)] #[serde(rename_all = "camelCase")]
pub struct ProtocolDto { /* espejo de Protocol/Stimulus/Acquisition del core */ }

#[derive(Deserialize, Serialize, specta::Type)] #[serde(rename_all = "camelCase")]
pub struct PeakMarkDto { label: String, pico_ms: f64, pico_uv: f64,
                         valle_ms: Option<f64>, valle_uv: Option<f64>,
                         conv: ConvAmplitud, auto: bool }
pub enum ConvAmplitud { PicoATrough, PicoALineaBase }
```

**Qué cruza realmente:**
- **Hacia el alumno →** `RecordingDto` (`detected` stripeado en Eval/OSCE), `OddballRecordingDto` (3 trazas), `AssrResultDto` (+ espectro/bin, gap #7), y `CasoResumenDto`/`VistaCiegaCaso` **(sin `seed_salt`)**.
- **Hacia Rust ←** `ProtocolDto` del alumno, `PeakMarkDto[]`, informe (borrador), `ActionLog`.
- **NUNCA cruza →** `TruthSheet`/`Lesion`/diagnóstico/`umbral_verdadero`/`seed_salt`/`hmac_key`.

### 4.2 Estado autoritativo en Rust (`tauri::State`, no cruza el IPC)

```rust
type AppState = std::sync::Mutex<SesionInterna>;   // alias; Tauri pone el Arc

struct SesionInterna {
    caso: Option<aep_core::CaseDef>,
    truth: Option<TruthSheet>,            // VERDAD. NO se serializa.
    seed_salt: u64,                       // backend-only; NUNCA al alumno
    modo: Modo,
    rol_docente_desbloqueado: bool,       // compuerta server-side (PIN hash); auto-relock
    capturas_en_curso: std::collections::HashMap<u64, std::sync::Arc<std::sync::atomic::AtomicBool>>,
    hmac_key: [u8; 32],                   // jamás en JS/webview
    inicio_osce: Option<std::time::Instant>, // cronómetro monótono
    action_log: Vec<AccionExamen>,        // log autoritativo (D5)
}
```
> Identidad por tipo: `manage()` guarda un valor por tipo `T`; si hubiera varios estados, usar newtypes (`struct VerdadState(...)`, `struct CapturaState(...)`).

```rust
// Sellada en el backend; SOLO scoring/rol docente la leen. NUNCA serializada al alumno.
struct TruthSheet {
    latencias_verdaderas: Vec<(String, f64, f64)>,   // label, latencia, amplitud
    presentes: Vec<(String, bool)>,                  // por DETECTABLE_UV sobre componente
    umbral_verdadero: f64,
    curva_li_verdadera: Vec<(f64, f64)>,
    lesiones: Vec<aep_core::Lesion>,
    diagnostico: String,
    version_motor: String, version_normas: String,
}

enum AccionExamen {                       // procedimiento (D5), reloj monótono en Rust
    ImpedanciaChequeada { ok: bool },
    Capturada { ear: aep_core::Ear, db: f64, sweeps: u32, replica: Replica },
    DetenidaCaptura { produced: u32, accepted: u32 }, // conteo de parada (reproducibilidad)
    Reconfigurada { campo: String },
    Enmascaramiento { activado: bool, nivel_db: f64 },
}
```

### 4.3 Lista de comandos `#[tauri::command]`

Cada comando es `async fn ... -> Result<DtoSalida, AppError>` con `AppError: Serialize`; `state` se inyecta y no viaja. Cómputo pesado a `spawn_blocking`.

| Comando | Firma (resumen) | Rol/Integridad |
|---|---|---|
| `listar_casos` | `() -> Vec<CasoResumenDto>` | Catálogo **ciego** (proyecta `CaseCatalog::embedded()` sin verdad). |
| `cargar_caso` | `(id, modo, seed_salt, state) -> VistaCiegaCaso` | Inicializa sesión; **precomputa y guarda `TruthSheet` y `seed_salt` en `state`**; retorna solo la vista ciega (**sin salt**). |
| `simular` | `(config: ProtocolDto, state) -> RecordingDto` | "Capturar de golpe" (G1). `spawn_blocking(EvokedPotentialEngine::simulate)`. **Stripping de `detected`** vía proyección en Eval/OSCE. |
| `iniciar_captura` | `(config, on_event: Channel<MensajeCaptura>, state) -> u64` | Captura progresiva (§5). Crea `CaptureSession` con el `seed_salt` de `state`; hilo emite snapshots. Devuelve `capture_id`. |
| `detener_captura` | `(capture_id, state) -> ConteoParada` | Activa el `AtomicBool`; el hilo sale limpio; **registra `produced`/`accepted` en el `ActionLog`** (reproducibilidad). |
| `estimar_umbral` | `(marcas_serie, state) -> UmbralDto` | Desde las **marcas del alumno**. Reusa `aep-core`. |
| `construir_li` | `(marcas_serie) -> Vec<(f64,f64)>` | Curva latencia‑intensidad desde marcas. |
| `ajustar_pico` | `(t_ms, ventana, max: bool) -> PeakMarkDto` | Snap a extremo local: `Waveform::find_extremum_in`/`amplitude_at`; devuelve pico + valle. |
| `calcular_scoring` | `(marcas, config_alumno, informe, action_log, state) -> ResultadoRubrica` | **Corazón de integridad.** Corre en Rust contra la `TruthSheet`. Gateado por modo/rol. Solo cruza `ResultadoRubrica`. |
| `autoguardar` | `(borrador: SesionDraft) -> ()` | Persiste el store del frontend **sin verdad** (~30 s). |
| `generar_pdf` / `guardar_pdf` | `(bytes) -> ruta` | El frontend genera los bytes (pdfmake); Rust los escribe (plugin fs/dialog). |
| `exportar_json` / `_csv` / `_gradebook` | `(...) -> bytes/ruta` | Export; gradebook de cohorte OSCE. |
| `docente_desbloquear` | `(pin, state) -> bool` | Verifica hash del PIN y marca rol docente en `state`. |
| `docente_relock` | `(state) -> ()` | **Auto‑relock** del rol docente (al cambiar de modo/ventana/handoff de alumno). |
| `ver_verdad` | `(state) -> Result<TruthSheetDto, AppError>` | Retorna verdad **solo si `state` indica rol docente**; si no, `Err`. |
| `sellar_sesion` | `(state) -> SesionSellada` | HMAC‑SHA256 de marcas+tiempos+config+**conteo de parada** con clave del backend. |

### 4.4 Eventos y `Channel`

- **Curva que emerge → `tauri::ipc::Channel<MensajeCaptura>`.** El motivo de usar `Channel` (no `emit/listen`) es **throughput/backpressure y entrega tipada con orden garantizado**, no que `emit` desordene (los eventos también llegan en orden por el IPC; esa afirmación del v1 estaba sobredicha). Para una curva que crece, el throughput y el orden son críticos.
  ```rust
  #[derive(Clone, Serialize, specta::Type)]
  #[serde(rename_all = "camelCase", tag = "event", content = "data")]
  enum MensajeCaptura {
      Iniciada  { objetivo: u32, times_ms: Vec<f64> }, // eje X UNA sola vez
      Parcial   { n: u32, fsp: f64, aceptados: u32, rechazados: u32,
                  muestras: Vec<f32> },     // SOLO Y, DECIMADO al ancho en píxeles
      Finalizada { n: u32 },
  }
  ```
  > **Corrección técnica (§14 #7):** `f32` **NO** abarata el JSON (un `f32` y un `f64` ocupan lo mismo como string decimal). La **única palanca real** del streaming es **decimar al ancho en píxeles** (~500–1000 pts) antes de mandar. `f32` solo ayuda en canal **binario** (`ipc::Response`/`ArrayBuffer`), reservado para export de épocas crudas. El eje X (`times_ms`) se manda **una sola vez** en `Iniciada` (la rejilla es constante).

  Frontend: `const ch = new Channel<MensajeCaptura>(); ch.onmessage = (m) => coalescer(m); await invoke('iniciar_captura', { config, onEvent: ch });`
- **`emit/listen` solo para ciclo de vida** (no la curva): autosave hecho, tick del cronómetro OSCE, sesión sellada, fin de estación. `emit_to` por **label de ventana**.
- **Cadencia/backpressure:** **no** emitir un mensaje por sweep. Snapshots a **~20–30 fps** agrupando N sweeps; el frontend **coalesce** (pinta el último snapshot en `requestAnimationFrame`, descarta intermedios).

### 4.5 Estado de UI en el frontend (stores TS, NO en Rust)

Todo lo puramente de UI y *work* no sensible: zoom/pan/base de tiempos/µV‑div (la `Vista`), selección de pico, cursores/readout, **marcas del alumno mientras edita**, qué capturas están visibles/colores/dash, idioma y formato es‑CL, borrador del informe, `ActionLog` de UI. Las marcas se mandan a Rust **solo** cuando hay que puntuar/exportar/sellar. El estado autoritativo de Rust se **reconstruye desde caso+config+seed_salt+conteo de parada** por determinismo.

```ts
// vista.svelte.ts — base de tiempos y ganancia, independientes del modelo
class Vista { tMinMs=$state(-1); tMaxMs=$state(10); uvPorDiv=$state(0.2);
              panUv=$state(0); gananciaPorCurva=$state<Map<number,number>>(new Map()); }

// marcado.svelte.ts — PeakMark del alumno (par pico-valle), no destructivo
interface PeakMark { label:string; picoMs:number; picoUv:number;
                     valleMs?:number; valleUv?:number;
                     conv:'PicoATrough'|'PicoALineaBase'; auto:boolean; }

// examen.svelte.ts — capturas visibles (proyección, NO fuente de verdad evaluable)
interface Captura { id:number; ear:'OD'|'OI'; intensidadDb:number;
                    replica:'A'|'B'|'Promedio'; datos:DatosCapturaDto;
                    marcas:PeakMark[]; visible:boolean; color:string;
                    dash:number[]; offsetY:number; } // offsetY se PRE-SUMA a los datos (§5)
```

---

## 5. El gráfico clínico interactivo (ECharts + capa de marcadores arrastrables)

**Stack: ECharts (`echarts-for-react`, render Canvas) para las trazas + capa de interacción para marcadores ARRASTRABLES** (picos/valles/cursores). Razones de la decisión vigente (React+ECharts):

1. **Robustez multi‑webview de Tauri:** ECharts en modo **Canvas** (no SVG, no WebGL) es estable en WebView2 (Windows), WKWebView (macOS) y WebKitGTK (Linux). **Se evita WebGL** (frágil en WebKitGTK/Linux).
2. **Drag/zoom/pan de fábrica:** ECharts trae `dataZoom`, `markArea`/`markLine` y `graphic` arrastrable (`draggable:true`) — menos código manual de interacción que con un canvas crudo.
3. **Ajuste al modelo del plan:** multi‑serie nativa, ejes value/time, `markArea` para bandas normativas, y `convertToPixel`/`convertFromPixel` que **son exactamente el "Plano" data↔pixel**. Sincronización de dos instancias (split OD/OI) con `echarts.connect`.

*Coste asumido (corrección §14):* ECharts cuesta más CPU/RAM que uPlot en captura en vivo. **Mitigación obligatoria:** decimar al ancho en píxeles antes de pintar, `setOption(..., {lazyUpdate:true, silent:true})` reutilizando la instancia (nunca recrearla por tick), y coalescing en `requestAnimationFrame`. **Validación en G0‑spike:** sostener ~20–30 fps de captura en WebKitGTK. Si no rinde, uPlot queda como alternativa documentada (la capa `plot/plano.ts` aísla el motor de gráfico para poder cambiarlo).

> **Trabajo manual de coordenadas:** el **stacking** vertical por serie se hace **pre‑sumando el `offsetY` a los datos** de cada serie; el overlay debe **restar ese offset** en `convertFromPixel` para readout/hit‑test. El **split OD/OI** usa dos instancias ECharts conectadas con `echarts.connect([od, oi])`. Todo esto se encapsula en `plot/plano.ts` y `plot/stacking.ts` para que el resto del código vea un "Plano" coherente.

### 5.1 El "Plano" data↔pixel y reuso para PDF

El transform usa `echartsInstance.convertToPixel`/`convertFromPixel`, **más la corrección del offset de stacking**, envuelto en `src/lib/plot/plano.ts` para que **el mismo cálculo sirva en pantalla, hit‑test y redibujo del informe** (PDF). El `Plano` respeta el zoom/pan vigente (`dataZoom`). Para el PDF el gráfico se exporta a **PNG hi‑res (`echartsInstance.getDataURL()` / `canvas.toDataURL`) como ruta primaria** (§10) — no se reimplementa un segundo motor de coordenadas.

### 5.2 Marcadores arrastrables (capa overlay DOM/SVG)

Cada pico/cursor es un objeto del **store del frontend** (`PeakMark`). La capa es **overlay DOM/SVG**: `<div>`/`<g>` con `position:absolute` reposicionados en los hooks `draw`/`setScale`/`setSize` de uPlot con `valToPos`. Ventajas frente a "todo‑canvas": **foco de teclado gratis** (`tabindex`), **Pointer Events** unificados (mouse + táctil + lápiz), **ARIA**, y **edición de etiqueta** con input flotante real.

- **Hit‑test:** al `pointerdown`, marcador más cercano dentro de un radio en px (**≥ 25 px en táctil**). Guardar `arrastre = {idx, modo}` (`Pico | Valle | CursorLatencia | Pan`). `setPointerCapture` en el handle.
- **Drag:** en `pointermove`, `posToVal(px)` (con resta de offset de stacking) ⇒ `(t_ms, uv)`; actualizar en el store (drag **optimista**, repintado en `rAF`). En `pointerup`, soltar y confirmar.
- **Snap al extremo local:** al soltar (o en vivo con debounce), enviar `t_ms` a `ajustar_pico` ⇒ Rust llama `Waveform::find_extremum_in`/`amplitude_at` y devuelve pico ajustado **y su par valle**. La verdad del ajuste vive en Rust.
- **Par pico‑valle (gap #14):** cada marca arrastra pico y opcionalmente valle según `trough_for(label)` del core; convención `PicoATrough`/`PicoALineaBase` alternable. La amplitud P‑V se **recalcula en el backend**.
- **Crear/borrar:** click/tap en zona vacía ⇒ nueva marca; arrastrar fuera o `Supr` borra. No destructivo.
- **Reposición en zoom/pan/resize:** re‑ejecutar el layout del overlay en `setScale`/`setSize` (o `ResizeObserver`).

### 5.3 Zoom / pan / base de tiempos / ganancia (anti‑fricción)

El store `Vista` muta y se aplica con `u.setScale('x',{min,max})` / `u.setScale('y',{min,max})`:
- Rueda o botones ⇒ zoom de tiempo / µV‑div; arrastre con botón medio/espacio o gesto de dos dedos ⇒ pan.
- **Ganancia por curva** (`gananciaPorCurva`) con `offset/escala` por serie para comparar trazas dispares.
- Reset a la ventana del `Protocol`.

### 5.4 Readout numérico de cursor

Componente `ReadoutCursor` (HTML, fuera del canvas) muestra en vivo **latencia y amplitud bajo el cursor**, formateadas con el `Locale` (coma decimal: "5,6 ms / 0,32 µV").

### 5.5 Accesibilidad y teclado de primera clase

`Tab`/`Shift+Tab` navegan picos (roving `tabindex`); flechas o `Ctrl+flechas` mueven el pico enfocado (1 px / 0,1 ms); `1‑5` etiquetan I–V (o P1/N1…); `Supr` borra; `Enter` edita etiqueta. **Toda acción de mouse tiene equivalente de teclado.** Cada marcador con `role`/`aria-label` ("Onda V, 5,6 ms, 0,32 µV, dentro de banda"). Pointer Events para un solo codepath.

### 5.6 Capas, overlay multi‑curva, stacking y bandas

- **Dos capas de render:** uPlot pinta la *capa estática* (rejilla, eje cero, trazas, **bandas normativas**, etiquetas dB del stacking); el *overlay dinámico* (marca arrastrándose, cursor, readout) es DOM/SVG. No recrear la instancia uPlot por tick: `setData()` reusa buffers.
- **Overlay multi‑curva con redundancia no‑cromática:** color por oído (OD rojo / OI azul) **y** patrón de línea (`dash`) + sufijo textual "OD"/"OI" + forma de marcador. **Réplica A sólida vs B punteada.**
- **Stacking por intensidad descendente:** `offsetY` **pre‑sumado a los datos** (no propiedad nativa) + etiqueta dB nHL a la izquierda; el overlay resta el offset. Una sola gráfica = un solo redibujo. **Split OD/OI:** dos uPlot con `cursor.sync`; zoom‑Y cableado manualmente.
- **Bandas normativas con estado de validación (§9, §14):** región sombreada por onda con `WaveNorm.latency_ms ± k·latency_sd_ms` corrida por intensidad con `SHIFT_PER_10DB` (`norm_band`, gap #4), dibujada como **band** estática. El estado `BandaEstado` rige su uso:
  - `Off`: no se dibujan.
  - `ReferenciaNoValidada`: se dibujan con marca de agua "referencia, no validada"; **peso 0 en scoring**. **Estado por defecto y entregable** hasta tener SD revisadas por el investigador (David Ávila).
  - `ValidadaConPeso`: solo cuando el investigador valida la SD; habilita peso en scoring.
- **Captura progresiva animada:** `Channel` entrega `Parcial`; `onmessage` guarda el último snapshot y repinta en `rAF` (coalescing), `u.setData(...)`. Al `Finalizada`, se consolida. **Start/Stop/Pause** vía `iniciar_captura`/`detener_captura`.
- **Sub‑modos por modalidad:** **3 trazas oddball** y **espectro ASSR** (`power_spectrum` µV² vs Hz con marca en `bin_fmod`; la matriz frecuencia×intensidad PASS/REFER es **tabla HTML** y **corre en `spawn_blocking`** —N FFTs— con feedback de progreso).

---

## 6. Cobertura de modalidades

**Una sola Estación parametrizada por la modalidad activa.** Al cambiar de modalidad solo cambian: el constructor de `Protocol`, el set de etiquetas, la salida del motor (`DatosCapturaDto`) y la vista del gráfico. Gráfico, drag, cursores, zoom, stacking y bandas se reusan.

| Modalidad | Constructor `Protocol` | Motor (comando) | Etiquetas | Vista | Medición clave | Defaults UI |
|-----------|------------------------|-------|-------------------|-------|----------------|-------------|
| **ABR click** | `abr_click(ear)` | `simular` | I, II, III, IV, V | Stacking / Split / Overlay | interpicos I‑III/III‑V/I‑V, V/I (P‑V), umbral | -1..10 ms, 100–3000 Hz |
| **ABR tone‑burst** | `abr_toneburst(ear,freq)` | `simular` | I–V | Stacking | umbral por frecuencia, L‑I | 500/1000/2000/4000 |
| **ABR chirp** | `abr_chirp(ear,kind)` / `abr_nbchirp(ear,freq)` | `simular` | I–V | Stacking | umbral, screening | CE/LS/NB‑Chirp |
| **ECochG** | `ecochg(ear)` | `simular` | SP, AP | Overlay | SP/AP (P‑V, desde marcas) | 0.5..5 ms, electrodo TT/TM/EAC |
| **MLR** | `mlr(ear)` | `simular` | Na, Pa, Nb, Pb | Stacking | latencias; estado/edad | 10..90 ms |
| **ALR/CAEP** | `alr(ear)` | `simular` | P1, N1, P2, N2 | Stacking | latencias; estado/atención | 50..350 ms |
| **P300** | `p300(ear)` | **`simular_oddball`** | P3a, P3b | 3 trazas oddball | P3b (Active) | oddball, 0.1–30 Hz |
| **MMN** | `mmn(ear)` | **`simular_oddball`** | MMN | 3 trazas oddball | MMN sobre diferencia (Passive) | oddball |
| **ASSR** | `assr(ear,carrier,modfreq)` / `assr_default(ear)` | **`simular_assr`** | (sin picos) | Espectro + matriz | `f_ratio`, `snr_db`, detectado | 40 Hz cortical / 80 Hz tronco |

**Reglas críticas de modalidad:**
- P300/MMN **deben** usar `simular_oddball` (no `simular`) para las 3 trazas.
- ASSR usa `simular_assr`; el espectro viene del `AssrResultDto` enriquecido con `power_spectrum` + `bin_fmod` (gap #7). La **matriz frecuencia×intensidad** (PASS/REFER por bin con F‑ratio > F‑crit) corre en **`spawn_blocking`** (N llamadas a `detect_assr`, una FFT por celda) con barra de progreso; se arma como **tabla HTML**.
- Corticales/cognitivos: el docente fija `ArousalState`/`Attention` como parte de la verdad (Sedated/NaturalSleep atenúan MLR/ALR; `Ignoring` borra P3b y conserva MMN; `Active` realza).

**Convención pico‑a‑valle (codificada, gap #14):** cada etiqueta tiene un **trough asociado** en el core. La medición P‑V usa `find_extremum_in` vía `ajustar_pico`. La UI alterna `PicoATrough`/`PicoALineaBase`.

**Pantalla Audiometría:** (a) curva latencia‑intensidad de la onda V construida con la **V marcada** por el alumno (`construir_li`/`estimar_umbral`, no `latency_intensity_curve` sobre la verdad), con banda normativa y flecha de umbral; (b) audiograma estimado por frecuencia con `estimate_audiogram` (tone‑burst), `estimate_audiogram_chirp` (NB‑chirp) y `assr_audiogram` (ASSR), con símbolos OD/OI **+ redundancia no‑cromática**.

---

## 7. Modelo del "paciente" y autoría del docente

**Un paciente = un `Subject` completo + una o más "órdenes" (modalidades, con oído e intensidades) + metadatos didácticos.** El docente declara la **causa**; el motor deriva la fisiología determinista.

> **Bloqueo de §12.A #12 (re‑dimensionado contra el código):** **`Lesion.ear` ya existe** (`lesion.rs:74`). Lo que colapsa el oído es **`CaseDef::subject()`** (`cases.rs:147`), que sobreescribe `ear` con `self.ear()` para todas las lesiones, más el esquema **mono‑oído/mono‑modalidad/mono‑intensidad** de `CaseDef` (campos `String` para `modality`/`ear`, `lesions` privado). El trabajo de core es **menor en el tipo `Lesion`** y se concentra en **el esquema de `CaseDef` + lista de órdenes + dejar de sobreescribir `ear`**. Hasta implementarlo, la autoría se restringe a mono‑oído y se documenta la limitación.

Mapeo directo (pantalla `ConfigPaciente`, **solo rol docente**):
- **Editor de Sujeto:** `Age` (`Gestational{weeks}`/`Postnatal{days}`/`Years{value}`), `Sex`, `temperature_c`, `ArousalState`, `Attention`. Validación de rangos plausibles.
- **Editor de Lesiones por oído (gap #12):** lista editable de `Lesion` **respetando su `ear` existente**; por fila `site` + `severity_db` + `freq_profile`. Ayuda visual: **audiograma esperado** por oído derivado de `threshold_shift_at(freq)`, **sin** mostrar la curva ABR.
- **Editor de órdenes (gap #12):** lista de modalidades a examinar, cada una con oído(s) e intensidad inicial.
- **Catálogo:** `CaseCatalog::embedded()` (19 casos) como punto de partida; el docente clona/edita. `name`/`description`/`lesions` se muestran **solo** al docente (`ver_verdad` gateado).
- **Previsualización docente (exclusiva):** botón que ejecuta `simular*` con un `Protocol` de referencia y muestra curva + `detected` + audiograma + L‑I + umbral, para **validar** el caso (comando que exige rol docente en `state`).
- **Plantilla de equipo "ideal":** el docente fija el `Protocol`/`Stimulus`/`Acquisition` correcto = referencia de rúbrica (D1) **y un rango de procedimiento aceptable** para D5.
- **Ocultar la verdad (invariante §2):** al publicar/cargar el caso, `cargar_caso` precomputa una `TruthSheet` (latencias/amplitudes, **presencia por `DETECTABLE_UV`**, umbral con `estimate_threshold`, curva L‑I, versiones) y la **guarda en `tauri::State`**. **Ningún comando del flujo del alumno la retorna**; el alumno recibe solo `VistaCiegaCaso` (sin `seed_salt`). La verdad **no cruza el IPC**.

El rol Estudiante **nunca** invoca `model_for`/`Component`/`generator`.

---

## 8. Modos de funcionamiento

| Aspecto | Práctica / Libre | Evaluación | OSCE |
|---------|------------------|------------|------|
| **Verdad del caso** | Visible (solo rol docente, vía `ver_verdad`) | **No cruza el IPC** | **No cruza el IPC** |
| **`detected` en `RecordingDto`** | Presente (Suggest) | **Vacío** (proyección) | **Vacío** |
| **`seed_salt`** | Backend-only | Backend-only | Backend-only (nunca al alumno) |
| **Anonimización** | No | Sí (Paciente N + motivo) | Sí (totalmente anónimo) |
| **`Suggest` de picos** | Activo (solo `DETECTABLE`) | Off | Off |
| **Bandas normativas** | Según `BandaEstado` (peso 0 por defecto) | Configurable (no validadas no puntúan) | Configurable |
| **Cronómetro** | No | No | Sí, **monótono** (`Instant` en Rust), por estación, auto‑avance |
| **Variante de ruido** | — | `seed_salt` por intento | `seed_salt` por estudiante (obligatorio) |
| **Flujo obligatorio** | Libre | impedancia→estímulo/adq→captura→réplica A/B→marcado→informe | Igual, exigido |
| **Feedback** | Inmediato | Diferido al entregar | Oculto al alumno; visible al docente al cerrar |
| **Cambio de modo / ver verdad** | Lock por PIN (server‑side) | Lock por PIN (server‑side) | Lock por PIN (server‑side) |
| **Auto‑relock docente** | Al cambiar de modo / handoff de alumno / cambio de ventana | Idem | Idem |
| **Persistencia** | Borrador + autosave | Resultado sellado + HMAC + **conteo de parada** | Idem + tiempos por estación |

Implementación: el `modo`/`rol` viven en `state` (Rust) **y** se reflejan en el store del frontend para visibilidad, **pero la compuerta real es server‑side**: los comandos sensibles (`ver_verdad`, `calcular_scoring`, previsualización docente) verifican el rol en `state` y devuelven `Err` si no, y `simular`/`iniciar_captura` aplican el stripping según `modo`. **Auto‑relock obligatorio** del rol docente al cambiar de modo, cerrar sesión de alumno o cambiar de ventana, para evitar fuga por estado pegajoso. **OSCE** añade `Vec<EstacionOsce>` con cronómetro **monótono** en Rust (§11.B). Aunque un alumno manipule el webview, **el dato no está del lado del webview**.

---

## 9. Motor de evaluación / rúbrica y scoring (corre en Rust, backend)

`scoring.rs` en `simpeatc-tauri` — **código puro, crítico y con suite de tests propia (casos dorados marca→medición y marca→nota) antes de usarse con peso real**. Corre contra la `TruthSheet` de `state`; al webview **solo cruza `ResultadoRubrica`** (versionado).

```rust
struct Rubrica { criterios: Vec<Criterio> }
struct Criterio { dimension: Dimension, descripcion: String, peso: f64,
                  tolerancia: Tolerancia, evaluador: Evaluador }
enum Resultado { Correcto, Parcial(f64), Incorrecto }
struct EvalItem { resultado: Resultado, medido: String, esperado: String, racional: String }
#[derive(Serialize, specta::Type)]
struct ResultadoRubrica { por_dimension: Vec<(Dimension, f64)>, global: f64,
    items: Vec<EvalItem>, version_motor: String, version_normas: String,
    hash_caso: u64, schema_version: u32 }
```

**Dimensiones:**

1. **Configuración de equipo** — `ProtocolDto` del alumno vs plantilla ideal por **rangos**: modalidad, oído, transductor, polaridad, tasa, intensidad inicial, filtro hp/lp/notch/order en banda, sweeps suficientes, `artifact_reject_uv` razonable, montaje, impedancias verificadas.
2. **Marcado de picos vs verdad con tolerancia** — `PeakMarkDto` vs `TruthSheet`. **Presencia/ausencia desde `DETECTABLE_UV` sobre el componente** (no de `Recording.detected`). Tolerancia por onda (≈±0.3 ms ABR, mayor en corticales). Interpicos vía `interpeak`. **Latencias e interpicos pesan alto.** **Amplitud / V‑I / SP‑AP desde marcas P‑V del alumno** (no `v_i_ratio`/`sp_ap_ratio`), peso **bajo o cualitativo**.
3. **Interpretación** — presencia/ausencia; **umbral vs `estimate_threshold` con tolerancia ≥ 1 paso (5–10 dB)**; topografía/clasificación vs `Lesion`; simetría interaural (**solo si gap #12 implementado**); coherencia L‑I.
4. **Calidad del informe** — checklist objetivo + coherencia interna + unidades correctas (dB nHL visible, **coma decimal es‑CL**). Parte automática + cualitativa con override docente.
5. **Proceso/flujo (sobre todo OSCE) — sobre el `ActionLog`, no el estado final.** Serie de intensidades, **bracketing** de umbral, **réplica A/B**, enmascaramiento cuando corresponde, impedancia chequeada, **conteo de parada**, tiempo. D5 evalúa la **secuencia** del `ActionLog` (autoritativo en `state`) contra el rango aceptable del docente.

**Bandas normativas en scoring:** solo puntúan en `ValidadaConPeso` (SD revisada). **Estado entregable por defecto: `ReferenciaNoValidada` ⇒ peso 0** (se ven, no afectan la nota). G2/G9 **no quedan bloqueados** por datos clínicos inexistentes.

**Feedback por modo:** Práctica inmediato; Evaluación diferido; OSCE oculto hasta cierre. El docente puede **override** de cualquier criterio (comando gateado por rol). Todo `ResultadoRubrica` es serializable, **versionado** (motor+normas+hash+`schema_version`) para auditoría y **recomputo idéntico**.

---

## 10. Constructor de informe clínico

`screens/Informe.svelte` + comandos de export. Construye un `Informe` serializable desde `RecordingDto(s)` + `ProtocolDto` + `Subject`‑visible + marcado del alumno. **Se descarta `printpdf` y el redibujo vectorial Rust**; el informe es HTML/CSS y las curvas ya son un gráfico web.

**Secciones:** encabezado (centro, **fecha con formato del `Locale`**, examinador=alumno); datos del paciente; parámetros del estímulo (modalidad, tipo, nivel **dB nHL con unidad visible**, polaridad, tasa, transductor, oído, **enmascaramiento — solo si gap #10 implementado**); parámetros de adquisición (ventana, filtro, sweeps aceptados/rechazados, `artifact_reject`, montaje, impedancias); **tabla de ondas por oído** (latencias, **amplitudes P‑V desde marcas del alumno**, interpicos, V/I y SP/AP **desde marcas P‑V, no `v_i_ratio`/`sp_ap_ratio`**); comparación interaural y vs normativo; curva L‑I / umbral estimado; **conclusión** redactada por el alumno; recomendaciones.

**Plantilla por modalidad (diseñada completa en G6 aunque solo se cablee ABR):** determina secciones, etiquetas de onda y gráficos (ABR I–V; ECochG SP/AP; MLR; ALR; P300/MMN 3 trazas; ASSR matriz + audiograma).

**Relleno automático:** tablas vía `interpeak` y **cálculo P‑V desde marcas**; el alumno solo redacta texto libre. Se incrusta snapshot de la(s) curva(s) **reusando el `Plano`/gráfico**.

**Motor de PDF — decisión (corregida):**
- **Ruta primaria de incrustación de curva: PNG hi‑res (`canvas.toDataURL`).** pdfmake tiene soporte **SVG parcial/limitado**; para curvas de uPlot el camino robusto y consistente en los 3 webviews es **PNG de alta resolución** (o jsPDF + `svg2pdf.js` si se requiere vectorial). **Se valida temprano en G6**, no al final.
- **Maqueta: `pdfmake` (o jsPDF), JS puro, headless y reproducible.** Control total de la maquetación clínica. Respeta convenciones (OD rojo/OI azul + redundancia no‑cromática, romanos I–V, eje X ms con pre‑estímulo negativo, eje Y µV, stacking descendente, flecha de umbral, **coma decimal es‑CL** con el mismo formatter de pantalla).
- **CSP y bundling (corrección §14):** incrustar fuentes de pdfmake (`vfs_fonts`) y PNG vía `data:` URI **requiere abrir `img-src 'self' data:` y `font-src 'self' data:`** en la CSP; con la CSP estricta por defecto esos `data:` se bloquean. pdfmake/uPlot se **bundlean (sin CDN)** bajo CSP estricta. Documentado y testeado en G6.
- **Secundario: `window.print()` + `@media print`** solo para "imprimir" rápido; **inconsistente entre webviews** (WebKitGTK flojo en print‑to‑PDF) ⇒ **no** para export automatizado/sellado.
- **El backend escribe el archivo:** el frontend genera los bytes y los pasa por `guardar_pdf(bytes)` (plugin‑fs/dialog requiere permiso en capabilities).

**Versionado/reproducibilidad (obligatorio):** el informe sella **versión de motor + versión de normativos + hash del caso + `seed_salt` + conteo de parada**. El **artefacto firmado/verificable es el JSON** (HMAC/timestamp del backend, con `schema_version` para migración, §11.B); el PDF es la vista humana.

**Export:** PDF (pdfmake; PNG hi‑res de curvas) · JSON (versionado, firmado) · CSV de `Waveform` y tabla de ondas (raw IPC `ArrayBuffer` para épocas grandes) · **CSV gradebook de cohorte OSCE** (`exportar_gradebook` desde Rust) · texto plano.

En Evaluación/OSCE el informe se **sella (timestamp + HMAC)** al entregar y se exporta junto a la rúbrica.

---

## 11. Roles, persistencia, integridad y formatos

### 11.A Roles y persistencia

- **Dos roles:** Docente y Estudiante. El rol/modo se refleja en el store del frontend para visibilidad, pero **la autoridad vive en `state` (Rust)**.
- **Lock por PIN (hash, server‑side):** entrada al panel docente, cambio de modo y revelación de la verdad exigen `docente_desbloquear(pin)`. **Auto‑relock** (`docente_relock`) al cambiar de modo, cerrar sesión de alumno o cambiar de ventana.
- **Autosave/recuperación (desde G0–G1):** el frontend serializa su store **sin verdad** vía `autoguardar(borrador)` cada ~30 s; `Recuperar` al arrancar. El estado autoritativo se **reconstruye desde caso+config+seed_salt+conteo de parada**. **No** usar `localStorage` para lo evaluable.
- **Formatos de archivo (con `schema_version` para migración):**
  - `.case.json` — paciente/caso del docente (lesiones por oído, órdenes, rúbrica). **Firmado**.
  - `.exam.json` / colección OSCE — secuencia de casos + tiempos + rúbrica.
  - `.session.json` — progreso del alumno (marcado, decisiones, `ActionLog`, timestamps, **conteo de parada**) **sin verdad**, para reanudar y **recomputar** nota.
  - Informe **PDF** + export CSV/JSON + gradebook.

### 11.B Integridad de evaluación (requisito, con framing honesto)

1. **Invariante estructural (lista blanca, no solo `detected`).** La `TruthSheet`/lesiones/diagnóstico/`umbral_verdadero`/`seed_salt`/`hmac_key` viven en `tauri::State` del proceso backend. **Test desde G0:** valida **campo a campo** que el payload del flujo del alumno solo contiene campos de una **lista blanca**; **falla** si aparece *cualquier* campo de `TruthSheet` o un `detected` no vacío. Esto protege contra que un **futuro DTO arrastre por error** un campo sensible (riesgo mayor que `detected`).
2. **Fuga por `detected`.** `simulate()` **siempre** rellena `Recording.detected` con latencias verdaderas. En Evaluación/OSCE, la **proyección vacía `detected` antes de serializar** (`proj.rs`/`strip.rs`).
3. **Seguridad IPC en Tauri 2 (corrección).** Los comandos **propios de la app** son accesibles por defecto desde **todas** las ventanas (a diferencia de los de plugins). **No existe** un mecanismo `AppManifest::commands` para "whitelistear comandos de app por ventana" como afirmaba el v1 — eso se **descarta**. La **única compuerta real** es **server‑side**: los comandos sensibles verifican el rol docente en `state` (PIN hash) y devuelven `Err` si no. Defensa en profundidad: capabilities scopeadas por **label de ventana** (válidas para permisos de plugins/core, p.ej. fs/dialog), CSP estricta y devtools off en release. La protección real es **que la verdad no viaje**, no las capabilities.
4. **Variación de ruido por determinismo (framing honesto).** Mismo caso+config+salt ⇒ curva idéntica. **`seed_salt` (gap #8) varía el RUIDO** entre alumnos, pero la **verdad evaluable (latencias, umbral, diagnóstico, topografía) es idéntica**. Por tanto el salt es **anti‑captura‑de‑pantalla/píxeles**, **no anti‑copia‑de‑respuestas**: copiar la interpretación dentro de tolerancia no se previene con salt. El salt es **backend‑only** (no se serializa al alumno: exponerlo debilita la auditoría sin ganancia).
5. **Cronómetro OSCE íntegro.** Reloj **`Instant` monótono en Rust** + hora de inicio sellada en `state` + tick por `emit`; el sellado calcula **HMAC‑SHA256** (`hmac`+`sha2`) sobre marcas+tiempos+config+**conteo de parada** con clave del backend.
6. **Reproducibilidad requiere sellar el conteo de parada.** Tras quitar `sweeps` del seed (G‑core), la curva a N sweeps es reproducible, **pero el alumno elige cuándo detener**. Para recomputar la curva sellada exacta hay que sellar el `produced`/`accepted` **al momento del Stop** (registrado en `ActionLog::DetenidaCaptura`), no solo el `Protocol`.
7. **Límite honesto del sellado en arquitectura 100 % local (corrección).** La `hmac_key` (y una eventual clave `ed25519`) **vive en la máquina del alumno**, que posee el binario y los archivos. Un alumno con acceso a disco **puede extraer la clave y forjar HMACs**; si la clave es aleatoria por arranque, el docente **no** puede verificar el sello en otra máquina. **Framing correcto:** "**evidencia de manipulación frente a estudiantes casuales, NO anti‑fraude criptográfico frente a uno determinado con acceso a archivos**". Si se requiere garantía fuerte, contemplar **un componente servidor mínimo** para custodia de clave / verificación (decisión adelantada, no diferida a G9).
8. **Compatibilidad de esquema.** Todo artefacto sellado lleva `schema_version`. Política: deserialización tolerante (campos `#[serde(default)]`) + **migradores versionados** para recomputar nota de `.session.json` antiguos cuando los DTOs cambien entre versiones de app.
9. **CSP estricta** en `tauri.conf.json` (la default es laxa en dev) **con `img-src/font-src 'self' data:` abiertos para pdfmake/PNG** (§10); **devtools deshabilitadas en release**; caso entregado al alumno como **payload ciego/firmado**.

---

## 12. GAPS en `aep-core` a cubrir

> **Regla:** todo gap se implementa en `aep-core` con tests propios **antes** de que la capa de GUI que lo consume se marque hecha. Los de §12.A son de **fidelidad clínica**: cada uno se **implementa o se recorta el objetivo** (decisión explícita). **Dimensiones re‑verificadas contra el código real** (§0.1).

### 12.A Gaps de fidelidad clínica (condicionan objetivos docentes)

| # | Necesidad | Propuesta (API) | Decisión / consecuencia si NO | Prioridad | Consume |
|---|-----------|-----------------|-------------------------------|-----------|---------|
| 10 | **Enmascaramiento sin efecto fisiológico.** `Masking` solo existe como struct + default `None` | Efecto de `Masking` en el motor: cross‑hearing, curva fantasma contralateral, sub/sobre‑enmascaramiento; o mínimo desplazamiento del nivel efectivo | Si NO: se **recorta** "enseñar enmascaramiento"; D5/sección de informe se eliminan | **Alta** (decisión de alcance) | G7, D5, informe |
| 11 | **Conducción ósea no evita la lesión conductiva.** `abr.rs:148` `level_at_cochlea = level_nhl - th.conductive` resta lo conductivo **siempre**; `Transducer` solo cambia `acoustic_delay_ms` | Gap aire‑hueso: `BoneConductor` **omite** la atenuación conductiva; `level_at_cochlea` condicionado al transductor | Si NO: **imposible** enseñar el diferencial conductivo vs sensorineural; se recortan D1/D3 | **Alta** (decisión de alcance) | G7, D1/D3 |
| 12 | **`CaseDef` mono‑oído/mono‑modalidad/mono‑intensidad.** `Lesion.ear` **YA existe** (`lesion.rs:74`); el colapso está en `CaseDef::subject()` (`cases.rs:147`) y el esquema (`String` para `modality`/`ear`, `lesions` privado) | **No sobreescribir `ear`** en `subject()`; `CaseDef` con lista de **órdenes** (modalidad+oído+intensidades); `RecordingSeries` por oído. **El trabajo es de esquema, no de `Lesion`** | Si NO: sin **asimetría interaural**, sin multi‑orden; se recorta D3 "simetría interaural" y §7 | **Media‑Alta** | G5, G7, G8, D3 |

### 12.B Gaps de scoring / lectura de curva

| # | Necesidad | Propuesta (API) | Prioridad | Consume |
|---|-----------|-----------------|-----------|---------|
| 13 | **Presencia/ausencia y `Suggest` correctos** (`detect_peaks` sobre‑detecta) | `presence_by_detectable(&Recording, DETECTABLE_UV)`; `Suggest` solo picos `DETECTABLE`; **helper de proyección/stripping de `detected`** | **Alta** | G2, scoring D2/D3, §11.B |
| 14 | **Convención pico‑a‑valle codificada** | `trough_for(label)` por modalidad; `find_extremum_in` parametrizado; `PicoATrough`/`PicoALineaBase` | **Alta** | G2, informe, scoring |
| 3 | **Lectura de curva para marcado P‑V** | `Waveform::amplitude_at(t_ms)` (interpol.), `index_at(t_ms)`, `find_extremum_in(t_lo,t_hi,max)` | **Alta** | G2 |
| 6 | **Series por intensidad / L‑I sobre marcas** | `latency_intensity_from_marks(&[(intensidad,WavePeak)])`; `RecordingSeries` serializable | **Media** | G5 |

### 12.C Gaps de infraestructura / técnicos

| # | Necesidad | Propuesta (API) | Prioridad | Consume |
|---|-----------|-----------------|-----------|---------|
| 2 | **Serialize del dominio + módulo report (RE‑DIMENSIONADO).** **NINGÚN tipo del dominio deriva `Serialize` hoy** (solo `Deserialize` en `cases.rs`/`norms.rs`). `CaseDef` usa `String` para `modality`/`ear`; `lesions` privado. **Prerequisito bloqueante del IPC, más trabajo del estimado** | `#[derive(Serialize)]` en `Recording, Waveform, WavePeak, OddballRecording, AssrResult, Protocol, Stimulus, Acquisition, Subject, Lesion` y enums; **decisión §0.2: ceguera por proyección, no DTOs espejo**; helper CSV | **Alta** | G0, G6, G7 |
| 1 | **Captura progresiva/streaming (RE‑DIMENSIONADO).** El **sembrado por‑sweep YA existe** (`engine.rs:189`); falta (a) quitar `sweeps` del seed base (`engine.rs:311,318`) y (b) **lo difícil: contador `produced` GLOBAL persistente entre `step()`**, con semilla por‑sweep indexada por ese contador, para que `step(n)` iguale `simulate(N)` pese al bucle de rechazo (`engine.rs:184‑189`) | `CaptureSession`/`StreamingAverager`: `new(&protocol,&subject,seed_salt)`, `step(n)`, `snapshot()->Recording`; **`produced` global**; **registrar conteo de parada** | **Alta** | G‑core/G3 |
| 8 | **Variantes deterministas por intento** | `seed_salt: u64` mezclado en `engine::seed`, propagado a `simulate*`/`CaptureSession`; **backend‑only** | **Alta** (junto a #1) | G‑core/G8 |
| 4 | **Bandas/rangos normativos + re‑export.** **Confirmado:** `lib.rs:47‑73` no re‑exporta `norms`; `WaveNorm` solo tiene `latency_ms`+`width_ms` (`norms.rs:20,24`), **sin SD** | `WaveNorm` con `latency_sd_ms`/`amplitude_sd_uv` (serde default); `norm_band(label,intensidad)->(min,max)` con `SHIFT_PER_10DB`; `pub use norms::{NormTable,WaveNorm}`. **Peso 0 hasta validar SD** | **Media‑Alta** | G2/G5/G9 |
| 7 | **ASSR: espectro para dibujar.** `power_spectrum` se calcula y descarta en `detect_assr` (`assr.rs:156`) | Enriquecer `AssrResult` con `power_spectrum: Vec<f64>` + `bin_fmod`. **Matriz freq×intensidad = N FFTs ⇒ `spawn_blocking` + progreso** | **Media** | G7 |
| 5 | **Carga de casos externos.** `CaseCatalog` solo `embedded()` | `CaseCatalog::from_json(text)`/`load(path)`/`save`; vista "ciega" de `CaseDef`; **firma/sellado** | **Media** | G8 |
| 15 | **Impedancia: agregado → escalar** | `Impedancias::impedance_kohm_efectiva()` (máx o media ponderada) mapeada al escalar de ruido | **Media** | G4 |
| 16 | **Versionado/reproducibilidad** | `engine::VERSION`, `norms::VERSION`, `CaseDef::hash()`; `schema_version`; sellar en informe/sesión (+ conteo de parada) | **Media** | G6/G9 |
| 9 | Oddball en UI | Documentar: usar `simulate_oddball`; sin cambio de core | — | G7 |

**Resumen de dependencias core↔GUI:** #2→G0 (prerequisito IPC, mayor de lo estimado) · #1+#8→G‑core/G3 · #3,#4,#13,#14→G2 · #15→G4 · #6→G5 · #16→G6 · #7→G7 · #5,#12→G8 · #10,#11→decisión de alcance antes de G7.

---

## 13. Roadmap por capas de GUI

Cada capa es **entregable e independiente**, con "Hecho cuando", dependencias y orden. Se intercala **G‑core** tras G1. La **lógica, dependencias y "Hecho cuando" se conservan del v2**; cambia el medio (Tauri/web) y se corrigen las estimaciones.

### Capa G0‑spike — Prueba desechable de los dos *unknowns* de Tauri *(antes de fijar arquitectura)*
- **Spike (a):** `Channel<MensajeCaptura>` streaming a **20–30 fps con decimado al ancho en píxeles** en **WebKitGTK + xvfb (Linux)**, midiendo jank real. Es el webview más frágil y el caso de uso central de §5/§4.4.
- **Spike (b):** tipar **`tauri::ipc::Channel<T>` como PARÁMETRO de comando** vía **tauri‑specta** sin drift (el borde más áspero de specta v2).
- **Hecho cuando:** ambos spikes corren en Linux CI; si alguno falla, se revisa §4.4/§5 **antes** de invertir en G0. Código desechable (no se mergea a la rama principal de features).
- **Depende de:** nada. **Orden:** cero (gate de arquitectura).

### Capa G0 — Andamiaje Tauri, IPC tipado, invariante verdad/ciego, i18n y autosave *(fundamento)*
- Crear `crates/simpeatc-tauri` dependiendo de `aep-core`; archivar `crates/simpeatc-gui` (iced). Frontend Vite + Svelte 5 + TS en `/src` (§3.3). `@tauri-apps/api` = versión de `tauri`. `cargo tauri dev` levanta front+back.
- **Prerequisito #2 (RE‑DIMENSIONADO):** derivar `Serialize` en el dominio del core (incluye normalizar `CaseDef` `modality`/`ear` y exponer `lesions` lo necesario); **ceguera por funciones de proyección** (§0.2), DTOs finos solo donde hay stripping/specta. **tauri‑specta** genera `bindings.ts`; check de CI contra drift.
- Backend mínimo: `AppState`, comandos `listar_casos`, `cargar_caso` (precomputa `TruthSheet`, **salt backend‑only**), `simular` (con stripping vía proyección), `autoguardar`; gateway IPC único con `mockIPC`.
- **i18n desde el inicio:** coma decimal (`Intl.NumberFormat('es-CL')`), fecha local, `parseNumEsCl`, opción OD/OI vs R/L.
- **Invariante verdad/ciego como LISTA BLANCA (§11.B):** **test en Rust** que valida campo a campo el payload del alumno y **falla** si aparece cualquier campo de `TruthSheet`, `seed_salt`, o un `detected` no vacío en Evaluación.
- **Autosave/recuperación** mínimo. **`schema_version`** en los artefactos desde el inicio.
- **Hecho cuando:** `cargo tauri dev` compila y corre, navega Inicio↔Examen, reproduce el ABR click actual (vía `simular`) sin regresión, strings desde i18n con coma decimal, `bindings.ts` tipado y sin drift, y el **test de invariante (lista blanca) pasa**.
- **Depende de:** G0‑spike + gap #2. **Orden:** primero.

### Capa G1 — Estación de examen ABR + panel de equipo editable *(MVP usable)*
- Layout clínico (CSS Grid): panel ~300 px + área central. `PanelEquipo` que **muta** el `ProtocolDto`. Botón Capturar ⇒ `simular` en **`spawn_blocking`** (anti‑freeze con sweeps altos: ECochG 1500, ABR 2000).
- Gráfico **uPlot**: OD rojo / OI azul **+ redundancia no‑cromática**, rejilla ms/µV, eje cero, pre‑estímulo negativo, dB nHL con unidad. `BarraMetricasLive` (F<sub>sp</sub>, aceptados/rechazados) y `TablaPicos`. Canvas HiDPI (`devicePixelRatio`).
- **`ActionLog`** registra capturas/configs en `state` (D5 futuro).
- **Hecho cuando:** el estudiante configura el equipo, captura un ABR (sin congelar con 2000 sweeps gracias a `spawn_blocking`) y ve la curva con etiquetas y colores clínicos; cambiar un control y recapturar refleja el efecto.
- **Depende de:** G0. **Orden:** segundo (MVP).

### Capa G‑core — Refactor de semilla unificado (`CaptureSession` + `seed_salt`) *(núcleo)*
- Implementar **#1 y #8 juntos**: `Averager`+`IirFilter`+contador en un struct reutilizable y determinista; **quitar `sweeps` del seed base** (`engine.rs:311,318`); mezclar `seed_salt`.
- **Hecho cuando (criterio explícito de la parte difícil):**
  1. El **contador `produced` persiste GLOBAL** entre `step()` y la **semilla por‑sweep se indexa por ese contador global**, de modo que `CaptureSession::step(n)` produce, al alcanzar N, **la misma** curva que `simulate(N)` **incluyendo el bucle de rechazo incremental** (no se reinicia `produced` por step).
  2. Dos `seed_salt` distintos dan curvas distintas y reproducibles.
  3. El **conteo de parada** (`produced`/`accepted`) queda disponible para sellado/reproducibilidad.
  4. Los tests de determinismo del core siguen verdes (rangos, no snapshots).
- **Depende de:** G1. **Orden:** tercero (antes de G3 y de cualquier golden de frontend).

### Capa G2 — Marcado interactivo: marcar/MOVER picos, P‑V, zoom y "Plano"
- Overlay DOM/SVG sobre uPlot: **drag de picos** (Pointer Events), `nueva marca`, `Cursores` con **readout numérico**. Atajos (1‑5, Ctrl+flechas, **Tab entre picos**), **táctil** (handles ≥25 px, `setPointerCapture`) y **snap al extremo** vía `ajustar_pico` (#3/#14). `Suggest` copia **solo `DETECTABLE`** (#13). Medición **P‑V** recalculada en Rust.
- **Zoom/pan/base de tiempos/ganancia** (`Vista` + `u.setScale`); **stacking offset manual** (pre‑suma datos / resta en hit‑test) encapsulado en `plano.ts`.
- **"Plano" data↔pixel** centralizado (incluye corrección de offset) reusable en pantalla y PDF.
- Bandas normativas como **`ReferenciaNoValidada`** (se ven, **peso 0**).
- **Tests propios:** golden de hit‑test y del "Plano" (con offset de stacking) + round‑trip de `parseNumEsCl` (Vitest).
- **Depende de core:** #3, #13, #14, #4. **Depende de GUI:** G1.
- **Hecho cuando:** el alumno coloca, arrastra (mouse/teclado/táctil) y renombra picos, hace zoom para marcar fino, ve readout y banda (no validada), y la tabla recalcula latencias/interpicos/**P‑V** al mover; los golden de "Plano"/hit‑test (incl. offset) pasan.
- **Orden:** cuarto.

### Capa G3 — Captura progresiva animada + réplicas A/B
- `iniciar_captura` con `tauri::ipc::Channel<MensajeCaptura>`: hilo en `spawn_blocking` que llama `session.step()` y emite snapshots a ~20–30 fps **con eje X una sola vez (`Iniciada`) y solo `muestras` decimadas en `Parcial`**; el frontend **coalesce** en `rAF` y hace `u.setData()`. Start/Stop/Pause con `detener_captura` (cancelación por `AtomicBool`; **registra conteo de parada**). EEG crudo + barra de rechazo. Réplica A/B (sólida vs punteada) + cross‑correlation opcional.
- **Depende de core:** G‑core (#1+#8). **Depende de GUI:** G1/G2.
- **Hecho cuando:** al pulsar Capturar la curva emerge sin jank, se puede detener a media captura registrando el conteo, y se superponen réplicas A y B reproducibles (mismo `seed_salt`+conteo ⇒ misma curva).
- **Orden:** quinto.

### Capa G4 — Stacking por intensidad, split OD/OI, overlay e impedancia que degrada
- Historial de capturas en el store con `visible`/`offsetY`/`color`/`dash`. Vistas: **stacking por intensidad** (offset **pre‑sumado** + dB a la izquierda), **split OD/OI** (dos uPlot con `cursor.sync` + **zoom‑Y cableado manualmente**), **overlay de réplicas**. Re‑marcar/comparar sin recapturar.
- **Impedancia funcional:** `PanelImpedancia` por electrodo → `impedance_kohm_efectiva()` (#15) mapeada al escalar, de modo que mala impedancia **degrada la curva**.
- **Hecho cuando:** el alumno apila intensidades con dB a la izquierda, compara OD/OI lado a lado (zoom sincronizado), re‑marca curvas guardadas sin perder datos, y una impedancia alta empeora visiblemente el ruido.
- **Depende de:** G2/G3 + #15. **Orden:** sexto.

### Capa G5 — Audiometría: latencia‑intensidad y audiograma estimado
- `screens/Audiometria.svelte`: curva L‑I de la V **marcada** (`construir_li`/`estimar_umbral`, banda según `BandaEstado`, flecha de umbral) y audiograma estimado (`estimate_audiogram`/`_chirp`/`assr_audiogram`) con símbolos OD/OI **+ redundancia no‑cromática**.
- **Depende de core:** #6, #4 (banda), #12 (asimetría, si se implementó). **Depende de GUI:** G4.
- **Hecho cuando:** apilando una serie, la curva L‑I y el umbral se construyen desde las marcas del alumno y se contrastan con la banda (no validada o validada según estado).
- **Orden:** séptimo.

### Capa G6 — Informe clínico + export (PDF web, versionado, cohorte)
- `screens/Informe.svelte` + comandos de export: **plantilla por modalidad diseñada completa** (aunque solo se cablee ABR), relleno automático (P‑V desde marcas), conclusión libre, **snapshot de curvas en PNG hi‑res (ruta primaria) incrustado en `pdfmake`**. Export JSON/CSV/texto/**PDF** + **CSV gradebook de cohorte** + **versionado** (motor+normas+hash+salt+conteo de parada+`schema_version`). JSON firmado = artefacto verificable; `guardar_pdf`/`exportar_*` escriben en disco vía Rust.
- **CSP:** abrir `img-src/font-src 'self' data:` para PNG y `vfs_fonts`; pdfmake/uPlot bundleados sin CDN. **Validar export PDF en los 3 webviews aquí, no al final.**
- **Depende de core:** #2 (Serialize), #16 (versiones/`schema_version`). **Depende de GUI:** G2/G4/G5.
- **Hecho cuando:** se genera un informe ABR completo con tabla de ondas (P‑V), interpicos, umbral y conclusión, con curvas (PNG) en el PDF, sellado con versiones+conteo, exportable a PDF/JSON/gradebook; el PDF es idéntico en los 3 webviews (pdfmake+PNG, no `window.print()`).
- **Orden:** octavo.

### Capa G7 — Multimodalidad completa (ECochG, MLR, ALR, P300/MMN, ASSR)
- Selector de modalidad que cambia constructor, etiquetas y vista. `DatosCapturaDto::{Oddball, Assr}` con `simular_oddball`/`simular_assr`. **3 trazas oddball** y **espectro ASSR** (con `bin_fmod`) + **matriz frecuencia×intensidad en `spawn_blocking` con progreso** (tabla HTML). Reusa el templating de G6.
- **Decisión de alcance previa:** enmascaramiento (#10) y aire‑hueso (#11) **implementados o recortados explícitamente** antes de cablear sus criterios/secciones.
- **Depende de core:** #7 (espectro ASSR); #10/#11 si se implementan. **Depende de GUI:** G2/G3/G6.
- **Hecho cuando:** las 7 modalidades se examinan, marcan e informan en la misma estación; oddball muestra 3 trazas y ASSR muestra espectro + matriz (sin congelar UI); los objetivos de enmascaramiento/aire‑hueso están implementados o documentados como fuera de alcance.
- **Orden:** noveno.

### Capa G8 — Roles, modos, autoría del docente y multi‑orden
- `Rol`/`Modo` con **lock por PIN (hash) server‑side** (`docente_desbloquear`) + **auto‑relock** (`docente_relock`) en handoff/cambio de modo/ventana. Editor de `Subject`/`Lesion` **por oído** (respetando `Lesion.ear` existente) y de **órdenes** (gap #12, trabajo de esquema en `CaseDef`/`subject()`). `TruthSheet` **sellada solo en `state`**. Vista ciega + **caso firmado** (#5), previsualización docente (gateada), carga/guardado. **Endurecimiento:** capabilities por **label de ventana** (fs/dialog), `ver_verdad`/scoring gateados en `state`, CSP estricta, devtools off. **Salt backend‑only** confirmado.
- **Decisión adelantada (§11.B #7):** definir aquí el **alcance honesto del sellado** (evidencia vs casuales) y si se incorpora un **componente servidor mínimo** para custodia de clave en despliegues de alto riesgo.
- **Depende de core:** #5 (from_json/load + firma), #12. **Depende de GUI:** G7.
- **Hecho cuando:** el docente crea/edita un paciente con asimetría interaural y varias órdenes, lo publica anonimizado y firmado, y el alumno en Evaluación **no recibe** verdad, ni `seed_salt`, ni `detected`, ni `Suggest`; los comandos sensibles devuelven `Err` sin rol; el rol docente se **auto‑relocka** en handoff.
- **Orden:** décimo.

### Capa G9 — Evaluación, rúbrica/scoring, proceso y OSCE íntegro
- `scoring.rs` (5 dimensiones, **con suite de casos dorados marca→nota antes de usar peso**), `screens/Revision.svelte`, feedback por modo. Todo el scoring **en Rust** contra la `TruthSheet`; solo cruza `ResultadoRubrica`. **D5 sobre `ActionLog`** (incluye conteo de parada). **OSCE íntegro:** cronómetro **monótono** (`Instant` en Rust) + inicio sellado + **HMAC** de sesión (sobre marcas+tiempos+config+**conteo de parada**); `seed_salt` por estudiante; export de cohorte. Persistencia/resultado **versionados** con `schema_version` + **migradores**; recomputo de nota.
- **Bandas:** **peso 0 (`ReferenciaNoValidada`) es el estado entregable por defecto**; el peso se activa solo cuando el investigador valida la SD.
- **Depende de core:** #2, #16, #4 (validación de SD para peso). **Depende de GUI:** G6/G8.
- **Hecho cuando:** un caso en Evaluación se corrige automáticamente (config + marcado por `DETECTABLE_UV` + interpretación con tolerancia ≥1 paso + informe + proceso por `ActionLog`) con desglose; una ronda OSCE cronometrada (monótona, sellada con HMAC sobre el conteo de parada, variada por salt) sella y exporta resultados por estudiante/estación; los golden de scoring pasan; el sellado está documentado con su **alcance honesto** (evidencia vs casuales).
- **Orden:** undécimo (cierre).

**Resumen de dependencias core↔GUI:** #2→G0 (mayor de lo estimado) · #1+#8→G‑core · #3,#4,#13,#14→G2 · #15→G4 · #6,#12→G5 · #2,#16→G6 · #7,#10,#11→G7 · #5,#12→G8 · validación SD→G9.

---

## 14. Riesgos y decisiones abiertas

**Riesgos clínicos (heredados del v2, vigentes):**

1. **Fidelidad clínica que invalida objetivos docentes (§12.A).** Enmascaramiento sin efecto (`Masking` default `None`), sin gap aire‑hueso (`abr.rs:148` resta lo conductivo siempre), `CaseDef` mono‑oído (colapso en `cases.rs:147`). **Decisión forzada antes de G7/G8:** implementar #10/#11/#12 o **recortar explícitamente** objetivos, criterios de rúbrica y secciones de informe. No se evalúa contra fisiología no simulada.
2. **Medición de amplitudes (limitación del motor).** Amplitud desde línea base y filtro IIR de fase no nula ⇒ V/I/SP‑AP aproximados. **Decisión:** rúbrica pesa latencias/interpicos; amplitudes cualitativas y **desde marcas P‑V**, nunca `v_i_ratio`/`sp_ap_ratio`. Refinamiento futuro: detección P‑V real + `filtfilt`.
3. **Bandas normativas sin SD validada.** `WaveNorm` solo tiene `latency_ms`+`width_ms` (`norms.rs:20,24`), `norms` no re‑exportado (`lib.rs:47‑73`). **Decisión:** bandas en `ReferenciaNoValidada` con **peso 0 como estado ENTREGABLE por defecto** hasta validación del investigador (David Ávila); G2/G9 no se bloquean.
4. **Accesibilidad.** Redundancia por forma/etiqueta/dash en gráfico e informe; marcado por **teclado completo y táctil** (Pointer Events); foco visible + ARIA; PDF legible en B/N.
5. **Versionado/reproducibilidad.** Cambios en normas (#4) o casos alteran coloreado y score. **Mitigación:** sellar motor+normas+hash+`seed_salt`+**conteo de parada**+`schema_version`; **migradores** para `.session.json` antiguos; recomputar con la versión sellada (artefacto verificable = JSON).
6. **Pérdida de trabajo / crash.** **Mitigación:** autosave (~30 s) + recuperación desde G0–G1; estado autoritativo reconstruible por determinismo (caso+config+salt+conteo).

**Riesgos de plataforma Tauri / webview / IPC / bundling (con imprecisiones del v1 corregidas):**

7. **Costo de IPC con arreglos a 30 fps — y corrección sobre `f32`.** El JSON de un `Vec` numérico es caro y en streaming satura el webview. **Corrección:** **`f32` NO abarata el JSON** (un `f32` y un `f64` ocupan lo mismo como string decimal); solo ayuda en canal **binario** (`ipc::Response`/`ArrayBuffer`). **La única palanca real del streaming es decimar al ancho en píxeles** (~500–1000 pts) y mandar el **eje X una sola vez**; coalescer en `rAF`. Para épocas crudas/export, raw IPC binario.
8. **Streaming por `Channel` vs render — y corrección de orden.** El `Channel` se usa por **throughput/backpressure y entrega tipada con orden**; la afirmación del v1 de que `emit/listen` "procesa fuera de orden" estaba **sobredicha** (los eventos también llegan en orden). **Mitigación:** emitir a ~20–30 fps (agrupando N sweeps), pintar el último snapshot en `rAF`, descartar intermedios.
9. **No bloquear el runtime.** DSP CPU‑bound; **`spawn_blocking`/hilo dedicado** para `simulate`/`CaptureSession` **y para la matriz ASSR (N FFTs)**; el comando retorna el `capture_id`/handle de inmediato.
10. **Mutex/estado en Rust.** El `MutexGuard` de std no es `Send` ⇒ no sostenerlo a través de `.await`. **Patrón:** lock → copiar → drop → await. Poisoning por panic. `manage()` guarda un valor por tipo ⇒ newtypes para múltiples estados.
11. **Seguridad IPC en Tauri 2 — corrección.** Los comandos **propios de la app** son accesibles por defecto desde cualquier ventana. **`AppManifest::commands` para whitelist por ventana NO es un mecanismo real** y se **descarta** (el propio plan lo admitía y se contradecía). **La única compuerta real es server‑side:** verificar rol docente en `state` (PIN hash) y `Err` si no. Defensa en profundidad: capabilities por **label de ventana** (válidas para plugins/core como fs/dialog), CSP estricta, devtools off. La protección real es **que la verdad no viaje**.
12. **Quirks de webview por SO.** Windows=WebView2, macOS=WKWebView, Linux=WebKitGTK. **Decisión:** gráfico en **Canvas2D (uPlot), no WebGL**; probar en los 3 webviews. **Linux webkit2gtk 4.1** (Ubuntu 22.04+): compilar sobre la distro más vieja; mitigar pantalla en blanco con `WEBKIT_DISABLE_COMPOSITING_MODE=1`.
13. **Export PDF — corrección pdfmake/SVG.** `window.print()` es irregular entre webviews. **pdfmake tiene soporte SVG parcial/limitado** ⇒ **ruta primaria = PNG hi‑res (`canvas.toDataURL`)** (o jsPDF+`svg2pdf.js` si vectorial). **CSP estricta rompe `data:`** de fuentes/canvas ⇒ abrir `img-src/font-src 'self' data:`; bundlear pdfmake/uPlot sin CDN. **Validar en los 3 webviews en G6, no al final.**
14. **Build de dos lenguajes / bundling.** `cargo tauri dev/build` orquesta front+back; matriz CI por SO. **Mitigación:** versiones idénticas de `tauri` y `@tauri-apps/api`; targets deb/rpm/AppImage, msi/NSIS, dmg; code signing/notarización; AppImage en la distro más vieja. **Type‑drift:** `bindings.ts` validado en CI. **Compat de esquema:** `schema_version` + migradores (§11.B #8).
15. **E2E del webview.** `tauri-driver` + WebDriver (WebKitWebDriver en Linux / Edge WebDriver en Windows; **macOS no soportado**). **Decisión:** E2E real con WebdriverIO en **Linux CI** (webkit2gtk + xvfb); Playwright contra el build web con IPC mockeado para UI rápida; el determinismo hace estables los golden.
16. **Integridad del sellado — framing honesto (corrección).** En arquitectura **100 % local**, la `hmac_key`/clave `ed25519` vive en la máquina del alumno: **un alumno determinado con acceso a disco puede extraer la clave y forjar sellos**, y una clave aleatoria por arranque impide verificar en otra máquina. **Alcance honesto: "evidencia de manipulación frente a estudiantes casuales, NO anti‑fraude criptográfico".** Si se requiere garantía fuerte, **un componente servidor mínimo** para custodia/verificación de clave (decisión adelantada a G8). Además: **`seed_salt` es anti‑captura‑de‑pantalla, no anti‑copia‑de‑respuestas** (la verdad evaluable es idéntica entre alumnos), y permanece **backend‑only**.

---

*Documento vivo. Hermano de `docs/MOTOR.md`: el motor define la verdad; este plan define cómo el equipo la mide, cómo se enseña a medirla, y qué objetivos clínicos quedan dentro o fuera del alcance según los huecos del motor que se decidan cubrir. Re‑plataformado del plan iced v2 a Tauri 2 + frontend web y **grounded contra el código real de `aep-core`**: corregidas las estimaciones de los gaps #1/#2/#12, las imprecisiones de Tauri (f32/JSON, whitelist por ventana, pdfmake‑SVG, CSP/`data:`, stacking/zoom en uPlot) y el framing de integridad OSCE (sellado local = evidencia, no anti‑fraude; salt backend‑only y anti‑screenshot). La lógica clínica, el scoring, la integridad y el roadmap por capas se conservan, reforzados por la frontera de proceso que impide que la verdad cruce el IPC hacia el alumno.*