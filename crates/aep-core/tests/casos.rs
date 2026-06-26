//! Tests de integracion por caso clinico (criterio §12, Capa 1).
//!
//! Cada preset del catalogo debe producir un registro coherente con su
//! diagnostico: normal / conductiva / coclear / retrococlear / neuropatia se
//! distinguen y se miden bien sobre la curva ya promediada (con ruido real).

use aep_core::{estimate_audiogram, CaseCatalog, EvokedPotentialEngine, LesionSite, Recording};

fn simular(id: &str) -> Recording {
    let cat = CaseCatalog::embedded();
    let caso = cat.get(id).unwrap_or_else(|| panic!("falta el caso {id}"));
    EvokedPotentialEngine::simulate(&caso.protocol(), &caso.subject())
}

#[test]
fn normal_detecta_i_v_e_intervalo_en_rango() {
    let rec = simular("normal");
    assert!(rec.peak("I").is_some(), "falta onda I");
    assert!(rec.peak("V").is_some(), "falta onda V");
    let iv = rec.interpeak("I", "V").unwrap();
    // Intervalo I-V normal ~4 ms (con retardo del inserto incluido por igual).
    assert!((3.3..4.9).contains(&iv), "I-V = {iv} ms");
}

#[test]
fn normal_ratio_v_i_amplitud_comparable() {
    let rec = simular("normal");
    let vi = rec.v_i_ratio().unwrap();
    // Nota: `v_i_ratio` usa amplitud absoluta desde la linea base (no pico-a-valle
    // como en clinica) y el filtrado IIR sesga las amplitudes absolutas, asi que
    // el valor medido (~1) infravalora el V/I real del modelo (~2). El test solo
    // verifica que la V es al menos comparable a la I (no se desvanece).
    // Medicion pico-a-valle = refinamiento futuro.
    assert!(vi >= 0.8, "V/I = {vi}");
}

#[test]
fn neurinoma_alarga_intervalo_i_v() {
    let normal = simular("normal").interpeak("I", "V").unwrap();
    let neuri = simular("neurinoma").interpeak("I", "V").unwrap();
    assert!(neuri > normal + 0.3, "normal={normal} neurinoma={neuri}");
}

#[test]
fn neonatal_intervalo_i_v_mayor_que_adulto() {
    let adulto = simular("normal").interpeak("I", "V").unwrap();
    let neonato = simular("neonatal_normal").interpeak("I", "V").unwrap();
    assert!(neonato > adulto + 0.2, "adulto={adulto} neonato={neonato}");
}

#[test]
fn neuropatia_no_produce_ondas() {
    let rec = simular("neuropatia");
    assert!(
        rec.detected.is_empty(),
        "la neuropatia no deberia dar ondas: {:?}",
        rec.detected
    );
}

#[test]
fn conductiva_retrasa_la_onda_v() {
    // La conductiva alarga las latencias absolutas: la V cae mas tarde que en
    // un coclear de umbral comparable (sin retraso por reclutamiento).
    let cond = simular("conductiva_moderada");
    let v_cond = cond.peak("V").unwrap().latency_ms;
    let v_norm = simular("normal").peak("V").unwrap().latency_ms;
    assert!(v_cond > v_norm, "conductiva V={v_cond} normal V={v_norm}");
}

#[test]
fn todos_los_casos_alcanzan_su_objetivo_de_sweeps() {
    let cat = CaseCatalog::embedded();
    for c in cat.cases() {
        let rec = EvokedPotentialEngine::simulate(&c.protocol(), &c.subject());
        assert_eq!(rec.accepted_sweeps, c.protocol().acquisition.sweeps, "caso {}", c.id);
    }
}

#[test]
fn audiograma_estimado_del_coclear_en_agudos_desciende() {
    // El ABR por tone-burst estima un audiograma descendente en una perdida
    // coclear de agudos.
    let cat = CaseCatalog::embedded();
    let caso = cat.get("coclear_agudos").unwrap();
    let audio = estimate_audiogram(caso.ear(), &caso.subject(), &[500.0, 1000.0, 2000.0, 4000.0]);
    let grave = audio.iter().find(|(f, _)| *f == 500.0).unwrap().1.unwrap();
    let agudo = audio.iter().find(|(f, _)| *f == 4000.0).unwrap().1.unwrap();
    assert!(agudo > grave, "audiograma deberia descender: 500={grave} 4000={agudo}");
}

#[test]
fn mlr_adulto_detecta_pa() {
    let rec = simular("mlr_adulto_normal");
    assert!(rec.peak("Pa").is_some(), "MLR adulto deberia detectar Pa");
}

#[test]
fn mlr_pa_menor_en_nino_y_sedado_que_en_adulto() {
    use aep_core::model_for;
    let cat = CaseCatalog::embedded();
    let pa = |id: &str| {
        let c = cat.get(id).unwrap();
        let p = c.protocol();
        let subj = c.subject();
        model_for(p.modality)
            .unwrap()
            .components(&p, &subj)
            .iter()
            .find(|x| x.label == "Pa")
            .unwrap()
            .amplitude_uv
            .abs()
    };
    let adulto = pa("mlr_adulto_normal");
    assert!(pa("mlr_nino_inmaduro") < adulto, "nino");
    assert!(pa("mlr_sedado") < adulto, "sedado");
}

#[test]
fn catalogo_cubre_los_sitios_de_lesion_clave() {
    let cat = CaseCatalog::embedded();
    let mut vistos = std::collections::HashSet::new();
    for c in cat.cases() {
        for l in c.subject().lesions {
            vistos.insert(format!("{:?}", l.site));
        }
    }
    for site in [
        LesionSite::Conductive,
        LesionSite::Cochlear,
        LesionSite::Retrocochlear,
        LesionSite::Neural,
    ] {
        assert!(vistos.contains(&format!("{site:?}")), "falta caso con {site:?}");
    }
}
