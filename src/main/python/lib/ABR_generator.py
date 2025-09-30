import random
import numpy as np
import lib.bezier_prop as bz
import scipy.signal as signal
import math
from scipy import interpolate

def scale_value(value):
    """
    Calcula el nivel de ruido base según el número de promediaciones.
    Usa función sigmoide para transición suave entre rangos.
    """
    if value <= 800:
        return 1 - (1 / (1 + math.exp(-0.005 * (value - 400))))
    elif 800 < value <= 1500:
        base = 1 / (1 + math.exp(-0.005 * (800 - 400)))
        return base - (0.7 / (1 + math.exp(-0.005 * (value - 1150))))
    elif 1500 < value < 2000:
        base1 = 1 / (1 + math.exp(-0.005 * (800 - 400)))
        base2 = base1 - (0.7 / (1 + math.exp(-0.005 * (1500 - 1150))))
        return base2 - (0.3 / (1 + math.exp(-0.005 * (value - 1750))))
    else:
        base1 = 1 / (1 + math.exp(-0.005 * (800 - 400)))
        base2 = base1 - (0.7 / (1 + math.exp(-0.005 * (1500 - 1150))))
        base3 = base2 - (0.3 / (1 + math.exp(-0.005 * (2000 - 1750))))
        return max(base3 - (base3 / (1 + math.exp(-0.0005 * (value - 6000)))), 0)


def scale_difference(value, max_value):
    """
    Calcula el ruido adicional por diferencia entre promediaciones actual y objetivo.
    """
    difference = max_value - value
    scaled_difference = (0.6 / max_value) * difference
    return max(scaled_difference, 0)


def ABR_Curve(actual_intencity, control_setting, preferences, repro_prev, prom, done):
    """
    Genera una curva ABR simulada.
    
    Parámetros:
    - actual_intencity: Intensidad del estímulo en dB nHL
    - control_setting: Dict con parámetros de control (pol, rate, filters, etc)
    - preferences: Dict con preferencias (type, lat, amp, repro, morfo, th)
    - repro_prev: Valor previo de reproductibilidad
    - prom: [promediaciones_actual, promediaciones_objetivo]
    - done: Flag de depuración
    
    Retorna:
    - px, y_new, x, y, var_repro
    """
    
    # Evitar promediaciones en cero
    prom[0] = prom[1] if prom[0] == 0.0 else prom[0]
    
    # Inicializar ajustes de polaridad y amplitud
    add_amp = [0, 0, 0, 0, 0]
    add_lat = [0, 0, 0, 0, 0]
    
    # Ajustes por polaridad
    if control_setting["pol"] == "Rarefacción":
        add_amp = [x + 0.2 for x in add_amp]
        add_lat[:2] = [x - 0.15 for x in add_lat[:2]]
        cm_pol = -0.2
    elif control_setting["pol"] == "Condensación":
        add_lat = [x + 0.15 for x in add_lat]
        add_amp[-1] += 0.2
        cm_pol = 0.2
    else:
        cm_pol = 0
    
    # Ajustes especiales para pérdida coclear
    if preferences["type"] == "coclear" and control_setting["pol"] == "Condensación":
        cm_pol = 0.0
    if preferences["type"] == "coclear" and control_setting["pol"] == "Alternada":
        cm_pol = -0.1
    
    # Ajustes por tasa de estimulación (rate)
    rate = control_setting["rate"]
    if 30 < rate < 65:
        add_lat[:2] = [x + 0.2 for x in add_lat[:2]]
        add_amp = [x - 0.1 for x in add_amp]
    elif rate < 15:
        add_lat = [x - 0.1 for x in add_lat]
        add_amp = [x + 0.1 for x in add_amp]
    elif rate > 65:
        add_lat[:2] = [x + 0.3 for x in add_lat[:2]]
        add_amp = [x - 0.2 for x in add_amp]
    
    # Morfología para pérdida neural según rate
    if 10 < rate < 30 and preferences["type"] == "neural":
        preferences["morfo"] = [False, False, False]
    elif rate < 10 and preferences["type"] == "neural":
        preferences["morfo"] = [True, True, True]
    
    # Extraer parámetros de filtros
    filter_down = float(control_setting["filter_down"])
    filter_passhigh = float(control_setting["filter_passhigh"])
    
    # Extraer preferencias
    threshold = preferences["th"]
    lat_I = preferences["lat"][0]
    lat_III = preferences["lat"][1]
    lat_V = preferences["lat"][2]
    amp = preferences["amp"]
    repro = preferences["repro"]
    window = 12
    zeros = False
    
    # Calcular variaciones por intensidad
    step_80_to_actual_int = abs(80 - actual_intencity) / 5
    
    # Dirección de cambios según intensidad
    if actual_intencity > 80:
        direc_amp = 1
        direcc_lat = -1
    else:
        direc_amp = -1
        direcc_lat = 1
    
    # Variación de latencia y amplitud según intensidad
    if actual_intencity >= 50:
        var_lat = 0.3
        var_amp = 0.06
    else:
        var_lat = 0.5
        var_amp = 0.08
    
    # Ajuste especial para pérdida coclear a baja intensidad
    if preferences["type"] == "coclear" and actual_intencity <= 60:
        var_lat = 1
    
    # Calcular pasos desde 80 dB al umbral
    step_for_80_to_th = (80 - threshold) / 5
    amp_v_in_step_80_to_th = amp[1] / step_for_80_to_th
    amp_I_in_step_80_to_th = amp[0] * 2 / step_for_80_to_th
    
    # Variaciones de intensidad
    var_int_V = step_80_to_actual_int * amp_v_in_step_80_to_th
    var_int_I = step_80_to_actual_int * amp_I_in_step_80_to_th
    
    # Desviaciones finales
    desv_lat = (var_lat * var_int_V) * direcc_lat
    desv_amp_V = (var_int_V + var_amp) * direc_amp
    desv_amp_I = (var_int_I + var_amp) * direc_amp
    
    # === CÁLCULO DE LATENCIAS ===
    lat_peak_I = lat_I + desv_lat + add_lat[0]
    lat_peak_III = lat_III + desv_lat + add_lat[2]
    dist_III_I = (lat_peak_III - lat_peak_I) / 2
    lat_peak_II = lat_peak_I + dist_III_I
    lat_peak_V = lat_V + desv_lat + add_lat[4]
    lat_peak_IV = lat_peak_V - 0.5
    lat_sn10 = lat_peak_V + 1
    
    # Punto final de la curva
    end = [window + desv_lat, 0]
    
    # === REPRODUCTIBILIDAD ===
    if not repro:
        if repro_prev == 0:
            var_repro = random.uniform(0.2, 0.4)
            var_repro = var_repro * -1 if random.choice([True, False]) else var_repro
        else:
            var_ = random.uniform(-0.1, 0.1)
            var_repro = (repro_prev * -1) + var_
        lat_peak_V = lat_peak_V + var_repro
    else:
        var_repro = 0
    
    # === CÁLCULO DE AMPLITUDES ===
    # Amplitudes base con ajustes por intensidad y polaridad
    current_amp_I = max((amp[0] + desv_amp_I) / 2 + add_amp[0], 0)
    current_amp_Ip = min(-(current_amp_I / 2), 0)
    current_amp_II = current_amp_Ip + 0.1
    current_amp_IIp = current_amp_II - 0.02
    
    # Onda III: corregido para evitar multiplicación innecesaria
    current_amp_III = max(amp[0] + desv_amp_I + add_amp[2], 0)
    current_amp_IIIp = min(-(current_amp_III / 2), 0)
    
    # Variación aleatoria del inicio de onda V respecto a onda III
    VrefIII = random.uniform(-0.1, 0.3) + current_amp_III
    
    # Ondas IV, V, VI
    current_amp_IV = max(VrefIII - 0.05, 0)
    current_amp_IVp = max(current_amp_IV - 0.05, 0)
    current_amp_V = max(amp[1] + desv_amp_V + add_amp[4], 0)
    current_amp_VI = max(current_amp_V - 0.3, 0)
    current_amp_sn10 = min(VrefIII - current_amp_V, 0)
    
    # === AJUSTE POR PROMEDIACIÓN (MEJORADO) ===
    # Factor de mejora de SNR: sqrt(N_actual / N_objetivo)
    # Amplitud aumenta con más promediaciones por mejor SNR
    prom_factor = np.sqrt(prom[0] / prom[1])
    
    # Aplicar factor a todas las amplitudes
    current_amp_I *= prom_factor
    current_amp_Ip *= prom_factor
    current_amp_II *= prom_factor
    current_amp_IIp *= prom_factor
    current_amp_III *= prom_factor
    current_amp_IIIp *= prom_factor
    current_amp_IV *= prom_factor
    current_amp_IVp *= prom_factor
    current_amp_V *= prom_factor
    current_amp_VI *= prom_factor
    current_amp_sn10 *= prom_factor
    
    # === CREACIÓN DE PUNTOS DE CURVA ===
    # Microfónico coclear
    curve_cm = (lat_peak_I / 3, cm_pol)
    curve_cmp = (curve_cm[0] + lat_peak_I / 3, 0)
    descanso_cm = (curve_cmp[0] + lat_peak_I / 6, 0)
    
    # Onda I
    curve_I = (lat_peak_I, current_amp_I)
    curve_Ip = (curve_I[0] + ((lat_peak_II - lat_peak_I) / 3), current_amp_Ip)
    
    # Onda II
    curve_II = (lat_peak_II, current_amp_II)
    curve_IIp = (curve_II[0] + ((lat_peak_III - lat_peak_II) / 2), 0)
    
    # Onda III
    curve_III = (lat_peak_III, current_amp_III)
    curve_IIIp = (curve_III[0] + 0.9, current_amp_IIIp)
    
    # Onda IV
    curve_IV = (lat_peak_IV, current_amp_IV)
    curve_IVp = (lat_peak_IV + 0.05, current_amp_IVp)
    
    # Onda V
    curve_V = (lat_peak_V, VrefIII)
    
    # SN10
    sn10 = (lat_sn10, current_amp_sn10)
    
    # Onda VI
    curve_VI = (lat_sn10 + 1.5, current_amp_VI)
    curve_VIp = (curve_VI[0] + 1.5, curve_VI[1] - 0.3)
    
    # Onda VII
    curve_VII = (curve_VIp[0] + 1.5, curve_VIp[1] + 0.6)
    
    # Ajustar fin si es necesario
    if curve_VII[0] > end[0]:
        end = curve_VII
    
    # Diccionario de datos
    data_points = {
        "cm": curve_cm, "cmp": curve_cmp, "cmd": descanso_cm,
        "i": curve_I, "ip": curve_Ip,
        "ii": curve_II, "iip": curve_IIp,
        "iii": curve_III, "iiip": curve_IIIp,
        "iv": curve_IV, "ivp": curve_IVp,
        "v": curve_V, "sn10": sn10,
        "vi": curve_VI, "vip": curve_VIp,
        "vii": curve_VII, "end": end
    }
    
    # Crear puntos para Bezier
    points = points_create(data_points, actual_intencity, preferences["morfo"], preferences["th"])
    
    # Generar curva Bezier
    Bezi = bz.Bezier()
    path = Bezi.evaluate_bezier(points, 20)
    
    # Extraer coordenadas
    nyquist = 2000 / 2
    x, y = points[:, 0], points[:, 1]
    px, py = path[:, 0], path[:, 1]
    
    # === GENERACIÓN DE RUIDO Y FILTROS (MEJORADO) ===
    # Conversión de parámetros de filtro a frecuencias normalizadas
    # Fórmulas simplificadas pero más comprensibles
    filter_high_normalized = min(filter_passhigh / nyquist, 0.99)
    filter_low_scale = max(0.01 * (1000 / filter_down), 0.0001)
    
    # Ruido por diferencia de promediaciones
    noise_value_prom = scale_difference(prom[0], prom[1])
    noise_prom = np.random.normal(0, noise_value_prom, py.shape)
    
    # Ruido base por número de promediaciones
    noise_base_value = scale_value((prom[0] * 100) / 2)
    noise_base = np.random.normal(0, noise_base_value, py.shape)
    
    # Ruido de fondo filtrado
    py_noisy = np.random.normal(0, filter_low_scale, py.shape)
    order = 4
    
    # Filtro paso bajo
    b_low, a_low = signal.butter(order, filter_low_scale, btype='low')
    py_low_filtered = signal.filtfilt(b_low, a_low, py_noisy)
    
    # Filtro paso alto
    b_high, a_high = signal.butter(order, filter_high_normalized, btype='high')
    py_high_filtered = signal.filtfilt(b_high, a_high, py_noisy)
    
    # Combinar ruidos
    noise_filtered = py_low_filtered + py_high_filtered
    
    # Señal final con ruido
    y_new = py + (noise_filtered * 0.1) + noise_prom + noise_base
    
    # Caso especial: señal en cero
    if zeros:
        px = np.zeros(20)
        y_new = np.zeros(20)
    
    return px, y_new, x, y, var_repro


def points_create(data, intencity, morpho, th):
    """
    Crea array de puntos para la curva Bezier según intensidad y morfología.
    Los puntos DEBEN estar ordenados cronológicamente (latencia creciente).
    """
    curve_cm = data["cm"]
    curve_cmp = data["cmp"]
    descanso_cm = data["cmd"]
    curve_I = data["i"]
    curve_Ip = data["ip"]
    curve_II = data["ii"]
    curve_IIp = data["iip"]
    curve_III = data["iii"]
    curve_IIIp = data["iiip"]
    curve_IV = data["iv"]
    curve_IVp = data["ivp"]
    curve_V = data["v"]
    sn10 = data["sn10"]
    curve_VI = data["vi"]
    curve_VIp = data["vip"]
    curve_VII = data["vii"]
    end = data["end"]
    
    # Estructuras de curvas
    _cm = [[curve_cm[0], curve_cm[1]],
           [curve_cmp[0], curve_cmp[1]]]
    
    _i = [[curve_I[0], curve_I[1]],
          [curve_Ip[0], curve_Ip[1]]]
    
    _ii = [[curve_II[0], curve_II[1]],
           [curve_IIp[0], curve_IIp[1]]]
    
    _iii = [[curve_III[0], curve_III[1]],
            [curve_IIIp[0], curve_IIIp[1]]]
    
    _iv = [[curve_IV[0], curve_IV[1]],
           [curve_IVp[0], curve_IVp[1]]]
    
    _v = [[curve_V[0], curve_V[1]],
          [sn10[0], sn10[1]]]
    
    _vi = [[curve_VI[0], curve_VI[1]],
           [curve_VIp[0], curve_VIp[1]]]
    
    _vii = [[curve_VII[0], curve_VII[1]],
            [end[0], end[1]]]
    
    zero = [[0, 0]]
    
    # Ondas principales para morfología
    _morpho = [_i, _iii, _v]
    curve = []
    tail = [_vi, _vii]
    
    # Si está bajo el umbral, solo mostrar ruido
    if intencity < th:
        points = np.concatenate((zero, _vi, _vii))
    else:
        # Construir curva en orden correcto
        curve.append(zero)
        curve.append(_cm)
        
        # Aplicar morfología a ondas I, III, V
        for i, value in enumerate(morpho):
            if value:
                curve.append(_morpho[i])
            else:
                # Ocultar onda poniendo amplitud en 0
                _morpho[i][0][1] = 0
                _morpho[i][1][1] = 0
                curve.append(_morpho[i])
        
        # AHORA añadir ondas finales (después de insertar II)
        # NO añadir tail aquí todavía
        
        # Verificar si hay IV
        yes_iv = True
        for i, value in enumerate(curve):
            if isinstance(value, bool):
                yes_iv = False
        
        if yes_iv:
            # Insertar onda II en posición 3 (después de cm e I, antes de III)
            curve.insert(3, _ii)
            # curve.insert(4, _iv)  # Comentado en original
        
        # Limpiar elementos booleanos si existen
        curve = [value for value in curve if not isinstance(value, bool)]
        
        # AHORA sí añadir tail al final
        curve.append(tail[0])
        curve.append(tail[1])
        
        # Aplanar lista de listas
        curve = [elemento for sublista in curve for elemento in sublista]
        points = np.array(curve)
    
    return points