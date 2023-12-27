
import random

combinaciones = [('n_1', 't_1'), ('n_1', 't_2'), ('n_1', 't_3'), ('n_1', 't_4'), ('n_1', 'c_1'),
 ('n_1', 'c_2'), ('n_1', 'c_3'), ('n_1', 'c_4'), ('n_1', 'm_1'), ('n_1', 'm_2'),
 ('n_1', 'm_3'), ('n_1', 'm_4'), ('n_2', 't_1'), ('n_2', 't_2'), ('n_2', 't_3'),
 ('n_2', 't_4'), ('n_2', 'c_1'), ('n_2', 'c_2'), ('n_2', 'c_3'), ('n_2', 'c_4'),
 ('n_2', 'm_1'), ('n_2', 'm_2'), ('n_2', 'm_3'), ('n_2', 'm_4'), ('n_3', 't_1'),
 ('n_3', 't_2'), ('n_3', 't_3'), ('n_3', 't_4'), ('n_3', 'c_1'), ('n_3', 'c_2'),
 ('n_3', 'c_3'), ('n_3', 'c_4'), ('n_3', 'm_1'), ('n_3', 'm_2'), ('n_3', 'm_3'),
 ('n_3', 'm_4'), ('n_4', 't_1'), ('n_4', 't_2'), ('n_4', 't_3'), ('n_4', 't_4'),
 ('n_4', 'c_1'), ('n_4', 'c_2'), ('n_4', 'c_3'), ('n_4', 'c_4'), ('n_4', 'm_1'),
 ('n_4', 'm_2'), ('n_4', 'm_3'), ('n_4', 'm_4'), ('t_1', 'n_1'), ('t_1', 'n_2'),
 ('t_1', 'n_3'), ('t_1', 'n_4'), ('t_1', 'c_1'), ('t_1', 'c_2'), ('t_1', 'c_3'),
 ('t_1', 'c_4'), ('t_1', 'm_1'), ('t_1', 'm_2'), ('t_1', 'm_3'), ('t_1', 'm_4'),
 ('t_2', 'n_1'), ('t_2', 'n_2'), ('t_2', 'n_3'), ('t_2', 'n_4'), ('t_2', 'c_1'),
 ('t_2', 'c_2'), ('t_2', 'c_3'), ('t_2', 'c_4'), ('t_2', 'm_1'), ('t_2', 'm_2'),
 ('t_2', 'm_3'), ('t_2', 'm_4'), ('t_3', 'n_1'), ('t_3', 'n_2'), ('t_3', 'n_3'),
 ('t_3', 'n_4'), ('t_3', 'c_1'), ('t_3', 'c_2'), ('t_3', 'c_3'), ('t_3', 'c_4'),
 ('t_3', 'm_1'), ('t_3', 'm_2'), ('t_3', 'm_3'), ('t_3', 'm_4'), ('t_4', 'n_1'),
 ('t_4', 'n_2'), ('t_4', 'n_3'), ('t_4', 'n_4'), ('t_4', 'c_1'), ('t_4', 'c_2'),
 ('t_4', 'c_3'), ('t_4', 'c_4'), ('t_4', 'm_1'), ('t_4', 'm_2'), ('t_4', 'm_3'),
 ('t_4', 'm_4'), ('c_1', 'n_1'), ('c_1', 'n_2'), ('c_1', 'n_3'), ('c_1', 'n_4'),
 ('c_1', 't_1'), ('c_1', 't_2'), ('c_1', 't_3'), ('c_1', 't_4'), ('c_1', 'm_1'),
 ('c_1', 'm_2'), ('c_1', 'm_3'), ('c_1', 'm_4'), ('c_2', 'n_1'), ('c_2', 'n_2'),
 ('c_2', 'n_3'), ('c_2', 'n_4'), ('c_2', 't_1'), ('c_2', 't_2'), ('c_2', 't_3'),
 ('c_2', 't_4'), ('c_2', 'm_1'), ('c_2', 'm_2'), ('c_2', 'm_3'), ('c_2', 'm_4'),
 ('c_3', 'n_1'), ('c_3', 'n_2'), ('c_3', 'n_3'), ('c_3', 'n_4'), ('c_3', 't_1'),
 ('c_3', 't_2'), ('c_3', 't_3'), ('c_3', 't_4'), ('c_3', 'm_1'), ('c_3', 'm_2'),
 ('c_3', 'm_3'), ('c_3', 'm_4'), ('c_4', 'n_1'), ('c_4', 'n_2'), ('c_4', 'n_3'),
 ('c_4', 'n_4'), ('c_4', 't_1'), ('c_4', 't_2'), ('c_4', 't_3'), ('c_4', 't_4'),
 ('c_4', 'm_1'), ('c_4', 'm_2'), ('c_4', 'm_3'), ('c_4', 'm_4'), ('m_1', 'n_1'),
 ('m_1', 'n_2'), ('m_1', 'n_3'), ('m_1', 'n_4'), ('m_1', 't_1'), ('m_1', 't_2'),
 ('m_1', 't_3'), ('m_1', 't_4'), ('m_1', 'c_1'), ('m_1', 'c_2'), ('m_1', 'c_3'),
 ('m_1', 'c_4'), ('m_2', 'n_1'), ('m_2', 'n_2'), ('m_2', 'n_3'), ('m_2', 'n_4'),
 ('m_2', 't_1'), ('m_2', 't_2'), ('m_2', 't_3'), ('m_2', 't_4'), ('m_2', 'c_1'),
 ('m_2', 'c_2'), ('m_2', 'c_3'), ('m_2', 'c_4'), ('m_3', 'n_1'), ('m_3', 'n_2'),
 ('m_3', 'n_3'), ('m_3', 'n_4'), ('m_3', 't_1'), ('m_3', 't_2'), ('m_3', 't_3'),
 ('m_3', 't_4'), ('m_3', 'c_1'), ('m_3', 'c_2'), ('m_3', 'c_3'), ('m_3', 'c_4'),
 ('m_4', 'n_1'), ('m_4', 'n_2'), ('m_4', 'n_3'), ('m_4', 'n_4'), ('m_4', 't_1'),
 ('m_4', 't_2'), ('m_4', 't_3'), ('m_4', 't_4'), ('m_4', 'c_1'), ('m_4', 'c_2'),
 ('m_4', 'c_3'), ('m_4', 'c_4')]



def elegir_combinacion_especifica():
    """
    Elige una combinación de dos pares de la lista de combinaciones,
    asegurándose de que los pares contengan un 'c', un 't', un 'm' y un 'n'.
    """
    while True:
        # Elegir dos índices aleatorios
        indices = random.sample(range(len(combinaciones)), 2)
        par1 = combinaciones[indices[0]]
        par2 = combinaciones[indices[1]]

        # Extraer elementos individuales de los pares y sus iniciales
        elementos = set(par1 + par2)
        iniciales = {elemento[0] for elemento in elementos}

        # Verificar si todos los elementos son únicos y cumplen con la condición específica
        if len(elementos) == 4 and iniciales == {'c', 't', 'm', 'n'}:
            return indices[0],indices[1]
        

def casos(n, side):
        dict_cases= {"n_1" :{"lat": [1.6, 3.7, 5.6], "amp":[.3, .3], "repro": True, "morfo": [True, True, True], "th":30, "type" : "normal"},
                    "n_2" : {"lat": [1.7,3.8, 5.7], "amp":[.5, .5], "repro": True, "morfo": [True, True, True], "th":20, "type" : "normal"},
        "n_3" : {"lat": [1.8, 3.5, 5.5], "amp":[.2, .4], "repro": True, "morfo": [True, True, True], "th":10, "type" : "normal"},
        "n_4" : {"lat": [1.75, 3.5, 5.5], "amp":[.4, .4], "repro": True, "morfo": [True, True, True], "th":0, "type" : "normal"},

        "t_1" : {"lat": [2.0, 4.1, 6.0], "amp":[.3, .3], "repro": True, "morfo": [True, True, True], "th":60, "type" : "transmission"},
        "t_2" : {"lat": [2.1, 4.3, 6.2], "amp":[.2, .4], "repro": True, "morfo": [True, True, True], "th":50, "type" : "transmission"},
        "t_3" : {"lat": [3.5, 5.2, 7.2], "amp":[.2, .5], "repro": True, "morfo": [True, True, True], "th":50, "type" : "transmission"},
        "t_4" : {"lat": [4.1, 5.1, 6.9], "amp":[.4, .5], "repro": True, "morfo": [True, True, True], "th":40, "type" : "transmission"},

        "c_1" : {"lat": [1.6, 3.7, 5.6], "amp":[.1, .8], "repro": True, "morfo": [True, True, True], "th":70, "type" : "coclear"},
        "c_2" : {"lat": [1.7,3.8, 5.7], "amp":[.2, .6], "repro": True, "morfo": [True, True, True], "th":50, "type" : "coclear"},
        "c_3" : {"lat": [1.8, 3.5, 5.5], "amp":[.2, .5], "repro": True, "morfo": [True, True, True], "th":35, "type" : "coclear"},
        "c_4" : {"lat": [1.75, 3.5, 5.5], "amp":[.3, .6], "repro": True, "morfo": [True, True, True], "th":40, "type" : "coclear"},


        "m_1" : {"lat": [1.6, 4.5, 7], "amp":[.7, .4], "repro": False, "morfo": [True, True, False], "th":40, "type" : "neural"},
        "m_2" : {"lat": [1.7, 5, 7.7], "amp":[.5, .5], "repro": False, "morfo": [True, False, True], "th":60, "type" : "neural"},
        "m_3" : {"lat": [1.8, 4.7, 6.8], "amp":[.8, .6], "repro": False, "morfo": [True, True, False], "th":70, "type" : "neural"},
        "m_4" : {"lat": [1.75, 4.4, 6.8], "amp":[.5, .7], "repro": False, "morfo": [True, False, True], "th":70, "type" : "neural"}}

        name_cases = combinaciones[n]

        return dict_cases[name_cases[side]]

def namecasos(n):
     return combinaciones[n]
