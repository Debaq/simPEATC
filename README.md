# simPEATC

Simulador educativo de Potenciales Evocados Auditivos de Tronco Cerebral (PEATC/ABR).

Universidad Austral de Chile — Sede Puerto Montt.

## Migración a Rust

Reescritura en Rust en curso. La versión Python original está en la rama `python_legacy`.

### Estructura (workspace)

- `crates/aep-core` — motor de simulación de potenciales evocados auditivos
  (ECochG → ABR → MLR → ALR → P300/MMN → ASSR), **sin GUI** (testeable solo).
- `app/` — interfaz de escritorio con [Tauri 2](https://tauri.app): backend Rust
  (`app/src-tauri`) que expone `aep-core` por comandos + frontend web
  (React + Vite + TypeScript, gráficos con [ECharts](https://echarts.apache.org)).

### Uso

```bash
cargo test -p aep-core      # pruebas del motor

cd app
npm install                 # dependencias del frontend (una vez)
npm run tauri dev           # abre la app de escritorio
```
