//! Reglas clinicas de modulacion (MOTOR.md §7).
//!
//! Funciones **puras** que ajustan un `Component` (latencia/amplitud) segun una
//! variable. Cada modalidad declara cuales aplica. Se testean de forma aislada
//! con valores normativos conocidos. Todas mutan el componente in situ para
//! poder encadenarse en el modelo de respuesta.
//!
//! La tabla normativa se toma como **varon adulto (~30 años)**; el sexo y la
//! edad se aplican como modulacion sobre esa referencia.

use crate::component::Component;
use crate::stimulus::Polarity;
use crate::subject::Sex;

/// Desplazamiento de latencia por intensidad (ms por 10 dB).
pub const SHIFT_PER_10DB: f64 = 0.3;
/// Temperatura de referencia (°C).
pub const TEMP_REF_C: f64 = 37.0;
/// Desplazamiento de latencia por hipotermia (ms por °C bajo la referencia).
pub const TEMP_COEF: f64 = 0.2;
/// Desplazamiento de latencia por tasa (ms por octava de tasa sobre la ref.).
pub const RATE_COEF: f64 = 0.15;
/// Frecuencia de referencia del tone-burst (Hz) para la dependencia de latencia.
pub const TONE_FREQ_REF_HZ: f64 = 2000.0;
/// Alargamiento de latencia por octava por debajo de la referencia (ms).
pub const TONE_FREQ_LAT_COEF: f64 = 0.5;
/// Acortamiento relativo de latencia en la mujer (factor multiplicativo).
pub const FEMALE_LAT_FACTOR: f64 = 0.98;
/// Aumento relativo de amplitud en la mujer.
pub const FEMALE_AMP_FACTOR: f64 = 1.15;

/// Aplica el efecto de la **intensidad** sobre latencia y amplitud por separado.
///
/// - `level_for_latency`: nivel (dB nHL) que determina la latencia. La perdida
///   conductiva lo reduce (alarga la latencia); la coclear NO (reclutamiento).
/// - `margin_db`: cuanto se supera el umbral total (determina la amplitud).
///   Si es ≤ 0 el componente desaparece (bajo umbral).
pub fn apply_intensity(c: &mut Component, level_for_latency: f64, margin_db: f64, ref_db: f64) {
    if margin_db <= 0.0 {
        c.amplitude_uv = 0.0;
        return;
    }
    let shift = (ref_db - level_for_latency) / 10.0 * SHIFT_PER_10DB;
    c.latency_ms += shift;
    let amp_factor = (margin_db / ref_db).clamp(0.0, 1.3);
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

/// Aplica el efecto del **sexo**: la mujer tiene latencias algo mas cortas y
/// amplitudes mayores que el varon (referencia normativa).
pub fn apply_sex(c: &mut Component, sex: Sex) {
    if let Sex::Female = sex {
        c.latency_ms *= FEMALE_LAT_FACTOR;
        c.amplitude_uv *= FEMALE_AMP_FACTOR;
    }
}

/// Cuanto madura una onda con la edad (las tardias maduran mas tarde).
fn wave_maturation_factor(label: &str) -> f64 {
    match label {
        "I" => 0.4,
        "II" => 0.5,
        "III" => 0.7,
        "IV" => 0.85,
        _ => 1.0, // V, VI, VII
    }
}

/// Aplica el efecto de la **edad** (maduracion).
///
/// Neonato/lactante: latencias largas (mielinizacion incompleta) que decaen
/// rapido hacia los ~2 años. Prematuro: efecto mayor. Adulto: referencia (~0).
/// Adulto mayor: leve aumento. El retraso es mayor en las ondas tardias, asi que
/// el intervalo I–V tambien se alarga en el neonato.
pub fn apply_age(c: &mut Component, years: f64) {
    let base = if years >= 0.0 {
        // Decaimiento exponencial desde ~1 ms al nacer (tau ~0.5 años).
        (-years / 0.5).exp()
    } else {
        // Prematuro (edad post-termino negativa): mas inmaduro.
        1.0 + (-years) * 3.0
    };
    let maturation = base * wave_maturation_factor(&c.label);
    let aging = if years > 60.0 {
        (years - 60.0) * 0.004 // leve aumento en el adulto mayor
    } else {
        0.0
    };
    c.latency_ms += maturation + aging;
}

/// Aplica la dependencia de **frecuencia** del tone-burst.
///
/// Los tonos graves dan latencias mas largas (la onda viajera tarda en llegar
/// al apice) y amplitudes algo menores (respuesta mas dispersa) que los agudos.
/// Solo se aplica a estimulos especificos en frecuencia (tone-burst), no al
/// click ni al chirp.
pub fn apply_tone_frequency(c: &mut Component, freq_hz: f64, ref_hz: f64) {
    if freq_hz <= 0.0 {
        return;
    }
    let octaves_below = (ref_hz / freq_hz).log2().max(0.0);
    c.latency_ms += octaves_below * TONE_FREQ_LAT_COEF;
    c.amplitude_uv *= (1.0 - 0.08 * octaves_below).max(0.6);
}

/// Aplica el efecto de la **polaridad** del estimulo (sutil en el ABR; afecta
/// sobre todo la onda I). La rarefaccion adelanta ligeramente; la condensacion
/// retrasa; la alternante promedia (sin efecto).
pub fn apply_polarity(c: &mut Component, polarity: Polarity) {
    let weight = match c.label.as_str() {
        "I" => 1.0,
        "II" | "III" => 0.4,
        _ => 0.0,
    };
    let shift = 0.05 * weight;
    match polarity {
        Polarity::Rarefaction => c.latency_ms -= shift,
        Polarity::Condensation => c.latency_ms += shift,
        Polarity::Alternating => {}
    }
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
        apply_intensity(&mut alta, 80.0, 80.0, 80.0);
        apply_intensity(&mut baja, 40.0, 40.0, 80.0);
        assert!(baja.latency_ms > alta.latency_ms);
        assert!(baja.amplitude_uv < alta.amplitude_uv);
    }

    #[test]
    fn intensidad_referencia_no_desplaza() {
        let mut c = comp();
        apply_intensity(&mut c, 80.0, 80.0, 80.0);
        assert!((c.latency_ms - 5.6).abs() < 1e-9);
    }

    #[test]
    fn reclutamiento_coclear_no_alarga_latencia() {
        // Coclear: level_for_latency alto (no resta umbral), margin reducido.
        let mut c = comp();
        apply_intensity(&mut c, 80.0, 30.0, 80.0);
        // Latencia normal (reclutamiento) pero amplitud reducida.
        assert!((c.latency_ms - 5.6).abs() < 1e-9);
        assert!(c.amplitude_uv < 0.5);
    }

    #[test]
    fn bajo_umbral_desaparece() {
        let mut c = comp();
        apply_intensity(&mut c, 80.0, -5.0, 80.0);
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

    #[test]
    fn mujer_latencia_mas_corta_amplitud_mayor() {
        let mut m = comp();
        let mut h = comp();
        apply_sex(&mut m, Sex::Female);
        apply_sex(&mut h, Sex::Male);
        assert!(m.latency_ms < h.latency_ms);
        assert!(m.amplitude_uv > h.amplitude_uv);
    }

    #[test]
    fn neonato_latencia_mas_larga_que_adulto() {
        let mut bebe = comp();
        let mut adulto = comp();
        apply_age(&mut bebe, 0.0);
        apply_age(&mut adulto, 30.0);
        assert!(bebe.latency_ms > adulto.latency_ms);
        assert!((adulto.latency_ms - 5.6).abs() < 0.01); // adulto ≈ referencia
    }

    #[test]
    fn maduracion_mayor_en_ondas_tardias() {
        let mut i = Component::gaussian("I", 1.5, 0.25, 0.3, "VIII");
        let mut v = comp();
        apply_age(&mut i, 0.0);
        apply_age(&mut v, 0.0);
        let shift_i = i.latency_ms - 1.5;
        let shift_v = v.latency_ms - 5.6;
        assert!(shift_v > shift_i); // la V madura mas tarde → mas desplazada
    }

    #[test]
    fn tono_grave_mas_tardio_y_menor_que_agudo() {
        let mut grave = comp();
        let mut agudo = comp();
        apply_tone_frequency(&mut grave, 500.0, TONE_FREQ_REF_HZ);
        apply_tone_frequency(&mut agudo, 4000.0, TONE_FREQ_REF_HZ);
        assert!(grave.latency_ms > agudo.latency_ms);
        assert!(grave.amplitude_uv < agudo.amplitude_uv);
    }

    #[test]
    fn polaridad_afecta_onda_i() {
        let mut rar = Component::gaussian("I", 1.5, 0.25, 0.3, "VIII");
        let mut cond = Component::gaussian("I", 1.5, 0.25, 0.3, "VIII");
        apply_polarity(&mut rar, Polarity::Rarefaction);
        apply_polarity(&mut cond, Polarity::Condensation);
        assert!(rar.latency_ms < cond.latency_ms);
    }
}
