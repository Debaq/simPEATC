"""
Definición de casos clínicos para ABR
Versión 2.0 - Sistema de desviaciones y FSP progresivo
"""

import random

# Lista de casos disponibles (solo ID)
casos_disponibles = ['normal_cl']

# Combinaciones para pruebas bilaterales (por ahora solo normal bilateral)
combinaciones = [('normal_cl', 'normal_cl')]


def elegir_combinacion_especifica():
    """
    Elige una combinación de casos para OD y OI
    Por ahora retorna siempre el caso normal bilateral
    """
    return 0, 0


def casos(n, side):
    """
    Retorna la configuración de un caso clínico
    
    Args:
        n: índice de la combinación
        side: 0 para OD, 1 para OI
        
    Returns:
        dict con configuración del caso (formato híbrido)
    """
    
    # Diccionario de casos
    dict_cases = {
        "normal_cl": {
            # ===== CAMPOS VIEJOS (compatibilidad) =====
            "lat": [1.6, 3.7, 5.6],      # Latencias I, III, V (se ignorarán)
            "amp": [0.3, 0.3],            # Amplitudes I, V (se ignorarán)
            "repro": True,                # Reproductibilidad
            "morfo": [True, True, True],  # Ondas I, III, V visibles
            "th": 20,                     # Umbral (se usará nuevo)
            "type": "normal",             # Tipo de patología
            
            # ===== CAMPOS NUEVOS =====
            "caso_id": "normal_cl",
            "nombre": "Audición Normal - Protocolo Chileno",
            "patologia": "normal",
            
            # Desviaciones respecto a valores normativos (por estímulo)
            "desviaciones": {
                "click": {
                    "onda_I": {"lat": 0.0, "amp": 0.0},
                    "onda_III": {"lat": 0.0, "amp": 0.0},
                    "onda_V": {"lat": 0.0, "amp": 0.0}
                },
                "chirp": {
                    "onda_I": {"lat": 0.0, "amp": 0.0},
                    "onda_III": {"lat": 0.0, "amp": 0.0},
                    "onda_V": {"lat": 0.0, "amp": 0.0}
                },
                "tone_burst_500": {
                    "onda_V": {"lat": 0.0, "amp": 0.0}
                },
                "tone_burst_1000": {
                    "onda_V": {"lat": 0.0, "amp": 0.0}
                },
                "tone_burst_2000": {
                    "onda_V": {"lat": 0.0, "amp": 0.0}
                },
                "tone_burst_4000": {
                    "onda_V": {"lat": 0.0, "amp": 0.0}
                }
            },
            
            # Umbral auditivo
            "umbral": 20,
            
            # Puntos de FSP para interpolación
            "fsp_puntos": {
                "800": 0.8,      # FSP esperado a 800 promediaciones
                "2000": 2.8,     # FSP esperado a 2000 promediaciones
                "objetivo": 3.0  # FSP objetivo (criterio de parada)
            },
            
            # Morfología de ondas
            "morfologia": {
                "onda_I": True,
                "onda_III": True,
                "onda_V": True
            },
            
            # Reproductibilidad
            "reproducibilidad": True
        }
    }
    
    # Obtener el caso de la combinación
    name_cases = combinaciones[n]
    case_id = name_cases[side]
    
    return dict_cases[case_id]


def namecasos(n):
    """
    Retorna el nombre de la combinación de casos
    """
    return combinaciones[n]