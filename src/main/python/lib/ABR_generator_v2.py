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
        

    def generar_caos_inicial(self, x, fsp_actual=1.0):
        """
        Genera ruido realista con ondas gaussianas + ruido base
        El ruido base escala según FSP
        
        Args:
            x: array de tiempo
            fsp_actual: FSP calculado (controla nivel de ruido)
            
        Returns:
            y: señal de ruido
        """
        y = np.zeros_like(x)
        
        # Ondas gaussianas (movimiento/animación) - más constantes
        n_ondas = random.randint(2, 4)
        
        for _ in range(n_ondas):
            # Posición aleatoria en toda la ventana
            lat_random = random.uniform(0.0, 12.0)
            # Amplitud aleatoria moderada
            amp_random = random.uniform(0.10, 0.25)
            # Ancho aleatorio (más ancho = más redondeado)
            ancho = random.uniform(0.5, 1.2)
            
            # Crear onda gaussiana
            onda = amp_random * np.exp(-((x - lat_random) ** 2) / (2 * ancho ** 2))
            
            # Signo aleatorio
            if random.choice([True, False]):
                onda = -onda
            
            y += onda
        
        # Ruido base escalado por FSP (textura picuda)
        if fsp_actual < 1.0:
            noise_level = 0.15
        elif fsp_actual < 1.5:
            noise_level = 0.12
        elif fsp_actual < 2.0:
            noise_level = 0.09
        elif fsp_actual < 2.5:
            noise_level = 0.06
        elif fsp_actual < 3.0:
            noise_level = 0.04
        else:
            noise_level = 0.02
        
        ruido_base = np.random.normal(0, noise_level, x.shape)
        y += ruido_base
        
        # Suavizar con filtro pasa-bajos
        b, a = signal.butter(3, 0.3, btype='low')
        y = signal.filtfilt(b, a, y)
        
        return y

    

    def interpolar_curva(self, y_caos, y_objetivo, prom_actual, fsp_800, fsp_2000, target_avg):
        """
        Interpola entre caos inicial y curva objetivo
        MODIFICADO: Llama a generar_caos_inicial con FSP
        
        Args:
            y_caos: señal caótica inicial (ya no se usa, se regenera)
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
        if target_avg > 0:
            factor_prom = min(prom_actual / target_avg, 1.0)
        else:
            factor_prom = 0.0
        
        # Ajustar factor según FSP - transición agresiva
        if fsp_actual < 1.0:
            factor_transicion = factor_prom * 0.4
        elif fsp_actual < 1.5:
            factor_transicion = factor_prom * 0.6
        elif fsp_actual < 2.0:
            factor_transicion = factor_prom * 0.8
        elif fsp_actual < 2.5:
            factor_transicion = factor_prom * 0.95
        else:
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
        MODIFICADO: Las ondas NUNCA desaparecen, solo se hacen imperceptibles
        - Amplitud decae exponencialmente
        - Las ondas se ensanchan a baja intensidad
        """
        modified = {}
        
        # Desplazamiento desde 80dB
        steps_from_80 = (80 - intensity) / 10
        
        # Latencia: bajo 60dB se desplaza 0.3ms por cada 10dB
        if intensity >= 60:
            lat_shift = steps_from_80 * 0.08
        else:
            lat_shift_60 = (80 - 60) / 10 * 0.08
            lat_shift_below_60 = (60 - intensity) / 10 * 0.3
            lat_shift = lat_shift_60 + lat_shift_below_60
        
        # Calcular para cada onda - SIEMPRE
        for wave in ['I', 'II', 'III', 'IV', 'V']:
            if wave not in baseline:
                continue
            
            # ========== LATENCIA ==========
            base_lat = baseline[wave]['lat']
            calculated_lat = base_lat + lat_shift
            
            # Onda I apenas se desplaza (origen coclear)
            if wave == 'I':
                calculated_lat = base_lat + lat_shift * 0.2
            
            # Aplicar desviación del caso
            if desviaciones and wave in ['I', 'III', 'V']:
                onda_key = f"onda_{wave}"
                if onda_key in desviaciones:
                    calculated_lat += desviaciones[onda_key]['lat']
            
            # ========== AMPLITUD ==========
            base_amp = baseline[wave]['amp']
            
            # Decaimiento LINEAL entre 80dB y umbral
            if wave == 'V':
                # Onda V: de 80dB (100%) a umbral (5%) linealmente
                if intensity >= threshold:
                    db_range = 80 - threshold
                    db_from_threshold = intensity - threshold
                    amp_factor = 0.05 + 0.95 * (db_from_threshold / db_range)
                else:
                    # Bajo umbral: sigue bajando linealmente a 0
                    db_range = 10  # 10dB bajo umbral = 0%
                    db_below = threshold - intensity
                    amp_factor = max(0.05 * (1 - db_below / db_range), 0.001)
            else:
                # Ondas I, II, III, IV desaparecen antes del umbral
                disappear_offset = {'I': 70, 'II': 70, 'III': threshold + 10, 'IV': threshold + 8}
                disappear_at = disappear_offset.get(wave, threshold + 10)
                
                if intensity >= disappear_at:
                    # De 80dB a punto de desaparición (5%) linealmente
                    db_range = 80 - disappear_at
                    db_from_disappear = intensity - disappear_at
                    amp_factor = 0.05 + 0.95 * (db_from_disappear / db_range)
                else:
                    # Bajo punto de desaparición: sigue a 0 linealmente
                    db_range = 10
                    db_below = disappear_at - intensity
                    amp_factor = max(0.05 * (1 - db_below / db_range), 0.001)
            
            calculated_amp = base_amp * amp_factor
            
            # Aplicar desviación del caso
            if desviaciones and wave in ['I', 'III', 'V']:
                onda_key = f"onda_{wave}"
                if onda_key in desviaciones:
                    calculated_amp += desviaciones[onda_key]['amp']
            
            # Asegurar valores positivos mínimos (pero NUNCA cero)
            calculated_amp = max(calculated_amp, 0.001)
            
            # ========== ANCHO DE ONDA (nuevo) ==========
            # A menor intensidad, las ondas se ensanchan (menos picudas)
            if intensity >= 70:
                width_factor = 1.0  # Ancho normal
            elif intensity >= 50:
                # Entre 70 y 50: ensancha progresivamente
                width_factor = 1.0 + (70 - intensity) * 0.03
            else:
                # Bajo 50dB: muy anchas
                width_factor = 1.6 + (50 - intensity) * 0.05
            
            modified[wave] = {
                'lat': calculated_lat,
                'amp': calculated_amp,
                'width': width_factor  # ← NUEVO campo
            }
        
        # waves_visible ya no determina si se dibuja, solo es informativo
        waves_visible = {w: True for w in ['I', 'II', 'III', 'IV', 'V']}
        
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
        """
        Crea puntos de control para Bézier con morfología realista de ABR
        
        PRINCIPIOS ELECTROFISIOLÓGICOS:
        - Lo importante es PICO → VALLE (la amplitud se mide pico-a-valle)
        - Ascensos no importan (directos y rápidos)
        - Las ondas pueden estar a cualquier altura (no importa relación con gap/0)
        - Descensos SÍ importan (morfología electrofisiológica)
        """
        points = [[0, gap]]
        
        # Altura base flotante para cada onda (pueden estar a diferentes niveles)
        base_height = gap + 0.05
        
        # Microfónico coclear
        if CM_value is not None and CM_value != 0:
            cm_lat = latencies.get('I', {'lat': 1.6})['lat'] / 3
            
            # Solo 3 puntos: subida rápida, pico, bajada rápida
            points.append([cm_lat - 0.15, base_height])
            points.append([cm_lat, base_height + CM_value])  # Pico único
            points.append([cm_lat + 0.15, base_height])
        
        # ========== ONDA I: PICO REDONDEADO → VALLE SUAVE ==========
        if 'I' in latencies:
            lat_I = latencies['I']['lat']
            amp_I = amplitudes['I']['amp']
            width_I = amplitudes['I'].get('width', 1.0)
            
            # Ascenso directo (no importante)
            points.append([lat_I - 0.20 * width_I, base_height])
            
            # Pico redondeado
            peak_I = base_height + amp_I
            points.append([lat_I - 0.05 * width_I, peak_I])
            points.append([lat_I + 0.08 * width_I, peak_I])
            
            # DESCENSO IMPORTANTE: suave y gradual
            points.append([lat_I + 0.20 * width_I, peak_I - amp_I * 0.5])
            points.append([lat_I + 0.35 * width_I, peak_I - amp_I * 0.8])
            
            # Valle de I
            valle_I_lat = lat_I + 0.45 * width_I
            valle_I = peak_I - amp_I * 1.25  # Valle un poco bajo el pico
            points.append([valle_I_lat, valle_I])
            
            # Retorno a nueva base
            base_height = valle_I + 0.03
            points.append([valle_I_lat + 0.10 * width_I, base_height])
        
        # ========== ONDA II: PICO PICUDO → VALLE ==========
        if 'II' in latencies:
            lat_II = latencies['II']['lat']
            amp_II = amplitudes['II']['amp']
            width_II = amplitudes['II'].get('width', 1.0)
            
            # Ascenso directo
            points.append([lat_II - 0.10 * width_II, base_height])
            
            # Pico picudo
            peak_II = base_height + amp_II
            points.append([lat_II, peak_II])
            
            # DESCENSO IMPORTANTE: rápido
            valle_II_lat = lat_II + 0.20 * width_II
            valle_II = peak_II - amp_II * 1.30
            points.append([valle_II_lat, valle_II])
            
            base_height = valle_II + 0.02
            points.append([valle_II_lat + 0.08 * width_II, base_height])
        
        # ========== ONDA III: PICO DEFINIDO → VALLE ==========
        if 'III' in latencies:
            lat_III = latencies['III']['lat']
            amp_III = amplitudes['III']['amp']
            width_III = amplitudes['III'].get('width', 1.0)
            
            # Ascenso directo
            points.append([lat_III - 0.12 * width_III, base_height])
            
            # Pico
            peak_III = base_height + amp_III
            points.append([lat_III, peak_III])
            points.append([lat_III + 0.08 * width_III, peak_III * 0.98])
            
            # DESCENSO IMPORTANTE
            points.append([lat_III + 0.20 * width_III, peak_III - amp_III * 0.6])
            
            valle_III_lat = lat_III + 0.35 * width_III
            valle_III = peak_III - amp_III * 1.40
            points.append([valle_III_lat, valle_III])
            
            base_height = valle_III + 0.03
            points.append([valle_III_lat + 0.10 * width_III, base_height])
        
        # ========== COMPLEJO IV-V: VALLE COMPARTIDO ==========
        if 'IV' in latencies and 'V' in latencies:
            lat_IV = latencies['IV']['lat']
            lat_V = latencies['V']['lat']
            amp_V = amplitudes['V']['amp']
            width_V = amplitudes['V'].get('width', 1.0)
            
            amp_IV = amp_V * 0.25  # IV más pequeña (~25% de V)
            
            # Ascenso directo a IV
            points.append([lat_IV - 0.08, base_height])
            
            # Pico IV pequeño y bajo
            peak_IV = base_height + amp_IV
            points.append([lat_IV, peak_IV])
            
            # VALLE COMPARTIDO: estrecho y pronunciado tipo "V"
            # Punto medio entre IV y V
            valle_compartido_lat = (lat_IV + lat_V) / 2
            valle_compartido = peak_IV - amp_IV * 1.2  # Valle estrecho
            points.append([valle_compartido_lat, valle_compartido])
            
            # ASCENSO A V: directo y rápido desde el valle
            peak_V = valle_compartido + amp_V
            points.append([lat_V, peak_V])
            points.append([lat_V + 0.15 * width_V, peak_V])
            
            # DESCENSO DE V: profundo
            points.append([lat_V + 0.30 * width_V, peak_V - amp_V * 0.5])
            points.append([lat_V + 0.45 * width_V, peak_V - amp_V * 0.8])
            
            valle_V_lat = lat_V + 0.60 * width_V
            valle_V = peak_V - amp_V * 1.60  # Valle profundo
            points.append([valle_V_lat, valle_V])
            
            base_height = valle_V + 0.05
            points.append([valle_V_lat + 0.15 * width_V, base_height])
        
        # Si solo existe V
        elif 'V' in latencies:
            lat_V = latencies['V']['lat']
            amp_V = amplitudes['V']['amp']
            width_V = amplitudes['V'].get('width', 1.0)
            
            points.append([lat_V - 0.12 * width_V, base_height])
            
            peak_V = base_height + amp_V
            points.append([lat_V, peak_V])
            points.append([lat_V + 0.15 * width_V, peak_V])
            
            points.append([lat_V + 0.35 * width_V, peak_V - amp_V * 0.6])
            
            valle_V_lat = lat_V + 0.55 * width_V
            valle_V = peak_V - amp_V * 1.60
            points.append([valle_V_lat, valle_V])
            
            base_height = valle_V + 0.05
            points.append([valle_V_lat + 0.15 * width_V, base_height])
        
        # Si solo existe IV
        elif 'IV' in latencies:
            lat_IV = latencies['IV']['lat']
            amp_IV = amplitudes['IV']['amp']
            width_IV = amplitudes['IV'].get('width', 1.0)
            
            points.append([lat_IV - 0.10 * width_IV, base_height])
            
            peak_IV = base_height + amp_IV
            points.append([lat_IV, peak_IV])
            
            valle_IV_lat = lat_IV + 0.25 * width_IV
            valle_IV = peak_IV - amp_IV * 1.30
            points.append([valle_IV_lat, valle_IV])
            
            base_height = valle_IV + 0.03
            points.append([valle_IV_lat + 0.10 * width_IV, base_height])
        
        # Ondas tardías suaves
        if 'V' in latencies:
            v_lat = latencies['V']['lat']
            v_amp = amplitudes['V']['amp']
            v_width = amplitudes['V'].get('width', 1.0)
            
            points.append([v_lat + 1.5 * v_width, base_height + v_amp * 0.30])
            points.append([v_lat + 2.0 * v_width, base_height + v_amp * 0.15])
            points.append([v_lat + 2.8 * v_width, base_height + v_amp * 0.20])
        
        points.append([12, base_height])
        
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
        USA generar_caos_inicial escalado según FSP
        
        Args:
            x, y: señal
            fsp_actual: FSP calculado
            impedance: impedancia de electrodos
            
        Returns:
            x, y_noisy
        """
        # Generar ruido base usando caos inicial (realista)
        noise_base = self.generar_caos_inicial(x, fsp_actual)
        
        # Escalar ruido según impedancia
        if impedance < 3:
            impedance_factor = 0.5
        elif impedance < 5:
            impedance_factor = 1.0
        else:
            impedance_factor = 1.5
        
        # Escalar ruido según FSP (más FSP = menos ruido)
        if fsp_actual < 1.0:
            fsp_factor = 2.5
        elif fsp_actual < 1.5:
            fsp_factor = 1.8
        elif fsp_actual < 2.0:
            fsp_factor = 1.3
        elif fsp_actual < 2.5:
            fsp_factor = 0.9
        elif fsp_actual < 3.0:
            fsp_factor = 0.6
        else:
            fsp_factor = 0.4
        
        # Aplicar escalado
        noise_scaled = noise_base * fsp_factor * impedance_factor
        
        # Añadir a la señal
        y_noisy = y + noise_scaled
        
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
        
        MODIFICADO: 
        - Accede a fsp_puntos desde case_config
        - Elimina lógica de "no hay ondas visibles"
        - Siempre genera curva objetivo + ruido
        
        Args:
            case_config: dict con 'desviaciones' y 'fsp_puntos' del caso
            
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
        
        # 4. Obtener FSP del caso (antes de calcular parámetros)
        if case_config and 'fsp_puntos' in case_config:
            fsp_800 = case_config['fsp_puntos']['800']
            fsp_2000 = case_config['fsp_puntos']['2000']
        else:
            fsp_800 = 2.3
            fsp_2000 = 2.8
        
        # 5. Calcular FSP actual
        fsp_actual = self.calcular_fsp(stimulus_config['current_avg'], fsp_800, fsp_2000)
        
        # 6. Calcular parámetros de ondas (con desviaciones)
        values, waves_visible = self.calculate_wave_parameters(
            baseline, 
            stimulus_config['int'], 
            threshold, 
            pathology,
            desviaciones
        )
        
        # 7. Aplicar efectos de polaridad y rate
        values, CM_value = self.apply_polarity_effects(values, stimulus_config['pol'])
        values = self.apply_rate_effects(values, stimulus_config['rate'], pathology)
        
        # 8. Crear curva objetivo (SIEMPRE, incluso con ondas muy pequeñas)
        latencies = {k: {'lat': v['lat']} for k, v in values.items()}
        amplitudes = {k: {'amp': v['amp']} for k, v in values.items()}
        
        control_points = self.create_wave_points(latencies, amplitudes, waves_visible, CM_value)
        x, y_objetivo = self.generate_bezier_curve(control_points, n_samples=20)
        
        # 9. Generar caos inicial con FSP
        y_caos = self.generar_caos_inicial(x, fsp_actual)
        
        # 10. Interpolar entre caos y objetivo
        y_transitoria = self.interpolar_curva(
            y_caos, 
            y_objetivo, 
            stimulus_config['current_avg'],
            fsp_800,
            fsp_2000,
            stimulus_config['average']
        )
        
        # 11. Escalar amplitud progresivamente
        y_escalada = self.escalar_amplitud_progresiva(
            y_transitoria,
            stimulus_config['current_avg'],
            stimulus_config['average']
        )
        
        # 12. Aplicar filtros
        y_filtered = self.apply_filters(
            x, y_escalada,
            stimulus_config['filter_down'],
            stimulus_config['filter_passhigh']
        )
        
        # 13. Añadir ruido según FSP
        x, y_noisy = self.add_noise_by_fsp(
            x, y_filtered,
            fsp_actual,
            technical_config['impedance']
        )
        
        # 14. Añadir artefacto electromagnético
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