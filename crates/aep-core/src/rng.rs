//! Generador pseudoaleatorio determinista, sin dependencias externas.
//!
//! Un LCG (generador congruencial lineal) de 64 bits basta para el ruido EEG
//! simulado: lo critico no es la calidad criptografica sino el **determinismo**
//! (misma semilla → misma secuencia) para reproducibilidad clinica y tests
//! (MOTOR.md §10). La semilla se deriva del protocolo+sujeto+sweep aguas arriba.

/// LCG de 64 bits (constantes de Knuth/MMIX).
#[derive(Debug, Clone)]
pub struct Lcg {
    state: u64,
    /// Cache del segundo valor de Box-Muller (genera gaussianas de a pares).
    spare: Option<f64>,
}

impl Lcg {
    /// Crea un generador a partir de una semilla.
    pub fn new(seed: u64) -> Self {
        // Mezcla inicial para evitar secuencias pobres con semillas pequenas.
        Self {
            state: seed ^ 0xDEAD_BEEF_CAFE_F00D,
            spare: None,
        }
    }

    /// Siguiente entero de 64 bits.
    pub fn next_u64(&mut self) -> u64 {
        self.state = self
            .state
            .wrapping_mul(6364136223846793005)
            .wrapping_add(1442695040888963407);
        // Devolver bits altos mezclados mejora la uniformidad de los bits bajos.
        let x = self.state;
        (x ^ (x >> 31)).wrapping_mul(0x2545_F491_4F6C_DD1D)
    }

    /// Siguiente flotante uniforme en `[0, 1)`.
    pub fn next_f64(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 / (1u64 << 53) as f64
    }

    /// Siguiente muestra gaussiana estandar `N(0, 1)` (Box-Muller polar).
    ///
    /// Genera dos valores por iteracion y cachea el segundo.
    pub fn next_gaussian(&mut self) -> f64 {
        if let Some(z) = self.spare.take() {
            return z;
        }
        // Box-Muller en forma trigonometrica.
        let u1 = (self.next_f64()).max(1e-12); // evita ln(0)
        let u2 = self.next_f64();
        let r = (-2.0 * u1.ln()).sqrt();
        let theta = std::f64::consts::TAU * u2;
        self.spare = Some(r * theta.sin());
        r * theta.cos()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn es_determinista() {
        let mut a = Lcg::new(42);
        let mut b = Lcg::new(42);
        for _ in 0..100 {
            assert_eq!(a.next_u64(), b.next_u64());
        }
    }

    #[test]
    fn semillas_distintas_difieren() {
        let mut a = Lcg::new(1);
        let mut b = Lcg::new(2);
        assert_ne!(a.next_u64(), b.next_u64());
    }

    #[test]
    fn uniforme_en_rango() {
        let mut g = Lcg::new(7);
        for _ in 0..10_000 {
            let x = g.next_f64();
            assert!((0.0..1.0).contains(&x));
        }
    }

    #[test]
    fn gaussiana_media_cero_aprox() {
        let mut g = Lcg::new(123);
        let n = 50_000;
        let mut sum = 0.0;
        let mut sum2 = 0.0;
        for _ in 0..n {
            let z = g.next_gaussian();
            sum += z;
            sum2 += z * z;
        }
        let mean = sum / n as f64;
        let var = sum2 / n as f64 - mean * mean;
        assert!(mean.abs() < 0.05, "media {mean}");
        assert!((var - 1.0).abs() < 0.1, "varianza {var}");
    }
}
