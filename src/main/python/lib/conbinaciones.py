"""
Definición de casos clínicos para ABR
Versión 3.0 - 30 casos con sistema de desviaciones y FSP progresivo
Compatible con ABR_generator_v2.py
"""

import random

# ============================================================================
# DICCIONARIO DE CASOS (30 CASOS)
# ============================================================================

DICT_CASES = {
    # ========== NORMALES (6 casos) ==========
    "normal_1": {
        "caso_id": "normal_1",
        "nombre": "Audición Normal - Umbral 10dB",
        "type": "normal",
        "patologia": "normal",
        "repro": True,
        "morfo": [True, True, True],
        "th": 10,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.0, "amp": 0.0},
                "onda_III": {"lat": 0.0, "amp": 0.0},
                "onda_V": {"lat": 0.0, "amp": 0.0}
            }
        },
        "umbral": 10,
        "fsp_puntos": {"800": 2.5, "2000": 3.0, "objetivo": 3.0}
    },
    
    "normal_2": {
        "caso_id": "normal_2",
        "nombre": "Audición Normal - Umbral 15dB",
        "type": "normal",
        "patologia": "normal",
        "repro": True,
        "morfo": [True, True, True],
        "th": 15,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.0, "amp": 0.02},
                "onda_III": {"lat": 0.0, "amp": 0.0},
                "onda_V": {"lat": 0.0, "amp": 0.03}
            }
        },
        "umbral": 15,
        "fsp_puntos": {"800": 2.4, "2000": 2.9, "objetivo": 3.0}
    },
    
    "normal_3": {
        "caso_id": "normal_3",
        "nombre": "Audición Normal - Umbral 20dB",
        "type": "normal",
        "patologia": "normal",
        "repro": True,
        "morfo": [True, True, True],
        "th": 20,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": -0.02, "amp": -0.01},
                "onda_III": {"lat": 0.0, "amp": 0.0},
                "onda_V": {"lat": 0.0, "amp": 0.0}
            }
        },
        "umbral": 20,
        "fsp_puntos": {"800": 2.3, "2000": 2.8, "objetivo": 3.0}
    },
    
    "normal_4": {
        "caso_id": "normal_4",
        "nombre": "Audición Normal - Latencias Cortas",
        "type": "normal",
        "patologia": "normal",
        "repro": True,
        "morfo": [True, True, True],
        "th": 15,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": -0.10, "amp": 0.05},
                "onda_III": {"lat": -0.12, "amp": 0.03},
                "onda_V": {"lat": -0.15, "amp": 0.05}
            }
        },
        "umbral": 15,
        "fsp_puntos": {"800": 2.5, "2000": 3.0, "objetivo": 3.0}
    },
    
    "normal_5": {
        "caso_id": "normal_5",
        "nombre": "Audición Normal - Latencias Largas",
        "type": "normal",
        "patologia": "normal",
        "repro": True,
        "morfo": [True, True, True],
        "th": 20,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.10, "amp": -0.03},
                "onda_III": {"lat": 0.12, "amp": 0.0},
                "onda_V": {"lat": 0.15, "amp": 0.0}
            }
        },
        "umbral": 20,
        "fsp_puntos": {"800": 2.2, "2000": 2.7, "objetivo": 3.0}
    },
    
    "normal_6": {
        "caso_id": "normal_6",
        "nombre": "Audición Normal - Amplitudes Altas",
        "type": "normal",
        "patologia": "normal",
        "repro": True,
        "morfo": [True, True, True],
        "th": 10,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.0, "amp": 0.08},
                "onda_III": {"lat": 0.0, "amp": 0.10},
                "onda_V": {"lat": 0.0, "amp": 0.15}
            }
        },
        "umbral": 10,
        "fsp_puntos": {"800": 2.6, "2000": 3.1, "objetivo": 3.2}
    },

    # ========== COCLEARES (9 casos) ==========
    "coclear_1": {
        "caso_id": "coclear_1",
        "nombre": "Hipoacusia Coclear Leve - 40dB",
        "type": "coclear",
        "patologia": "cochlear",
        "repro": True,
        "morfo": [False, True, True],
        "th": 40,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.05, "amp": -0.15},
                "onda_III": {"lat": 0.05, "amp": 0.0},
                "onda_V": {"lat": 0.08, "amp": 0.05}
            }
        },
        "umbral": 40,
        "fsp_puntos": {"800": 2.1, "2000": 2.6, "objetivo": 2.8}
    },
    
    "coclear_2": {
        "caso_id": "coclear_2",
        "nombre": "Hipoacusia Coclear Moderada - 50dB",
        "type": "coclear",
        "patologia": "cochlear",
        "repro": True,
        "morfo": [False, True, True],
        "th": 50,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.08, "amp": -0.18},
                "onda_III": {"lat": 0.10, "amp": 0.0},
                "onda_V": {"lat": 0.15, "amp": 0.08}
            }
        },
        "umbral": 50,
        "fsp_puntos": {"800": 2.0, "2000": 2.5, "objetivo": 2.7}
    },
    
    "coclear_3": {
        "caso_id": "coclear_3",
        "nombre": "Hipoacusia Coclear Moderada - 55dB",
        "type": "coclear",
        "patologia": "cochlear",
        "repro": True,
        "morfo": [False, True, True],
        "th": 55,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.10, "amp": -0.19},
                "onda_III": {"lat": 0.12, "amp": -0.02},
                "onda_V": {"lat": 0.18, "amp": 0.10}
            }
        },
        "umbral": 55,
        "fsp_puntos": {"800": 1.9, "2000": 2.4, "objetivo": 2.6}
    },
    
    "coclear_4": {
        "caso_id": "coclear_4",
        "nombre": "Hipoacusia Coclear Moderada-Severa - 60dB",
        "type": "coclear",
        "patologia": "cochlear",
        "repro": True,
        "morfo": [False, True, True],
        "th": 60,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.13, "amp": -0.20},
                "onda_III": {"lat": 0.15, "amp": -0.03},
                "onda_V": {"lat": 0.22, "amp": 0.12}
            }
        },
        "umbral": 60,
        "fsp_puntos": {"800": 1.8, "2000": 2.3, "objetivo": 2.5}
    },
    
    "coclear_5": {
        "caso_id": "coclear_5",
        "nombre": "Hipoacusia Coclear Severa - 70dB",
        "type": "coclear",
        "patologia": "cochlear",
        "repro": True,
        "morfo": [False, True, True],
        "th": 70,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.16, "amp": -0.20},
                "onda_III": {"lat": 0.19, "amp": -0.05},
                "onda_V": {"lat": 0.30, "amp": 0.15}
            }
        },
        "umbral": 70,
        "fsp_puntos": {"800": 1.7, "2000": 2.2, "objetivo": 2.4}
    },
    
    "coclear_6": {
        "caso_id": "coclear_6",
        "nombre": "Hipoacusia Coclear Severa - 75dB",
        "type": "coclear",
        "patologia": "cochlear",
        "repro": True,
        "morfo": [False, False, True],
        "th": 75,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.18, "amp": -0.20},
                "onda_III": {"lat": 0.22, "amp": -0.08},
                "onda_V": {"lat": 0.35, "amp": 0.18}
            }
        },
        "umbral": 75,
        "fsp_puntos": {"800": 1.6, "2000": 2.1, "objetivo": 2.3}
    },
    
    "coclear_7": {
        "caso_id": "coclear_7",
        "nombre": "Hipoacusia Coclear Profunda - 80dB",
        "type": "coclear",
        "patologia": "cochlear",
        "repro": True,
        "morfo": [False, False, True],
        "th": 80,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.20, "amp": -0.21},
                "onda_III": {"lat": 0.25, "amp": -0.10},
                "onda_V": {"lat": 0.40, "amp": 0.20}
            }
        },
        "umbral": 80,
        "fsp_puntos": {"800": 1.5, "2000": 2.0, "objetivo": 2.2}
    },
    
    "coclear_8": {
        "caso_id": "coclear_8",
        "nombre": "Hipoacusia Coclear con Reclutamiento",
        "type": "coclear",
        "patologia": "cochlear",
        "repro": True,
        "morfo": [False, True, True],
        "th": 55,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.12, "amp": -0.19},
                "onda_III": {"lat": 0.08, "amp": 0.02},
                "onda_V": {"lat": 0.10, "amp": 0.18}
            }
        },
        "umbral": 55,
        "fsp_puntos": {"800": 2.0, "2000": 2.5, "objetivo": 2.7}
    },
    
    "coclear_9": {
        "caso_id": "coclear_9",
        "nombre": "Hipoacusia Coclear Bilateral Asimétrica",
        "type": "coclear",
        "patologia": "cochlear",
        "repro": True,
        "morfo": [False, True, True],
        "th": 65,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.15, "amp": -0.20},
                "onda_III": {"lat": 0.18, "amp": -0.04},
                "onda_V": {"lat": 0.28, "amp": 0.14}
            }
        },
        "umbral": 65,
        "fsp_puntos": {"800": 1.7, "2000": 2.2, "objetivo": 2.4}
    },

    # ========== CONDUCTIVOS (6 casos) ==========
    "conductivo_1": {
        "caso_id": "conductivo_1",
        "nombre": "Hipoacusia Conductiva Leve - 30dB",
        "type": "transmission",
        "patologia": "conductive",
        "repro": True,
        "morfo": [True, True, True],
        "th": 30,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.20, "amp": -0.05},
                "onda_III": {"lat": 0.20, "amp": -0.05},
                "onda_V": {"lat": 0.20, "amp": -0.05}
            }
        },
        "umbral": 30,
        "fsp_puntos": {"800": 2.3, "2000": 2.8, "objetivo": 3.0}
    },
    
    "conductivo_2": {
        "caso_id": "conductivo_2",
        "nombre": "Hipoacusia Conductiva Moderada - 40dB",
        "type": "transmission",
        "patologia": "conductive",
        "repro": True,
        "morfo": [True, True, True],
        "th": 40,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.30, "amp": -0.08},
                "onda_III": {"lat": 0.30, "amp": -0.08},
                "onda_V": {"lat": 0.30, "amp": -0.08}
            }
        },
        "umbral": 40,
        "fsp_puntos": {"800": 2.2, "2000": 2.7, "objetivo": 2.9}
    },
    
    "conductivo_3": {
        "caso_id": "conductivo_3",
        "nombre": "Hipoacusia Conductiva Moderada - 45dB",
        "type": "transmission",
        "patologia": "conductive",
        "repro": True,
        "morfo": [True, True, True],
        "th": 45,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.35, "amp": -0.10},
                "onda_III": {"lat": 0.35, "amp": -0.10},
                "onda_V": {"lat": 0.35, "amp": -0.10}
            }
        },
        "umbral": 45,
        "fsp_puntos": {"800": 2.1, "2000": 2.6, "objetivo": 2.8}
    },
    
    "conductivo_4": {
        "caso_id": "conductivo_4",
        "nombre": "Hipoacusia Conductiva Moderada-Severa - 50dB",
        "type": "transmission",
        "patologia": "conductive",
        "repro": True,
        "morfo": [True, True, True],
        "th": 50,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.40, "amp": -0.12},
                "onda_III": {"lat": 0.40, "amp": -0.12},
                "onda_V": {"lat": 0.40, "amp": -0.12}
            }
        },
        "umbral": 50,
        "fsp_puntos": {"800": 2.0, "2000": 2.5, "objetivo": 2.7}
    },
    
    "conductivo_5": {
        "caso_id": "conductivo_5",
        "nombre": "Hipoacusia Conductiva Severa - 55dB",
        "type": "transmission",
        "patologia": "conductive",
        "repro": True,
        "morfo": [True, True, True],
        "th": 55,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.45, "amp": -0.14},
                "onda_III": {"lat": 0.45, "amp": -0.14},
                "onda_V": {"lat": 0.45, "amp": -0.14}
            }
        },
        "umbral": 55,
        "fsp_puntos": {"800": 1.9, "2000": 2.4, "objetivo": 2.6}
    },
    
    "conductivo_6": {
        "caso_id": "conductivo_6",
        "nombre": "Hipoacusia Conductiva Máxima - 60dB",
        "type": "transmission",
        "patologia": "conductive",
        "repro": True,
        "morfo": [True, True, True],
        "th": 60,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.50, "amp": -0.15},
                "onda_III": {"lat": 0.50, "amp": -0.15},
                "onda_V": {"lat": 0.50, "amp": -0.15}
            }
        },
        "umbral": 60,
        "fsp_puntos": {"800": 1.8, "2000": 2.3, "objetivo": 2.5}
    },

    # ========== NEURALES (9 casos) ==========
    "neural_1": {
        "caso_id": "neural_1",
        "nombre": "Patología Neural Leve - I-III Prolongado",
        "type": "neural",
        "patologia": "neural",
        "repro": False,
        "morfo": [True, True, True],
        "th": 40,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.0, "amp": 0.0},
                "onda_III": {"lat": 0.30, "amp": -0.05},
                "onda_V": {"lat": 0.50, "amp": -0.08}
            }
        },
        "umbral": 40,
        "fsp_puntos": {"800": 1.8, "2000": 2.3, "objetivo": 2.5}
    },
    
    "neural_2": {
        "caso_id": "neural_2",
        "nombre": "Patología Neural Moderada - III-V Prolongado",
        "type": "neural",
        "patologia": "neural",
        "repro": False,
        "morfo": [True, False, True],
        "th": 50,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.0, "amp": -0.02},
                "onda_III": {"lat": 0.20, "amp": -0.10},
                "onda_V": {"lat": 0.60, "amp": -0.12}
            }
        },
        "umbral": 50,
        "fsp_puntos": {"800": 1.6, "2000": 2.1, "objetivo": 2.3}
    },
    
    "neural_3": {
        "caso_id": "neural_3",
        "nombre": "Patología Neural Severa - I-V Prolongado",
        "type": "neural",
        "patologia": "neural",
        "repro": False,
        "morfo": [True, False, True],
        "th": 60,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.0, "amp": -0.03},
                "onda_III": {"lat": 0.40, "amp": -0.15},
                "onda_V": {"lat": 0.80, "amp": -0.15}
            }
        },
        "umbral": 60,
        "fsp_puntos": {"800": 1.5, "2000": 2.0, "objetivo": 2.2}
    },
    
    "neural_4": {
        "caso_id": "neural_4",
        "nombre": "Schwannoma Vestibular Pequeño",
        "type": "neural",
        "patologia": "neural",
        "repro": False,
        "morfo": [True, True, True],
        "th": 45,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.0, "amp": 0.0},
                "onda_III": {"lat": 0.25, "amp": -0.08},
                "onda_V": {"lat": 0.55, "amp": -0.10}
            }
        },
        "umbral": 45,
        "fsp_puntos": {"800": 1.7, "2000": 2.2, "objetivo": 2.4}
    },
    
    "neural_5": {
        "caso_id": "neural_5",
        "nombre": "Schwannoma Vestibular Mediano",
        "type": "neural",
        "patologia": "neural",
        "repro": False,
        "morfo": [True, False, True],
        "th": 55,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.0, "amp": -0.02},
                "onda_III": {"lat": 0.35, "amp": -0.12},
                "onda_V": {"lat": 0.70, "amp": -0.14}
            }
        },
        "umbral": 55,
        "fsp_puntos": {"800": 1.5, "2000": 2.0, "objetivo": 2.2}
    },
    
    "neural_6": {
        "caso_id": "neural_6",
        "nombre": "Schwannoma Vestibular Grande",
        "type": "neural",
        "patologia": "neural",
        "repro": False,
        "morfo": [False, False, True],
        "th": 65,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.0, "amp": -0.05},
                "onda_III": {"lat": 0.50, "amp": -0.18},
                "onda_V": {"lat": 0.90, "amp": -0.20}
            }
        },
        "umbral": 65,
        "fsp_puntos": {"800": 1.3, "2000": 1.8, "objetivo": 2.0}
    },
    
    "neural_7": {
        "caso_id": "neural_7",
        "nombre": "Neuropatía Auditiva",
        "type": "neural",
        "patologia": "neural",
        "repro": False,
        "morfo": [False, False, True],
        "th": 50,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.0, "amp": -0.20},
                "onda_III": {"lat": 0.30, "amp": -0.20},
                "onda_V": {"lat": 0.50, "amp": -0.15}
            }
        },
        "umbral": 50,
        "fsp_puntos": {"800": 1.4, "2000": 1.9, "objetivo": 2.1}
    },
    
    "neural_8": {
        "caso_id": "neural_8",
        "nombre": "Esclerosis Múltiple - Afectación Tronco",
        "type": "neural",
        "patologia": "neural",
        "repro": False,
        "morfo": [True, False, True],
        "th": 40,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.0, "amp": 0.0},
                "onda_III": {"lat": 0.45, "amp": -0.15},
                "onda_V": {"lat": 0.75, "amp": -0.12}
            }
        },
        "umbral": 40,
        "fsp_puntos": {"800": 1.6, "2000": 2.1, "objetivo": 2.3}
    },
    
    "neural_9": {
        "caso_id": "neural_9",
        "nombre": "Patología Tronco Cerebral Difusa",
        "type": "neural",
        "patologia": "neural",
        "repro": False,
        "morfo": [False, False, True],
        "th": 70,
        "desviaciones": {
            "click": {
                "onda_I": {"lat": 0.0, "amp": -0.10},
                "onda_III": {"lat": 0.60, "amp": -0.20},
                "onda_V": {"lat": 1.00, "amp": -0.25}
            }
        },
        "umbral": 70,
        "fsp_puntos": {"800": 1.2, "2000": 1.7, "objetivo": 1.9}
    },
}

# ============================================================================
# COMBINACIONES BILATERALES (30 combinaciones)
# ============================================================================

# Lista de casos disponibles (IDs)
casos_disponibles = list(DICT_CASES.keys())

# Combinaciones para pruebas bilaterales (OD, OI)
combinaciones = [
    # Normales bilaterales
    ('normal_1', 'normal_1'),
    ('normal_2', 'normal_2'),
    ('normal_3', 'normal_3'),
    ('normal_4', 'normal_4'),
    ('normal_5', 'normal_5'),
    ('normal_6', 'normal_6'),
    
    # Cocleares bilaterales
    ('coclear_1', 'coclear_1'),
    ('coclear_2', 'coclear_2'),
    ('coclear_3', 'coclear_3'),
    ('coclear_4', 'coclear_4'),
    ('coclear_5', 'coclear_5'),
    ('coclear_6', 'coclear_6'),
    
    # Conductivos bilaterales
    ('conductivo_1', 'conductivo_1'),
    ('conductivo_2', 'conductivo_2'),
    ('conductivo_3', 'conductivo_3'),
    
    # Neurales unilaterales (más realista)
    ('normal_3', 'neural_1'),      # Neural OI
    ('neural_2', 'normal_3'),      # Neural OD
    ('normal_2', 'neural_4'),      # Schwannoma OI
    ('neural_5', 'normal_2'),      # Schwannoma OD
    ('normal_1', 'neural_7'),      # Neuropatía OI
    
    # Mixtos (coclear + conductivo)
    ('coclear_2', 'conductivo_2'),
    ('conductivo_3', 'coclear_3'),
    
    # Asimetrías
    ('coclear_1', 'coclear_4'),    # Coclear asimétrico
    ('normal_3', 'coclear_2'),     # Normal vs Coclear
    ('coclear_7', 'normal_1'),     # Coclear severo unilateral
    
    # Casos complejos
    ('neural_3', 'coclear_5'),
    ('conductivo_4', 'neural_6'),
    ('coclear_8', 'coclear_9'),
    ('neural_8', 'neural_9'),

    # Casos OSCE Estación 4 (agregados para evaluación)
    ('normal_1', 'conductivo_1'),   # Estación 4 - Caso 1: OD Normal, OI Conductivo
    ('coclear_2', 'normal_2'),      # Estación 4 - Caso 2: OD Coclear, OI Normal
    ('neural_4', 'neural_5'),       # Estación 4 - Caso 3: OD Schwannoma pequeño, OI Schwannoma mediano
]


# ============================================================================
# FUNCIONES DE ACCESO
# ============================================================================

def elegir_combinacion_especifica():
    """
    Elige una combinación aleatoria de casos para OD y OI
    Retorna índice de la combinación
    """
    idx = random.randint(0, len(combinaciones) - 1)
    return idx, idx


def casos(n, side):
    """
    Retorna la configuración de un caso clínico
    
    Args:
        n: índice de la combinación
        side: 0 para OD, 1 para OI
        
    Returns:
        dict con configuración del caso (formato híbrido compatible)
    """
    if n < 0 or n >= len(combinaciones):
        n = 0
    
    # Obtener el caso de la combinación
    name_cases = combinaciones[n]
    case_id = name_cases[side]
    
    return DICT_CASES[case_id]


def namecasos(n):
    """
    Retorna el nombre de la combinación de casos
    
    Args:
        n: índice de la combinación
        
    Returns:
        tuple (nombre_OD, nombre_OI)
    """
    if n < 0 or n >= len(combinaciones):
        n = 0
    
    od_id, oi_id = combinaciones[n]
    return (DICT_CASES[od_id]['nombre'], DICT_CASES[oi_id]['nombre'])


def get_caso_by_id(caso_id):
    """
    Obtiene un caso por su ID
    
    Args:
        caso_id: ID del caso (string)
        
    Returns:
        dict con configuración del caso o None
    """
    return DICT_CASES.get(caso_id, None)


def listar_casos_por_patologia(patologia):
    """
    Lista todos los casos de una patología específica
    
    Args:
        patologia: 'normal', 'cochlear', 'conductive', 'neural'
        
    Returns:
        list de IDs de casos
    """
    return [caso_id for caso_id, caso in DICT_CASES.items() 
            if caso['patologia'] == patologia]


# ============================================================================
# INFO Y ESTADÍSTICAS
# ============================================================================

def info_casos():
    """Imprime información sobre los casos disponibles"""
    print(f"Total de casos: {len(DICT_CASES)}")
    print(f"Total de combinaciones: {len(combinaciones)}")
    print("\nCasos por patología:")
    for patologia in ['normal', 'cochlear', 'conductive', 'neural']:
        casos_patologia = listar_casos_por_patologia(patologia)
        print(f"  {patologia}: {len(casos_patologia)}")
    print(f"\nCasos disponibles: {casos_disponibles[:5]}... (y {len(casos_disponibles)-5} más)")


if __name__ == "__main__":
    # Test rápido
    info_casos()
    print("\n--- Test de 5 combinaciones aleatorias ---")
    for i in range(5):
        idx, _ = elegir_combinacion_especifica()
        od_name, oi_name = namecasos(idx)
        print(f"Combinación {idx}:")
        print(f"  OD: {od_name}")
        print(f"  OI: {oi_name}")