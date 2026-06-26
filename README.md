# simPEATC

Simulador educativo de Potenciales Evocados Auditivos de Tronco Cerebral (PEATC/ABR).

Universidad Austral de Chile — Sede Puerto Montt.

## Migración a Rust

Reescritura en Rust en curso. La versión Python original está en la rama `python_legacy`.

### Estructura (workspace)

- `crates/abr-core` — motor de simulación ABR, **sin GUI** (testeable solo).
- `crates/simpeatc-gui` — interfaz gráfica con [`iced`](https://iced.rs).

### Uso

```bash
cargo test -p abr-core   # pruebas del motor
cargo run -p simpeatc-gui  # abre la GUI
```
