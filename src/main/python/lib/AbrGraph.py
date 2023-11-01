import contextlib
import inspect

import numpy as np
import pyqtgraph as pg
from lib.helpers import Storage
from lib.WidgetsMods import (GraphicsLayoutWidgetMod, InfiniteLineMod,
                             TextItemMod)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget


class AbrGraph(GraphicsLayoutWidgetMod):
    data_info = Signal(dict)
    del_curve = Signal(str)
    change_value_mark = Signal(dict)

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
        self.current_lat = 0

    def configure_pyqtgraph(self):
        color_background = pg.mkColor(255, 255, 255, 255)
        self.color_pen = pg.mkColor(0, 0, 0, 255)
        self.setBackground(color_background)
    
    def setup_ui_elements(self):
        """Set up UI elements for the graph"""
        self.pw = self.addPlot(row=0,col=1)
        self.pw.setRange(yRange=(-3, 3), xRange=(0, 13), disableAutoRange=True)
        self.grid = pg.GridItem(textPen='white')
        self.pw.addItem(self.grid)
        self.grid.setTickSpacing(x=[1.0], y=[1.0])
        self.pw.setMouseEnabled(x=False, y=False)
        self.pw.setMenuEnabled(False)
        self.pw.hideButtons()
        ay = self.pw.getAxis('left')
        ay.setStyle(showValues=False)

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

    def create_line(self, data):
        for name, values in data.items():
            if name in self.data: #si la curva ya existe solo se actualiza el grafico correspondiente
                self.update_data(name, values)
                self.update_graph(name,values)

            else: #si la curva no existe se crea en self.data y se crea el label que lo acompaña
                self.act_curve = name
                self.data[name] = values
                self.marks[name] = {}
                y = values['ipsi_xy'][1] + values['gap']
                self.pw.plot(x=values['ipsi_xy'][0],y=y, pen=self.active_color ,name=name)
                label = self.create_label(name, name, 1.8)
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
            self.del_curve.emit(self.act_curve)
            self.act_curve = None

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
                    lbl = self.label_html(self.act_curve, fill)
                    item.setHtml(lbl)
                else:
                    if item.tipo == 'label':
                        fill = self.inactive_fill_color
                        lbl = self.label_html(item.name, fill)
                        item.setHtml(lbl)

    def get_amplitude(self):
        if self.act_curve:
            x = self.data[self.act_curve]['ipsi_xy'][0]
            y = self.data[self.act_curve]['ipsi_xy'][1]
            lat_a = self.inf_a.getXPos()
            if lat_a > 12:
                pos_b = self.inf_b.getXPos()
                self.inf_a.setPos(12,0)
                self.inf_b.setPos(pos_b,0)
            if lat_a < 0:
                pos_b = self.inf_b.getXPos
                self.inf_a.setPos(0,0)
                self.inf_b.setPos(pos_b,0)()
            lat_b = self.inf_b.getXPos()
            if lat_b > 12:
                pos_a = self.inf_a.getXPos()
                self.inf_a.setPos(pos_a,0)
                self.inf_b.setPos(12,0)
            if lat_b < 0:
                pos_a = self.inf_a.getXPos()
                self.inf_a.setPos(pos_a,0)
                self.inf_b.setPos(0,0)
            amp_a = self.find_nearest(x, lat_a, y)
            amp_b = self.find_nearest(x, lat_b, y)
            order_amp = np.sort(np.array([amp_a,amp_b]))
            order_lat = np.sort(np.array([lat_a,lat_b]))
            dif_amp = order_amp[1] - order_amp[0]
            dif_lat = order_lat[1] - order_lat[0]
            response = {'curve':self.act_curve, 
                        'data':{"side": self.side, "lat_A": lat_a, 
                                "lat_B": lat_b, "amp_AB": dif_amp, 
                                "lat_AB": dif_lat}}
            self.data_info.emit(response)
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
                    self.update_value_mark(mark) # este no es necesario
      
               
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
        self.change_value_mark.emit(result)



    ###############HELPERS
    def set_windows(self, ms:int) -> None:
        self.pw.setXRange(ms)

    def _scale(self, direction):
        Yrange = self.pw.getViewBox().state["targetRange"][1][1]
        new_range = Yrange * 2 if direction == 'plus' else Yrange / 2
        self.pw.setYRange(-new_range,new_range)
        
    def find_nearest(self, array_in, value, array_out):
        array = np.asarray(array_in)
        idx = (np.abs(array - value)).argmin()
        return array_out[idx]

    def find_idx(self, array_in, value):
        array = np.asarray(array_in)
        return (np.abs(array - value)).argmin()





#########################
    def refresh_keys(self):
        for k in self.data:
            curve = k
            if self.data[curve]['view']:
                for i in range(2):
                    for d , val in enumerate(self.marks[curve][i].data):
                        if val is not None:
                            self.create_marks(i,d,curveName=curve, useAct=False)



    def remove_if_exist_mark(self, idx, subidx):
        mark = self.marks[self.act_curve][idx].get_all()
        mark = mark[subidx]
        if mark is None:
            return False
        self.marks[self.act_curve][idx].set(subidx, None)
        return True
    
    def update_data_marks(self):
        def idx2number(list_idx):
            input_list = list_idx.get_all()
            data = [0,0,0,0,0]
            for i, pos in enumerate(input_list):
                data[i] = self.data[self.act_curve]['ipsi_xy'][0][pos] if pos is not None else 0
            return data
        
        if self.act_curve is not None:
            non_prima = idx2number(self.marks[self.act_curve][0])
            prima = idx2number(self.marks[self.act_curve][1])
            data_emit = {'action':'latency_flag_update', 
                                'data': {'side':self.side, 'non_prima':non_prima,
                                        'prima': prima, 'curve':self.act_curve}}
            self.data_info.emit(data_emit)
                    
    def save_image(self):
        exporter = pg.exporters.ImageExporter(self.pw)
        exporter.parameters()['width'] = 800
        file = context.get_resource(f'image_{self.side}.png')
        exporter.export(file)


class LatencyIntencity():
    def __init__(self) -> None:
        pass