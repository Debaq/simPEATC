# Motor de Simulación de Potenciales Evocados Auditivos (AEP)

> Plan de diseño del motor de `simPEATC` (reescritura en Rust).
> Alcance: desde **electrococleografía (ECochG)** hasta **potenciales cognitivos (P300/MMN)** y **ASSR**.
> Estado: **diseño**. Este documento define la arquitectura objetivo y el roadmap por capas.

---

## 1. Visión y alcance

El motor debe simular **toda la familia de potenciales evocados auditivos** con una sola arquitectura, recibiendo siempre el conjunto completo de variables que existen en un equipo real:

- **Estímulo**: tipo, polaridad, intensidad, frecuencia, tasa, transductor, enmascaramiento.
- **Adquisición**: filtros, ventana de análisis, promediaciones, rechazo de artefactos, montaje de electrodos, tasa de muestreo, ganancia, impedancia.
- **Sujeto**: edad, sexo, temperatura, estado de alerta, atención, lesión/patología.
- **Paradigma**: transitorio, oddball (P300/MMN), estado estable (ASSR).

El resultado es un **registro** (una o más curvas por canal) que evoluciona con las promediaciones, fiel a cómo se comporta un equipo clínico real.

### Por qué un solo motor

Todos los AEP comparten la misma estructura subyacente:

```
estímulo → generadores neurales → componentes (picos con latencia/amplitud/ancho/polaridad)
        → modulación por sujeto y parámetros → síntesis (señal + ruido EEG)
        → cadena de adquisición (filtro, ventana, promediación, artefactos) → curva
```

Lo único que cambia entre ECochG, ABR, MLR, ALR y P300 es: **la escala temporal**, **qué componentes existen**, **los filtros apropiados** y **de qué depende cada componente** (la atención importa para P300, no para ABR). Esto se modela con **un núcleo común** + **un modelo de respuesta intercambiable por modalidad**.

---

## 2. El espectro de potenciales

| Modalidad | Ventana | Componentes | Filtro típico (Hz) | Generadores | Depende de |
|-----------|---------|-------------|--------------------|-------------|------------|
| **ECochG** | 0–5 ms | CM, SP, AP (N1, N2) | 10–1500 | Células ciliadas, nervio auditivo distal | Polaridad, electrodo (TT/TM/EAC) |
| **ABR/PEATC** | 0–10 (15) ms | I–VII (I, III, V) | 100–3000 | N. auditivo → colículo inferior | Intensidad, tasa, edad, temp. |
| **MLR** | 10–80 ms | Na, Pa, Nb, Pb | 10–300 | Tálamo, corteza auditiva primaria | Edad (Pa madura tarde), estado, sedación |
| **ALR / CAEP** | 50–300 ms | P1, N1, P2, N2 | 1–30 | Corteza auditiva 2ª / asociación | Estado de alerta, atención |
| **P300** | 250–500 ms | P3a, P3b | 0.1–30 | Frontal (P3a), parietal (P3b) | **Atención**, paradigma oddball, edad/cognición |
| **MMN** | 100–250 ms | MMN (onda diferencia) | 0.1–30 | Corteza auditiva (preatencional) | Discriminabilidad del desviante |
| **ASSR** | — (estado estable) | Pico espectral en f<sub>mod</sub> | depende de f<sub>mod</sub> | 40 Hz: cortical / 80 Hz: tronco | Estimación objetiva de umbral |

**Nota sobre ASSR**: no produce una curva de picos en el tiempo, sino una **respuesta en el dominio de la frecuencia** (detección estadística de energía en la frecuencia de modulación). Es el caso más distinto y se trata como sub-motor especializado (Capa 7).

---

## 3. Decisiones de diseño confirmadas

1. **Patología paramétrica + presets.** El motor recibe una **lesión** descrita por *sitio* (coclear, retrococlear, neural, central, conductiva) + *grado* + *perfil frecuencial*, y deriva los componentes alterados. Encima, un **catálogo de casos** prearmados (presets clínicos) para enseñanza y evaluación.
2. **DSP real.** Filtros IIR Butterworth reales, promediación sweep-a-sweep, rechazo de artefactos real. El alumno ve el efecto de configurar mal el filtro o la ventana.
3. **Datos normativos embebidos + override externo.** Valores por defecto compilados en Rust (siempre arranca) + archivos JSON opcionales que el investigador edita sin recompilar.

---

## 4. Arquitectura del motor

```
                          ┌─────────────────────────────────────────────┐
                          │                 Protocol                     │
                          │  Modality · Stimulus · Acquisition · Paradigm│
                          └───────────────┬─────────────────────────────┘
                                          │  + Subject (edad, sexo, temp,
                                          │            estado, atención, Lesion)
                                          ▼
        ┌──────────────────────────── EvokedPotentialEngine ───────────────────────────┐
        │                                                                               │
        │  1. ResponseModel::components(protocol, subject)                              │
        │       → Vec<Component>  (latencia, amplitud, ancho, polaridad)  [VERDAD]      │
        │                                                                               │
        │  2. Modulation: aplica intensidad, edad, sexo, temp, tasa, estado, atención,  │
        │       lesión → ajusta cada Component                                          │
        │                                                                               │
        │  3. Synthesis: Σ componentes (gaussianas/plantillas) + ruido EEG de fondo     │
        │       → señal "cruda" continua por sweep                                      │
        │                                                                               │
        │  4. Acquisition (DSP real):                                                   │
        │       filtro IIR → ventana/baseline → promediación N sweeps →                 │
        │       rechazo de artefactos → cálculo FSP/SNR                                 │
        │                                                                               │
        └───────────────────────────────────┬───────────────────────────────────────┘
                                             ▼
                                       Recording
                          (Channels[], picos detectados, FSP, metadatos)
```

**Separación clave**: la *verdad fisiológica* (pasos 1–2, lo que el cerebro genera) está separada de la *adquisición* (paso 4, lo que el equipo mide). Así un mismo paciente "real" se ve distinto según cómo configures el equipo — que es exactamente lo que se enseña.

---

## 5. Modelo de datos (tipos Rust)

> Ilustrativo; los nombres finales se afinan en implementación. Unidades **fuertemente tipadas** para no confundir dB nHL con dB SPL.

### 5.1 Estímulo

```rust
pub enum Modality { ECochG, Abr, Mlr, Alr, P300, Mmn, Assr }

pub enum StimulusKind {
    Click { duration_us: f64 },                 // banda ancha
    ToneBurst { freq_hz: f64, cycles_rise: u8,  // específico en frecuencia
                cycles_plateau: u8, cycles_fall: u8, window: RampWindow },
    Chirp { kind: ChirpKind },                  // CE-Chirp, LS-Chirp
    Speech { token: SpeechToken },              // /ba/, /da/ para cognitivos
    Noise { band: NoiseBand },                  // enmascaramiento
}

pub enum RampWindow { Linear, Hanning, Blackman, Gaussian }
pub enum Polarity   { Rarefaction, Condensation, Alternating }
pub enum Transducer { Insert, Supraaural, BoneConductor, FreeField }

pub enum Level { DbNhl(f64), DbSpl(f64), DbHl(f64), DbPeSpl(f64) }

pub struct Stimulus {
    pub kind: StimulusKind,
    pub polarity: Polarity,
    pub level: Level,
    pub rate_hz: f64,                 // tasa de estimulación (p.ej. 11.1, 27.7)
    pub transducer: Transducer,
    pub masking: Option<Masking>,     // ruido contralateral, nivel
}
```

### 5.2 Adquisición

```rust
pub struct TimeWindow { pub pre_ms: f64, pub post_ms: f64 }   // baseline + ventana

pub struct Bandpass {
    pub hp_hz: f64,                   // pasa-altos
    pub lp_hz: f64,                   // pasa-bajos
    pub notch_hz: Option<f64>,        // 50/60 Hz
    pub order: u8,                    // orden del Butterworth
}

pub struct Electrode { pub site: ElectrodeSite }            // Cz, Fz, M1, M2, A1, A2, lóbulo, EAC...
pub struct Channel  { pub noninv: ElectrodeSite, pub inv: ElectrodeSite } // diferencial
pub struct Montage  { pub channels: Vec<Channel>, pub ground: ElectrodeSite }

pub struct Acquisition {
    pub window: TimeWindow,
    pub filter: Bandpass,
    pub sweeps: u32,                  // promediaciones objetivo
    pub artifact_reject_uv: f64,      // umbral de rechazo
    pub sample_rate_hz: f64,
    pub gain: f64,
    pub montage: Montage,
    pub impedance_kohm: f64,          // afecta nivel de ruido
}
```

### 5.3 Sujeto y lesión

```rust
pub enum Age {
    Gestational { weeks: f64 },       // prematuro
    Postnatal { days: u32 },          // neonato/lactante (maduración rápida)
    Years { value: f64 },             // niño/adulto/adulto mayor
}

pub enum Sex { Male, Female }

pub enum ArousalState { Awake, NaturalSleep, Sedated, Anesthetized }
pub enum Attention    { Active, Passive, Ignoring }   // crítico para P300/MMN

pub struct Subject {
    pub age: Age,
    pub sex: Sex,
    pub temperature_c: f64,           // hipotermia alarga latencias
    pub state: ArousalState,
    pub attention: Attention,
    pub lesions: Vec<Lesion>,         // varias coexistentes (p.ej. mixta)
}

// --- Patología paramétrica ---
pub enum LesionSite {
    Conductive,            // transmisión (oído medio): desplaza umbral, alarga latencias absolutas, intervalos normales
    Cochlear,              // sensorial: reclutamiento, latencias casi normales a alta intensidad
    Retrocochlear,         // VIII par: alarga I-V, I-III; afecta onda V/morfología
    Neural,                // neuropatía/desincronía: AP/ABR ausentes con CM presente
    Central,               // tronco/corteza: afecta componentes tardíos según nivel
}

pub struct Lesion {
    pub site: LesionSite,
    pub ear: Ear,
    pub severity_db: f64,             // grado (umbral añadido)
    pub freq_profile: FreqProfile,    // plano, agudos, graves, en cubeta...
}
```

### 5.4 Componente, protocolo y registro

```rust
/// Unidad atómica común a TODAS las modalidades.
pub struct Component {
    pub label: &'static str,          // "I","V","SP","AP","Pa","N1","P3b","MMN"...
    pub latency_ms: f64,
    pub amplitude_uv: f64,            // con signo (polaridad de la deflexión)
    pub width_ms: f64,                // sigma de la plantilla
    pub shape: ComponentShape,        // Gaussian, Template(coclear/CM), Step(SP)
    pub generator: &'static str,      // texto didáctico del generador anatómico
}

pub struct Protocol {
    pub modality: Modality,
    pub stimulus: Stimulus,
    pub acquisition: Acquisition,
    pub paradigm: Paradigm,
}

pub enum Paradigm {
    Transient,                                       // un estímulo repetido (ECochG..ALR)
    Oddball { standard: Stimulus, deviant: Stimulus, // P300/MMN
              deviant_prob: f64 },
    SteadyState { mod_freq_hz: f64 },                // ASSR
}

pub struct Recording {
    pub channels: Vec<Waveform>,      // una curva por canal del montaje
    pub detected: Vec<Component>,     // picos tras la adquisición
    pub fsp: f64,                     // factor señal/promedio alcanzado
    pub rejected_sweeps: u32,
}
```

### 5.5 El trait de modelo por modalidad

```rust
pub trait ResponseModel {
    /// Componentes neurales "verdaderos", ya modulados por sujeto y parámetros.
    fn components(&self, protocol: &Protocol, subject: &Subject) -> Vec<Component>;

    /// Configuración de adquisición recomendada (filtro/ventana por defecto).
    fn recommended_acquisition(&self) -> Acquisition;

    /// Ruido EEG de fondo característico (banda, amplitud) para esta modalidad.
    fn background_noise(&self, subject: &Subject) -> NoiseProfile;
}
```

`EvokedPotentialEngine::simulate(protocol, subject)` selecciona el `ResponseModel` según `protocol.modality`, ejecuta el pipeline de la §4 y devuelve `Recording`.

---

## 6. Cadena de adquisición (DSP real)

El paso 4 del pipeline reproduce el equipo real, sweep a sweep:

1. **Síntesis por sweep**: señal continua = Σ componentes + ruido EEG (depende de impedancia, estado, edad) + artefactos ocasionales (parpadeo, muscular).
2. **Filtro IIR Butterworth**: pasa-banda `hp_hz..lp_hz` + notch opcional, orden configurable. Implementación propia (biquads en cascada) — sin dependencias pesadas. El filtro mal puesto **debe** distorsionar (p.ej. HP alto borra componentes lentos del ALR).
3. **Ventana y baseline**: recorte a `[-pre_ms, post_ms]`, corrección de línea base con el pre-estímulo.
4. **Rechazo de artefactos**: descarta sweeps que superan `artifact_reject_uv`; cuenta rechazados.
5. **Promediación**: media acumulada de sweeps aceptados → el ruido cae ~√N, la señal emerge.
6. **FSP / SNR**: factor señal/promedio (modelo heredado del Python, ver §8) y métrica de calidad.

> **Decisión técnica**: el filtrado y la promediación son **reales** sobre las muestras, no un efecto aproximado. Es más trabajo pero es el contenido educativo central del simulador.

---

## 7. Modulación: reglas clínicas

Funciones puras que ajustan cada `Component` (latencia/amplitud/morfología). Cada modalidad declara qué reglas aplica.

| Factor | Efecto | Aplica a |
|--------|--------|----------|
| **Intensidad** | ↓ intensidad → ↑ latencia (~0.3 ms/10 dB) y ↓ amplitud; cerca del umbral solo sobrevive onda V | Todas |
| **Umbral / lesión** | desplaza el "cero efectivo"; perfil frecuencial define qué tono-burst responde | Todas |
| **Tasa de estímulo** | ↑ tasa → ↑ latencia (fatiga neural), más en patología retrococlear | ABR, ECochG |
| **Polaridad** | invierte el CM; alternante lo cancela; pequeños cambios en I/III | ECochG, ABR |
| **Edad** | neonato: latencias largas (mielinización); Pa/corticales maduran en la infancia; adulto mayor: P300 más tardío | Todas (curvas de maduración) |
| **Sexo** | mujer: latencias ligeramente más cortas, amplitudes mayores | ABR+ |
| **Temperatura** | hipotermia → ↑ latencias (~0.2 ms/°C) | ABR |
| **Estado de alerta** | sueño/sedación atenúan MLR/ALR; ABR casi intacto | MLR, ALR |
| **Atención** | sin atención no hay P3b; MMN es preatencional (sí aparece) | P300, MMN |

Cada regla es una función testeable de forma aislada (ver §10).

---

## 8. Sistema FSP / ruido (diseño desde cero)

> **Decisión (reescritura):** no se porta el modelo del Python. El SNR **no se
> modela** con una curva ajustada (`a·avg^b` ni puntos interpolados): **emerge de
> la física**. Cada sweep lleva la señal evocada (coherente) + ruido EEG
> independiente; al promediar N sweeps reales, la señal se suma y el ruido cae
> ~√N. La "textura picuda que se suaviza" aparece sola al aumentar N.

El **FSP** se calcula como métrica estadística real: **F<sub>sp</sub> single-point**
(Elberling & Don, 1984):

```text
F_sp = M · Var_a / Var_sp
```

donde `M` = sweeps promediados, `Var_a` = varianza de la curva promediada sobre
la ventana, `Var_sp` = varianza, entre sweeps, de un único punto temporal fijo.
Sin respuesta → `F_sp ≈ 1`; con respuesta sube, y sube con `M` (umbral clínico de
detección ≈ 3.1). La impedancia de electrodos eleva el piso de ruido (el motor
escala el RMS del ruido por la impedancia). Implementado en `dsp/fsp.rs` y
`dsp/average.rs`.

---

## 9. Datos normativos

```
abr-core/data/
├── norms_abr.json        # latencias/amplitudes I–V por edad, sexo, intensidad
├── norms_ecochg.json     # SP/AP, ratio normal
├── norms_mlr.json        # Na/Pa por edad y estado
├── norms_alr.json        # P1/N1/P2 por edad
├── norms_p300.json       # P3b por edad (latencia ↑ con edad)
└── maturation.json       # curvas de maduración por componente
```

- **Embebidos** vía `include_str!` → siempre arranca.
- **Override**: si existe un JSON externo en una ruta de configuración, lo carga encima.
- Validación de esquema al cargar; si el override es inválido, se ignora con aviso (no rompe).
- El investigador (David Ávila) ajusta valores clínicos sin tocar Rust.

---

## 10. Determinismo y testeo

- **Determinismo total**: PRNG con semilla derivada del protocolo+sujeto (ya implementado, `Lcg`). Mismos parámetros → misma curva. Imprescindible para tests y reproducibilidad clínica.
- **Tests por nivel**:
  - *Reglas de modulación*: cada función (intensidad, edad…) probada aislada con valores normativos conocidos.
  - *Modelos de respuesta*: dado un caso normal, los picos caen en rango normativo; dado retrococlear, I-V se alarga.
  - *Cadena DSP*: un filtro pasa-banda atenúa fuera de banda; la promediación reduce el ruido ~√N.
  - *Presets*: cada caso del catálogo produce un registro coherente con su diagnóstico.
- **Golden tests**: curvas de referencia versionadas para detectar regresiones del motor.

---

## 11. Paradigmas especiales

### Oddball (P300 / MMN) — Capa 6
Dos flujos de estímulo (estándar frecuente + desviante/raro). El motor genera la respuesta a cada tipo y la **onda diferencia** (desviante − estándar): ahí emerge P300 (con atención activa) o MMN (preatencional). La amplitud/latencia de P3b dependen de la probabilidad del raro, la atención y la edad.

### ASSR — Capa 7
Sub-motor en **dominio de frecuencia**: estímulo modulado (portadora + f<sub>mod</sub> de 40 u 80 Hz), respuesta = energía en f<sub>mod</sub> detectada por FFT + test estadístico (F-test / magnitud-cuadrada de coherencia). Salida: presencia/ausencia de respuesta por frecuencia → **audiograma objetivo estimado**. No reusa la síntesis temporal de picos; comparte tipos de estímulo/sujeto/lesión.

---

## 12. Roadmap por capas

Cada capa es entregable e independiente: añade variables y una modalidad, con tests y presets propios. El núcleo (Capa 0) se construye una vez; las demás son incrementos.

### Capa 0 — Núcleo genérico  *(fundamento)* — ✅ HECHA
- Tipos comunes (§5), `EvokedPotentialEngine`, trait `ResponseModel`.
- Síntesis por composición de componentes + ruido.
- **Cadena DSP real**: filtro IIR Butterworth, ventana/baseline, promediación, rechazo de artefactos, FSP.
- Determinismo + framework de tests + carga de normativos (embebido+override).
- *Hecho cuando*: el ABR actual se reproduce sobre esta base con tests verdes.

### Capa 1 — ABR por clicks  *(modalidad estrella)* — ✅ HECHA
- Modelo ABR completo: ondas I–VII, intervalos, V/I.
- Variables: intensidad, polaridad, tasa, transductor, edad, sexo, temperatura.
- Lesiones: conductiva, coclear, retrococlear, neural (paramétricas) + perfil frecuencial.
- Catálogo de presets (portar los 30 casos del Python).
- *Hecho cuando*: casos normal/conductiva/retrococlear/neuropatía se distinguen y miden bien.

### Capa 2 — ECochG
- Componentes CM, SP, AP (N1/N2); ratio SP/AP.
- Dependencia de polaridad (CM se invierte/cancela) y electrodo (TT/TM/EAC).
- Preset Ménière (hidrops → SP/AP elevado).

### Capa 3 — ABR tone-burst + latencia/intensidad
- Estímulos específicos en frecuencia (500–4000 Hz), CE-Chirp.
- Búsqueda de umbral por frecuencia, gráfico latencia-intensidad, **audiograma estimado**.

### Capa 4 — MLR
- Componentes Na, Pa, Nb, Pb; ventana media; filtro 10–300 Hz.
- Dependencia de **edad** (Pa madura ~10–12 años), **estado** y **sedación**.

### Capa 5 — ALR / CAEP
- Componentes P1, N1, P2, N2; ventana larga; filtro 1–30 Hz.
- Dependencia de **estado de alerta** y **atención**; uso con estímulos de habla.

### Capa 6 — Cognitivos (P300, MMN)
- Paradigma **oddball**, doble flujo, onda diferencia.
- P3a/P3b, dependencia de atención y edad; MMN preatencional.

### Capa 7 — ASSR
- Sub-motor en dominio de frecuencia; detección estadística en f<sub>mod</sub>.
- Estimación objetiva de umbrales (40 Hz adulto / 80 Hz lactante).

---

## 13. Estructura de módulos del crate

> Propuesta: **renombrar `abr-core` → `aep-core`** (Auditory Evoked Potentials), ya que el alcance excede al ABR. El crate actual tiene poco código; el cambio es barato ahora.

```
aep-core/
├── src/
│   ├── lib.rs
│   ├── units.rs            # Level (dB*), tiempos, conversiones tipadas
│   ├── stimulus.rs         # Stimulus, StimulusKind, Polarity, Transducer
│   ├── acquisition.rs      # Acquisition, Bandpass, Montage, TimeWindow
│   ├── subject.rs          # Subject, Age, Sex, ArousalState, Attention
│   ├── lesion.rs           # Lesion, LesionSite, FreqProfile
│   ├── component.rs        # Component, ComponentShape, WavePeak
│   ├── waveform.rs         # Waveform, Recording, Channel
│   ├── protocol.rs         # Protocol, Modality, Paradigm
│   ├── engine.rs           # EvokedPotentialEngine (pipeline §4)
│   ├── synth.rs            # síntesis señal + ruido (PRNG determinista)
│   ├── dsp/                # cadena de adquisición real
│   │   ├── filter.rs       # IIR Butterworth (biquads)
│   │   ├── average.rs      # promediación, rechazo de artefactos
│   │   └── fsp.rs          # factor señal/promedio
│   ├── modulation.rs       # reglas clínicas (§7)
│   ├── norms.rs            # carga embebido+override (§9)
│   ├── models/             # un ResponseModel por modalidad
│   │   ├── mod.rs
│   │   ├── ecochg.rs
│   │   ├── abr.rs
│   │   ├── mlr.rs
│   │   ├── alr.rs
│   │   ├── cognitive.rs    # P300, MMN
│   │   └── assr.rs
│   └── cases.rs            # catálogo de presets clínicos
├── data/                   # JSON normativos embebidos
└── tests/                  # golden tests, integración por modalidad
```

---

## 14. Relación con el motor Python (NO se porta código)

> **Decisión del proyecto:** el motor Rust se construye **desde cero**. El motor
> Python (`python_legacy`) estaba limitado y era una estructura que no se
> sostenía sola; sirve solo como **referencia conceptual**, no como fuente de
> código a portar.

Equivalencias *conceptuales* (qué problema resolvía cada parte, reimplementado
con un diseño nuevo):

| Concepto del Python (referencia) | Rust (diseño nuevo) | Cómo cambia |
|----------------------------------|---------------------|-------------|
| FSP por puntos interpolados | `dsp/fsp.rs` | F<sub>sp</sub> estadístico real (§8), no curva ajustada |
| ruido escalado por FSP | `synth.rs` + `dsp/average.rs` | ruido independiente por sweep; el SNR emerge al promediar |
| cálculo de parámetros de onda | `modulation.rs` + `models/abr.rs` | reglas clínicas puras + tabla normativa |
| efectos de polaridad / tasa | `modulation.rs` | funciones puras testeables |
| valores baseline por población | `norms.rs` + `data/norms_abr.json` | normativos embebidos + override |
| catálogo de casos (DICT_CASES) | `cases.rs` (capas futuras) | lesión paramétrica + presets |

El modelo de **componentes** (`component.rs`) y la **lesión paramétrica**
(`lesion.rs`) sustituyen al esquema de `desviaciones` + `patologia` del Python.

---

## 15. Decisiones abiertas / riesgos

1. ~~**Renombrar el crate** `abr-core → aep-core`~~: **hecho** (Capa 0).
2. **Validación clínica de valores**: las tablas normativas de MLR/ALR/P300 requieren revisión del investigador (David Ávila) antes de considerarse fiables para enseñanza.
3. **Morfología realista**: gaussianas simples bastan para ABR; ECochG (SP escalón) y corticales (ondas anchas asimétricas) pueden necesitar plantillas. Se resuelve con `ComponentShape`.
4. **ASSR** podría justificar su propio crate si el dominio de frecuencia diverge mucho; por ahora, sub-módulo.
5. **Rendimiento**: la GUI llama al motor en tiempo real durante la captura; la cadena DSP debe ser barata por sweep. Mantener todo en `f32`/`f64` sin asignaciones por frame.
6. **Medición de amplitudes**: la detección actual mide amplitud *absoluta desde la línea base*, no *pico-a-valle*, y el filtro IIR es *forward* (no fase cero). Las **latencias** son fiables; las **amplitudes y razones (V/I)** quedan aproximadas. Refinamiento futuro: detección pico-a-valle + filtrado de fase cero (filtfilt).

---

*Documento vivo. Las capas 0 y 1 son el foco inmediato; el resto se detalla al llegar a cada una.*
