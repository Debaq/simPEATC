import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QFont
from lib.helpers import Storage
import contextlib
from pyqtgraph import InfiniteLine
from pyqtgraph import InfLineLabel
from pyqtgraph import TextItem


class TextItemMod(TextItem):
    sigDragged = Signal(dict)
    sigPositionChangeFinished = Signal(object)
    sigPositionChangeStarted= Signal(str)

    def __init__(self,name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moving = False
        self.name = name


    def mouseDragEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            if ev.isStart():
                self.moving = True
                self.cursorOffset = self.pos() - self.mapToParent(ev.buttonDownPos())
                self.startPosition = self.pos()
                self.pos_x = self.pos().x()
                self.sigPositionChangeStarted.emit(self.name)
            ev.accept()
            
            if not self.moving:
                return
            pos = self.cursorOffset + self.mapToParent(ev.pos())
            
            self.setPos(self.pos_x, pos.y())
            list_pos = {"pos":(self.pos_x, pos.y()),"name":self.name}
            self.sigDragged.emit(list_pos)

            if ev.isFinish():
                self.moving = False
                self.sigPositionChangeFinished.emit(self)




class InfiniteLineMod(InfiniteLine):

    def __init__(self, lbl, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #if self.label:
        #    self.label.scene().removeItem(self.label) # Esto elimina el label de la escena
        self.label = None
        
        # Crea el label modificado
        labelopt = kwargs['labelOpts']
        self.label = InfiniteLineLabelMod(self, text=lbl, **labelopt)


class InfiniteLineLabelMod(InfLineLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos_line = self.line.getPos()

    def mouseDragEvent(self, ev):
        super().mouseDragEvent(ev)
        pos = ev.pos()
        pos = self.mapToItem(self, pos)
        prev_pos = self.line.getXPos()
        new_pos = prev_pos + pos.x()/60
        self.line.setPos([new_pos,0])

        


class GraphABR(QWidget):
    data_info = Signal(dict)

    def __init__(self, side):
        super().__init__()
        self.side = side
        self.configure_pyqtgraph()
        self.setup_ui_elements()
        self.act_curve = None
        self.marks = {}
        self.inf_a = None
        self.inf_b = None
        self.data = {}

    def configure_pyqtgraph(self):
        color_backgorund = pg.mkColor(255, 255, 255, 255)
        self.color_pen = pg.mkColor(0, 0, 0, 255)
        pg.setConfigOption('background', color_backgorund)
        pg.setConfigOption('foreground', self.color_pen)
    
    def setup_ui_elements(self):
        """Set up UI elements for the graph"""
        self.win = pg.GraphicsLayoutWidget(show=True)
        self.pw1 = self.win.addPlot(row=1,col=0)
        self.win.sigMouseReleased.connect(self.on_mouse_released)

        self.pw1.setRange(yRange=(-3, 3), xRange=(0, 13), disableAutoRange=True)
        self.grid = pg.GridItem(textPen='white')
        self.pw1.addItem(self.grid)
        self.grid.setTickSpacing(x=[1.0], y=[1.0])

        self.pw1.setMouseEnabled(x=False, y=False)
        self.pw1.setMenuEnabled(False)
        self.pw1.hideButtons()
        ay = self.pw1.getAxis('left')
        ay.setStyle(showValues=False)

    def on_mouse_released(self, data):
        print(data)

    def scale(self, direction):
        Yrange = self.pw1.getViewBox().state["targetRange"][1][1]
        new_range = Yrange * 2 if direction == 'plus' else Yrange / 2
        self.pw1.setYRange(-new_range,new_range)
        
    def find_nearest(self, array_in, value, array_out):
        array = np.asarray(array_in)
        idx = (np.abs(array - value)).argmin()
        return array_out[idx]

    def find_idx(self, array_in, value):
        array = np.asarray(array_in)
        return (np.abs(array - value)).argmin()

    def inifine_ab(self, pos_A = 0, pos_B = 12):
        if self.inf_a is not None and self.inf_b is not None:
            self.pw1.removeItem(self.inf_a)
            self.pw1.removeItem(self.inf_b)
        #Variables internas
        pen1 = pg.mkPen('b', width=1, style=Qt.PenStyle.DashLine)
        opst = {'position':0.9, 'color': (255,255,255), 'fill': (0,0,0,255), 'movable': True}
        name_a = f"A{self.side}"
        name_b = f"B{self.side}"
        #Lineas infinitas
        self.inf_a = InfiniteLineMod(lbl='A', pos=pos_A, movable=True, angle=90, pen=pen1, labelOpts=opst, name=name_a)
        self.inf_b = InfiniteLineMod(lbl='B', pos=pos_B, movable=True, angle=90, pen=pen1, labelOpts=opst, name=name_b)
        #Posición en X de las lineas infinitas
        self.inf_a.sigPositionChanged.connect(self.get_amplitude)
        self.inf_b.sigPositionChanged.connect(self.get_amplitude)
        #Se agregan lineas infinitas a la grafica
        self.pw1.addItem(self.inf_a)
        self.pw1.addItem(self.inf_b)

    def update_data(self, data):
        mem = {}
        for i in data:
            side_in = data[i]['side']
            if side_in == self.side:
                mem[i] = data[i]
        self.data = mem
        marks_flags = [Storage(5),Storage(5)]
        for i, value in self.data.items():
            if value['side'] == self.side and i not in self.marks:
                self.marks[i] = marks_flags
        self.update_graph()

    def update_graph(self):
        self.clearGraph()
        self.pw1.addItem(self.grid)

        with contextlib.suppress(Exception):
            pos_A = self.inf_a.getXPos()
            pos_B = self.inf_b.getXPos()

        for key, value in self.data.items():
            if value['view']:
                color_name = value['side']
                act = self.act_curve == key

                if color_name == 0:
                    if act:
                        color = pg.mkColor(255, 0, 0, 255)
                        fill = (14, 250, 0)
                    else:
                        color = pg.mkColor(180, 0, 0, 255)
                        fill = (180, 0, 0)
                elif act:
                    color = pg.mkColor(106, 154, 242, 255)
                    fill = (14, 250, 0)
                else:
                    color = pg.mkColor(112, 142, 199, 255)
                    fill = (112, 142, 199)

                lbl = f"""
                    <div style='text-align: center'>
                    <span style='color: #000; font-size: 7pt;'>
                    {value['intencity']} dBnHl
                    </span></div>
                    """
                text = TextItemMod(name=key, html=lbl, border="w", fill=fill)
                text.sigDragged.connect(self.print_drag)
                text.sigPositionChangeStarted.connect(self.active_curve)
                self.pw1.addItem(text)
                x = value['ipsi_xy'][0]
                y = value['ipsi_xy'][1] + value['gap']
                h = self.find_nearest(x, x.max(), y)
                text.setPos(12, h)
                self.pw1.plot(x, y, pen=color, name=key)  # now each curve has its name

        try:
            self.inifine_ab(pos_A, pos_B)
            self.refresh_keys()
        except UnboundLocalError:
            self.inifine_ab()


    def update_graph_by_name(self, graph_name, new_x, new_y):
        for item in self.pw1.listDataItems():
            if item.name() == graph_name:
                item.setData(new_x, new_y)
                break

    def print_drag(self, value):
        gap_y = value['pos'][1]
        print(gap_y)
        curve = value['name']
        self.data[curve]['gap'] = gap_y
        x = self.data[curve]['ipsi_xy'][0]
        y = self.data[curve]['ipsi_xy'][1] + gap_y
        self.update_graph_by_name(curve, x, y)

 
    def clearGraph(self):
        y, x = [],[]        
        self.pw1.plot(x, y, pen='w', clear=True)

    def create_marks(self, idx, subidx, curveName = None, useAct = True):
        curve = self.act_curve if useAct else curveName
        lbl_marks = [
            ["I","II","III","IV","V", "VI","VII"],
            ["I'","II'","III'","IV'","V'", "VI'", "VII'"]
            ]
        lbl = lbl_marks[idx][subidx]
        id_X = self.marks[curve][idx].get(subidx)
        lat = self.data[curve]['ipsi_xy'][0][id_X]
        amp = self.data[curve]['ipsi_xy'][1][id_X] + self.data[curve]['gap']
        curve_mark = f"<h3>&darr;<sup>{lbl}</sup></h3>"
        text = pg.TextItem(html = curve_mark, anchor=(0.34,0.6), color=(0,0,0,255))
        font = QFont()
        font.setPixelSize(13)
        text.setFont(font)
        text.setPos(lat, amp+0.1)
        self.pw1.addItem(text)

    def refresh_keys(self):
        for k in self.data:
            curve = k
            if self.data[curve]['view']:
                for i in range(2):
                    for d , val in enumerate(self.marks[curve][i].data):
                        if val is not None:
                            self.create_marks(i,d,curveName=curve, useAct=False)

    def update_marks(self,idx, subidx, btn='A'):
        #verify if exist
        mark_exist = self.remove_if_exist_mark(idx,subidx)
        
        if mark_exist == False:
            lat = self.inf_a.getXPos() if btn == 'A' else self.inf_b.getXPos()
            id_x = self.find_idx(self.data[self.act_curve]['ipsi_xy'][0], lat)
            self.marks[self.act_curve][idx].set(subidx, id_x)
        self.update_graph()
        self.update_data_marks()


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
            
    def active_curve(self, curves):
        if isinstance(curves, list):
            self.act_curve = curves[self.side]
        else:
            self.act_curve = curves

        self.update_data_marks()

        self.update_graph()

   #def move_graph(self, str_ud):
   #    if self.act_curve is not None:
   #        curve = self.act_curve
   #        y = self.data[curve]['gap']
   #        if str_ud == "down":
   #            y = y - .1
   #        elif str_ud == "up":
   #            y = y + .1
   #        self.data[curve]['gap'] = y
   #        self.update_graph()
        
    
    def get_amplitude(self):
        x = self.data[self.act_curve]['ipsi_xy'][0]
        y = self.data[self.act_curve]['ipsi_xy'][1]
        lat_a = self.inf_a.getXPos()
        if lat_a > 12:
            pos_b = self.inf_b.getXPos()
            self.inifine_ab(pos_A=12, pos_B=pos_b)
        if lat_a < 0:
            pos_b = self.inf_b.getXPos()
            self.inifine_ab(pos_A=0, pos_B=pos_b)
        lat_b = self.inf_b.getXPos()
        if lat_b > 12:
            pos_a = self.inf_a.getXPos()
            self.inifine_ab(pos_A=pos_a, pos_B=12)
        if lat_b < 0:
            pos_a = self.inf_a.getXPos()
            self.inifine_ab(pos_A=pos_a, pos_B=0)
        amp_a = self.find_nearest(x, lat_a, y)
        amp_b = self.find_nearest(x, lat_b, y)
        order_amp = np.sort(np.array([amp_a,amp_b]))
        order_lat = np.sort(np.array([lat_a,lat_b]))
        dif_amp = order_amp[1] - order_amp[0]
        dif_lat = order_lat[1] - order_lat[0]
        response = {'action':'latency_flag_update', 
                    'data':{"side": self.side, "lat_A": lat_a, 
                            "lat_B": lat_b, "amp_AB": dif_amp, 
                            "lat_AB": dif_lat}}
        self.data_info.emit(response)
        
    def save_image(self):
        exporter = pg.exporters.ImageExporter(self.pw1)
        exporter.parameters()['width'] = 800
        file = context.get_resource(f'image_{self.side}.png')
        exporter.export(file)


class LatencyIntencity():
    def __init__(self) -> None:
        pass