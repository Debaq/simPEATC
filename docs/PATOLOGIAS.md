# Roadmap de patologías y modelo de caso

## 1. Modelo (objetivo)

Separar dos conceptos que hoy están mezclados en `CaseDef`:

- **Patología** (núcleo del caso): qué está dañado en la vía auditiva. Se define por
  **lesiones** = `{ sitio, severidad_dB, perfil_frecuencial }`. El motor (`aep-core`)
  ya sabe traducir esa fisiología a la respuesta de **cualquier** examen:
  tempranas (ECochG, ABR), medias (MLR), tardías (ALR/CAEP), cognitivas (P300, MMN)
  y estado estable (ASSR). La patología es la fuente de verdad **transversal a todos
  los exámenes**.
- **Variables externas** (knobs de sesión, NO parte de la patología): modulan el
  registro sin cambiar el diagnóstico. Se ajustan al montar el caso en el slot.

Una misma patología + distintas variables externas = registros distintos, mismo
diagnóstico. (Ej.: neurinoma en neonato dormido vs adulto despierto.)

### Slots OD / OI
Cada slot recibe **una patología** (perfil por oído). Permite asimetría (la mayoría
de neurinomas son unilaterales). Las variables externas se ajustan aparte (a nivel
de paciente/sesión y de equipo).

---

## 2. Variables externas (knobs de sesión)

| Variable | Efecto fisiológico | Dónde vive |
|---|---|---|
| Edad (neonato→adulto→présbita) | Madurez: latencias largas en neonato, Pa madura ~10-12 a, P300 ↑ con edad | sesión |
| Sexo | Pequeñas diferencias de latencia/amplitud | sesión |
| Temperatura corporal | Velocidad de conducción → latencias (hipotermia las alarga) | sesión |
| Estado (vigilia/sueño/sedación/anestesia) | Atenúa MLR/ALR/cognitivos; ABR y ASSR robustos | sesión |
| Atención (activa/pasiva/ignorando) | P300 (P3b) vs MMN preatencional | sesión |
| Impedancia / limpieza de electrodos (kΩ) | Sube el piso de ruido → más sweeps para FSP | equipo |
| Ruido eléctrico de red (50/60 Hz) | Artefacto → notch | equipo |

---

## 3. Catálogo de patologías a fabricar

`normal` ya está. El resto se fabrica por sitio × perfil × severidad. Para cada una se
documenta la **firma por examen** (lo que el motor debe reproducir).

### 0. Normal *(hecho)*
Sin lesiones. Todas las respuestas normales según edad/estado.

### 1. Conductivas (oído medio)
Lesión `Conductive` (perfil Flat). Etiologías representables variando severidad:
otitis media serosa, otosclerosis, perforación timpánica, discontinuidad osicular.
- `conductiva_leve` (25 dB), `conductiva_moderada` (40 dB), `conductiva_severa` (55 dB).
- **Firma:** latencias absolutas ↑ uniformes (todos los exámenes), interpicos normales,
  umbral aéreo ↑ con óseo normal (gap aéreo-óseo). ASSR/ABR umbral aéreo ↑.

### 2. Cocleares (sensoriales) — perfil × severidad
Lesión `Cochlear`.
- Agudos (`HighFrequency`): `coclear_agudos_leve/mod/sev` (35/50/70 dB) —
  presbiacusia, trauma acústico, ototóxicos.
- Graves (`LowFrequency`): `coclear_graves` (45 dB) — hidrops inicial.
- Plana (`Flat`): `coclear_plana_mod/sev/prof` (45/65/85 dB).
- En U (`CookieBite`): `cookie_bite` (45 dB) — genética.
- **Firma:** reclutamiento (latencia casi normal a alta intensidad, umbral ↑, amplitudes ↓),
  audiograma por tone-burst/ASSR coherente con el perfil. ECochG sin SP/AP elevado
  (salvo hidrops). Corticales presentes si hay audición residual.

### 3. Mixtas
`Conductive` + `Cochlear`.
- `mixta` (Cond 30 + Cocl 40).
- **Firma:** gap aéreo-óseo sobre coclea ya dañada.

### 4. Retrococleares (VIII par) — típicamente unilateral
Lesión `Retrocochlear`.
- `neurinoma_inicial/mod/avanzado` (25/40/60 dB).
- **Firma:** I-V ↑, V/I ↓, ondas tardías retrasadas/ausentes con onda I preservada.
  ABR es el examen clave. ECochG normal. ASSR poco específico.

### 5. Neural / Neuropatía auditiva (desincronía)
Lesión `Neural`.
- `neuropatia` (60 dB).
- **Firma:** ABR ausente/muy anómalo con función coclear (CM/OEA) conservada
  (disociación ECochG–ABR). ASSR poco fiable. Corticales variables.

### 6. Central
Lesión `Central`.
- `central_tronco`, `central_cortical` (30 dB).
- **Firma:** ABR normal; MLR/ALR/P300 alterados. Trastorno de procesamiento auditivo (TPA).

### 7. Casos límite / didácticos
- `anacusia` / muerte de vía (lesión total): ausencia de toda respuesta (umbral objetivo).
- *(No orgánica / funcional: fuera de alcance del motor por ahora.)*

---

## 3-bis. Eje neurológico en el motor *(implementado)*

PEATC/AEP son neurodiagnósticos. Se añadieron sitios de lesión `LesionSite` que el
motor traduce a la firma correcta por examen (tests de criterio en `tests/casos.rs`):

| Sitio | Entidad | Firma (validada por test) |
|---|---|---|
| `Retrocochlear` | Schwannoma/neurinoma | ABR: I-V ↑, V/I ↓, ondas tardías retrasadas/ausentes, I preservada |
| `Neural` | Neuropatía/desincronía | ABR ausente, coclea (CM) conservada |
| `CentralConduction` | EM / desmielinización | ABR: III-V ↑ preservando I-III |
| `Brainstem` | Lesión de tronco → muerte encefálica | abole de rostral (V) a caudal según severity; ≥90 dB solo onda I |
| `Cortical` | TPAC | MLR Pa / ALR N1 ↓ aun despierto; ABR normal |
| `Cognitive` | Demencia / daño cognitivo | P300: P3b latencia ↑, amplitud ↓ (indep. de atención) |

Casos en el catálogo: `neurinoma`, `neuropatia`, `esclerosis_multiple`, `lesion_tronco`,
`muerte_encefalica`, `tpac`, `deterioro_cognitivo` (+ `normal`).

## 4. Fases de implementación

1. **(hecho)** Modelo confirmado · catálogo reducido a `normal` · este roadmap.
   Fixtures de validación del motor movidos a `tests/fixtures/`.
2. **(hecho)** Refactor del modelo: `CaseDef` → patología (solo lesiones + id/nombre/descr).
   Variables externas (edad, sexo, temp, estado, atención) en el **panel de sesión**
   (`SessionVarsPanel`); impedancia/notch ya viven en el equipo. El backend arma el
   sujeto de captura = variables de sesión + lesiones del slot.
3. **(hecho)** Flujo del alumno: el docente monta el escenario en su modal
   (patología en slots OD/OI + variables de sesión); el alumno opera el equipo
   (examen, intensidad, oído, electrodos) y captura.
4. **(hecho)** Resultados por examen: la estación cambia de vista según la familia
   del examen activo — transitorio (apilado OD/OI + latencias), oddball (3 trazas
   + P3b/MMN), ASSR (tabla por frecuencia + espectro F-test). Batería acumulada por
   (oído, examen); captura one-shot para oddball/ASSR, progresiva para transitorios.
5. **(en curso)** Fabricar patologías con su firma por examen. Hecho: **eje
   neurológico** (§3-bis) + **audiológicas** (conductivas leve/mod/severa; cocleares
   agudos/plana severa/profunda/graves/cookie-bite; mixta) como diferencial. 18 casos
   en el catálogo. Pendiente: afinar magnitudes y sumar más severidades/variantes.
6. **(hecho)** Evaluación / OSCE / scoring. En Evaluación/OSCE el alumno explora,
   marca y emite un **diagnóstico por oído** (sitios de lesión); el backend
   (`calificar`) puntúa contra la verdad oculta: **diagnóstico** (Jaccard de sitios,
   60%) + **marcado** (latencias vs. la clave recomputada del motor, ±0.6 ms, 40%),
   y revela la verdad. UI: `AnswerModal` (botón "Responder y entregar").
