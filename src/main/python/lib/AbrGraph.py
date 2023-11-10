

import numpy as np
import pyqtgraph as pg
from base import context
from lib.smooth import smooth_curve_gaussian
from lib.WidgetsMods import (GraphicsLayoutWidgetMod, InfiniteLineMod,
                             TextItemMod)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class AbrGraph(GraphicsLayoutWidgetMod):
    sig_data_info = Signal(dict)
    sig_del_curve = Signal(str)
    sig_change_value_mark = Signal(dict)
    sig_curve_selected = Signal(str)

    def __init__(self, side):
        super().__init__()
        self.side = side
        self.configure_pyqtgraph()
        self.setup_ui_elements()
        self.colors_side()
        self.inifine_ab()
        self.act_curve = None
        self.marks = {}
        self.data = {}
        self.curve_int = {}
        self.current_lat = 0

    def configure_pyqtgraph(self):
        self.color_background = pg.mkColor(255, 255, 255, 255)
        self.color_pen = pg.mkColor(0, 0, 0, 255)
        self.setBackground(self.color_background)
    
    def setup_ui_elements(self):
        """Set up UI elements for the graph"""
        self.pw = self.addPlot(row=0,col=1)
        self.pw.setRange(yRange=(-3, 3), xRange=(0, 13), disableAutoRange=True)
        self.grid = pg.GridItem(textPen='white')
        self.pw.addItem(self.grid)
        self.grid.setTickSpacing(x=[1.0], y=[1.0])
        self.pw.setMouseEnabled(x=False, y=True)
       
        self.pw.setMenuEnabled(False)
        self.pw.hideButtons()
        ay = self.pw.getAxis('left')
        ay.setStyle(showValues=False)
        view_box = self.pw.getViewBox()
        view_box.setMouseMode(pg.ViewBox.PanMode)

    def colors_side(self):
        if self.side == 0:
            self.active_color = pg.mkColor(255, 0, 0, 255)
            self.active_fill_color = '#0EFA00'
            self.inactive_color = pg.mkColor(180, 0, 0, 255)
            self.inactive_fill_color = '#B40000'
        else:
            self.active_color = pg.mkColor(106, 154, 242, 255)
            self.active_fill_color = '#0EFA00'
            self.inactive_color = pg.mkColor(112, 142, 199, 255)
            self.inactive_fill_color = '#708EC7'
    
    def inifine_ab(self, pos_A = 0, pos_B = 12):
        #Variables internas
        pen1 = pg.mkPen('b', width=1, style=Qt.PenStyle.DashLine)
        opst = {'position':0.9, 'color': (255,255,255), 'fill': (0,0,0,255), 'movable': True}
        name_a = f"A{self.side}"
        name_b = f"B{self.side}"
        #Lineas infinitas
        self.inf_a = InfiniteLineMod(lbl='A', pos=pos_A, movable=True, angle=90, pen=pen1, labelOpts=opst, name=name_a)
        self.inf_b = InfiniteLineMod(lbl="A'", pos=pos_B, movable=True, angle=90, pen=pen1, labelOpts=opst, name=name_b)
        #Posición en X de las lineas infinitas
        self.inf_a.sigPositionChanged.connect(self.get_amplitude)
        self.inf_b.sigPositionChanged.connect(self.get_amplitude)
        #Se agregan lineas infinitas a la grafica
        self.pw.addItem(self.inf_a)
        self.pw.addItem(self.inf_b)

    def create_line(self, data, intencity):
        for name, values in data.items():
            if name in self.data: #si la curva ya existe solo se actualiza el grafico correspondiente
                self.update_data(name, values)
                self.update_graph(name,values)

            else: #si la curva no existe se crea en self.data y se crea el label que lo acompaña
                self.act_curve = name
                self.data[name] = values
                self.marks[name] = {}
                self.curve_int[name] = intencity
                y = values['ipsi_xy'][1] + values['gap']
                self.pw.plot(x=values['ipsi_xy'][0],y=y, pen=self.active_color ,name=name)
                label = self.create_label(name, intencity, 1.8)
                self.pw.addItem(label)
    
    def update_graph(self, graph_name, data):
        for item in self.pw.listDataItems():
            if item.name() == graph_name:
                y = data['ipsi_xy'][1] + self.data[graph_name]['gap']
                item.setData(x=data['ipsi_xy'][0],y=y)
                self.get_amplitude()
                break

    def update_data(self,name ,values):
        for key, val in values.items():
            if key == 'gap':
                if 'gap' in self.data[name]:
                    continue
            self.data[name][key] = val

    def drag_curve(self, value):
        gap_y = value['pos'][1]
        curve = value['name']
        self.data[curve]['gap'] = gap_y
        x = self.data[curve]['ipsi_xy'][0]
        y = self.data[curve]['ipsi_xy'][1]
        data = {'ipsi_xy': [x,y]}
        self.update_graph(curve, data)
        self.move_marks(curve)

    def label_html(self,text:str, fill:str) -> str :
        return f"""
                <div style='text-align: center; background-color: {fill};'>
                <span style='color: #000; font-size: 7pt;'>
                {text} dBnHl
                </span>
                </div>
                """
    def smooth(self, ev):
        curve = self.act_curve
        x = self.data[self.act_curve]['ipsi_xy'][0]
        y = self.data[self.act_curve]['ipsi_xy'][1]
        y = smooth_curve_gaussian(y, sigma=float(ev))
        data = {'ipsi_xy': [x,y]}
        self.update_graph(curve, data)
        self.move_marks(curve)


    def create_label(self,key, text, h):
        fill = self.active_fill_color
        lbl = self.label_html(text, fill)
        text = TextItemMod(name=key, tipo='label', curve_parent= key, html=lbl, border="w")
        text.sigDragged.connect(self.drag_curve)
        text.sigPositionChangeStarted.connect(self.active_curve)
        text.setPos(12, h)
        return text

    def delete_curve(self):
        delete = False
        for item in self.pw.listDataItems():
            if item.name() == self.act_curve:
                self.pw.removeItem(item)
                delete = True

        for item in self.pw.items[:]:
            if isinstance(item, TextItemMod) and item.curve_parent == self.act_curve:
                self.pw.removeItem(item)
                delete = True

        if delete:
            self.sig_del_curve.emit(self.act_curve)
            self.act_curve = None

    def get_active(self):
        return self.act_curve

    def active_curve(self, sender):
        self.act_curve = sender
        #se selecciona la curva
        for item in self.pw.listDataItems():
            if item.name() == self.act_curve:
                item.setPen(self.active_color)
            else:
                item.setPen(self.inactive_color)
        #se selecciona el label de la curva
        for item in self.pw.items:
            if isinstance(item, TextItemMod): 
                if item.name == self.act_curve:
                    fill = self.active_fill_color
                    lbl_name = self.curve_int[self.act_curve]
                    lbl = self.label_html(lbl_name, fill)
                    item.setHtml(lbl)
                else:
                    if item.tipo == 'label':
                        fill = self.inactive_fill_color
                        lbl_name = self.curve_int[item.name]

                        lbl = self.label_html(lbl_name, fill)
                        item.setHtml(lbl)
        self.sig_curve_selected.emit(self.act_curve)
        #se actualizan los datos de las marcas
        #print(self.marks[self.act_curve])

    def get_amplitude(self):
        # Obtener posiciones actuales de las líneas
        lat_a = self.inf_a.getXPos()
        lat_b = self.inf_b.getXPos()

        # Asegurarse de que las líneas no superen los límites de 0 y 12
        lat_a = max(0, min(12, lat_a))
        lat_b = max(0, min(12, lat_b))

        # Establecer las posiciones corregidas
        self.inf_a.setPos((lat_a, 0))
        self.inf_b.setPos((lat_b, 0))
        if self.act_curve:
            x = self.data[self.act_curve]['ipsi_xy'][0]
            y = self.data[self.act_curve]['ipsi_xy'][1]

            # Encontrar los valores de amplitud más cercanos a las posiciones lat_a y lat_b
            amp_a = self.find_nearest(x, lat_a, y)
            amp_b = self.find_nearest(x, lat_b, y)

            # Ordenar las amplitudes y latencias
            order_amp = np.sort([amp_a, amp_b])
            order_lat = np.sort([lat_a, lat_b])

            # Calcular la diferencia de amplitud y latencia
            dif_amp = order_amp[1] - order_amp[0]
            dif_lat = order_lat[1] - order_lat[0]

            # Preparar la respuesta
            response = {
                'curve': self.act_curve,
                'data': {
                    "side": self.side,
                    "lat_A": lat_a,
                    "lat_B": lat_b,
                    "amp_AB": dif_amp,
                    "lat_AB": dif_lat
                }
            }

            # Emitir la información calculada
            self.sig_data_info.emit(response)
            # Actualizar la latencia actual
            self.current_lat = lat_a

    def create_marks(self, lbl_mark):
        name_curve = self.act_curve
        lbl = lbl_mark
        id_X = self.find_idx(self.data[name_curve]['ipsi_xy'][0], self.current_lat)
        x = self.data[name_curve]['ipsi_xy'][0][id_X]
        y = self.data[name_curve]['ipsi_xy'][1][id_X]
        name = f'{name_curve}_{lbl}'
        if lbl not in self.marks[name_curve]:
            self.marks[name_curve][lbl] = [x,y]
            y = y + self.data[name_curve]['gap']
            curve_mark = f"<h3>&darr;<sup>{lbl}</sup></h3>"
            text = TextItemMod(name = name, tipo='mark', curve_parent=name_curve, html = curve_mark,  anchor=(0.34,0.6), color=(0,0,0,255))
            font = QFont()
            font.setPixelSize(13)
            text.setFont(font)
            text.setPos(x, y+0.1)
            self.pw.addItem(text)
        else:
            self.update_marks(x,y, name)

    def update_marks(self,x , y, name):
        name_curve,mark = name.split('_')
        self.marks[name_curve][mark][0] = x
        self.marks[name_curve][mark][1] = y
        y = y + self.data[name_curve]['gap']
        for item in self.pw.items:                
            if isinstance(item, TextItemMod): 
                if item.name == name and item.tipo == 'mark':
                    item.setPos(x,y)
                    self.update_value_mark(mark) 
      
    def move_marks(self, name_curve):
        for mark in self.marks[name_curve]:
            x, y = self.marks[name_curve][mark]
            name_mark = f'{name_curve}_{mark}'
            self.update_marks(x,y,name_mark)
        
    def delete_mark(self, sender):
        _,mark = sender.split(' ')
        name_mark = f'{self.act_curve}_{mark}'
        for item in self.pw.items[:]:  
            if isinstance(item, TextItemMod) and item.tipo == 'mark' and item.name == name_mark:
                self.pw.removeItem(item)
                self.update_value_mark(mark, True)

    def delete_all_marks(self):
        for item in self.pw.items[:]:  
            if isinstance(item, TextItemMod) and item.tipo == 'mark':
                self.pw.removeItem(item)
                _,mark = item.name.split('_')
                self.update_value_mark(mark, True)

    def update_value_mark(self, mark, delete = False):
        curve = self.act_curve
        if not delete:
            x = self.marks[curve][mark]
        else:
            del self.marks[curve][mark]
            x = None
        result = {curve:{mark:x}}
        self.sig_change_value_mark.emit(result)



    ###############HELPERS
    def set_windows(self, ms:int) -> None:
        self.pw.setXRange(ms)

    def scale(self, direction):
        current_scale = self.get_scale()
        if direction == 'plus':
            new_scale = min(current_scale * 2, 200)
        elif direction == 'minus':
            new_scale = max(current_scale / 2, 1)   
        else:
            new_scale = current_scale
        if new_scale != current_scale:
            self.pw.setYRange(-new_scale / 2, new_scale / 2, padding=0) 
        return self.get_scale()
       
    def get_scale(self):
        yAxis = self.pw.getAxis('left')
        yRange = yAxis.range
        yTicks = yAxis.tickValues(*yRange, size=1)
        scale = abs(yRange[0] - yRange[1])
        return scale
        
    def find_nearest(self, array_in, value, array_out):
        array = np.asarray(array_in)
        idx = (np.abs(array - value)).argmin()
        return array_out[idx]

    def find_idx(self, array_in, value):
        array = np.asarray(array_in)
        return (np.abs(array - value)).argmin()

    def export_(self):
        self.inf_a.hide()
        self.inf_b.hide()
        width = self.pw.size().width()
        height = self.pw.size().height()
        options = {'width':width, 'height':height, 'background': self.color_background}
        #export = generateSvg(self.pw, options=options)
        export = pg.exporters.ImageExporter(self.pw)
        export.export(context.get_resource(f'temp/{self.side}.png'))

        self.inf_a.show()
        self.inf_b.show()
       

