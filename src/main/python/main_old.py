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

from base import context
from lib.ABR_generator import ABR_creator
from lib.ABR_generator_2 import ABR_Curve
from main.python.lib.AbrGraph import AbrGraph
from lib.AbrControl import AbrControl
from lib.AbrDetail import AbrDetail
from lib.AbrLatSelect import AbrLatSelect
from lib.EEG import EEG
from lib.pdf_abr import create_pdf
from lib.pdf_abr import dataset as dataset_pdf
from lib.pdf_abr import image_ABR
from PySide6.QtCore import QTimer
######COSAS PARA EL WIDGET DE LA PRUEBA
from PySide6.QtWidgets import (QFileDialog,QWidget)
from UI.Ui_ABR_control import Ui_ABRSim
from lib.AbrCtrlCurve import AbrCtrlCurve
from lib.CaseSelect import CaseSelect


        


class MainWindow(QWidget, Ui_ABRSim):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.control = AbrControl()
        self.detail = AbrDetail()
        self.eeg = EEG()
        self.detail.layout_eeg.addWidget(self.eeg.pw)

        self.lat_select_R = AbrLatSelect(0)
        self.lat_select_L = AbrLatSelect(1)
        self.lat_select_L.data.connect(self.capture_actions)
        self.lat_select_R.data.connect(self.capture_actions)
        self.ctrl_curve_rigth = AbrCtrlCurve(0)
        self.ctrl_curve_left = AbrCtrlCurve(1)
        self.ctrl_curve_rigth.data.connect(self.capture_actions)
        self.ctrl_curve_left.data.connect(self.capture_actions)

        self.graph_right = AbrGraph(0)
        self.graph_left = AbrGraph(1)
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

        self.graph_right.active_curve(self.current_curves)
        self.graph_left.active_curve(self.current_curves)

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

            self.store[name] = {'ipsi_xy':[[],[]],'contra_xy':[[],[]],'mem_a':[[],[]],'mem_b':[[],[]],
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
        
        
        

    def updateGraph(self, remove = False):
        if remove:
            print("se esta eliminando")
        if self.new_curve is False:
            _, side = self.new_current_curve.split("_")
            side , _ = side.split(":")
            if side == "R":
                self.graph_right.update_graph(self.store)
            else:
                self.graph_left.update_graph(self.store)


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
    window = MainWindow()
    window.show()
    exit_code = context.app.exec()
    sys.exit(exit_code)
