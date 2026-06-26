//! El sujeto explorado y sus variables fisiologicas.

use crate::lesion::Lesion;

/// Oido estimulado / lateralidad.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Ear {
    /// Oido izquierdo (OI).
    Left,
    /// Oido derecho (OD).
    Right,
}

impl Ear {
    /// Etiqueta clinica en espanol ("OD" / "OI").
    pub fn label(self) -> &'static str {
        match self {
            Ear::Left => "OI",
            Ear::Right => "OD",
        }
    }

    /// El oido contrario.
    pub fn opposite(self) -> Ear {
        match self {
            Ear::Left => Ear::Right,
            Ear::Right => Ear::Left,
        }
    }
}

/// Edad del sujeto, en la unidad clinicamente relevante segun la etapa.
///
/// La maduracion auditiva es muy rapida en los primeros meses, por eso se
/// distingue prematuro (semanas de gestacion), neonato/lactante (dias) y
/// nino/adulto (anos).
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Age {
    /// Prematuro: edad gestacional en semanas.
    Gestational { weeks: f64 },
    /// Neonato/lactante: edad postnatal en dias.
    Postnatal { days: u32 },
    /// Nino/adulto/adulto mayor: edad en anos.
    Years { value: f64 },
}

impl Age {
    /// Edad aproximada en anos (post-termino), para curvas de maduracion.
    ///
    /// El prematuro se cuenta negativo respecto a las 40 semanas de termino.
    pub fn approx_years(self) -> f64 {
        match self {
            Age::Gestational { weeks } => (weeks - 40.0) / 52.0,
            Age::Postnatal { days } => days as f64 / 365.25,
            Age::Years { value } => value,
        }
    }
}

/// Sexo biologico (afecta latencias/amplitudes del ABR).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Sex {
    /// Masculino.
    Male,
    /// Femenino.
    Female,
}

/// Estado de alerta. Atenua componentes corticales (MLR/ALR); el ABR es robusto.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ArousalState {
    /// Despierto.
    Awake,
    /// Sueno natural.
    NaturalSleep,
    /// Sedado.
    Sedated,
    /// Anestesiado.
    Anesthetized,
}

/// Atencion del sujeto. Critico para P300 (sin atencion no hay P3b); el MMN es
/// preatencional.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Attention {
    /// Atiende activamente al estimulo (cuenta los raros).
    Active,
    /// Pasivo: oye pero no atiende.
    Passive,
    /// Ignora activamente (distraido con otra tarea).
    Ignoring,
}

/// Sujeto completo: variables fisiologicas + lesiones coexistentes.
#[derive(Debug, Clone, PartialEq)]
pub struct Subject {
    /// Edad.
    pub age: Age,
    /// Sexo.
    pub sex: Sex,
    /// Temperatura corporal en °C (la hipotermia alarga latencias).
    pub temperature_c: f64,
    /// Estado de alerta.
    pub state: ArousalState,
    /// Atencion.
    pub attention: Attention,
    /// Lesiones presentes (pueden coexistir, p.ej. mixta).
    pub lesions: Vec<Lesion>,
}

impl Default for Subject {
    /// Adulto sano, despierto, normotermico, sin lesiones.
    fn default() -> Self {
        Self {
            age: Age::Years { value: 30.0 },
            sex: Sex::Female,
            temperature_c: 37.0,
            state: ArousalState::Awake,
            attention: Attention::Passive,
            lesions: Vec::new(),
        }
    }
}

impl Subject {
    /// Lesiones que afectan a un oido dado.
    pub fn lesions_on(&self, ear: Ear) -> impl Iterator<Item = &Lesion> {
        self.lesions.iter().filter(move |l| l.ear == ear)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ear_label_y_opposite() {
        assert_eq!(Ear::Right.label(), "OD");
        assert_eq!(Ear::Left.label(), "OI");
        assert_eq!(Ear::Right.opposite(), Ear::Left);
    }

    #[test]
    fn edad_a_anos() {
        assert!((Age::Years { value: 25.0 }.approx_years() - 25.0).abs() < 1e-9);
        assert!(Age::Gestational { weeks: 32.0 }.approx_years() < 0.0);
        assert!((Age::Postnatal { days: 365 }.approx_years() - 1.0).abs() < 0.01);
    }

    #[test]
    fn default_es_adulto_sano() {
        let s = Subject::default();
        assert!(s.lesions.is_empty());
        assert_eq!(s.temperature_c, 37.0);
    }
}
