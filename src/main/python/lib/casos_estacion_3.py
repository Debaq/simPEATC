"""
Definición de casos de la Estación 3 del OSCE - CONFIGURACIÓN DEL EQUIPO
Cada caso tiene parámetros correctos predefinidos según el contexto clínico
Versión 1.0
"""

# ============================================================================
# CASOS ESTACIÓN 3: CONFIGURACIÓN DEL EQUIPO
# ============================================================================

CASOS_ESTACION_3 = {
    1: {
        "nombre": "Adulto - Screening Auditivo",
        "descripcion": "Evaluación estándar de adulto para screening auditivo",
        "instrucciones": "Paciente adulto de 35 años, derivado para screening auditivo. Configure los parámetros apropiados.",
        "parametros_correctos": {
            # Parámetros básicos
            "stim": "Click",
            "pol": "Alternante",  # Mejor para adultos (reduce artefacto)
            "int": 80,  # Intensidad inicial estándar
            "rate": 21.1,  # Rate estándar para adultos
            "filter_down": "100",  # Filtro paso alto
            "filter_passhigh": "3000",  # Filtro paso bajo
            "average": 2000,  # Promediaciones estándar
            "side": "OD",  # Iniciar con oído derecho
            "atten": False,

            # Parámetros avanzados
            "transductor": "Fono inserción",
            "ventana": 12,  # 12 ms para adultos
            "fsp": "Detección 99% y FSP de 3.1",
            "ruido_residual": "40nV",
            "electrodo_vertex": "Cz",
            "electrodo_derecho": "A1",
            "electrodo_izquierdo": "A2",
            "electrodo_tierra": "Fpz"
        },
        "parametros_aceptables": {
            # Alternativas aceptables (no óptimas pero no erróneas)
            "pol": ["Alternante", "Rarefacción"],  # Ambas son válidas
            "rate": [21.1, 19.1],  # Variantes cercanas aceptables
            "average": [2000, 1500, 1024],  # Rangos aceptables
            "ventana": [12, 10, 15],  # Ventanas aceptables
            "electrodo_tierra": ["Fpz", "Cz"]  # Ambos son válidos
        }
    },

    2: {
        "nombre": "Neonato de Alto Riesgo",
        "descripcion": "Evaluación de neonato prematuro con factores de riesgo auditivo",
        "instrucciones": "Neonato de 2 meses (edad corregida), prematuro, con antecedentes de UCIN. Configure los parámetros apropiados para screening neonatal.",
        "parametros_correctos": {
            # Parámetros básicos
            "stim": "Click",
            "pol": "Alternante",  # Esencial para neonatos (reduce artefacto eléctrico)
            "int": 80,  # Intensidad inicial (puede ser mayor en neonatos)
            "rate": 11.1,  # Rate MÁS LENTO para neonatos (crítico)
            "filter_down": "30",  # Filtro MÁS BAJO para neonatos (crítico)
            "filter_passhigh": "1500",  # Filtro diferente para neonatos (crítico)
            "average": 4000,  # MÁS promediaciones debido a ruido fisiológico
            "side": "OD",
            "atten": False,

            # Parámetros avanzados
            "transductor": "Fono inserción",
            "ventana": 15,  # VENTANA MÁS LARGA para latencias prolongadas (crítico)
            "fsp": "Detección 99% y FSP de 3.1",
            "ruido_residual": "40nV",
            "electrodo_vertex": "Cz",
            "electrodo_derecho": "A1",
            "electrodo_izquierdo": "A2",
            "electrodo_tierra": "Fpz"
        },
        "parametros_aceptables": {
            "rate": [11.1, 13.1],  # Rates lentos aceptables
            "filter_down": ["30", "50"],  # Filtros bajos aceptables
            "filter_passhigh": ["1500", "2000"],
            "average": [4000, 3000, 2048],
            "ventana": [15, 18],  # Ventanas largas
            "int": [80, 90]  # Puede necesitar más intensidad
        }
    },

    3: {
        "nombre": "Evaluación Neurológica - Sospecha Schwannoma",
        "descripcion": "Evaluación neurológica con sospecha de lesión retrococlear",
        "instrucciones": "Paciente de 45 años con acúfeno unilateral e hipoacusia asimétrica. Sospecha de schwannoma vestibular. Configure parámetros para evaluación neurológica.",
        "parametros_correctos": {
            # Parámetros básicos
            "stim": "Click",
            "pol": "Rarefacción",  # CRÍTICO: Rarefacción para mejor visualización de onda I
            "int": 80,
            "rate": 11.1,  # Rate LENTO para mejor morfología de onda I (crítico)
            "filter_down": "150",  # Filtro ligeramente más alto para reducir ruido
            "filter_passhigh": "3000",
            "average": 4000,  # MÁS promediaciones para mejor resolución de ondas
            "side": "OD",
            "atten": False,

            # Parámetros avanzados
            "transductor": "Fono inserción",
            "ventana": 12,  # Ventana estándar o ligeramente más larga
            "fsp": "Detección 99% y FSP de 3.1",
            "ruido_residual": "40nV",
            "electrodo_vertex": "Cz",
            "electrodo_derecho": "A1",
            "electrodo_izquierdo": "A2",
            "electrodo_tierra": "Fpz"
        },
        "parametros_aceptables": {
            "pol": ["Rarefacción", "Alternante"],  # Rarefacción es mejor pero alternante es válido
            "rate": [11.1, 13.1, 9.1],  # Rates lentos
            "filter_down": ["150", "100"],
            "average": [4000, 3000, 2048],
            "ventana": [12, 15],
            "int": [80, 90]
        }
    }
}


def validar_configuracion(caso_numero, config_estudiante):
    """
    Valida la configuración del estudiante contra los parámetros correctos

    Args:
        caso_numero: 1, 2 o 3
        config_estudiante: dict con la configuración que ingresó el estudiante

    Returns:
        dict con:
            - 'correcto': bool
            - 'errores': list de parámetros incorrectos
            - 'advertencias': list de parámetros subóptimos pero aceptables
            - 'puntaje': 8 si todo correcto, 0 si hay errores
    """
    if caso_numero not in CASOS_ESTACION_3:
        return {'correcto': False, 'errores': ['Caso no válido'], 'puntaje': 0}

    caso = CASOS_ESTACION_3[caso_numero]
    parametros_correctos = caso['parametros_correctos']
    parametros_aceptables = caso.get('parametros_aceptables', {})

    errores = []
    advertencias = []

    # Lista de parámetros críticos que deben estar correctos
    parametros_criticos = [
        'stim', 'pol', 'rate', 'filter_down', 'filter_passhigh',
        'average', 'ventana', 'transductor'
    ]

    for param in parametros_criticos:
        if param not in config_estudiante:
            errores.append(f"{param}: No configurado")
            continue

        valor_estudiante = config_estudiante[param]
        valor_correcto = parametros_correctos[param]

        # Convertir a string para comparación uniforme
        valor_estudiante_str = str(valor_estudiante)
        valor_correcto_str = str(valor_correcto)

        # Verificar si el valor es correcto
        if valor_estudiante_str == valor_correcto_str:
            continue  # Correcto

        # Verificar si está en los valores aceptables
        if param in parametros_aceptables:
            valores_aceptables = parametros_aceptables[param]
            if isinstance(valores_aceptables, list):
                if valor_estudiante in valores_aceptables or valor_estudiante_str in [str(v) for v in valores_aceptables]:
                    advertencias.append(f"{param}: {valor_estudiante} (aceptable, pero {valor_correcto} es óptimo)")
                    continue

        # Si llegamos aquí, es incorrecto
        errores.append(f"{param}: {valor_estudiante} (esperado: {valor_correcto})")

    # Determinar si está correcto (sin errores críticos)
    correcto = len(errores) == 0
    puntaje = 8 if correcto else 0

    return {
        'correcto': correcto,
        'errores': errores,
        'advertencias': advertencias,
        'puntaje': puntaje,
        'total': 8
    }


def get_descripcion_caso(caso_numero):
    """Retorna la descripción e instrucciones de un caso"""
    if caso_numero in CASOS_ESTACION_3:
        caso = CASOS_ESTACION_3[caso_numero]
        return {
            'nombre': caso['nombre'],
            'descripcion': caso['descripcion'],
            'instrucciones': caso['instrucciones']
        }
    return None


def get_parametros_correctos(caso_numero):
    """Retorna los parámetros correctos de un caso (para docente)"""
    if caso_numero in CASOS_ESTACION_3:
        return CASOS_ESTACION_3[caso_numero]['parametros_correctos']
    return None


if __name__ == "__main__":
    # Test de validación
    print("=== TEST DE VALIDACIÓN ESTACIÓN 3 ===\n")

    # Configuración correcta para Caso 1
    config_correcta_caso1 = {
        'stim': 'Click',
        'pol': 'Alternante',
        'int': 80,
        'rate': 21.1,
        'filter_down': '100',
        'filter_passhigh': '3000',
        'average': 2000,
        'side': 'OD',
        'transductor': 'Fono inserción',
        'ventana': 12
    }

    resultado = validar_configuracion(1, config_correcta_caso1)
    print(f"Caso 1 - Configuración correcta:")
    print(f"  Correcto: {resultado['correcto']}")
    print(f"  Puntaje: {resultado['puntaje']}/{resultado['total']}")
    print(f"  Errores: {resultado['errores']}")
    print()

    # Configuración incorrecta para Caso 2 (usando parámetros de adulto)
    config_incorrecta_caso2 = {
        'stim': 'Click',
        'pol': 'Alternante',
        'int': 80,
        'rate': 21.1,  # ERROR: Debería ser 11.1
        'filter_down': '100',  # ERROR: Debería ser 30
        'filter_passhigh': '3000',  # ERROR: Debería ser 1500
        'average': 2000,  # ERROR: Debería ser 4000
        'side': 'OD',
        'transductor': 'Fono inserción',
        'ventana': 12  # ERROR: Debería ser 15
    }

    resultado = validar_configuracion(2, config_incorrecta_caso2)
    print(f"Caso 2 - Configuración incorrecta (parámetros de adulto):")
    print(f"  Correcto: {resultado['correcto']}")
    print(f"  Puntaje: {resultado['puntaje']}/{resultado['total']}")
    print(f"  Errores:")
    for error in resultado['errores']:
        print(f"    - {error}")
