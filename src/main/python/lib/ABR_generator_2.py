import random
import numpy as np
import lib.bezier_prop as bz



def ABR_Curve(actual_intencity, control_setting, preferences, repro_prev):
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


    threshold = preferences["th"]
    lat_I = preferences["lat"]
    lat_III = preferences["ink"][0]+lat_I
    lat_V =  preferences["ink"][1] + lat_I
    amp = preferences["amp"]
    morfo = preferences["morfo"]
    repro = preferences["repro"]
    window = 12
    VrelI = True
    zeros = False

    none = False

  
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
    var_int_I = step_80_to_actual_int * amp_I_in_step_80_to_th #variación de intencidad onda V

    desv_lat = (var_lat * var_int_V) * direcc_lat
    desv_amp_V = (var_int_V + var_amp) * direc_amp
    #lam_V = 0 if lam_V < 0 else lam_V
    desv_amp_I = (var_int_I + var_amp) * direc_amp

###################################################################
    #Se comienza con el calculo de cada peak
    #Latencias
    
    lat_peak_I   =  lat_I + desv_lat
    lat_peak_II  =  lat_peak_I + 1 #le agre 1 ms desde la onda I
    lat_peak_III =  lat_III + desv_lat
    lat_peak_V   =  lat_V + desv_lat
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
    curve_cm = (0.6+desv_lat, 0.15)
    curve_cmp = (0.7+desv_lat, -0.05)
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
    print(curve_V)
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


            [curve_cmp[0],curve_cmp[1]],

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
    if none:
        y_noise = np.random.normal(0, .06, py.shape)
    else:
        y_noise = np.random.normal(0, .03, py.shape)
    y_new = py + y_noise

    if zeros:
        px = np.zeros(20)
        y_new = np.zeros(20)
    return  px, y_new, x, y, var_repro

#px, y_new = ABR_Curve()