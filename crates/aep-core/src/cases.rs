//! Catalogo de **patologias** clinicas (MOTOR.md §3, §12; docs/PATOLOGIAS.md).
//!
//! Un caso es una **patologia**: su(s) lesion(es) (sitio, severidad, perfil). NO
//! incluye datos del sujeto (edad, sexo, temperatura, estado, atencion): esas son
//! **variables externas** de la sesion. La patologia sabe responder en TODOS los
//! examenes (ECochG, ABR, MLR, ALR, P300, MMN, ASSR): el motor deriva cada uno a
//! partir de las lesiones. El oido lo da el slot; el examen y la intensidad, el
//! equipo. Embebidos via `include_str!`.

use serde::{Deserialize, Serialize};

use crate::lesion::{FreqProfile, Lesion, LesionSite};
use crate::subject::Ear;

/// Una lesion del paciente (texto que se mapea al dominio). El oido lo fija el
/// slot al que se asigna el paciente, no la lesion.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CaseLesionDef {
    pub site: String,
    pub severity_db: f64,
    #[serde(default = "default_profile")]
    pub profile: String,
}

fn default_profile() -> String {
    "Flat".to_string()
}

/// Definicion de un caso clinico = **patologia** (lesiones, sin datos de sujeto).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CaseDef {
    /// Identificador estable (slug).
    pub id: String,
    /// Nombre legible.
    pub name: String,
    /// Descripcion didactica.
    pub description: String,
    /// Lesiones de la patologia (se aplican al oido del slot).
    #[serde(default)]
    pub lesions: Vec<CaseLesionDef>,
}

fn parse_site(s: &str) -> LesionSite {
    match s {
        "Conductive" => LesionSite::Conductive,
        "Cochlear" => LesionSite::Cochlear,
        "Retrocochlear" => LesionSite::Retrocochlear,
        "Neural" => LesionSite::Neural,
        "Central" => LesionSite::Central,
        "CentralConduction" => LesionSite::CentralConduction,
        "Brainstem" => LesionSite::Brainstem,
        "Cortical" => LesionSite::Cortical,
        "Cognitive" => LesionSite::Cognitive,
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
    /// Lesiones de la patologia aplicadas a `ear` (el oido del slot). Las
    /// variables del sujeto (edad, sexo, estado…) son externas y se combinan con
    /// estas lesiones al capturar.
    pub fn lesions(&self, ear: Ear) -> Vec<Lesion> {
        self.lesions
            .iter()
            .map(|l| Lesion {
                site: parse_site(&l.site),
                ear,
                severity_db: l.severity_db,
                freq_profile: parse_profile(&l.profile),
            })
            .collect()
    }

    /// Resumen corto de la patologia, para listarlo en el catalogo.
    pub fn summary(&self) -> String {
        if self.lesions.is_empty() {
            return "Normal".to_string();
        }
        self.lesions
            .iter()
            .map(|l| format!("{} {:.0} dB {}", l.site, l.severity_db, l.profile))
            .collect::<Vec<_>>()
            .join(" + ")
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

    /// Carga un catalogo desde un JSON (mismo formato que `cases.json`). Util para
    /// catalogos externos y para fixtures de prueba.
    pub fn from_json(s: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(s)
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
    use crate::protocol::Protocol;
    use crate::subject::{Age, Attention, ArousalState, Sex, Subject};

    fn adulto(lesions: Vec<Lesion>) -> Subject {
        Subject {
            age: Age::Years { value: 30.0 },
            sex: Sex::Female,
            temperature_c: 37.0,
            state: ArousalState::Awake,
            attention: Attention::Passive,
            lesions,
        }
    }

    #[test]
    fn catalogo_embebido_parsea_y_trae_normal() {
        let cat = CaseCatalog::embedded();
        assert!(!cat.is_empty());
        assert!(cat.get("normal").is_some());
    }

    #[test]
    fn normal_no_tiene_lesiones_y_examina() {
        let cat = CaseCatalog::embedded();
        let normal = cat.get("normal").unwrap();
        assert!(normal.lesions(Ear::Right).is_empty());
        let s = adulto(normal.lesions(Ear::Right));
        for proto in [
            Protocol::abr_click(Ear::Right),
            Protocol::mlr(Ear::Right),
            Protocol::alr(Ear::Right),
        ] {
            let rec = EvokedPotentialEngine::simulate(&proto, &s);
            assert!(rec.primary().is_some());
        }
    }

    #[test]
    fn lesiones_se_aplican_al_oido_del_slot() {
        let json = r#"{ "cases": [ {
            "id": "x", "name": "X", "description": "",
            "lesions": [ { "site": "Cochlear", "severity_db": 50, "profile": "HighFrequency" } ]
        } ] }"#;
        let cat = CaseCatalog::from_json(json).unwrap();
        let les = cat.get("x").unwrap().lesions(Ear::Left);
        assert_eq!(les.len(), 1);
        assert!(les.iter().all(|l| l.ear == Ear::Left));
    }

    #[test]
    fn summary_resume_la_patologia() {
        let cat = CaseCatalog::embedded();
        assert_eq!(cat.get("normal").unwrap().summary(), "Normal");
    }
}
