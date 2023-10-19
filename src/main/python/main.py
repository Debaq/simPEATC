# -*- coding: utf-8 -*-
#################################################################
#                                                               #
#                  NOMBRE PROYECTO : LabSim                     #
#                          VER. 0.7.5                           #
#               CREADOR : NICOLÁS QUEZADA QUEZADA               #
#                                                               #
#################################################################

import random
import sys


from PySide6.QtWidgets import QPushButton, QWidget
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QFileDialog
from datetime import datetime

from lib.ABR_generator import ABR_creator
from lib.ABR_graph import GraphABR
from lib.EEG import EEG
from UI.Ui_ABR_config import Ui_ABR_config
from UI.Ui_ABR_control import Ui_ABRSim
from UI.Ui_ABR_ctrl_graph import Ui_ABR_control_curve
from UI.Ui_ABR_detail import Ui_ABR_detail
from UI.Ui_ABR_lat_select import Ui_ABR_lat_select
from lib.pdf_abr import dataset as dataset_pdf
from lib.pdf_abr import image_ABR, create_pdf
from lib.ABR_generator_2 import ABR_Curve
from PySide6.QtCore import QTimer

######COSAS PARA EL WIDGET DE LA PRUEBA
from PySide6.QtWidgets import QMessageBox, QSpinBox, QScrollArea, QVBoxLayout, QLabel

from PySide6.QtWidgets import QFileDialog



class ABR_control(QWidget, Ui_ABR_config):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        
    def get_data(self):
        
        stim = self.cb_stim.currentText()
        pol = self.cb_pol.currentText()
        inty = self.sb_intencity.value()
        mkg = self.sb_mskg.value()
        rate = self.sb_rate.value()
        
        filter_passdown = self.cb_filter_down.currentText()
        filter_passhigh =self.cb_filter_up.currentText()
        prom = self.sb_prom.value()
        side = self.cb_side.currentText()
        
        return {"stim":stim, "pol":pol, "int":inty, "mkg":mkg, 
                "rate":rate, "filter_down":filter_passdown, 
                "filter_passhigh": filter_passhigh, "prom" : prom,
                "side":side}
        


class ABR_detail(QWidget, Ui_ABR_detail):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        


class ABR_lat_select(QWidget, Ui_ABR_lat_select):
    data = Signal(dict)
    def __init__(self, side):
        QWidget.__init__(self)
        self.side = side
        self.setupUi(self)

        self.update_data({})
        self.configure_btn()
        self.flag_ab = "A"
        self.list_marks = { 'I':0,'Ip':0,'II':1,'IIp':1,
                            'III':2,'IIIp':2,'IV':3,'IVp':3,
                            'V':4,'Vp':4}


    def configure_btn(self):
        self.btn_AB.clicked.connect(self.toogle_AB)
        list_btn_waves = [i for i in dir(self) if i.startswith('btn_wave')]
        for i in list_btn_waves:
            getattr(self, i).clicked.connect(self.update_marks)

    def update_marks(self):
        widget = self.sender()
        name = widget.objectName()
        end = name.endswith('p')
        idx = 1 if end else 0
        _,_,name_wave = name.split('_')
        subidx = self.list_marks[name_wave]
        self.data.emit({'action':'update_mark', 
                        'data':{'prima': idx, 'n_curve':subidx,
                                'side':self.side, 'flag' : self.flag_ab}})
        
    def toogle_AB(self):
        widget = self.sender()
        text = widget.text()
        if text == "|A":
            text = "B|"
            new = "B"
        else:
            text = "|A"
            new = "A"
        widget.setText(text)
        self.flag_ab = new
        

    def update_data(self, data):
        
        if 'lat_A' in data:
            self.lbl_1.setText('A:{:.1f}ms B:{:.1f}ms'.format(data['lat_A'], data['lat_B']))
            self.lbl_2.setText('A-B:{:.2f}μV'.format(data['amp_AB']))
            self.lbl_3.setText('A<>B:{:.2f}ms'.format(data['lat_AB']))
        if 'non_prima' in data:
            self._extracted_from_update_data_8(data)

    # TODO Rename this here and in `update_data`
    def _extracted_from_update_data_8(self, data):
        self.lbl_4.setText("I:{:.1f}ms I':{:.1f}ms".format(data['non_prima'][0],data['prima'][0]))
        self.lbl_5.setText("II:{:.1f}ms II':{:.1f}ms".format(data['non_prima'][1],data['prima'][1]))
        self.lbl_6.setText("III:{:.1f}ms III':{:.1f}ms".format(data['non_prima'][2],data['prima'][2]))
        self.lbl_7.setText("IV:{:.1f}ms IV':{:.1f}ms".format(data['non_prima'][3],data['prima'][3]))
        self.lbl_8.setText("V:{:.1f}ms V':{:.1f}ms".format(data['non_prima'][4],data['prima'][4]))
        I_III = data['non_prima'][2]-data['non_prima'][0]
        III_V = data['non_prima'][4]-data['non_prima'][2]
        I_V = data['non_prima'][4]-data['non_prima'][0]
        self.lbl_9.setText("I-III:{:.1f}ms".format(I_III))
        self.lbl_10.setText("III-V:{:.1f}ms".format(III_V))
        self.lbl_11.setText("I-V:{:.1f}ms".format(I_V))

class ABR_ctrl_curve(QWidget, Ui_ABR_control_curve):
    data = Signal(dict)
    def __init__(self, side):
        QWidget.__init__(self)
        self.contra_view = False
        self.side = side
        self.setupUi(self)
        self.config_btn()
        self.lbl_scale.setText('0.5')

    
    def config_btn(self):
        self.btn_up.clicked.connect(self.move_curve)
        self.btn_down.clicked.connect(self.move_curve)
        self.btn_del.clicked.connect(self.remove_curve)
        self.btn_scale_plus.clicked.connect(self.scale_graph)
        self.btn_scale_minus.clicked.connect(self.scale_graph)
        self.btn_contra.clicked.connect(self.contra_activate_toggle)
        
    
    def move_curve(self):
        widget = self.sender()
        _,direction = widget.objectName().split('_')
        self.data.emit({'action':'move', 
                        'data':{'direction': direction, 'side':self.side}})
    
    def scale_graph(self):
        widget = self.sender()
        _,_,direction = widget.objectName().split('_')
        self.scale_lbl_change(direction)
        self.data.emit({'action':'scale', 
                        'data':{'direction': direction, 'side':self.side}})
    
    def scale_lbl_change(self, direction):
        scale = float(self.lbl_scale.text())
        if direction == 'plus':
            scale *= 2
        else:
            scale = scale/2
        
        self.lbl_scale.setText(str(scale))
            
    def remove_curve(self):
        self.data.emit({'action':'remove', 
                        'data':{'side':self.side}})
        
    def contra_activate_toggle(self):
        self.contra_view = not self.contra_view
        self.data.emit({'action':'contra', 
                    'data':{'contra_view':self.contra_view}})
        
    def update_flag_curves(self, list_btns:list) -> None:
        for i in reversed(range( self.layout_curves.count())): 
            self.layout_curves.itemAt(i).widget().deleteLater()
        
        self.btns_flags_curves(list_btns)
        
    
    def btns_flags_curves(self, btns:list):
        color = "255,0,0" if self.side == 0 else "106,154,242"
        style =f"""
                    QWidget {'{'}
                    color: rgb(0, 0, 0);
                    background-color: rgb({color});
                    border-style: outset;
                    border-width: 0px;
                    {'}'}"""
        for btn_ in btns:
            btn = QPushButton(f'{btn_[0]}')
            btn.setObjectName(btn_[1])
            btn.setStyleSheet(style)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(self.selected_curve)
            btn.setMaximumSize(30,30)
            font = QFont('Times', 7)
            btn.setFont(font)
            btn.setToolTip(f'{btn_[2]}')
            btn.setChecked(True)
            self.layout_curves.addWidget(btn)
        
    def selected_curve(self):
        widget = self.sender()
        curve = widget.objectName()
        self.data.emit({'action':'selected', 
                        'data':{'curve': curve}})


class CaseSelect(QMessageBox):
    sig = Signal(int)
    def __init__(self, l, *args, **kwargs):
        QMessageBox.__init__(self, *args, **kwargs)
        self.get_n = QSpinBox(self)
        self.get_n.setMaximum(26)
        self.get_n.setMinimum(1)
        self.get_n.setPrefix("Caso: ")
               
        lay = QVBoxLayout()
        lay.addWidget(self.get_n)

        self.setStyleSheet("QScrollArea{min-width:300 px; min-height: 400px}")
        #self.buttons[0].clicked.connect(self.test)

        
    def closeEvent(self, *args):
        self.sig.emit(self.get_n.value())
        
    def changeEvent(self, *args):
        self.sig.emit(self.get_n.value())

        
        


class MainWindow(QWidget, Ui_ABRSim):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.control = ABR_control()
        self.detail = ABR_detail()
        self.eeg = EEG()
        self.detail.layout_eeg.addWidget(self.eeg.pw)

        self.lat_select_R = ABR_lat_select(0)
        self.lat_select_L = ABR_lat_select(1)
        self.lat_select_L.data.connect(self.capture_actions)
        self.lat_select_R.data.connect(self.capture_actions)
        self.ctrl_curve_rigth = ABR_ctrl_curve(0)
        self.ctrl_curve_left = ABR_ctrl_curve(1)
        self.ctrl_curve_rigth.data.connect(self.capture_actions)
        self.ctrl_curve_left.data.connect(self.capture_actions)

        self.graph_right = GraphABR(0)
        self.graph_left = GraphABR(1)
        self.graph_right.data_info.connect(self.capture_actions)
        self.graph_left.data_info.connect(self.capture_actions)

        #LAYOUTS
        self.layout_left.addWidget(self.control)
        self.layout_left.addWidget(self.detail)
        self.layout_left.addWidget(self.eeg)

        self.layourt_ctrl_R.addWidget(self.lat_select_R)
        self.layourt_ctrl_L.addWidget(self.lat_select_L)
        self.layout_ctrl_curve_R.addWidget(self.ctrl_curve_rigth)
        self.layout_ctrl_curve_L.addWidget(self.ctrl_curve_left)


        self.layout_graph_R.addWidget(self.graph_right.win)
        self.layout_graph_L.addWidget(self.graph_left.win)
        self.store = {}
        self.data = ABR_creator()

        self.detail.btn_start.setText("EMPEZAR")
        self.detail.btn_stop.setText("IMPRIMIR")
        self.detail.btn_start.clicked.connect(self.init_capture)
        self.detail.btn_stop.clicked.connect(self.open_save_dialog)

        self.current_curves = [None, None]
        self.cases_list = [str(i) for i in range(25)]
        self.cases_()
        self.repro = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.anim_upgradeGraph)
        #self.prom = 20
        self.count_prom = 0
        self.new_curve = True
        self.new_current_curve = ""
        
    def open_save_dialog(self):
        """
        Abre un cuadro de diálogo para guardar un archivo.
        
        Args:
        - parent (QWidget, optional): El widget padre para el cuadro de diálogo.
        
        Returns:
        - str or None: La ruta del archivo seleccionado o None si se canceló.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Pdf (*.pdf)", options=options)
        if file_name:
            self.printer(file_name)
        return None
        
    def prom(self):
        prom = self.control.sb_prom.value() 
        result = prom / 100
        result = result * 2
        return result
        
    def init_capture (self):
        self.disabled_in_capture()

        self.timer.start(1000) # 1000 ms = 1 segundo

    def anim_upgradeGraph(self):
        prom = self.prom()
        if self.count_prom < prom:
            self.count_prom += 1
            self.capture()
        else:
            self.timer.stop()
            self.count_prom = 0
            self.new_curve = True
            self.disabled_in_capture(False)



    def cases_(self):
      result = CaseSelect(self.cases_list, None)
      result.sig.connect(self.cases)
      result.exec()
    

    def printer(self, direccion):
        #print(self.store)     
        self.graph_right.save_image()
        self.graph_left.save_image()
        table = dataset_pdf(self.store)
        image_ABR()
        create_pdf(table, self.number_user_case, direccion)
        
        """

        self.control.get_data()
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            pass
        """
    def laSuper(self, data):
        self.Sdata = data
        self.entry = False
    
    def capture_actions(self, data):
        if data['action'] == 'move':
            self.move_curve(data['data'])
        if data['action'] == 'remove':
            self.remove_curve(data['data'])
        if data['action'] == 'selected':
            self.selectCurve(data['data'])
        if data['action'] == 'update_mark':
            self.update_markers(data['data'])
        if data['action'] == 'scale':
            self.scale_graph(data['data'])
        if data['action'] == 'latency_flag_update':
            
            self.update_data_lat_ab(data['data'])

    def scale_graph(self, data):
       if data['side'] == 0:
            self.graph_right.scale(data['direction'])
       else:
            self.graph_left.scale(data['direction'])
           
    def move_curve(self, data):
            direction = data['direction']
            side = data['side']
            if side == 0:
                self.graph_right.move_graph(direction)
            else:
                self.graph_left.move_graph(direction)

    def remove_curve(self, data):
        side = data['side']
        self.store[self.current_curves[side]]['view'] = False
        self.updateFlagsCurves()
        self.updateGraph()
  
    def selectCurve(self, data):
        _,x = data['curve'].split('_')
        side,_ = x.split(':')
        side = 0 if side == 'R' else 1
        self.current_curves[side] = data['curve']
        repro = self.store[data['curve']]["repro"]
        self.detail.pb_repro.setValue(repro)

        self.graph_right.activeCurve(self.current_curves)
        self.graph_left.activeCurve(self.current_curves)

    def capture(self):
        repro = random.randint(80,99)

        intencity = self.control.sb_intencity.value()
        if self.new_curve:
            self.new_curve = False
            self.detail.pb_repro.setValue(0)

            side = self.control.cb_side.currentText()
            if side == 'OD':
                side = 0
                letter = 'R'
            else: 
                side = 1
                letter = 'L'
            gap = 1.8
            name = f"{intencity}_{letter}:0"
            if name in self.store:
                name, _ = self.numberName(name, letter, intencity)
            gap = self.calGap(letter, gap)
            view = True
            setting= (self.control.get_data())
            
            self.new_current_curve=name

            self.store[name] = {'ipsi_xy':[[],[]],'contra_xy':[[],[]],
                                'side':side, 'intencity':intencity, 'repro':repro, 
                                'view':view, 'gap':gap, 'stim':setting['stim'], 
                                'pol':setting['pol'], 'mkg':setting['mkg'], 'rate':setting['rate'],
                                'filter':f"{setting['filter_passhigh']}-{setting['filter_down']}",
                                'prom':setting['prom'], 'marks' : [0,0,0,0,0]}
            
        #self.data.set_intencity(intencity)
        #x, y = self.data.get()

        control_setting = self.control.get_data()
        if self.new_curve is False:

            self.detail.pb_repro.setValue(repro)
            _, side = self.new_current_curve.split("_")
            side , _ = side.split(":")
            side = 0 if side == "R" else 1
            name = self.new_current_curve
        
        prom = self.prom()
                
        if side == 0:
            x,y, dx, dy, self.repro = ABR_Curve(intencity, control_setting, self.case_master[0], self.repro, [self.count_prom, prom])
        else: 
            x,y, dx, dy, self.repro = ABR_Curve(intencity, control_setting, self.case_master[1], self.repro, [self.count_prom, prom])
        
            
        self.store[name]['ipsi_xy'][0] = x
        self.store[name]['ipsi_xy'][1] = y
        self.updateFlagsCurves()
        self.updateGraph()
        name_curve = {'curve':name}
        self.selectCurve(name_curve)

    def cases(self, n):
        self.number_user_case = n
        #n: normal
        #c: coclear
        #t: transmission
        #m: normal
        #latI80 : latencia onda I a 80
        #ink: interpeaks [1_3, 1_5]
        #amp: amplitud [1,5]
        #repro: reproductividad
        #morfo: morfología
        #th : umbral
        n_1 = {"lat": 1.53, "ink":[3.58, 5.37], "amp":[.5, 1], "repro": True, "morfo": [True, True, True], "th":20}
        n_2 = {"lat": 1.7, "ink":[3.5, 5.5], "amp":[.4, .5], "repro": False, "morfo": [True, True, True], "th":50}
        n_3 = {"lat": 1.6, "ink":[4, 6], "amp":[.4, .4], "repro": True, "morfo": [True, False, True], "th":40}
        c_1 = {"lat": 2.6, "ink":[2.2, 4], "amp":[.7, 1], "repro": True, "morfo": [False, True, True], "th":60}
        c_2 = {"lat": 3.6, "ink":[2.4, 3.8], "amp":[.7, 1], "repro": True, "morfo": [False, True, True], "th":70}
        c_3 = {"lat": 2.1, "ink":[1.9, 4.1], "amp":[.7, 1], "repro": True, "morfo": [False, True, True], "th":40}
        t_1 = {"lat": 2.0, "ink":[2, 4], "amp":[.5, .5], "repro": True, "morfo": [True, True, True], "th":60}
        t_2 = {"lat": 3.1, "ink":[2.2, 3.8], "amp":[.4, .5], "repro": True, "morfo": [True, True, True], "th":70}
        m_1 = {"lat": 1.5, "ink":[2, 3.8], "amp":[.7, .9], "repro": True, "morfo": [True, True, True], "th":20}
        m_2 = {"lat": 1.7, "ink":[2.1, 4], "amp":[.3, .8], "repro": True, "morfo": [True, True, True], "th":30}
        m_3 = {"lat": 1.6, "ink":[1.8, 3.6], "amp":[.5, .9], "repro": True, "morfo": [True, True, True], "th":10}

        cases = [[n_1,n_1],[m_2,n_2],[n_3,m_3],[c_1,m_1],[m_2,c_2],[c_3,m_3],[m_1,t_1],
                 [t_2,m_2],[n_1,c_1],[c_2,n_2],[n_3,c_3],[n_1,t_1],[t_2,n_2],[c_1,t_1],
                 [t_2,c_2],[m_1,n_3],[c_1,m_2],[m_3,n_1],[t_2,n_1],[c_2,n_3],[m_3,c_2],
                 [c_3,n_2],[n_2,m_1],[m_1,t_2],[n_1,m_2],[m_2,n_3]]
        self.case_master = cases[n-1]
        
        
        

    def updateGraph(self):
        if self.new_curve is False:
            _, side = self.new_current_curve.split("_")
            side , _ = side.split(":")
            if side == "R":
                self.graph_right.update_data(self.store)
            else:
                self.graph_left.update_data(self.store)


    def updateFlagsCurves(self):
        btns_left = []
        btns_right = []
        for k in self.store:
            if self.store[k]['view']:
                y, x = k.split('_')
                l,num = x.split(':')
                name = f"{y}"
                short = f"{y} {l}{num}"
                id_x = k
                btn = [name,id_x, short]
                if l == 'L':
                    btns_left.append(btn)
                else:
                    btns_right.append(btn)
        self.ctrl_curve_rigth.update_flag_curves(btns_right)
        self.ctrl_curve_left.update_flag_curves(btns_left)

    def numberName(self, name, ltr, tin):
        n = []
        g = []
        db = []
        for i in self.store:
            dbi,x = i.split('_')
            l,num = x.split(':')
            if l == ltr:
                n.append(int(num))
            g.append(self.store[i]['gap'])
            db.append(dbi)

        n.sort()
        g.sort(reverse=True)
        resultG = g[-1] -0.6
        resultN = n[-1]+1
        name = f"{tin}_{ltr}:{resultN}"
        return name , resultG

    def calGap(self,  ltr,  gap):
        g = []
        for i in self.store:
            _,x = i.split('_')
            l,_ = x.split(':')
            if l == ltr:
                g.append(self.store[i]['gap'])

        g.sort(reverse=True)
        return g[-1] -0.4 if g else gap

    def disabled_in_capture(self, dis = True):
        self.detail.btn_start.setDisabled(dis)
        self.control.sb_intencity.setDisabled(dis)
        self.control.cb_side.setDisabled(dis)

    def update_data_lat_ab(self, data):
        side = data["side"]
        if "non_prima" in data:
            marks = data["non_prima"]
            curve = data["curve"]
            self.store[curve]['marks'] = marks
        if side == 0:
            self.lat_select_R.update_data(data)
        else:
            self.lat_select_L.update_data(data)


    def update_markers(self, data):
        side = data['side']
        idx = data['prima']
        subidx = data['n_curve']
        flag = data['flag']
        
        
        if side == 0:
            self.graph_right.update_marks(idx,subidx,flag)
        else:
            self.graph_left.update_marks(idx,subidx,flag)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Crea y muestra tu ventana principal
    window = MainWindow()
    window.show()

    # Ejecuta el loop de eventos
    exit_code = app.exec()

    # Finaliza el programa
    sys.exit(exit_code)
