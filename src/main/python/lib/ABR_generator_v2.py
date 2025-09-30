"""
ABR Generator V3 - Progressive SNR Improvement
Genera curvas ABR con mejora progresiva de SNR según promediaciones
La curva INICIA ruidosa y MEJORA gradualmente
"""

import json
import random
import numpy as np
import scipy.signal as signal
from base import context


class ABRGenerator:
    """
    Generador de curvas ABR con SNR progresivo
    """
    
    def __init__(self, normative_data_path=None):
        if normative_data_path is None:
            normative_data_path = context.get_resource('json/normative_data.json')
        
        with open(normative_data_path, 'r', encoding='utf-8') as f:
            self.norms = json.load(f)
    
    def get_baseline_values(self, population='adult_female', stimulus='click', pathway='air_conduction'):
        """Obtiene valores normativos base a 80dB"""
        pop_data = self.norms['populations'][population]
        
        if stimulus.startswith('tone_burst'):
            stim_data = pop_data[pathway]['tone_burst']
        else:
            stim_data = pop_data[pathway].get(stimulus, pop_data[pathway]['click'])
        
        return stim_data
    
    def calculate_wave_parameters(self, baseline, intensity, threshold, pathology):
        """
        Calcula latencias y amplitudes según intensidad
        
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
                threshold_wave = threshold + {'I': 35, 'II': 25, 'III': 30, 'IV': 15, 'V': 10}[wave]
            else:
                threshold_wave = threshold + {'I': 25, 'II': 20, 'III': 15, 'IV': 10, 'V': 5}[wave]
            
            waves_visible[wave] = intensity >= threshold_wave
            
            if waves_visible[wave]:
                lat_shift = lat_shift_per_10dB * steps_from_80
                decay_rate = amp_decay_rates.get(wave, 0.08)
                amp_factor = max(1 - (decay_rate * abs(steps_from_80)), 0.1)
                
                modified[wave] = {
                    'lat': baseline[wave]['lat'] + lat_shift,
                    'amp': baseline[wave]['amp'] * amp_factor
                }
        
        return modified, waves_visible
    
    def apply_polarity_effects(self, values, polarity):
        """Aplica efectos de polaridad"""
        pol_adjustments = {
            'Rarefacción': {'lat': -0.1, 'amp': 1.05, 'CM': -0.2},
            'Condensación': {'lat': 0.1, 'amp': 1.0, 'CM': 0.2},
            'Alternada': {'lat': 0, 'amp': 1.0, 'CM': 0}
        }
        
        pol_mods = pol_adjustments.get(polarity, pol_adjustments['Alternada'])
        
        modified = {}
        for wave in values:
            modified[wave] = {
                'lat': values[wave]['lat'] + pol_mods['lat'],
                'amp': values[wave]['amp'] * pol_mods['amp']
            }
        
        return modified, pol_mods['CM']
    
    def apply_rate_effects(self, values, rate, pathology):
        """Aplica efectos de tasa de estimulación"""
        if rate < 20:
            lat_adj, amp_factor = -0.1, 1.1
        elif rate <= 40:
            lat_adj, amp_factor = 0, 1.0
        else:
            lat_adj, amp_factor = 0.3, 0.8
        
        # Neural muy sensible a rate alto
        if pathology == 'neural' and rate > 30:
            lat_adj *= 2.0
            amp_factor *= 0.6
        
        modified = {}
        for wave in values:
            # I y III más afectadas por rate alto
            wave_lat_adj = lat_adj * (1.5 if rate > 40 and wave in ['I', 'III'] else 1.0)
            wave_amp_factor = amp_factor * (0.8 if rate > 40 and wave in ['I', 'III'] else 1.0)
            
            modified[wave] = {
                'lat': values[wave]['lat'] + wave_lat_adj,
                'amp': values[wave]['amp'] * wave_amp_factor
            }
        
        return modified
    
    def create_wave_points(self, latencies, amplitudes, waves_visible, CM_value=None, gap=0):
        """
        Crea puntos de control para Bézier
        """
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
                # Onda no visible
                lat = latencies[wave]['lat']
                points.append([lat, gap])
                points.append([lat + 0.2, gap])
            else:
                # Onda visible
                lat = latencies[wave]['lat']
                amp = amplitudes[wave]['amp'] + gap
                
                # Pico
                points.append([lat, amp])
                
                # Valle
                valle_lat = lat + 0.35
                valle_amp = -amp * 0.4 + gap
                points.append([valle_lat, valle_amp])
        
        # Ondas tardías VI y VII (simplificadas)
        if 'V' in latencies and waves_visible.get('V', False):
            v_lat = latencies['V']['lat']
            v_amp = amplitudes['V']['amp']
            
            points.append([v_lat + 1.6, v_amp * 0.5 + gap])
            points.append([v_lat + 2.2, v_amp * 0.3 + gap])
            points.append([v_lat + 2.8, v_amp * 0.4 + gap])
            points.append([v_lat + 3.2, v_amp * 0.2 + gap])
        
        # Punto final
        points.append([12, gap])
        
        return np.array(points)
    
    def generate_bezier_curve(self, control_points, n_samples=20):
        """Genera curva Bézier suave"""
        from lib.bezier_prop import Bezier
        
        bezier = Bezier()
        path = bezier.evaluate_bezier(control_points, n_samples)
        
        return path[:, 0], path[:, 1]
    
    def calculate_fsp_and_noise(self, signal_amplitude, current_avg, target_avg, impedance=3.0, fsp_threshold=3.1):
        """
        Calcula FSP (Fidelity of Single Point) y nivel de ruido resultante
        
        FSP = Amplitud de Señal / Ruido Residual
        - FSP > 3.1 = Detección con 99% confianza (señal claramente visible)
        - FSP 2.0-3.1 = Señal detectable pero ruidosa
        - FSP < 2.0 = Señal dudosa, dominada por ruido
        
        Args:
            signal_amplitude: amplitud promedio de la señal (estimada)
            current_avg: promediaciones actuales
            target_avg: promediaciones objetivo
            impedance: impedancia electrodos
            fsp_threshold: umbral de FSP deseado (default 3.1)
        
        Returns:
            noise_level, fsp_current
        """
        # Estimar amplitud típica de señal ABR (onda V)
        # En condiciones normales, onda V tiene ~0.5 µV
        typical_signal_amplitude = 0.50
        
        # Ruido base EEG (sin promediaciones)
        # Depende de impedancia de electrodos
        if impedance < 3:
            base_eeg_noise = 0.15  # µV
        elif impedance < 5:
            base_eeg_noise = 0.25  # µV
        else:
            base_eeg_noise = 0.40  # µV
        
        # El ruido disminuye con √N promediaciones
        # Esta es la fórmula fundamental del SNR
        if current_avg > 0:
            noise_reduction_factor = np.sqrt(current_avg)
            current_noise = base_eeg_noise / noise_reduction_factor
        else:
            current_noise = base_eeg_noise * 3  # Sin promediaciones: ruido extremo
        
        # Calcular FSP actual
        if current_noise > 0:
            fsp_current = typical_signal_amplitude / current_noise
        else:
            fsp_current = 100  # Perfecto (teórico)
        
        # AJUSTE CRÍTICO: Si FSP es bajo, aumentar ruido para que sea más realista
        # Con pocas promediaciones, el ruido debe DOMINAR
        if fsp_current < 1.0:
            # FSP < 1: señal invisible, solo ruido
            noise_multiplier = 3.0
        elif fsp_current < 2.0:
            # FSP 1-2: señal apenas emergiendo
            noise_multiplier = 2.0
        elif fsp_current < 3.1:
            # FSP 2-3.1: señal visible pero ruidosa
            noise_multiplier = 1.5
        else:
            # FSP > 3.1: buena detección
            noise_multiplier = 1.0
        
        final_noise = current_noise * noise_multiplier
        
        # Añadir componente adicional si no alcanzamos objetivo
        completion_ratio = current_avg / max(target_avg, 1)
        if completion_ratio < 0.25:
            final_noise *= 2.0
        elif completion_ratio < 0.5:
            final_noise *= 1.5
        elif completion_ratio < 0.75:
            final_noise *= 1.2
        
        return final_noise, fsp_current
        """
        Calcula nivel de ruido según promediaciones actuales
        
        CRÍTICO: Al inicio el ruido debe DOMINAR completamente la señal
        
        Args:
            current_avg: promediaciones acumuladas hasta ahora
            target_avg: promediaciones objetivo finales
            impedance: impedancia de electrodos
        
        Returns:
            noise_level (float)
        """
        # Ruido base según impedancia (aumentado sustancialmente)
        if impedance < 3:
            base_noise = 0.25  # Era 0.08, ahora 3x más
        elif impedance < 5:
            base_noise = 0.40  # Era 0.15
        else:
            base_noise = 0.60  # Era 0.25
        
        # SNR mejora con raíz cuadrada del número de promediaciones
        # CRÍTICO: El ruido debe ser EXTREMO al inicio
        if current_avg < 10:
            # Casi sin promediaciones: ruido MASIVO (10x)
            snr_factor = 15.0
        elif current_avg < 50:
            # Muy pocas promediaciones: ruido extremo (8x)
            snr_factor = 10.0
        elif current_avg < 100:
            # Pocas promediaciones: ruido muy alto (6x)
            snr_factor = 7.0
        elif current_avg < 200:
            # Ruido alto (4x)
            snr_factor = 5.0
        elif current_avg < 400:
            # Ruido moderado-alto (3x)
            snr_factor = 3.5
        elif current_avg < 600:
            # Ruido moderado (2.5x)
            snr_factor = 2.5
        elif current_avg < 800:
            # Ruido moderado-bajo (2x)
            snr_factor = 2.0
        elif current_avg < 1200:
            # Ruido bajo (1.5x)
            snr_factor = 1.5
        elif current_avg < 1600:
            # Ruido bajo (1.2x)
            snr_factor = 1.2
        elif current_avg < 2000:
            # Muy poco ruido
            snr_factor = 0.8
        else:
            # Ruido mínimo
            snr_factor = 0.5
        
        # Aplicar mejora por SNR (pero muy limitada al inicio)
        if current_avg > 20:
            snr_improvement = np.sqrt(current_avg / 100)  # Normalizado
            snr_improvement = min(snr_improvement, 6.0)  # Limitar mejora máxima
        else:
            snr_improvement = 0.15  # Casi nada al inicio
        
        # Ruido final
        noise_level = (base_noise * snr_factor) / max(snr_improvement, 0.15)
        
        # Ruido adicional por no alcanzar objetivo (más agresivo)
        completion_ratio = current_avg / max(target_avg, 1)
        if completion_ratio < 0.05:
            noise_level *= 3.0  # Menos del 5%: triplicar ruido
        elif completion_ratio < 0.25:
            noise_level *= 2.2  # Menos del 25%: duplicar+
        elif completion_ratio < 0.5:
            noise_level *= 1.6  # Menos del 50%
        elif completion_ratio < 0.75:
            noise_level *= 1.2  # Menos del 75%
        
        return noise_level
    
    def add_noise_and_artifacts(self, x, y, current_avg, target_avg, impedance=3.0, fsp_threshold=3.1):
        """
        Añade ruido realista basado en FSP que DISMINUYE con las promediaciones
        
        CRÍTICO: Usa cálculo FSP para determinar ruido
        """
        # Calcular nivel de ruido basado en FSP
        noise_level, fsp_current = self.calculate_fsp_and_noise(
            signal_amplitude=0.5,  # Amplitud típica onda V
            current_avg=current_avg,
            target_avg=target_avg,
            impedance=impedance,
            fsp_threshold=fsp_threshold
        )
        
        # Debug FSP
        if current_avg % 500 < 150 or current_avg < 100:  # Imprimir cada ~500 prom
            print(f"DEBUG FSP: current_avg={current_avg:.0f}, FSP={fsp_current:.2f}, noise_level={noise_level:.4f}")
        
        # Ruido gaussiano blanco (componente principal)
        noise_white = np.random.normal(0, noise_level, y.shape)
        
        # Ruido de baja frecuencia (drift de línea base)
        time = np.linspace(0, 12, len(y))
        drift = noise_level * 0.3 * np.sin(2 * np.pi * 0.5 * time)
        
        # Ruido de alta frecuencia (actividad muscular/EMG)
        noise_hf = np.random.normal(0, noise_level * 0.4, y.shape)
        # Filtrar HF para simular EMG (>100Hz)
        b_hf, a_hf = signal.butter(2, 0.3, btype='high')
        noise_hf_filtered = signal.filtfilt(b_hf, a_hf, noise_hf)
        
        # Componente de 50/60Hz (interferencia eléctrica) - solo si FSP bajo
        if fsp_current < 2.0:
            power_line = noise_level * 0.2 * np.sin(2 * np.pi * 50 * time)
        else:
            power_line = 0
        
        # Combinar todos los ruidos
        total_noise = noise_white + drift + noise_hf_filtered + power_line
        
        # Señal final
        y_noisy = y + total_noise
        
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
        
        # Crear artefacto exponencial decreciente
        artifact_mask = x < duration
        artifact = np.where(artifact_mask, amplitude * np.exp(-x * 4), 0)
        
        return x, y + artifact
    
    def apply_filters(self, x, y, filter_low, filter_high, fs=20000):
        """Aplica filtros digitales"""
        nyquist = fs / 2
        
        # Filtro pasa bajo
        low_norm = min(filter_low / nyquist, 0.99)
        b_low, a_low = signal.butter(4, low_norm, btype='low')
        y_filtered = signal.filtfilt(b_low, a_low, y)
        
        # Filtro pasa alto
        high_norm = max(filter_high / nyquist, 0.01)
        b_high, a_high = signal.butter(4, high_norm, btype='high')
        y_filtered = signal.filtfilt(b_high, a_high, y_filtered)
        
        return y_filtered
    
    def generate_curve(self, population, pathology, stimulus_config, technical_config):
        """
        Genera curva ABR completa
        
        Returns:
            (x, y, metadata)
        """
        # 1. Obtener valores base
        baseline = self.get_baseline_values(population, stimulus_config['stim'])
        
        # 2. Obtener umbral
        threshold = self.norms['pathology_modifiers'][pathology]['threshold_range'][0]
        
        # 3. Calcular parámetros de ondas según intensidad
        values, waves_visible = self.calculate_wave_parameters(
            baseline, 
            stimulus_config['int'], 
            threshold, 
            pathology
        )
        
        # Si no hay ondas visibles, retornar solo ruido
        if not any(waves_visible.values()):
            x = np.linspace(0, 12, 240)
            y = np.zeros_like(x)
            x, y = self.add_noise_and_artifacts(
                x, y, 
                stimulus_config['current_avg'],
                stimulus_config['average'],
                technical_config['impedance']
            )
            return x, y, {'waves_visible': waves_visible}
        
        # 4. Aplicar efectos de polaridad
        values, CM_value = self.apply_polarity_effects(values, stimulus_config['pol'])
        
        # 5. Aplicar efectos de rate
        values = self.apply_rate_effects(values, stimulus_config['rate'], pathology)
        
        # 6. Crear puntos de onda
        latencies = {k: {'lat': v['lat']} for k, v in values.items()}
        amplitudes = {k: {'amp': v['amp']} for k, v in values.items()}
        
        control_points = self.create_wave_points(latencies, amplitudes, waves_visible, CM_value)
        
        # 7. Generar curva Bézier
        x, y = self.generate_bezier_curve(control_points, n_samples=20)
        
        # 8. Aplicar filtros
        y = self.apply_filters(
            x, y,
            stimulus_config['filter_down'],
            stimulus_config['filter_passhigh']
        )
        
        # 9. CRÍTICO: Añadir ruido ANTES de artefacto
        # El ruido debe ser proporcional a las promediaciones actuales
        x, y = self.add_noise_and_artifacts(
            x, y,
            stimulus_config['current_avg'],
            stimulus_config['average'],
            technical_config['impedance']
        )
        
        # 10. Añadir artefacto electromagnético
        x, y = self.add_artifact(x, y, technical_config['transducer'])
        
        metadata = {
            'population': population,
            'pathology': pathology,
            'waves_visible': waves_visible,
            'current_avg': stimulus_config['current_avg'],
            'target_avg': stimulus_config['average']
        }
        
        return x, y, metadata


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
    
    IMPORTANTE: 
    - prom[0] es un contador que va de 0 a N (número de llamadas)
    - prom[1] es el objetivo de promediaciones
    - current_avg debe CRECER con cada llamada
    
    La curva INICIA muy ruidosa y MEJORA gradualmente
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
    
    # CRÍTICO: Calcular promediaciones actuales efectivas
    # prom[0] es el contador de llamadas (va de 1 a total_averages)
    # prom[1] es el número objetivo de promediaciones
    
    # Debug: imprimir valores para diagnóstico
    print(f"DEBUG ABR_Curve: prom[0]={prom[0]}, prom[1]={prom[1]}, done={done}")
    
    # SOLUCIÓN: Si done=True y prom[0]=0, usar el objetivo completo
    # Esto pasa cuando se detiene la animación
    if done and prom[0] == 0:
        current_averages = prom[1]  # Usar el objetivo como si estuviera completo
        print(f"DEBUG: done=True con prom[0]=0, usando target como current")
    elif prom[0] <= 1.0:
        # prom[0] es una fracción (0.0 a 1.0)
        current_averages = prom[0] * prom[1]
    else:
        # prom[0] es un contador absoluto
        current_averages = prom[0] * 2.5
    
    target_averages = prom[1]
    
    # CRÍTICO: Nunca superar el objetivo
    # Si ya llegamos o superamos el objetivo, mantener en el objetivo
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
        'current_avg': current_averages  # ← ESTO ES LA CLAVE
    }
    
    # Configuración técnica
    technical_config = {
        'impedance': 3.0,
        'transducer': 'insert_earphone'
    }
    
    # Generar curva con ruido proporcional a promediaciones actuales
    x, y, metadata = generator.generate_curve(
        population='adult_female',
        pathology=pathology,
        stimulus_config=stimulus_config,
        technical_config=technical_config
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