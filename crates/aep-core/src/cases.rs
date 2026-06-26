//! Catalogo de presets clinicos (MOTOR.md §3, §12).
//!
//! Casos prearmados para ensenanza y evaluacion: cada uno fija un sujeto (edad,
//! sexo, lesiones) y un protocolo (intensidad, oido, promediaciones) que el
//! motor convierte en un registro coherente con su diagnostico. Disenados desde
//! cero (no portados); embebidos via `include_str!`.

use serde::Deserialize;

use crate::acquisition::Acquisition;
use crate::lesion::{FreqProfile, Lesion, LesionSite};
use crate::protocol::Protocol;
use crate::stimulus::Stimulus;
use crate::subject::{Age, ArousalState, Attention, Ear, Sex, Subject};
use crate::units::Level;

/// Una lesion dentro de un caso (texto que se mapea al dominio).
#[derive(Debug, Clone, Deserialize)]
struct CaseLesionDef {
    site: String,
    severity_db: f64,
    #[serde(default = "default_profile")]
    profile: String,
}

fn default_profile() -> String {
    "Flat".to_string()
}

fn default_temp() -> f64 {
    37.0
}

fn default_modality() -> String {
    "Abr".to_string()
}

fn default_state() -> String {
    "Awake".to_string()
}

/// Definicion de un caso clinico.
#[derive(Debug, Clone, Deserialize)]
pub struct CaseDef {
    /// Identificador estable (slug).
    pub id: String,
    /// Nombre legible.
    pub name: String,
    /// Descripcion didactica.
    pub description: String,
    /// Modalidad ("Abr"/"ECochG"). Por defecto "Abr".
    #[serde(default = "default_modality")]
    pub modality: String,
    /// Oido explorado ("Left"/"Right").
    pub ear: String,
    /// Intensidad del estimulo (dB nHL).
    pub intensity_db_nhl: f64,
    /// Promediaciones objetivo.
    pub sweeps: u32,
    /// Edad en años.
    pub age_years: f64,
    /// Sexo ("Male"/"Female").
    pub sex: String,
    /// Temperatura corporal (°C).
    #[serde(default = "default_temp")]
    pub temperature_c: f64,
    /// Estado de alerta ("Awake"/"NaturalSleep"/"Sedated"/"Anesthetized").
    #[serde(default = "default_state")]
    pub state: String,
    /// Lesiones del caso (sobre el oido explorado).
    #[serde(default)]
    lesions: Vec<CaseLesionDef>,
}

fn parse_ear(s: &str) -> Ear {
    match s {
        "Left" | "OI" | "left" => Ear::Left,
        _ => Ear::Right,
    }
}

fn parse_sex(s: &str) -> Sex {
    match s {
        "Male" | "male" | "M" => Sex::Male,
        _ => Sex::Female,
    }
}

fn parse_state(s: &str) -> ArousalState {
    match s {
        "NaturalSleep" => ArousalState::NaturalSleep,
        "Sedated" => ArousalState::Sedated,
        "Anesthetized" => ArousalState::Anesthetized,
        _ => ArousalState::Awake,
    }
}

fn parse_site(s: &str) -> LesionSite {
    match s {
        "Conductive" => LesionSite::Conductive,
        "Cochlear" => LesionSite::Cochlear,
        "Retrocochlear" => LesionSite::Retrocochlear,
        "Neural" => LesionSite::Neural,
        "Central" => LesionSite::Central,
        _ => LesionSite::Cochlear,
    }
}

fn parse_profile(s: &str) -> FreqProfile {
    match s {
        "HighFrequency" => FreqProfile::HighFrequency,
        "LowFrequency" => FreqProfile::LowFrequency,
        "CookieBite" => FreqProfile::CookieBite,
        _ => FreqProfile::Flat,
    }
}

impl CaseDef {
    /// Oido explorado.
    pub fn ear(&self) -> Ear {
        parse_ear(&self.ear)
    }

    /// Construye el sujeto del caso.
    pub fn subject(&self) -> Subject {
        let ear = self.ear();
        let lesions = self
            .lesions
            .iter()
            .map(|l| Lesion {
                site: parse_site(&l.site),
                ear,
                severity_db: l.severity_db,
                freq_profile: parse_profile(&l.profile),
            })
            .collect();
        Subject {
            age: Age::Years {
                value: self.age_years,
            },
            sex: parse_sex(&self.sex),
            temperature_c: self.temperature_c,
            state: parse_state(&self.state),
            attention: Attention::Passive,
            lesions,
        }
    }

    /// Construye el protocolo del caso segun su modalidad.
    pub fn protocol(&self) -> Protocol {
        let ear = self.ear();
        let mut p = match self.modality.as_str() {
            "ECochG" | "Ecochg" | "ecochg" => Protocol::ecochg(ear),
            "Mlr" | "MLR" | "mlr" => Protocol::mlr(ear),
            _ => Protocol::abr_click(ear),
        };
        p.stimulus = Stimulus {
            level: Level::DbNhl(self.intensity_db_nhl),
            ..p.stimulus
        };
        p.acquisition = Acquisition {
            sweeps: self.sweeps,
            ..p.acquisition
        };
        p
    }
}

/// Catalogo de casos.
#[derive(Debug, Clone, Deserialize)]
pub struct CaseCatalog {
    cases: Vec<CaseDef>,
}

const EMBEDDED_CASES: &str = include_str!("../data/cases.json");

impl CaseCatalog {
    /// Catalogo embebido.
    pub fn embedded() -> Self {
        serde_json::from_str(EMBEDDED_CASES).expect("cases.json embebido invalido")
    }

    /// Casos del catalogo.
    pub fn cases(&self) -> &[CaseDef] {
        &self.cases
    }

    /// Identificadores disponibles.
    pub fn ids(&self) -> Vec<&str> {
        self.cases.iter().map(|c| c.id.as_str()).collect()
    }

    /// Busca un caso por id.
    pub fn get(&self, id: &str) -> Option<&CaseDef> {
        self.cases.iter().find(|c| c.id == id)
    }

    /// Numero de casos.
    pub fn len(&self) -> usize {
        self.cases.len()
    }

    /// `true` si el catalogo esta vacio.
    pub fn is_empty(&self) -> bool {
        self.cases.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::engine::EvokedPotentialEngine;

    #[test]
    fn catalogo_embebido_parsea() {
        let cat = CaseCatalog::embedded();
        assert!(!cat.is_empty());
        assert!(cat.get("normal").is_some());
        assert!(cat.get("neurinoma").is_some());
    }

    #[test]
    fn caso_normal_construye_sujeto_sano() {
        let cat = CaseCatalog::embedded();
        let normal = cat.get("normal").unwrap();
        let s = normal.subject();
        assert!(s.lesions.is_empty());
        let p = normal.protocol();
        assert_eq!(p.stimulus.level.as_nhl(), 80.0);
    }

    #[test]
    fn mixta_tiene_dos_lesiones_en_el_oido() {
        let cat = CaseCatalog::embedded();
        let mixta = cat.get("mixta").unwrap();
        let s = mixta.subject();
        assert_eq!(s.lesions.len(), 2);
        assert!(s.lesions.iter().all(|l| l.ear == mixta.ear()));
    }

    #[test]
    fn meniere_es_ecochg_con_sp_ap_elevada() {
        use crate::models::model_for;
        let cat = CaseCatalog::embedded();
        let meniere = cat.get("meniere").unwrap();
        let p = meniere.protocol();
        assert_eq!(p.modality, crate::protocol::Modality::ECochG);
        // Razon SP/AP a nivel de componentes (fisiologia limpia, sin sesgo DSP).
        let model = model_for(p.modality).unwrap();
        let comps = model.components(&p, &meniere.subject());
        let sp = comps.iter().find(|c| c.label == "SP").unwrap().amplitude_uv.abs();
        let ap = comps.iter().find(|c| c.label == "AP").unwrap().amplitude_uv.abs();
        assert!(sp / ap > 0.4, "SP/AP = {}", sp / ap);
    }

    #[test]
    fn todos_los_casos_simulan_sin_panico() {
        let cat = CaseCatalog::embedded();
        for c in cat.cases() {
            let rec = EvokedPotentialEngine::simulate(&c.protocol(), &c.subject());
            assert!(rec.primary().is_some(), "caso {} sin canal", c.id);
        }
    }
}
