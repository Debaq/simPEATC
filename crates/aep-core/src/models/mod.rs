//! Modelos de respuesta por modalidad.
//!
//! Cada modalidad implementa `ResponseModel`: produce los componentes neurales
//! "verdaderos" (ya modulados por sujeto y parametros), declara su adquisicion
//! recomendada y su ruido de fondo. El motor (`engine.rs`) selecciona el modelo
//! segun `protocol.modality` y ejecuta la cadena de adquisicion comun.
//!
//! Capa 0 implementa solo el ABR; el resto llega en capas posteriores.

pub mod abr;
pub mod alr;
pub mod cognitive;
pub mod ecochg;
pub mod mlr;

use crate::acquisition::Acquisition;
use crate::component::Component;
use crate::protocol::{Modality, Protocol};
use crate::subject::Subject;
use crate::synth::NoiseProfile;

/// Modelo de respuesta intercambiable por modalidad.
pub trait ResponseModel {
    /// Componentes neurales "verdaderos", ya modulados por sujeto y parametros.
    fn components(&self, protocol: &Protocol, subject: &Subject) -> Vec<Component>;

    /// Configuracion de adquisicion recomendada (filtro/ventana por defecto).
    fn recommended_acquisition(&self) -> Acquisition;

    /// Ruido EEG de fondo caracteristico de esta modalidad para el sujeto.
    fn background_noise(&self, subject: &Subject) -> NoiseProfile;
}

/// Selecciona el modelo de respuesta para una modalidad.
///
/// Devuelve `None` para las modalidades aun no implementadas (Capas 2-7).
pub fn model_for(modality: Modality) -> Option<Box<dyn ResponseModel>> {
    match modality {
        Modality::Abr => Some(Box::new(abr::AbrModel::new())),
        Modality::ECochG => Some(Box::new(ecochg::EcochgModel::new())),
        Modality::Mlr => Some(Box::new(mlr::MlrModel::new())),
        Modality::Alr => Some(Box::new(alr::AlrModel::new())),
        _ => None,
    }
}
