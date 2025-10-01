"""
ABR Generator V3 - Sistema FSP y Transición Progresiva
Genera curvas ABR con mejora progresiva según promediaciones
Implementa transición desde caos aleatorio → curva objetivo
"""

import json
import random
import numpy as np
import scipy.signal as signal
from base import context


class ABRGenerator:
    """
    Generador de curvas ABR con sistema FSP progresivo
    """
    
    def __init__(self, normative_data_path=None):
        if normative_data_path is None:
            normative_data_path = context.get_resource('json/normative_data.json')
        
        with open(normative_data_path, 'r', encoding='utf-8') as f:
            self.norms = json.load(f)
    
    # =====================================================================
    # NUEVAS FUNCIONES: SISTEMA FSP Y TRANSICIÓN PROGRESIVA
    # =====================================================================
    
    def calcular_fsp(self, prom_actual, fsp_800, fsp_2000):
        """
        Calcula FSP en cualquier número de promediaciones
        Interpolación/extrapolación lineal entre puntos conocidos
        
        Args:
            prom_actual: número de promediaciones actuales
            fsp_800: FSP esperado a 800 promediaciones
            fsp_2000: FSP esperado a 2000 promediaciones
            
        Returns:
            FSP calculado
        """
        if prom_actual <= 0:
            return 0.5  # FSP muy bajo al inicio
        elif prom_actual < 800:
            # Extrapolar hacia abajo (asumiendo FSP=0.5 en prom=0)
            fsp_0 = 0.5
            slope = (fsp_800 - fsp_0) / 800
            return fsp_0 + slope * prom_actual
        elif prom_actual <= 2000:
            # Interpolación lineal entre 800 y 2000
            slope = (fsp_2000 - fsp_800) / (2000 - 800)
            return fsp_800 + slope * (prom_actual - 800)
        else:
            # Mantener FSP@2000 (no mejora más allá)
            return fsp_2000
    
    def generar_caos_inicial(self, x):
        """
        Genera ondas aleatorias caóticas para el estado inicial
        AJUSTADO: Menos agresivo para mejor transición
        
        Args:
            x: array de tiempo
            
        Returns:
            y: señal caótica
        """
        y = np.zeros_like(x)
        
        # Generar 4-6 ondas aleatorias (reducido de 5-8)
        n_ondas = random.randint(4, 6)
        
        for _ in range(n_ondas):
            # Posición aleatoria entre 0 y 10 ms
            lat_random = random.uniform(1.0, 10.0)
            # Amplitud aleatoria moderada (reducido de 0.3-0.8 a 0.15-0.4)
            amp_random = random.uniform(0.15, 0.4)
            # Ancho aleatorio
            ancho = random.uniform(0.3, 0.8)
            
            # Crear onda gaussiana
            onda = amp_random * np.exp(-((x - lat_random) ** 2) / (2 * ancho ** 2))
            
            # Signo aleatorio
            if random.choice([True, False]):
                onda = -onda
            
            y += onda
        
        # Añadir ruido de fondo moderado (reducido de 0.4 a 0.15)
        ruido_base = np.random.normal(0, 0.15, x.shape)
        y += ruido_base
        
        return y
    
    def interpolar_curva(self, y_caos, y_objetivo, prom_actual, fsp_800, fsp_2000, target_avg):
        """
        Interpola entre caos inicial y curva objetivo
        AJUSTADO: Transición más agresiva y natural
        
        Args:
            y_caos: señal caótica inicial
            y_objetivo: señal objetivo final
            prom_actual: promediaciones actuales
            fsp_800, fsp_2000: puntos FSP del caso
            target_avg: promediaciones objetivo totales
            
        Returns:
            y_mezclada: señal en estado intermedio
        """
        # Calcular FSP actual
        fsp_actual = self.calcular_fsp(prom_actual, fsp_800, fsp_2000)
        
        # Factor de transición basado en promediaciones
        # Va de 0 (todo caos) a 1 (todo objetivo)
        if target_avg > 0:
            factor_prom = min(prom_actual / target_avg, 1.0)
        else:
            factor_prom = 0.0
        
        # Ajustar factor según FSP - MUCHO MÁS AGRESIVO
        # Queremos que la señal emerja rápidamente
        if fsp_actual < 1.0:
            factor_transicion = factor_prom * 0.4  # Era 0.3
        elif fsp_actual < 1.5:
            factor_transicion = factor_prom * 0.6  # Era 0.5
        elif fsp_actual < 2.0:
            factor_transicion = factor_prom * 0.8  # Era 0.7
        elif fsp_actual < 2.5:
            factor_transicion = factor_prom * 0.95  # Era 0.85
        else:
            # FSP bueno (>2.5): transición completa
            factor_transicion = factor_prom
        
        # Mezcla progresiva
        y_mezclada = (1 - factor_transicion) * y_caos + factor_transicion * y_objetivo
        
        return y_mezclada
    
    def escalar_amplitud_progresiva(self, y, prom_actual, target_avg):
        """
        Escala la amplitud de la señal progresivamente
        Las amplitudes CRECEN con más promediaciones
        
        Args:
            y: señal a escalar
            prom_actual: promediaciones actuales
            target_avg: promediaciones objetivo
            
        Returns:
            y_escalada: señal con amplitud ajustada
        """
        if target_avg <= 0:
            return y * 0.2  # Muy pequeña
        
        # Factor de escala: va de 0.2 (inicio) a 1.0 (final)
        completion_ratio = min(prom_actual / target_avg, 1.0)
        
        # Curva no lineal: inicio lento, luego crece más rápido
        # Usando función sigmoide desplazada
        scale_factor = 0.2 + 0.8 * (1 / (1 + np.exp(-8 * (completion_ratio - 0.5))))
        
        return y * scale_factor
    
    # =====================================================================
    # FUNCIONES EXISTENTES (mantenidas)
    # =====================================================================
    
    def get_baseline_values(self, population='adult_female', stimulus='click', pathway='air_conduction'):
        """Obtiene valores normativos base a 80dB"""
        pop_data = self.norms['populations'][population]
        
        if stimulus.startswith('tone_burst'):
            stim_data = pop_data[pathway]['tone_burst']
        else:
            stim_data = pop_data[pathway].get(stimulus, pop_data[pathway]['click'])
        
        return stim_data
    
    def calculate_wave_parameters(self, baseline, intensity, threshold, pathology, desviaciones=None):
        """
        Calcula latencias y amplitudes según intensidad
        MODIFICADO: Ahora aplica desviaciones del caso
        
        Args:
            baseline: valores normativos
            intensity: intensidad del estímulo
            threshold: umbral auditivo
            pathology: tipo de patología
            desviaciones: dict con desviaciones del caso (nuevo)
            
        Returns:
            dict de valores modificados, dict de ondas visibles
        """
        modified = {}
        waves_visible = {}
        
        # Si está bajo umbral: nada visible
        if intensity < threshold:
            waves_visible = {w: False for w in ['I', 'II', 'III', 'IV', 'V']}
            return modified, waves_visible
        
        # Desplazamiento desde 80dB
        intensity_diff = 80 - intensity
        steps_from_80 = intensity_diff / 10
        
        # Modificadores
        lat_shift_per_10dB = 0.30
        amp_decay_rates = {'I': 0.12, 'II': 0.10, 'III': 0.08, 'IV': 0.07, 'V': 0.05}
        
        # Calcular para cada onda
        for wave in ['I', 'II', 'III', 'IV', 'V']:
            if wave not in baseline:
                continue
            
            # Determinar si está visible
            if pathology == 'cochlear':
                threshold_wave = threshold + {'I': 30, 'II': 25, 'III': 20, 'IV': 15, 'V': 10}[wave]
            elif pathology == 'neural':
                threshold_wave = threshold + {'I': 10, 'II': 15, 'III': 20, 'IV': 25, 'V': 30}[wave]
            else:  # normal o conductive
                threshold_wave = threshold + {'I': 15, 'II': 12, 'III': 10, 'IV': 8, 'V': 5}[wave]
            
            waves_visible[wave] = intensity >= threshold_wave
            
            if not waves_visible[wave]:
                continue
            
            # Calcular latencia
            base_lat = baseline[wave]['lat']  # ← CORREGIDO
            lat_shift = steps_from_80 * lat_shift_per_10dB
            calculated_lat = base_lat + lat_shift
            
            # NUEVO: Aplicar desviación del caso
            if desviaciones and wave in ['I', 'III', 'V']:
                onda_key = f"onda_{wave}"
                if onda_key in desviaciones:
                    calculated_lat += desviaciones[onda_key]['lat']
            
            # Calcular amplitud
            base_amp = baseline[wave]['amp']  # ← CORREGIDO
            amp_decay = amp_decay_rates[wave]
            amp_factor = np.exp(-amp_decay * abs(steps_from_80))
            calculated_amp = base_amp * amp_factor
            
            # NUEVO: Aplicar desviación del caso
            if desviaciones and wave in ['I', 'III', 'V']:
                onda_key = f"onda_{wave}"
                if onda_key in desviaciones:
                    calculated_amp += desviaciones[onda_key]['amp']
            
            # Asegurar valores positivos
            calculated_amp = max(calculated_amp, 0.05)
            
            modified[wave] = {
                'lat': calculated_lat,
                'amp': calculated_amp
            }
        
        return modified, waves_visible
    
    def apply_polarity_effects(self, values, polarity):
        """Aplica efectos de polaridad"""
        CM_value = None
        
        if polarity == 'Rarefacción':
            for wave in values:
                values[wave]['amp'] *= 1.1
            if 'I' in values:
                values['I']['lat'] -= 0.1
            CM_value = -0.15
        elif polarity == 'Condensación':
            if 'V' in values:
                values['V']['amp'] *= 1.15
            if 'I' in values:
                values['I']['lat'] += 0.1
            CM_value = 0.15
        
        return values, CM_value
    
    def apply_rate_effects(self, values, rate, pathology):
        """Aplica efectos de tasa de estimulación"""
        if rate > 50:
            lat_increase = (rate - 50) * 0.008
            for wave in values:
                values[wave]['lat'] += lat_increase
            
            if rate > 70:
                for wave in values:
                    values[wave]['amp'] *= 0.85
        elif rate < 15:
            for wave in values:
                values[wave]['lat'] -= 0.05
                values[wave]['amp'] *= 1.1
        
        if pathology == 'neural' and 10 < rate < 30:
            if 'II' in values:
                values['II']['amp'] *= 0.3
            if 'IV' in values:
                values['IV']['amp'] *= 0.3
        
        return values
    
    def create_wave_points(self, latencies, amplitudes, waves_visible, CM_value=None, gap=0):
        """Crea puntos de control para Bézier"""
        points = [[0, 0]]
        
        # Microfónico coclear
        if CM_value is not None and CM_value != 0:
            cm_lat = latencies.get('I', {'lat': 1.6})['lat'] / 3
            points.append([cm_lat, CM_value])
            points.append([cm_lat * 2, 0])
            points.append([cm_lat * 2.5, 0])
        
        # Ondas I a V
        for wave in ['I', 'II', 'III', 'IV', 'V']:
            if wave not in latencies:
                continue
            
            if not waves_visible.get(wave, False):
                lat = latencies[wave]['lat']
                points.append([lat, gap])
                points.append([lat + 0.2, gap])
            else:
                lat = latencies[wave]['lat']
                amp = amplitudes[wave]['amp'] + gap
                
                points.append([lat, amp])
                
                valle_lat = lat + 0.35
                valle_amp = -amp * 0.4 + gap
                points.append([valle_lat, valle_amp])
        
        # Ondas tardías
        if 'V' in latencies and waves_visible.get('V', False):
            v_lat = latencies['V']['lat']
            v_amp = amplitudes['V']['amp']
            
            points.append([v_lat + 1.6, v_amp * 0.5 + gap])
            points.append([v_lat + 2.2, v_amp * 0.3 + gap])
            points.append([v_lat + 2.8, v_amp * 0.4 + gap])
            points.append([v_lat + 3.2, v_amp * 0.2 + gap])
        
        points.append([12, gap])
        
        return np.array(points)
    
    def generate_bezier_curve(self, control_points, n_samples=20):
        """Genera curva Bézier suave"""
        from lib.bezier_prop import Bezier
        
        bezier = Bezier()
        path = bezier.evaluate_bezier(control_points, n_samples)
        
        return path[:, 0], path[:, 1]
    
    def add_noise_by_fsp(self, x, y, fsp_actual, impedance=3.0):
        """
        Añade ruido basado en FSP calculado
        CORREGIDO: Ruido con componentes de BAJA frecuencia (más realista)
        
        El ruido en ABR real es principalmente de baja frecuencia (10-100Hz),
        no ruido blanco de alta frecuencia.
        
        Args:
            x, y: señal
            fsp_actual: FSP calculado
            impedance: impedancia de electrodos
            
        Returns:
            x, y_noisy
        """
        # Ruido base según impedancia - REDUCIDO
        if impedance < 3:
            base_noise = 0.02
        elif impedance < 5:
            base_noise = 0.04
        else:
            base_noise = 0.07
        
        # Ajustar ruido según FSP - MULTIPLICADORES REDUCIDOS
        if fsp_actual < 1.0:
            noise_multiplier = 3.0
        elif fsp_actual < 1.5:
            noise_multiplier = 2.2
        elif fsp_actual < 2.0:
            noise_multiplier = 1.6
        elif fsp_actual < 2.5:
            noise_multiplier = 1.2
        elif fsp_actual < 3.0:
            noise_multiplier = 0.9
        else:
            noise_multiplier = 0.6
        
        noise_level = base_noise * noise_multiplier
        
        time = x
        
        # 1. RUIDO GAUSSIANO BASE
        noise_raw = np.random.normal(0, noise_level, y.shape)
        
        # 2. FILTRAR PARA DEJAR SOLO FRECUENCIAS BAJAS (más realista)
        # El ruido real en ABR es principalmente de baja frecuencia
        b_low, a_low = signal.butter(4, 0.55, btype='low')
        noise_filtered = signal.filtfilt(b_low, a_low, noise_raw)
        
        # 3. DRIFT de muy baja frecuencia (desplazamiento de línea base)
        drift = noise_level * 0.3 * np.sin(2 * np.pi * 0.5 * time)
        
        # 4. INTERFERENCIA ELÉCTRICA 50/60Hz (solo si FSP bajo)
        if fsp_actual < 2.0:
            power_line = noise_level * 0.15 * np.sin(2 * np.pi * 50 * time)
        else:
            power_line = 0
        
        # 5. COMBINAR todos los componentes
        noise_total = noise_filtered + drift + power_line
        
        y_noisy = y + noise_total
        
        return x, y_noisy
    
    def add_artifact(self, x, y, transducer='insert_earphone'):
        """Añade artefacto electromagnético del transductor"""
        artifacts = {
            'insert_earphone': {'duration': 0.8, 'amplitude': 0.05},
            'TDH39_headphone': {'duration': 1.2, 'amplitude': 0.12},
            'bone_vibrator': {'duration': 1.5, 'amplitude': 0.20}
        }
        
        artifact_data = artifacts.get(transducer, artifacts['insert_earphone'])
        
        duration = artifact_data['duration']
        amplitude = artifact_data['amplitude']
        
        artifact_mask = x < duration
        artifact = np.where(artifact_mask, amplitude * np.exp(-x * 4), 0)
        
        return x, y + artifact
    
    def apply_filters(self, x, y, filter_low, filter_high, fs=20000):
        """Aplica filtros digitales"""
        nyquist = fs / 2
        
        low_norm = min(filter_low / nyquist, 0.99)
        b_low, a_low = signal.butter(4, low_norm, btype='low')
        y_filtered = signal.filtfilt(b_low, a_low, y)
        
        high_norm = max(filter_high / nyquist, 0.01)
        b_high, a_high = signal.butter(4, high_norm, btype='high')
        y_filtered = signal.filtfilt(b_high, a_high, y_filtered)
        
        return y_filtered
    
    def generate_curve(self, population, pathology, stimulus_config, technical_config, case_config=None):
        """
        Genera curva ABR completa con sistema de transición progresiva
        
        MODIFICADO: Implementa caos inicial → curva objetivo
        
        Args:
            case_config: dict con 'desviaciones' y 'fsp_puntos' del caso (nuevo)
            
        Returns:
            (x, y, metadata)
        """
        # 1. Obtener valores base
        baseline = self.get_baseline_values(population, stimulus_config['stim'])
        
        # 2. Obtener umbral (del caso o de patología)
        if case_config and 'umbral' in case_config:
            threshold = case_config['umbral']
        else:
            threshold = self.norms['pathology_modifiers'][pathology]['threshold_range'][0]
        
        # 3. Obtener desviaciones del caso
        desviaciones = None
        if case_config and 'desviaciones' in case_config:
            stim_type = stimulus_config['stim']
            if stim_type in case_config['desviaciones']:
                desviaciones = case_config['desviaciones'][stim_type]
        
        # 4. Calcular parámetros de ondas (con desviaciones)
        values, waves_visible = self.calculate_wave_parameters(
            baseline, 
            stimulus_config['int'], 
            threshold, 
            pathology,
            desviaciones
        )
        
        # 5. Si no hay ondas visibles, retornar solo ruido
        if not any(waves_visible.values()):
            x = np.linspace(0, 12, 240)
            y_caos = self.generar_caos_inicial(x)
            
            # Calcular FSP
            fsp_800 = case_config['fsp_puntos']['800'] if case_config else 2.3
            fsp_2000 = case_config['fsp_puntos']['2000'] if case_config else 2.8
            fsp_actual = self.calcular_fsp(stimulus_config['current_avg'], fsp_800, fsp_2000)
            
            # Solo ruido (no hay señal)
            x, y = self.add_noise_by_fsp(x, y_caos * 0.3, fsp_actual, technical_config['impedance'])
            
            return x, y, {'waves_visible': waves_visible, 'fsp': fsp_actual}
        
        # 6. Aplicar efectos de polaridad y rate
        values, CM_value = self.apply_polarity_effects(values, stimulus_config['pol'])
        values = self.apply_rate_effects(values, stimulus_config['rate'], pathology)
        
        # 7. Crear curva objetivo (sin promediación progresiva todavía)
        latencies = {k: {'lat': v['lat']} for k, v in values.items()}
        amplitudes = {k: {'amp': v['amp']} for k, v in values.items()}
        
        control_points = self.create_wave_points(latencies, amplitudes, waves_visible, CM_value)
        x, y_objetivo = self.generate_bezier_curve(control_points, n_samples=20)
        
        # 8. Generar caos inicial
        y_caos = self.generar_caos_inicial(x)
        
        # 9. Obtener FSP del caso
        if case_config and 'fsp_puntos' in case_config:
            fsp_800 = case_config['fsp_puntos']['800']
            fsp_2000 = case_config['fsp_puntos']['2000']
        else:
            fsp_800 = 2.3
            fsp_2000 = 2.8
        
        # 10. Calcular FSP actual
        fsp_actual = self.calcular_fsp(stimulus_config['current_avg'], fsp_800, fsp_2000)
        
        # 11. Interpolar entre caos y objetivo
        y_transitoria = self.interpolar_curva(
            y_caos, 
            y_objetivo, 
            stimulus_config['current_avg'],
            fsp_800,
            fsp_2000,
            stimulus_config['average']
        )
        
        # 12. Escalar amplitud progresivamente
        y_escalada = self.escalar_amplitud_progresiva(
            y_transitoria,
            stimulus_config['current_avg'],
            stimulus_config['average']
        )
        
        # 13. Aplicar filtros
        y_filtered = self.apply_filters(
            x, y_escalada,
            stimulus_config['filter_down'],
            stimulus_config['filter_passhigh']
        )
        
        # 14. Añadir ruido según FSP
        x, y_noisy = self.add_noise_by_fsp(
            x, y_filtered,
            fsp_actual,
            technical_config['impedance']
        )
        
        # 15. Añadir artefacto electromagnético
        x, y_final = self.add_artifact(x, y_noisy, technical_config['transducer'])
        
        metadata = {
            'population': population,
            'pathology': pathology,
            'waves_visible': waves_visible,
            'current_avg': stimulus_config['current_avg'],
            'target_avg': stimulus_config['average'],
            'fsp': fsp_actual
        }
        
        # Debug
        if stimulus_config['current_avg'] % 200 < 50:
            print(f"DEBUG: prom={stimulus_config['current_avg']:.0f}, FSP={fsp_actual:.2f}")
        
        return x, y_final, metadata


# ============================================================================
# INTERFAZ DE COMPATIBILIDAD
# ============================================================================

_generator = None

def _get_generator():
    global _generator
    if _generator is None:
        _generator = ABRGenerator()
    return _generator


def ABR_Curve(actual_intencity, control_setting, preferences, repro_prev, prom, done):
    """
    Función de compatibilidad - GENERA CURVA PROGRESIVA
    MODIFICADO: Lee campos nuevos del caso
    """
    generator = _get_generator()
    
    # Mapear patología
    pathology_map = {
        'normal': 'normal',
        'coclear': 'cochlear',
        'transmission': 'conductive',
        'neural': 'neural'
    }
    pathology = pathology_map.get(preferences.get('type', 'normal'), 'normal')
    
    # Calcular promediaciones actuales
    print(f"DEBUG ABR_Curve: prom[0]={prom[0]}, prom[1]={prom[1]}, done={done}")
    
    if done and prom[0] == 0:
        current_averages = prom[1]
    elif prom[0] <= 1.0:
        current_averages = prom[0] * prom[1]
    else:
        current_averages = prom[0] * 2.5
    
    target_averages = prom[1]
    
    if current_averages >= target_averages:
        current_averages = target_averages
    
    print(f"DEBUG: current_averages={current_averages}, target_averages={target_averages}")
    
    # Configuración de estímulo
    stimulus_config = {
        'stim': 'click',
        'pol': control_setting['pol'],
        'int': actual_intencity,
        'rate': control_setting['rate'],
        'filter_down': float(control_setting['filter_down']),
        'filter_passhigh': float(control_setting['filter_passhigh']),
        'average': target_averages,
        'current_avg': current_averages
    }
    
    # Configuración técnica
    technical_config = {
        'impedance': 3.0,
        'transducer': 'insert_earphone'
    }
    
    # NUEVO: Pasar configuración del caso
    case_config = {
        'desviaciones': preferences.get('desviaciones', {}),
        'fsp_puntos': preferences.get('fsp_puntos', {'800': 2.3, '2000': 2.8}),
        'umbral': preferences.get('umbral', preferences.get('th', 20))
    }
    
    # Generar curva con sistema progresivo
    x, y, metadata = generator.generate_curve(
        population='adult_female',
        pathology=pathology,
        stimulus_config=stimulus_config,
        technical_config=technical_config,
        case_config=case_config
    )
    
    # Reproductibilidad
    if not preferences.get('repro', True):
        var_repro = random.uniform(-0.2, 0.2) if repro_prev == 0 else -repro_prev + random.uniform(-0.1, 0.1)
    else:
        var_repro = 0
    
    # Retornar en formato compatible
    dx = x.copy()
    dy = y.copy()
    
    return x, y, dx, dy, var_repro