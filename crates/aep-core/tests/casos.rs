//! Tests de criterio del motor por escenario clinico (§12, Capa 1).
//!
//! Una **patologia** son lesiones; las variables del sujeto (edad, estado,
//! atencion) son externas. Aqui se combinan explicitamente para verificar que el
//! motor produce, en el examen apropiado, una respuesta coherente con el
//! diagnostico. Independiente del catalogo que se envia con la app.

use aep_core::{
    assr_audiogram, estimate_audiogram, model_for, Age, ArousalState, Attention, Ear,
    EvokedPotentialEngine, FreqProfile, Lesion, LesionSite, Protocol, Recording, Sex, Subject,
};

fn les(site: LesionSite, sev: f64, prof: FreqProfile) -> Lesion {
    Lesion { site, ear: Ear::Right, severity_db: sev, freq_profile: prof }
}

fn patient(age: f64, state: ArousalState, attention: Attention, lesions: Vec<Lesion>) -> Subject {
    Subject {
        age: Age::Years { value: age },
        sex: Sex::Female,
        temperature_c: 37.0,
        state,
        attention,
        lesions,
    }
}

fn adulto(lesions: Vec<Lesion>) -> Subject {
    patient(30.0, ArousalState::Awake, Attention::Passive, lesions)
}

fn abr(s: &Subject) -> Recording {
    EvokedPotentialEngine::simulate(&Protocol::abr_click(Ear::Right), s)
}

#[test]
fn normal_detecta_i_v_e_intervalo_en_rango() {
    let rec = abr(&adulto(vec![]));
    assert!(rec.peak("I").is_some(), "falta onda I");
    assert!(rec.peak("V").is_some(), "falta onda V");
    let iv = rec.interpeak("I", "V").unwrap();
    assert!((3.3..4.9).contains(&iv), "I-V = {iv} ms");
}

#[test]
fn normal_ratio_v_i_amplitud_comparable() {
    let vi = abr(&adulto(vec![])).v_i_ratio().unwrap();
    assert!(vi >= 0.8, "V/I = {vi}");
}

#[test]
fn neurinoma_alarga_i_v_y_baja_v_sobre_i() {
    let n = abr(&adulto(vec![]));
    let r = abr(&adulto(vec![les(LesionSite::Retrocochlear, 40.0, FreqProfile::Flat)]));
    let iv_n = n.interpeak("I", "V").unwrap();
    let iv_r = r.interpeak("I", "V").unwrap();
    assert!(iv_r > iv_n + 0.3, "I-V normal={iv_n} neurinoma={iv_r}");
    // El retrococlear baja la razon V/I (la V se atenua mas que la I).
    assert!(
        r.v_i_ratio().unwrap() < n.v_i_ratio().unwrap(),
        "V/I deberia bajar: normal={:?} neurinoma={:?}",
        n.v_i_ratio(),
        r.v_i_ratio()
    );
}

#[test]
fn neonatal_intervalo_i_v_mayor_que_adulto() {
    let adulto = abr(&adulto(vec![])).interpeak("I", "V").unwrap();
    let neonato = abr(&patient(0.05, ArousalState::NaturalSleep, Attention::Passive, vec![]))
        .interpeak("I", "V")
        .unwrap();
    assert!(neonato > adulto + 0.2, "adulto={adulto} neonato={neonato}");
}

#[test]
fn neuropatia_no_produce_ondas() {
    let rec = abr(&adulto(vec![les(LesionSite::Neural, 60.0, FreqProfile::Flat)]));
    assert!(rec.detected.is_empty(), "la neuropatia no deberia dar ondas: {:?}", rec.detected);
}

#[test]
fn conductiva_retrasa_la_onda_v() {
    let v_cond = abr(&adulto(vec![les(LesionSite::Conductive, 40.0, FreqProfile::Flat)]))
        .peak("V")
        .unwrap()
        .latency_ms;
    let v_norm = abr(&adulto(vec![])).peak("V").unwrap().latency_ms;
    assert!(v_cond > v_norm, "conductiva V={v_cond} normal V={v_norm}");
}

#[test]
fn varias_patologias_simulan_abr_sin_panico() {
    let casos = [
        adulto(vec![]),
        adulto(vec![les(LesionSite::Conductive, 40.0, FreqProfile::Flat)]),
        adulto(vec![les(LesionSite::Cochlear, 50.0, FreqProfile::HighFrequency)]),
        adulto(vec![les(LesionSite::Retrocochlear, 35.0, FreqProfile::Flat)]),
        adulto(vec![les(LesionSite::Neural, 60.0, FreqProfile::Flat)]),
    ];
    let proto = Protocol::abr_click(Ear::Right);
    for s in &casos {
        let rec = EvokedPotentialEngine::simulate(&proto, s);
        assert_eq!(rec.accepted_sweeps, proto.acquisition.sweeps);
    }
}

#[test]
fn meniere_es_ecochg_con_sp_ap_elevada() {
    // Hidrops = coclear en graves: ECochG con razon SP/AP elevada.
    let subject = adulto(vec![les(LesionSite::Cochlear, 40.0, FreqProfile::LowFrequency)]);
    let p = Protocol::ecochg(Ear::Right);
    let comps = model_for(p.modality).unwrap().components(&p, &subject);
    let sp = comps.iter().find(|c| c.label == "SP").unwrap().amplitude_uv.abs();
    let ap = comps.iter().find(|c| c.label == "AP").unwrap().amplitude_uv.abs();
    assert!(sp / ap > 0.4, "SP/AP = {}", sp / ap);
}

#[test]
fn audiograma_estimado_del_coclear_en_agudos_desciende() {
    let s = adulto(vec![les(LesionSite::Cochlear, 50.0, FreqProfile::HighFrequency)]);
    let audio = estimate_audiogram(Ear::Right, &s, &[500.0, 1000.0, 2000.0, 4000.0]);
    let grave = audio.iter().find(|(f, _)| *f == 500.0).unwrap().1.unwrap();
    let agudo = audio.iter().find(|(f, _)| *f == 4000.0).unwrap().1.unwrap();
    assert!(agudo > grave, "audiograma deberia descender: 500={grave} 4000={agudo}");
}

#[test]
fn mlr_adulto_detecta_pa() {
    let rec = EvokedPotentialEngine::simulate(&Protocol::mlr(Ear::Right), &adulto(vec![]));
    assert!(rec.peak("Pa").is_some(), "MLR adulto deberia detectar Pa");
}

#[test]
fn mlr_pa_menor_en_nino_y_sedado_que_en_adulto() {
    let p = Protocol::mlr(Ear::Right);
    let pa = |s: &Subject| {
        model_for(p.modality)
            .unwrap()
            .components(&p, s)
            .iter()
            .find(|x| x.label == "Pa")
            .unwrap()
            .amplitude_uv
            .abs()
    };
    let adulto_pa = pa(&adulto(vec![]));
    let nino = patient(3.0, ArousalState::Awake, Attention::Passive, vec![]);
    let sedado = patient(40.0, ArousalState::Sedated, Attention::Passive, vec![]);
    assert!(pa(&nino) < adulto_pa, "nino");
    assert!(pa(&sedado) < adulto_pa, "sedado");
}

#[test]
fn alr_despierto_detecta_n1() {
    let rec = EvokedPotentialEngine::simulate(&Protocol::alr(Ear::Right), &adulto(vec![]));
    assert!(rec.peak("N1").is_some(), "ALR despierto deberia detectar N1");
}

#[test]
fn alr_n1_mayor_atendiendo_y_menor_dormido() {
    let p = Protocol::alr(Ear::Right);
    let n1 = |s: &Subject| {
        model_for(p.modality)
            .unwrap()
            .components(&p, s)
            .iter()
            .find(|x| x.label == "N1")
            .unwrap()
            .amplitude_uv
            .abs()
    };
    let pasivo = n1(&adulto(vec![]));
    let atento = patient(30.0, ArousalState::Awake, Attention::Active, vec![]);
    let dormido = patient(30.0, ArousalState::NaturalSleep, Attention::Passive, vec![]);
    assert!(n1(&atento) > pasivo, "atento deberia realzar N1");
    assert!(n1(&dormido) < pasivo, "el sueno deberia atenuar N1");
}

#[test]
fn p300_atento_detecta_p3b_pero_ignorando_no() {
    let p = Protocol::p300(Ear::Right);
    let atento = patient(30.0, ArousalState::Awake, Attention::Active, vec![]);
    let ignorando = patient(30.0, ArousalState::Awake, Attention::Ignoring, vec![]);
    let ra = EvokedPotentialEngine::simulate(&p, &atento);
    assert!(ra.peak("P3b").is_some(), "atento deberia dar P3b");
    assert!(ra.peak("MMN").is_some(), "deberia haber MMN");
    let ri = EvokedPotentialEngine::simulate(&p, &ignorando);
    assert!(ri.peak("P3b").is_none(), "ignorando no deberia dar P3b");
    assert!(ri.peak("MMN").is_some(), "la MMN persiste sin atender");
}

#[test]
fn mmn_basico_detecta_mmn_sin_atender() {
    let ignorando = patient(30.0, ArousalState::Awake, Attention::Ignoring, vec![]);
    let rec = EvokedPotentialEngine::simulate(&Protocol::mmn(Ear::Right), &ignorando);
    assert!(rec.peak("MMN").is_some(), "MMN preatencional");
    assert!(rec.peak("P3b").is_none(), "la modalidad MMN no da P3b");
}

#[test]
fn assr_normal_detecta_respuesta() {
    let r = EvokedPotentialEngine::simulate_assr(&Protocol::assr_default(Ear::Right), &adulto(vec![]));
    assert!(r.detected, "ASSR normal deberia detectar respuesta (F={})", r.f_ratio);
}

// --- Eje neurologico central ---

#[test]
fn conduccion_central_alarga_iii_v_preservando_i_iii() {
    // Desmielinizacion / EM: prolonga la conduccion central (III-V) dejando la
    // porcion periferica (I-III) ~normal.
    let cc = adulto(vec![les(LesionSite::CentralConduction, 45.0, FreqProfile::Flat)]);
    let r = abr(&cc);
    let n = abr(&adulto(vec![]));
    let iii_v = |x: &Recording| x.interpeak("III", "V").unwrap();
    let i_iii = |x: &Recording| x.interpeak("I", "III").unwrap();
    assert!(iii_v(&r) > iii_v(&n) + 0.3, "III-V no se alargo: {} vs {}", iii_v(&r), iii_v(&n));
    assert!((i_iii(&r) - i_iii(&n)).abs() < 0.4, "I-III deberia preservarse: {} vs {}", i_iii(&r), i_iii(&n));
}

#[test]
fn muerte_encefalica_solo_deja_onda_i() {
    // Bloqueo de tronco maximo (severity 100): solo sobrevive la onda I.
    let bd = abr(&adulto(vec![les(LesionSite::Brainstem, 100.0, FreqProfile::Flat)]));
    assert!(bd.peak("I").is_some(), "la onda I (distal) deberia persistir");
    assert!(bd.peak("V").is_none(), "la V no deberia sobrevivir");
    assert!(bd.peak("III").is_none(), "la III no deberia sobrevivir");
}

#[test]
fn lesion_de_tronco_intermedia_abole_v_pero_conserva_i_iii() {
    // Severidad intermedia: cae la V (rostral) antes que la III/I.
    let r = abr(&adulto(vec![les(LesionSite::Brainstem, 55.0, FreqProfile::Flat)]));
    assert!(r.peak("I").is_some(), "I presente");
    assert!(r.peak("III").is_some(), "III presente a severidad intermedia");
    assert!(r.peak("V").is_none(), "V abolida a severidad intermedia");
}

#[test]
fn cortical_atenua_alr_pero_deja_abr_normal() {
    let p = Protocol::alr(Ear::Right);
    let n1 = |s: &Subject| {
        model_for(p.modality)
            .unwrap()
            .components(&p, s)
            .iter()
            .find(|x| x.label == "N1")
            .map(|x| x.amplitude_uv.abs())
            .unwrap_or(0.0)
    };
    let sano = patient(30.0, ArousalState::Awake, Attention::Active, vec![]);
    let tpac = patient(
        30.0,
        ArousalState::Awake,
        Attention::Active,
        vec![les(LesionSite::Cortical, 50.0, FreqProfile::Flat)],
    );
    assert!(n1(&tpac) < n1(&sano), "TPAC deberia atenuar la N1 cortical");
    // El ABR de tronco se mantiene normal.
    let abr_tpac = abr(&tpac);
    assert!(abr_tpac.peak("V").is_some(), "el ABR debe ser normal en TPAC");
    let iv = abr_tpac.interpeak("I", "V").unwrap();
    assert!((3.3..4.9).contains(&iv), "I-V normal en TPAC: {iv}");
}

#[test]
fn cognitivo_retrasa_y_baja_la_p3b() {
    let p = Protocol::p300(Ear::Right);
    let sano = patient(30.0, ArousalState::Awake, Attention::Active, vec![]);
    let demencia = patient(
        30.0,
        ArousalState::Awake,
        Attention::Active,
        vec![les(LesionSite::Cognitive, 50.0, FreqProfile::Flat)],
    );
    let rn = EvokedPotentialEngine::simulate(&p, &sano);
    let rc = EvokedPotentialEngine::simulate(&p, &demencia);
    let pn = rn.peak("P3b").unwrap();
    let pc = rc.peak("P3b").unwrap();
    assert!(pc.latency_ms > pn.latency_ms + 10.0, "P3b deberia retrasarse");
    assert!(pc.amplitude_uv.abs() < pn.amplitude_uv.abs(), "P3b deberia bajar");
}

#[test]
fn assr_audiograma_objetivo_desciende_en_perdida_agudos() {
    let s = adulto(vec![les(LesionSite::Cochlear, 50.0, FreqProfile::HighFrequency)]);
    let audio = assr_audiogram(Ear::Right, &s, &[500.0, 4000.0], 80.0);
    let grave = audio.iter().find(|(f, _)| *f == 500.0).unwrap().1.unwrap();
    let agudo = audio.iter().find(|(f, _)| *f == 4000.0).unwrap().1.unwrap();
    assert!(agudo > grave + 20.0, "500={grave} 4000={agudo}");
}
