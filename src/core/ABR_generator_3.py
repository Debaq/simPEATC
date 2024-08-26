import xml.etree.ElementTree as ET
import re
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from scipy.interpolate import UnivariateSpline
import numpy as np
from scipy.interpolate import interp1d

class SVGPathToMatplotlib:

    def __init__(self, data):
        if isinstance(data, str):  # Si se proporciona un SVG en formato de cadena
            self.svg_data = data
            self.path_string = self._extract_path_string()
            self.coordinates = self._parse_path()
        elif isinstance(data, list):  # Si se proporciona una lista de puntos
            self.coordinates = [(data[i], data[i + 1]) for i in range(len(data) - 1)]
        else:
            raise ValueError("Unsupported data format")

    def _extract_path_string(self):
        tree = ET.ElementTree(ET.fromstring(self.svg_data))
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}
        return tree.find(".//svg:path", namespaces).get("d")

    def _parse_path(self):
        commands = re.findall('[a-z]', self.path_string, re.I)
        coordinates = [list(map(float, coord.split(','))) for coord in re.findall('(-?\d+\.?\d*,-?\d+\.?\d*)', self.path_string)]

        current_position = [0, 0]
        all_coordinates = []

        if commands[0].lower() == 'm':
            current_position = coordinates[0]
            coordinates = coordinates[1:]

        for coord in coordinates:
            new_position = [current_position[0] + coord[0], current_position[1] + coord[1]]
            all_coordinates.append((current_position, new_position))
            current_position = new_position

        return all_coordinates

    def _smooth_coordinates(self, s=2):
        x, y = self._dense_coordinates()

        spl = UnivariateSpline(x, y, s=s)
        xnew = np.linspace(min(x), max(x), len(x))
        ynew = spl(xnew)

        return xnew, ynew
    
    
    def _dense_coordinates(self, num_points=500, interpolation_method='linear', noise_std=0.0):
        x = []
        y = []

        for coord in self.coordinates:
            x.append(coord[0][0])
            y.append(coord[0][1])

        # Agregar la última coordenada
        x.append(self.coordinates[-1][1][0])
        y.append(self.coordinates[-1][1][1])

        if len(set(x)) != len(x):  # Si hay duplicados en x
            unique_x, indices = np.unique(x, return_index=True)
            y = np.array(y)[indices]
            x = unique_x.tolist()

        f = interp1d(x, y, kind=interpolation_method)
        xnew = np.linspace(min(x), max(x), num_points * len(x))
        ynew = f(xnew)

        # Añadir ruido gaussiano
        ynew += np.random.normal(0, noise_std, ynew.shape)

        return xnew, ynew


    def plot(self, smooth=False):
        if smooth:
            xnew, ynew = self._smooth_coordinates()
            plt.plot(xnew, ynew, 'k-')
        else:
            for line in self.coordinates:
                x = [line[0][0], line[1][0]]
                y = [line[0][1], line[1][1]]
                plt.plot(x, y, 'k-')

        plt.gca()
        plt.show()

# Uso:
svg_data = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   width="210mm"
   height="297mm"
   viewBox="0 0 210 297"
   version="1.1"
   id="svg1"
   inkscape:version="1.3 (0e150ed6c4, 2023-07-21)"
   sodipodi:docname="dibujo.svg"
   xml:space="preserve"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg"><sodipodi:namedview
     id="namedview1"
     pagecolor="#ffffff"
     bordercolor="#000000"
     borderopacity="0.25"
     inkscape:showpageshadow="2"
     inkscape:pageopacity="0.0"
     inkscape:pagecheckerboard="0"
     inkscape:deskcolor="#d1d1d1"
     inkscape:document-units="mm"
     inkscape:zoom="1.1477291"
     inkscape:cx="505.34571"
     inkscape:cy="509.2665"
     inkscape:window-width="1920"
     inkscape:window-height="1151"
     inkscape:window-x="0"
     inkscape:window-y="0"
     inkscape:window-maximized="1"
     inkscape:current-layer="layer1" /><defs
     id="defs1" /><g
     inkscape:label="Capa 1"
     inkscape:groupmode="layer"
     id="layer1"><path
       style="fill:none;stroke:#000000;stroke-width:0.1;stroke-opacity:1"
       d="m 8.7512577,123.22083 6.0283893,6.22279 10.499765,-17.25109 11.004974,25.79241points_data = [(0,0), (1,2), (2,3), (3,2), (4,5), (5,1)]
converter = SVGPathToMatplotlib(points_data)
converter.plot(smooth=True, s=2) 10.379218,-21.767 8.606025,15.1223 9.403191,-21.84734 9.479873,19.30875 14.682237,-41.272301 3.155489,8.711157 7.192791,-25.641413 20.87736,109.188957 16.66951,-52.96937 16.31321,30.51151 24.0213,-63.635224 20.60607,29.126254"
       id="path1" /></g></svg>'''  # Debes pegar tu SVG aquí
#converter = SVGPathToMatplotlib(svg_data)
#converter.plot(smooth=True)
class Curva:
    def __init__(self, ventana):
        self.inicio = [(0,0),(0,0)]
        self.I = [(1.62,0.1),(1.8,-0.2)]
        self.II = [(2.68,0.1),(3,-0.03)]
        self.III = [(3.68,0.4),(4,-0.15)]
        self.IV = [(4.68,-0.1),(5,-0.15)]
        self.V = [(5.57,0.13),(6,-0.4)]
        self.VI = [(7.29,0.13),(8,-0.4)]
        self.final = [(7,0),(12,0)]
        self.threshold = 20

    def modificar_latencia_completas(self, latencia):
        self.I = [(p[0] + latencia, p[1]) for p in self.I]
        self.II = [(p[0] + latencia, p[1]) for p in self.II]
        self.III = [(p[0] + latencia , p[1]) for p in self.III]
        self.IV = [(p[0] + latencia , p[1]) for p in self.IV]
        self.V = [(p[0] + latencia , p[1]) for p in self.V]
        self.VI = [(p[0] + latencia , p[1]) for p in self.VI]
        self.final = [(p[0] + latencia , p[1]) for p in self.final]

    def modificar_latencias_tempranas(self, latencia):
        self.I = [(p[0] + latencia, p[1]) for p in self.I]
        self.II = [(p[0] + latencia, p[1]) for p in self.II]
        if self.II[1][0] >= self.III[0][0]:
            latencia = 0.1
            self.III = [(p[0] + latencia , p[1]) for p in self.III]
            self.IV = [(p[0] + latencia , p[1]) for p in self.IV]
            self.V = [(p[0] + latencia , p[1]) for p in self.V]
            self.VI = [(p[0] + latencia , p[1]) for p in self.VI]
            self.final = [(p[0] + latencia , p[1]) for p in self.final]
            
    def modificar_latencias_tardias(self, latencia):
        self.III = [(p[0] + latencia , p[1]) for p in self.III]
        self.IV = [(p[0] + latencia , p[1]) for p in self.IV]
        self.V = [(p[0] + latencia , p[1]) for p in self.V]
        self.VI = [(p[0] + latencia , p[1]) for p in self.VI]
        self.final = [(p[0] + latencia , p[1]) for p in self.final]
        
    def modificar_amplitudes_completas(self, amplitud):
        step_to_threshold = (80 - self.threshold)/10
        amplitude_V = abs(self.V[0][1] - self.V[1][1])
        step_v_amplitude = amplitude_V / step_to_threshold
        self.I = [(p[0], p[1]) for p in self.I]
        self.II = [(p[0], p[1]) for p in self.II]
        self.III = [(p[0], p[1]) for p in self.III]
        self.IV = [(p[0], p[1]) for p in self.IV]
        self.V = [(p[0], p[1]) for p in self.V]
        self.VI = [(p[0], p[1]) for p in self.VI]
        self.final = [(p[0], p[1]) for p in self.final]
        
    def modificar_amplitud(self, curva, factor_amplitud):
        if hasattr(self, curva):
            curva_actual = getattr(self, curva)
            setattr(self, curva, [(point[0], point[1] * factor_amplitud) for point in curva_actual])
        else:
            print(f"La curva {curva} no existe.")
    
    def obtener_curva_completa(self):
        return self.inicio + self.I + self.II + self.III + self.IV + self.V + self.V + self.final

# Ejemplo de uso:
c = Curva(12)
c.modificar_latencias_tardias(3)  # Cambiar latencia de curva III. Las otras curvas también se ajustarán según los interpeaks.

print(c.obtener_curva_completa())


points_data = c.obtener_curva_completa()
converter = SVGPathToMatplotlib(points_data)
converter.plot(smooth=True)
