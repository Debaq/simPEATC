//! El componente: unidad atomica comun a TODAS las modalidades.
//!
//! Un potencial evocado es una suma de componentes (picos) con latencia,
//! amplitud, ancho, forma y polaridad. Lo que cambia entre ECochG, ABR, MLR…
//! es *que* componentes existen y *de que* dependen, no la estructura. Por eso
//! `Component` es el tipo central que produce cada `ResponseModel`.

/// Forma de onda de un componente.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ComponentShape {
    /// Pico gaussiano simetrico (la mayoria de los picos de AEP).
    Gaussian,
    /// Escalon sostenido (p.ej. el Summating Potential de la ECochG).
    Step,
    /// Microfonico coclear: oscilacion a la frecuencia del estimulo bajo una
    /// envolvente gaussiana. Sigue la forma del estimulo y se invierte con la
    /// polaridad (el modelo lo cancela en alternante poniendo amplitud 0).
    Microphonic {
        /// Frecuencia de la oscilacion (Hz), tipicamente la del estimulo.
        freq_hz: f64,
    },
}

/// Componente neural "verdadero" (antes de la adquisicion).
///
/// `label`/`generator` son `String` para poder construirse desde datos
/// normativos cargados en runtime (JSON), no solo desde literales.
#[derive(Debug, Clone, PartialEq)]
pub struct Component {
    /// Etiqueta clinica ("I", "III", "V", "SP", "AP", "Pa", "P3b"…).
    pub label: String,
    /// Latencia del pico (ms) relativa al estimulo.
    pub latency_ms: f64,
    /// Amplitud con signo (µV); el signo codifica la polaridad de la deflexion.
    pub amplitude_uv: f64,
    /// Ancho (sigma de la plantilla, ms).
    pub width_ms: f64,
    /// Forma.
    pub shape: ComponentShape,
    /// Texto didactico del generador anatomico.
    pub generator: String,
}

impl Component {
    /// Constructor conciso para un pico gaussiano.
    pub fn gaussian(
        label: impl Into<String>,
        latency_ms: f64,
        amplitude_uv: f64,
        width_ms: f64,
        generator: impl Into<String>,
    ) -> Self {
        Self {
            label: label.into(),
            latency_ms,
            amplitude_uv,
            width_ms,
            shape: ComponentShape::Gaussian,
            generator: generator.into(),
        }
    }

    /// Constructor conciso para un microfonico coclear.
    pub fn microphonic(
        label: impl Into<String>,
        latency_ms: f64,
        amplitude_uv: f64,
        width_ms: f64,
        freq_hz: f64,
        generator: impl Into<String>,
    ) -> Self {
        Self {
            label: label.into(),
            latency_ms,
            amplitude_uv,
            width_ms,
            shape: ComponentShape::Microphonic { freq_hz },
            generator: generator.into(),
        }
    }

    /// Evalua la contribucion del componente en el instante `t` (ms).
    pub fn evaluate(&self, t: f64) -> f64 {
        let w = self.width_ms.max(1e-6);
        match self.shape {
            ComponentShape::Gaussian => {
                let d = t - self.latency_ms;
                self.amplitude_uv * (-(d * d) / (2.0 * w * w)).exp()
            }
            ComponentShape::Step => {
                // Escalon suave (tanh) centrado en la latencia, anchura `w`.
                let d = t - self.latency_ms;
                self.amplitude_uv * 0.5 * (1.0 + (d / w).tanh())
            }
            ComponentShape::Microphonic { freq_hz } => {
                // Oscilacion bajo una envolvente gaussiana. `t` en ms → s.
                let d = t - self.latency_ms;
                let env = (-(d * d) / (2.0 * w * w)).exp();
                let phase = std::f64::consts::TAU * freq_hz * (t / 1000.0);
                self.amplitude_uv * env * phase.sin()
            }
        }
    }
}

/// Pico **detectado** sobre la curva ya promediada (lo que el equipo mide).
///
/// A diferencia de `Component` (la verdad fisiologica), solo lleva lo medible:
/// etiqueta, latencia y amplitud.
#[derive(Debug, Clone, PartialEq, serde::Serialize)]
pub struct WavePeak {
    /// Etiqueta de la onda.
    pub label: String,
    /// Latencia medida (ms).
    pub latency_ms: f64,
    /// Amplitud medida (µV).
    pub amplitude_uv: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    fn gauss(lat: f64) -> Component {
        Component::gaussian("V", lat, 0.5, 0.3, "coliculo inferior")
    }

    #[test]
    fn gaussiana_maxima_en_latencia() {
        let c = gauss(5.6);
        assert!((c.evaluate(5.6) - 0.5).abs() < 1e-9);
        assert!(c.evaluate(5.6) > c.evaluate(6.6));
        assert!(c.evaluate(5.6) > c.evaluate(4.6));
    }

    #[test]
    fn microphonic_oscila_y_decae() {
        let c = Component::microphonic("CM", 0.0, 0.3, 2.0, 2000.0, "celulas ciliadas externas");
        // Lejos de la latencia la envolvente decae a ~0.
        assert!(c.evaluate(10.0).abs() < 1e-3);
        // Dentro de la envolvente la oscilacion toma valores de ambos signos.
        let vals: Vec<f64> = (0..200).map(|i| c.evaluate(i as f64 * 0.01)).collect();
        assert!(vals.iter().any(|&v| v > 0.01));
        assert!(vals.iter().any(|&v| v < -0.01));
    }

    #[test]
    fn step_satura_a_amplitud() {
        let c = Component {
            label: "SP".into(),
            latency_ms: 1.0,
            amplitude_uv: 0.4,
            width_ms: 0.2,
            shape: ComponentShape::Step,
            generator: "celulas ciliadas".into(),
        };
        // Muy despues del escalon → ~amplitud plena.
        assert!((c.evaluate(5.0) - 0.4).abs() < 1e-3);
        // Muy antes → ~0.
        assert!(c.evaluate(-3.0).abs() < 1e-3);
    }
}
