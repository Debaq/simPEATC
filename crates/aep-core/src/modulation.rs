//! Reglas clinicas de modulacion (MOTOR.md §7).
//!
//! Funciones **puras** que ajustan un `Component` (latencia/amplitud) segun una
//! variable. Cada modalidad declara cuales aplica. Se testean de forma aislada
//! con valores normativos conocidos. Todas mutan el componente in situ para
//! poder encadenarse en el modelo de respuesta.

use crate::component::Component;

/// Desplazamiento de latencia por intensidad (ms por 10 dB).
pub const SHIFT_PER_10DB: f64 = 0.3;
/// Temperatura de referencia (°C).
pub const TEMP_REF_C: f64 = 37.0;
/// Desplazamiento de latencia por hipotermia (ms por °C bajo la referencia).
pub const TEMP_COEF: f64 = 0.2;
/// Desplazamiento de latencia por tasa (ms por octava de tasa sobre la ref.).
pub const RATE_COEF: f64 = 0.15;

/// Aplica el efecto de la **intensidad efectiva** (nivel sobre umbral).
///
/// - A menor nivel respecto a `ref_db`, ↑ latencia (`SHIFT_PER_10DB` por 10 dB).
/// - La amplitud escala con el nivel efectivo; por debajo del umbral
///   (`effective_level_nhl <= 0`) el componente desaparece (amplitud 0).
pub fn apply_intensity(c: &mut Component, effective_level_nhl: f64, ref_db: f64) {
    if effective_level_nhl <= 0.0 {
        c.amplitude_uv = 0.0;
        return;
    }
    let shift = (ref_db - effective_level_nhl) / 10.0 * SHIFT_PER_10DB;
    c.latency_ms += shift;
    let amp_factor = (effective_level_nhl / ref_db).clamp(0.0, 1.3);
    c.amplitude_uv *= amp_factor;
}

/// Aplica el efecto de la temperatura: la hipotermia alarga la latencia.
pub fn apply_temperature(c: &mut Component, temp_c: f64) {
    let delta = TEMP_REF_C - temp_c; // hipotermia → positivo
    c.latency_ms += delta * TEMP_COEF;
}

/// Aplica el efecto de la **tasa de estimulacion**: tasas altas alargan la
/// latencia (fatiga neural) y atenuan algo la amplitud.
pub fn apply_rate(c: &mut Component, rate_hz: f64, ref_rate_hz: f64) {
    if rate_hz <= ref_rate_hz {
        return;
    }
    let octaves = (rate_hz / ref_rate_hz).log2();
    c.latency_ms += octaves * RATE_COEF;
    c.amplitude_uv *= (1.0 - 0.05 * octaves).max(0.5);
}

#[cfg(test)]
mod tests {
    use super::*;

    fn comp() -> Component {
        Component::gaussian("V", 5.6, 0.5, 0.4, "coliculo inferior")
    }

    #[test]
    fn menor_intensidad_alarga_y_atenua() {
        let mut alta = comp();
        let mut baja = comp();
        apply_intensity(&mut alta, 80.0, 80.0);
        apply_intensity(&mut baja, 40.0, 80.0);
        assert!(baja.latency_ms > alta.latency_ms);
        assert!(baja.amplitude_uv < alta.amplitude_uv);
    }

    #[test]
    fn intensidad_referencia_no_desplaza() {
        let mut c = comp();
        apply_intensity(&mut c, 80.0, 80.0);
        assert!((c.latency_ms - 5.6).abs() < 1e-9);
    }

    #[test]
    fn bajo_umbral_desaparece() {
        let mut c = comp();
        apply_intensity(&mut c, -5.0, 80.0);
        assert_eq!(c.amplitude_uv, 0.0);
    }

    #[test]
    fn hipotermia_alarga_latencia() {
        let mut frio = comp();
        let mut normo = comp();
        apply_temperature(&mut frio, 33.0); // 4 °C bajo 37
        apply_temperature(&mut normo, 37.0);
        assert!(frio.latency_ms > normo.latency_ms);
        assert!((frio.latency_ms - normo.latency_ms - 0.8).abs() < 1e-9);
    }

    #[test]
    fn tasa_alta_alarga_latencia() {
        let mut lenta = comp();
        let mut rapida = comp();
        apply_rate(&mut lenta, 11.1, 11.1);
        apply_rate(&mut rapida, 88.8, 11.1); // 3 octavas
        assert!(rapida.latency_ms > lenta.latency_ms);
    }
}
