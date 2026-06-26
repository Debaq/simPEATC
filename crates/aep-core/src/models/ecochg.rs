//! Modelo de respuesta de la electrococleografia (ECochG).
//!
//! Tres componentes con generadores distintos (MOTOR.md §2):
//! - **CM** (microfonico coclear): oscilacion de las celulas ciliadas externas
//!   que **sigue la polaridad** del estimulo (se invierte; se **cancela** con
//!   estimulo alternante). Presente aunque el nervio falle (neuropatia).
//! - **SP** (potencial de sumacion): deflexion DC sostenida (escalon) de las
//!   celulas ciliadas; el **hidrops endolinfatico (Ménière)** lo aumenta.
//! - **AP** (potencial de accion, N1/N2): descarga del nervio auditivo distal
//!   (equivale a la onda I); ausente en la neuropatia.
//!
//! La amplitud depende mucho del **electrodo**: promontorio (transtimpanica,
//! TT) ≫ membrana timpanica (TM) ≫ conducto (extratimpanica, EAC).

use super::ResponseModel;
use crate::acquisition::{Acquisition, ElectrodeSite};
use crate::component::{Component, ComponentShape};
use crate::lesion::{Lesion, LesionSite};
use crate::protocol::Protocol;
use crate::stimulus::Polarity;
use crate::subject::{Ear, Subject};
use crate::synth::NoiseProfile;

/// Modelo ECochG.
#[derive(Debug, Clone, Default)]
pub struct EcochgModel;

impl EcochgModel {
    /// Crea el modelo.
    pub fn new() -> Self {
        Self
    }
}

/// Ganancia de amplitud segun la cercania del electrodo a la coclea.
fn electrode_gain(site: ElectrodeSite) -> f64 {
    match site {
        ElectrodeSite::Promontory(_) => 1.0,        // transtimpanica (TT)
        ElectrodeSite::TympanicMembrane(_) => 0.5,  // timpanica (TM)
        ElectrodeSite::EarCanal(_) => 0.15,         // extratimpanica (EAC)
        _ => 0.1,                                   // lejana
    }
}

impl ResponseModel for EcochgModel {
    fn components(&self, protocol: &Protocol, subject: &Subject) -> Vec<Component> {
        let stim = &protocol.stimulus;
        let ear = stim.ear;
        let freq = stim.kind.dominant_freq_hz();
        let level = stim.level.as_nhl();

        // Electrodo activo del montaje.
        let active = protocol
            .acquisition
            .montage
            .channels
            .first()
            .map(|c| c.noninv)
            .unwrap_or(ElectrodeSite::Promontory(ear));
        let gain = electrode_gain(active);

        // Reparto de umbral + hidrops + estado neural.
        let lesions: Vec<&Lesion> = subject.lesions_on(ear).collect();
        let mut th_cond = 0.0;
        let mut th_coch = 0.0_f64;
        let mut hydrops = 0.0_f64;
        let mut neural_keep = 1.0_f64;
        for l in &lesions {
            let s = l.threshold_shift_at(freq);
            match l.site {
                LesionSite::Conductive => th_cond += s,
                LesionSite::Cochlear => {
                    th_coch = th_coch.max(s);
                    // En ECochG, una alteracion coclear se interpreta como
                    // hidrops endolinfatico: aumenta el SP.
                    hydrops = hydrops.max(l.severity_db);
                }
                LesionSite::Neural => {
                    neural_keep = neural_keep.min((1.0 - l.severity_db / 60.0).clamp(0.0, 1.0));
                }
                _ => {}
            }
        }
        let level_at_cochlea = level - th_cond;
        let margin = (level_at_cochlea - th_coch).max(0.0);
        let resp = (margin / 80.0).clamp(0.0, 1.2);

        let mut comps = Vec::new();

        // CM: sigue la polaridad; se cancela en alternante. Robusto al estado
        // neural (es coclear), por eso persiste en la neuropatia.
        let cm_sign = match stim.polarity {
            Polarity::Rarefaction => 1.0,
            Polarity::Condensation => -1.0,
            Polarity::Alternating => 0.0,
        };
        if cm_sign != 0.0 {
            let cm_amp = 0.30 * gain * cm_sign;
            comps.push(Component::microphonic(
                "CM",
                0.0,
                cm_amp,
                1.2,
                freq,
                "Celulas ciliadas externas (microfonico coclear)",
            ));
        }

        // SP: escalon DC negativo; el hidrops lo aumenta de forma marcada.
        let sp_amp = -(0.08 + hydrops / 100.0 * 0.4) * gain * (0.5 + 0.5 * resp);
        comps.push(Component {
            label: "SP".into(),
            latency_ms: 0.6,
            amplitude_uv: sp_amp,
            width_ms: 0.3,
            shape: ComponentShape::Step,
            generator: "Celulas ciliadas (distorsion: potencial de sumacion)".into(),
        });

        // AP (N1/N2): nervio auditivo distal, deflexion negativa; ausente si hay
        // desincronia neural.
        let ap_amp = -0.5 * gain * resp * neural_keep;
        if ap_amp.abs() > 1e-6 {
            comps.push(Component::gaussian(
                "AP",
                1.5,
                ap_amp,
                0.3,
                "Nervio auditivo distal (potencial de accion, N1)",
            ));
            comps.push(Component::gaussian(
                "N2",
                2.4,
                ap_amp * 0.5,
                0.35,
                "Nervio auditivo (N2)",
            ));
        }
        comps
    }

    fn recommended_acquisition(&self) -> Acquisition {
        Acquisition::ecochg_default(Ear::Right)
    }

    fn background_noise(&self, _subject: &Subject) -> NoiseProfile {
        // El registro de promontorio tiene buena relacion senal/ruido.
        NoiseProfile::new(0.3)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::lesion::FreqProfile;
    use crate::stimulus::StimulusKind;
    use crate::units::Level;

    fn amp(comps: &[Component], label: &str) -> Option<f64> {
        comps.iter().find(|c| c.label == label).map(|c| c.amplitude_uv)
    }

    fn sp_ap_ratio(comps: &[Component]) -> f64 {
        let sp = amp(comps, "SP").unwrap().abs();
        let ap = amp(comps, "AP").unwrap().abs();
        sp / ap
    }

    #[test]
    fn cm_sigue_la_polaridad() {
        let model = EcochgModel::new();
        let mut p = Protocol::ecochg(Ear::Right);
        let s = Subject::default();

        p.stimulus.polarity = Polarity::Rarefaction;
        let rar = amp(&model.components(&p, &s), "CM").unwrap();
        p.stimulus.polarity = Polarity::Condensation;
        let cond = amp(&model.components(&p, &s), "CM").unwrap();
        // Se invierte con la polaridad.
        assert!(rar > 0.0 && cond < 0.0);
        assert!((rar + cond).abs() < 1e-9);
    }

    #[test]
    fn cm_se_cancela_en_alternante() {
        let model = EcochgModel::new();
        let mut p = Protocol::ecochg(Ear::Right);
        p.stimulus.polarity = Polarity::Alternating;
        let comps = model.components(&p, &Subject::default());
        assert!(comps.iter().all(|c| c.label != "CM"));
    }

    #[test]
    fn electrodo_promontorio_da_mas_amplitud_que_conducto() {
        let model = EcochgModel::new();
        let ear = Ear::Right;
        let mut tt = Protocol::ecochg(ear);
        tt.acquisition.montage =
            crate::acquisition::Montage::ecochg(ear, ElectrodeSite::Promontory(ear));
        let mut eac = Protocol::ecochg(ear);
        eac.acquisition.montage =
            crate::acquisition::Montage::ecochg(ear, ElectrodeSite::EarCanal(ear));
        let ap_tt = amp(&model.components(&tt, &Subject::default()), "AP").unwrap().abs();
        let ap_eac = amp(&model.components(&eac, &Subject::default()), "AP").unwrap().abs();
        assert!(ap_tt > ap_eac * 3.0, "TT={ap_tt} EAC={ap_eac}");
    }

    #[test]
    fn neuropatia_cm_presente_ap_ausente() {
        let model = EcochgModel::new();
        let p = Protocol::ecochg(Ear::Right);
        let mut s = Subject::default();
        s.lesions.push(Lesion {
            site: LesionSite::Neural,
            ear: Ear::Right,
            severity_db: 60.0,
            freq_profile: FreqProfile::Flat,
        });
        let comps = model.components(&p, &s);
        assert!(comps.iter().any(|c| c.label == "CM"), "CM deberia persistir");
        assert!(comps.iter().all(|c| c.label != "AP"), "AP deberia desaparecer");
    }

    #[test]
    fn hidrops_eleva_la_razon_sp_ap() {
        let model = EcochgModel::new();
        let p = Protocol::ecochg(Ear::Right);
        let sano = Subject::default();
        let mut meniere = Subject::default();
        meniere.lesions.push(Lesion {
            site: LesionSite::Cochlear,
            ear: Ear::Right,
            severity_db: 40.0,
            freq_profile: FreqProfile::Flat,
        });
        let r_sano = sp_ap_ratio(&model.components(&p, &sano));
        let r_men = sp_ap_ratio(&model.components(&p, &meniere));
        assert!(r_men > r_sano, "sano={r_sano} meniere={r_men}");
        assert!(r_men > 0.4, "ratio Ménière deberia estar elevada: {r_men}");
    }

    #[test]
    fn cm_freq_sigue_al_tono() {
        // Con tone-burst la frecuencia del CM es la del tono.
        let model = EcochgModel::new();
        let mut p = Protocol::ecochg(Ear::Right);
        p.stimulus.kind = StimulusKind::ToneBurst {
            freq_hz: 1000.0,
            cycles_rise: 2,
            cycles_plateau: 1,
            cycles_fall: 2,
            window: crate::stimulus::RampWindow::Hanning,
        };
        p.stimulus.level = Level::DbNhl(90.0);
        let comps = model.components(&p, &Subject::default());
        let cm = comps.iter().find(|c| c.label == "CM").unwrap();
        match cm.shape {
            ComponentShape::Microphonic { freq_hz } => assert!((freq_hz - 1000.0).abs() < 1e-9),
            _ => panic!("CM deberia ser microfonico"),
        }
    }
}
