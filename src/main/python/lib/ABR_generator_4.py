from enum import Enum
from dataclasses import dataclass
import random
import numpy as np
import scipy.signal as signal
from scipy import interpolate
import math

class Polarity(Enum):
    RAREFACTION = "Rarefacción"
    CONDENSATION = "Condensación"
    ALTERNATING = "Alternada"

class HearingLossType(Enum):
    NORMAL = "normal"
    COCHLEAR = "coclear"
    NEURAL = "neural"

@dataclass
class ControlSettings:
    stim: str
    pol: Polarity
    intensity: float
    rate: float
    filter_down: float
    filter_passhigh: float
    prom: list
    side: str

@dataclass
class Preferences:
    type: HearingLossType
    threshold: float
    latencies: list
    amplitudes: list
    repro: bool
    morpho: list

def adjust_for_polarity(polarity: Polarity, hearing_loss_type: HearingLossType):
    add_amp = [0, 0, 0, 0, 0]
    add_lat = [0, 0, 0, 0, 0]
    cm_pol = 0

    if polarity == Polarity.RAREFACTION:
        add_amp = [x + 0.2 for x in add_amp]
        add_lat[:2] = [x - 0.15 for x in add_lat[:2]]
        cm_pol = -0.2
    elif polarity == Polarity.CONDENSATION:
        add_lat = [x + 0.15 for x in add_lat]
        add_amp[-1] += 0.2
        cm_pol = 0.2

    if hearing_loss_type == HearingLossType.COCHLEAR:
        if polarity == Polarity.CONDENSATION:
            cm_pol = 0.0
        elif polarity == Polarity.ALTERNATING:
            cm_pol = -0.1

    return add_amp, add_lat, cm_pol

def adjust_for_rate(rate: float, hearing_loss_type: HearingLossType):
    add_lat = [0, 0, 0, 0, 0]
    add_amp = [0, 0, 0, 0, 0]
    morpho = [True, True, True]

    if 30 < rate < 65:
        add_lat[:2] = [x + 0.2 for x in add_lat[:2]]
        add_amp = [x - 0.1 for x in add_amp]
    elif rate < 15:
        add_lat = [x - 0.1 for x in add_lat]
        add_amp = [x + 0.1 for x in add_amp]
    elif rate > 65:
        add_lat[:2] = [x + 0.3 for x in add_lat[:2]]
        add_amp = [x - 0.2 for x in add_amp]

    if hearing_loss_type == HearingLossType.NEURAL:
        if 10 < rate < 30:
            morpho = [False, False, False]
        elif rate < 10:
            morpho = [True, True, True]

    return add_lat, add_amp, morpho

def calculate_latencies_and_amplitudes(preferences: Preferences, control_settings: ControlSettings):
    # ... (implementar la lógica para calcular latencias y amplitudes)
    pass

def generate_abr_curve(control_settings: ControlSettings, preferences: Preferences):
    add_amp, add_lat, cm_pol = adjust_for_polarity(control_settings.pol, preferences.type)
    rate_lat, rate_amp, morpho = adjust_for_rate(control_settings.rate, preferences.type)

    # Combinar ajustes
    add_lat = [a + b for a, b in zip(add_lat, rate_lat)]
    add_amp = [a + b for a, b in zip(add_amp, rate_amp)]

    # Ajustar para intensidad
    actual_intensity = control_settings.intensity
    step_80_to_actual_int = abs(80 - actual_intensity) / 5
    direc_amp = 1 if actual_intensity > 80 else -1
    direcc_lat = -1 if actual_intensity > 80 else 1

    var_lat = 1 if preferences.type == HearingLossType.COCHLEAR and actual_intensity <= 60 else (0.5 if actual_intensity < 50 else 0.3)
    var_amp = 0.08 if actual_intensity < 50 else 0.06

    # Calcular variaciones de amplitud y latencia
    step_for_80_to_th = (80 - preferences.threshold) / 5
    amp_v_in_step_80_to_th = preferences.amplitudes[1] / step_for_80_to_th
    amp_I_in_step_80_to_th = preferences.amplitudes[0] * 2 / step_for_80_to_th

    var_int_V = step_80_to_actual_int * amp_v_in_step_80_to_th
    var_int_I = step_80_to_actual_int * amp_I_in_step_80_to_th

    desv_lat = (var_lat * var_int_V) * direcc_lat
    desv_amp_V = (var_int_V + var_amp) * direc_amp
    desv_amp_I = (var_int_I + var_amp) * direc_amp

    # Calcular latencias
    lat_peak_I = preferences.latencies[0] + desv_lat + add_lat[0]
    lat_peak_III = preferences.latencies[1] + desv_lat + add_lat[2]
    lat_peak_II = lat_peak_I + (lat_peak_III - lat_peak_I) / 2
    lat_peak_V = preferences.latencies[2] + desv_lat + add_lat[4]
    lat_peak_IV = lat_peak_V - 0.5
    lat_sn10 = lat_peak_V + 1

    # Calcular amplitudes
    current_amp_I = max((preferences.amplitudes[0] + desv_amp_I) / 2, 0)
    current_amp_Ip = min(-(current_amp_I / 2), 0)
    current_amp_II = current_amp_Ip + 0.1
    current_amp_IIp = current_amp_II - 0.02
    current_amp_III = max(((preferences.amplitudes[0] * 2) / 2) + desv_amp_I, 0)
    current_amp_IIIp = min(-(current_amp_III / 2), 0)

    VrefIII = (random.uniform(-.1, .3)) + current_amp_III

    current_amp_IV = max(VrefIII - .05, 0)
    current_amp_IVp = max(current_amp_IV - .05, 0)
    current_amp_V = max(preferences.amplitudes[1] + desv_amp_V, 0)
    current_amp_VI = max(current_amp_V - .3, 0)
    current_amp_sn10 = min(VrefIII - current_amp_V, 0)

    # Ajustar para promediación
    adjusted_prom = cubic_adjustment(control_settings.prom[0], control_settings.prom[1])
    
    amplitudes = [current_amp_I, current_amp_Ip, current_amp_II, current_amp_IIp, 
                  current_amp_III, current_amp_IIIp, current_amp_IV, current_amp_IVp, 
                  current_amp_V, current_amp_VI, current_amp_sn10]
    
    amplitudes = [amp * (adjusted_prom / control_settings.prom[1]) for amp in amplitudes]

    # Generar puntos de la curva
    data_points = generate_data_points(lat_peak_I, lat_peak_II, lat_peak_III, lat_peak_IV, lat_peak_V, 
                                       lat_sn10, amplitudes, cm_pol)

    points = points_create(data_points, actual_intensity, morpho, preferences.threshold)

    # Generar curva Bezier
    Bezi = Bezier()
    path = Bezi.evaluate_bezier(points, 20)
    x, y = points[:,0], points[:,1]
    px, py = path[:,0], path[:,1]

    # Aplicar filtros y ruido
    nyquist = 2000 / 2
    filter_passhigh = (9 / int(control_settings.filter_passhigh)) + 0.81
    filter_down = ((9 / int(control_settings.filter_down)) * 100) - 0.2
    filter_down = max(filter_down, 0.0001)

    noise_value_prom = scale_difference(control_settings.prom[0], control_settings.prom[1])
    noise_prom = np.random.normal(0, noise_value_prom, py.shape)
    noise_value_prom_total = scale_value((control_settings.prom[0] * 100) / 2)
    noise_prom_total = np.random.normal(0, noise_value_prom_total, py.shape)

    py_noisy = np.random.normal(0, filter_down, py.shape)
    order = 4

    b_low, a_low = signal.butter(order, filter_down, btype='low')
    py_low_filtered = signal.filtfilt(b_low, a_low, py_noisy)

    cutoff_high = filter_passhigh / nyquist
    b_high, a_high = signal.butter(order, cutoff_high, btype='high')
    py_high_filtered = signal.filtfilt(b_high, a_high, py_noisy)

    noise = py_low_filtered + py_high_filtered

    y_new = py + (noise / 10) + noise_prom + noise_prom_total

    # Calcular variación de reproductibilidad
    var_repro = calculate_repro_variation(preferences.repro, control_settings.repro_prev)

    return px, y_new, x, y, var_repro

def generate_data_points(lat_peak_I, lat_peak_II, lat_peak_III, lat_peak_IV, lat_peak_V, lat_sn10, amplitudes, cm_pol):
    curve_cm = (lat_peak_I / 3, cm_pol)
    curve_cmp = (curve_cm[0] + lat_peak_I / 3, 0)
    descanso_cm = (curve_cmp[0] + lat_peak_I / 6, 0)

    return {
        "cm": curve_cm, "cmp": curve_cmp, "cmd": descanso_cm,
        "i": (lat_peak_I, amplitudes[0]),
        "ip": (lat_peak_I + ((lat_peak_II - lat_peak_I) / 3), amplitudes[1]),
        "ii": (lat_peak_II, amplitudes[2]),
        "iip": (lat_peak_II + ((lat_peak_III - lat_peak_II) / 2), 0),
        "iii": (lat_peak_III, amplitudes[4]),
        "iiip": (lat_peak_III + 0.9, amplitudes[5]),
        "iv": (lat_peak_IV, amplitudes[6]),
        "ivp": (lat_peak_IV + 0.05, amplitudes[7]),
        "v": (lat_peak_V, amplitudes[8]),
        "sn10": (lat_sn10, amplitudes[10]),
        "vi": (lat_sn10 + 1.5, amplitudes[9]),
        "vip": (lat_sn10 + 3, amplitudes[9] - 0.3),
        "vii": (lat_sn10 + 4.5, amplitudes[9] - 0.3 + 0.6),
        "end": (12 + desv_lat, 0)
    }

def calculate_repro_variation(repro, repro_prev):
    if not repro:
        if repro_prev == 0:
            var_repro = random.uniform(0.2, 0.4)
            var_repro = var_repro * -1 if random.choice([True, False]) else var_repro
        else:
            var_ = random.uniform(-0.1, 0.1)
            var_repro = (repro_prev * -1) + var_
    else:
        var_repro = 0
    return var_repro

def cubic_adjustment(value, max_value):
    """
    Ajusta un valor usando una función cúbica.

    Esta función toma un valor y lo ajusta de manera no lineal utilizando una curva cúbica.
    Esto puede ser útil para crear una respuesta más pronunciada en ciertos rangos de valores.

    Args:
    value (float): El valor a ajustar.
    max_value (float): El valor máximo posible, usado para normalizar.

    Returns:
    float: El valor ajustado.

    Ejemplo:
    >>> cubic_adjustment(50, 100)
    12.5
    >>> cubic_adjustment(100, 100)
    100.0
    """
    # Evitar división por cero
    if max_value == 0:
        return 0

    # Normalizar el valor al rango [0, 1]
    normalized_value = value / max_value

    # Ajustar usando una función cúbica
    adjusted_normalized_value = normalized_value**3

    # Escalar nuevamente al rango original
    adjusted_value = adjusted_normalized_value * max_value

    return adjusted_value


# Uso
control_settings = ControlSettings(
    stim="Click",
    pol=Polarity.ALTERNATING,
    intensity=80,
    rate=10.1,
    filter_down=1000,
    filter_passhigh=50,
    prom=[1000, 1000],
    side="OD"
)

preferences = Preferences(
    type=HearingLossType.NORMAL,
    threshold=20,
    latencies=[1.6, 3.7, 5.6],
    amplitudes=[0.8, 0.8],
    repro=True,
    morpho=[True, True, True]
)

px, y_new, x, y, var_repro = generate_abr_curve(control_settings, preferences)