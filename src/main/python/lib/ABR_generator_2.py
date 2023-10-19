import random
import numpy as np
import lib.bezier_prop as bz
import scipy.signal as signal
import math

def scale_value(value):
    # Para el intervalo [1, 800]
    if value <= 800:
        return 1 - (1 / (1 + math.exp(-0.005 * (value - 400))))
    
    # Para el intervalo [800, 1500]
    elif 800 < value <= 1500:
        base = 1 / (1 + math.exp(-0.005 * (800 - 400)))
        return base - (0.7 / (1 + math.exp(-0.005 * (value - 1150))))
    
    # Para el intervalo [1500, 2000]
    elif 1500 < value < 2000:
        base1 = 1 / (1 + math.exp(-0.005 * (800 - 400)))
        base2 = base1 - (0.7 / (1 + math.exp(-0.005 * (1500 - 1150))))
        return base2 - (0.3 / (1 + math.exp(-0.005 * (value - 1750))))
    
    # Para el intervalo [2000, 10000]
    else:
        base1 = 1 / (1 + math.exp(-0.005 * (800 - 400)))
        base2 = base1 - (0.7 / (1 + math.exp(-0.005 * (1500 - 1150))))
        base3 = base2 - (0.3 / (1 + math.exp(-0.005 * (2000 - 1750))))
        return max(base3 - (base3 / (1 + math.exp(-0.0005 * (value - 6000)))), 0)


def cubic_adjustment(value, max_value):
    # Normalizar el valor al rango [0, 1]
    normalized_value = value / max_value

    # Ajustar usando una función cúbica
    adjusted_normalized_value = normalized_value**3

    # Escalar nuevamente al rango original
    adjusted_value = adjusted_normalized_value * max_value

    return adjusted_value

def scale_difference(value, max_value):
    # Calcula la diferencia
    difference = max_value - value
    
    # Reescala la diferencia al rango deseado [0, 0.6]
    scaled_difference = (0.6 / max_value) * difference

    return scaled_difference



def ABR_Curve(actual_intencity, control_setting, preferences, repro_prev, prom):
#def ABR_Curve(none = False, nHL = 80, p_I=1.6, p_III=3.7, p_V=5.6, a_V = 0.8, VrelI = True, zeros = False):
    #n: normal
    #c: coclear
    #t: transmission
    #m: normal
    #latI80 : latencia onda I a 80
    #ink: interpeaks [1_3, 1_5, 3_5]
    #amp: amplitud [1,5]
    #repro: reproductividad
    #morfo: morfología
    #th : umbral

    #print(f"control_setting: {control_setting}")
    
    
    
    add_amp = [0,0,0,0,0]
    add_lat = [0,0,0,0,0]
    #control_setting: {'stim': 'Click', 'pol': 'Alternada', 'int': 80, 'mkg': 0, 'rate': 10.1, 'filter_down': '1000', 'filter_passhigh': '50', 'prom': 1000, 'side': 'OD'}
    if control_setting["pol"] == "Rarefac.":
        add_amp = [x + 0.2 for x in add_amp]
        add_lat[:2] = [x - 0.15 for x in add_lat[:2]]
        cm_pol = -0.5
    elif control_setting["pol"] == "Conden.":
        add_lat = [x + 0.15 for x in add_lat]
        add_amp[-1]+=0.2
        cm_pol=0.5
    else:
        cm_pol = 0
    ########################## RATE
    rate = control_setting["rate"]
    if rate > 30 and rate < 65:
        add_lat[:2] = [x +0.2 for x in add_lat[:2]]
        add_amp=[x - 0.1 for x in add_amp]
    elif rate < 15:
        add_lat = [x - 0.1 for x in add_lat]
        add_amp=[x + 0.1 for x in add_amp]
    elif rate > 65:
        add_lat[:2] = [x + 0.3 for x in add_lat[:2]]
        add_amp=[x - 0.2 for x in add_amp]
    
    ########################  
    filter_down = control_setting["filter_down"]
    filter_passhigh = control_setting["filter_passhigh"]
    
    threshold = preferences["th"]
    lat_I = preferences["lat"]
    lat_III = preferences["ink"][0]
    lat_V =  preferences["ink"][1]
    amp = preferences["amp"]
    morfo = preferences["morfo"]
    repro = preferences["repro"]
    window = 12
    VrelI = True
    zeros = False


  
    #att = 0
    step_80_to_actual_int = abs(80 - actual_intencity)/5
    # verifica si la intensidad es mayor o menor a 80, en el caso de ser mayor aumenta 
    # la amplitud y disminuye la latencia y en el caso de ser menor al revez
    if actual_intencity > 80: 
        direc_amp = 1
        direcc_lat = -1
    else:
        direc_amp = -1
        direcc_lat = 1
    # agrega una variación extra que corresponde a la desviación propia de las intensidades
    if actual_intencity >=50:
        var_lat = .3
        var_amp = .06
    else:
        var_lat = .5
        var_amp = .08
    step_for_80_to_th = (80 - threshold)/5
    amp_v_in_step_80_to_th = amp[1] / step_for_80_to_th
    amp_I_in_step_80_to_th = amp[0]*2 / step_for_80_to_th

    #calcula los valores standares que se le agregarán finalmente al las latencias y amplitudes
    var_int_V = step_80_to_actual_int * amp_v_in_step_80_to_th #variación de intencidad onda V
    var_int_I = step_80_to_actual_int * amp_I_in_step_80_to_th #variación de intencidad onda I

    desv_lat = (var_lat * var_int_V) * direcc_lat
    desv_amp_V = (var_int_V + var_amp) * direc_amp
    #lam_V = 0 if lam_V < 0 else lam_V
    desv_amp_I = (var_int_I + var_amp) * direc_amp

###################################################################
    #Se comienza con el calculo de cada peak
    #Latencias
    
    lat_peak_I   =  lat_I + desv_lat + add_lat[0]
    lat_peak_II  =  lat_peak_I + 1 #le agre 1 ms desde la onda I
    lat_peak_III =  lat_III + desv_lat + add_lat[2]
    lat_peak_V   =  lat_V + desv_lat + add_lat[4]
    lat_peak_IV  =  lat_peak_V-.5
    lat_sn10     = lat_peak_V + 1

    #ultimo dato que aparece en la curva se iguala al tamaño de la ventana + la desviación de la latencia
    end = [window + desv_lat, 0]
    
    #Reproductibilidad
    if not repro:
        if repro_prev == 0:

            var_repro = random.uniform(0.2,0.4) #????
            sig_repro = random.choice([True, False])
            var_repro = var_repro * -1 if sig_repro is False else var_repro
        else:
            var_ = random.uniform(-0.1,0.1) #????

            var_repro = (repro_prev * -1) + var_
        lat_peak_V   =  lat_peak_V + var_repro
    else:
        var_repro = 0
   

    #Amplitudes
    current_amp_I = max((amp[0] + desv_amp_I)/2,0)
    current_amp_Ip = min(-(current_amp_I/2),0)
    current_amp_II = current_amp_Ip+0.1
    current_amp_IIp = current_amp_II-.02
    current_amp_III = ((amp[0]*2)/2) + desv_amp_I
    current_amp_III = max(current_amp_III, 0)
    current_amp_IIIp = min(-(current_amp_III/2),0)

    VrefIII = (random.uniform(-.1,.3)) + current_amp_III #variación de comienzo de la onda V respecto a la onda III

    current_amp_IV = max(VrefIII-.05, 0)
    current_amp_IVp = max(current_amp_IV-.05, 0)
    current_amp_V = max(amp[1] + desv_amp_V, 0)
    current_amp_VI = max(current_amp_V-.3, 0)
    current_amp_sn10 = min(VrefIII - current_amp_V, 0)
   
    adjusted_prom = cubic_adjustment(prom[0], prom[1])
   
    d_amp_I = current_amp_I/prom[1]
    d_amp_I_p = current_amp_Ip/prom[1]
    d_amp_II = current_amp_II/prom[1]
    d_amp_IIp = current_amp_IIp/prom[1]
    d_amp_III = current_amp_III/prom[1]
    d_amp_IIIp = current_amp_IIIp/prom[1]
    d_amp_IV = current_amp_IV/prom[1]
    d_amp_IVp = current_amp_IVp/prom[1]
    d_amp_V = current_amp_V/prom[1]
    d_amp_VI = current_amp_VI/prom[1]
    d_amp_sn10 = current_amp_sn10/prom[1]
    
    current_amp_I = d_amp_I * adjusted_prom
    current_amp_Ip = d_amp_I_p * adjusted_prom
    current_amp_II = d_amp_II * adjusted_prom
    current_amp_IIp = d_amp_IIp * adjusted_prom
    current_amp_III = d_amp_III * adjusted_prom
    current_amp_IIIp = d_amp_IIIp * adjusted_prom
    current_amp_IV = d_amp_IV * adjusted_prom
    current_amp_IVp = d_amp_IVp * adjusted_prom
    current_amp_V = d_amp_V * adjusted_prom
    current_amp_VI = d_amp_VI * adjusted_prom
    current_amp_sn10 = d_amp_sn10 * adjusted_prom

    #print(f"amplitud onda V: {current_amp_V}")


    #MORFOLOGIA
    if not morfo[0]:
        current_amp_I = 0
        current_amp_Ip = 0
    
    if current_amp_Ip == 0:
        current_amp_II = 0
        current_amp_IIp=0
        
    if not morfo[1]:
        current_amp_III = 0
        current_amp_IIIp = 0

    if not morfo[2]:
        current_amp_V = current_amp_IIIp        
        current_amp_sn10 = current_amp_IIIp
        VrefIII = current_amp_IIIp
        current_amp_IV = current_amp_IIIp
        current_amp_IVp = current_amp_IIIp
        
    
    #se crean las curvas con su (latencia, amplitud)
    #MC    
    curve_cm = (lat_peak_I-0.7, 1)
    curve_cmp = (curve_cm[0]+0.1, cm_pol)
    descanso_cm = (curve_cmp[0]+0.2,0)
    #print(curve_cm)
    #ONDA I
    curve_I = (lat_peak_I,current_amp_I)
    curve_Ip = (curve_I[0]+.5,current_amp_Ip)
    #ONDA II
    curve_II = (lat_peak_II, current_amp_II)
    curve_IIp = (curve_II[0]+.3,curve_II[1]-.02)
    #ONDA III
    curve_III = (lat_peak_III,current_amp_III)
    curve_IIIp = (curve_III[0]+.9,current_amp_IIIp)
    #ONDA IV
    curve_IV = (lat_peak_IV, current_amp_IV)
    curve_IVp = (lat_peak_IV+.05, current_amp_IVp)
    #ONDA V
    curve_V = (lat_peak_V,VrefIII)
    #print(f"curva V {curve_V}")
    sn10 = (lat_sn10,current_amp_sn10)
    #ONDA VI
    curve_VI = (lat_sn10+1.5, current_amp_VI)
    curve_VIp = (curve_VI[0]+1.5, curve_VI[1]-.3)
    #ONDA VI
    curve_VII = (curve_VIp[0]+1.5, curve_VIp[1]+.6)

    if curve_VII[0] > end[0]:
        end = curve_VII

    points = np.array([
            [0,0],

            [curve_cm[0]-0.05,0],
            [curve_cmp[0],curve_cmp[1]],
            [descanso_cm[0],descanso_cm[1]],
            [curve_I[0],curve_I[1]],
            [curve_Ip[0],curve_Ip[1]],

            [curve_II[0],curve_II[1]],
            [curve_IIp[0],curve_IIp[1]],

            [curve_III[0],curve_III[1]],
            [curve_IIIp[0],curve_IIIp[1]],

            [curve_IV[0], curve_IV[1]],
            [curve_IVp[0], curve_IVp[1]],

            [curve_V[0],curve_V[1]],
            [sn10[0],sn10[1]],

            [curve_VI[0],curve_VI[1]],
            [curve_VIp[0],curve_VIp[1]],
            [curve_VII[0],curve_VII[1]],
            [end[0],end[1]]        
    ])
    
    Bezi = bz.Bezier()
    path = Bezi.evaluate_bezier(points, 20)

    # extract x & y coordinates of points
    x, y = points[:,0], points[:,1]
    px, py = path[:,0], path[:,1]

    filter_passhigh = (9 / int(filter_passhigh))+0.81
    filter_down = ((9 / int(filter_down))*100)-0.2
    if filter_down == 0.0:
        filter_down = 0.0001
        
    noise_value_prom = scale_difference(prom[0], prom[1])
    noise_prom = np.random.normal(0, noise_value_prom, py.shape)
    noise_value_prom_total= scale_value((prom[0]*100)/2)
    noise_prom_total = np.random.normal(0, noise_value_prom_total, py.shape)
    #print(noise_value_prom_total)
    
    py_noisy = np.random.normal(0, filter_down, py.shape)
    order = 4

    # Diseñar un filtro de paso bajo
    cutoff_low = filter_down
    b_low, a_low = signal.butter(order, cutoff_low, btype='low')
    py_low_filtered = signal.filtfilt(b_low, a_low, py_noisy)

    # Diseñar un filtro de paso alto
    cutoff_high = filter_passhigh
    b_high, a_high = signal.butter(order, cutoff_high, btype='high')
    py_high_filtered = signal.filtfilt(b_high, a_high, py_noisy)
    
    noise = py_low_filtered + py_high_filtered
    
    y_new = py + noise + noise_prom + noise_prom_total


    if zeros:
        px = np.zeros(20)
        y_new = np.zeros(20)
    return  px, y_new, x, y, var_repro

#px, y_new = ABR_Curve()