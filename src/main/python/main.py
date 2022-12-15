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

import numpy as np
from base import context

from PySide6.QtWidgets import QPushButton, QWidget
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QFileDialog
from datetime import datetime

import lib.bezier_prop as bz
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
        self.detail.btn_start.clicked.connect(self.capture)
        self.detail.btn_stop.clicked.connect(self.printer)

        self.current_curves = [None, None]

    def printer(self):
        #print(self.store)     
        self.graph_right.save_image()
        self.graph_left.save_image()
        table = dataset_pdf(self.store)
        image_ABR()
        create_pdf(table)
        
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
        self.graph_right.activeCurve(self.current_curves)
        self.graph_left.activeCurve(self.current_curves)

    def capture(self):
        intencity = self.control.sb_intencity.value()
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
        repro = random.randint(80,99)
        setting= (self.control.get_data())
        

        self.store[name] = {'ipsi_xy':[[],[]],'contra_xy':[[],[]],
                            'side':side, 'intencity':intencity, 'repro':repro, 
                            'view':view, 'gap':gap, 'stim':setting['stim'], 
                            'pol':setting['pol'], 'mkg':setting['mkg'], 'rate':setting['rate'],
                            'filter':f"{setting['filter_passhigh']}-{setting['filter_down']}",
                            'prom':setting['prom'], 'marks' : [0,0,0,0,0]}
        
        self.data.set_intencity(intencity)
        #x, y = self.data.get()
        if side == 0:
            x, y, dx,dy = ABR_Curve(none=False, nHL=intencity, p_I=1.3, a_V = 0.6, zeros=False, VrelI = False)
        else: 
            x, y, dcx,dy = ABR_Curve(none=False, nHL=intencity, p_I=2, a_V = 0.3, zeros=False, VrelI = False)
        self.store[name]['ipsi_xy'][0] = x
        self.store[name]['ipsi_xy'][1] = y
        self.disabled_in_capture()
        self.updateFlagsCurves()
        self.updateGraph()
        name_curve = {'curve':name}
        self.selectCurve(name_curve)

    def cases(self, n):
        neural = {}
        coclear = {}
        transmissión = {}
        normal = {"threshold":20, }

    def updateGraph(self):
        self.graph_right.update_data(self.store)
        self.graph_left.update_data(self.store)
        self.disabled_in_capture(False)

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

def ABR_Curve(none = False, nHL = 80, p_I=1.6, p_III=3.7, p_V=5.6, a_V = 0.8, VrelI = True, zeros = False):
    if none:
        nHL = -15

    att = 0
    lam = 0
    varInt = abs(80 - nHL)
    fvarInt = varInt/5
    if nHL > 80:
        sideAmp = 1
        sideLat = -1
    else:
        sideAmp = -1
        sideLat = 1

    if nHL >=50:
        fvarLat = .15
        fvarAmp = .06
    else:
        fvarLat = .2
        fvarAmp = .08

    att = (fvarLat * fvarInt) * sideLat
    lam = (fvarAmp * fvarInt) * sideAmp/2

    peak_I =  p_I + att
    peak_II =  p_I+1+ att

    peak_III =  p_III + att
    peak_V =  p_V + att

    peak_IV = peak_V-.5
    end = 12 + att
    amp_V = a_V + lam
    amp_V = max(amp_V, 0)
    VrelI = VrelI

    var = random.uniform(0,0.2)
    amp_I = amp_V / 3 if VrelI else amp_V / 1
    amp_I = amp_I + lam
    amp_I = max(amp_I, 0)
    amp_Ip = -(amp_I/2)
    amp_II = amp_Ip+0.1
    amp_IIp = amp_II-.02

    if amp_Ip == 0:
        amp_II = 0
        amp_IIp=0

    amp_III = 0.3 +lam
    amp_III = max(amp_III, 0)
    amp_IIIp = 0

    amp_VI = amp_V -.3

    amp_VI = max(amp_VI, 0)
    curve_cm = (0.6+att, 0.15)
    curve_cmp = (0.7+att, -0.05)

    curve_I = (peak_I,amp_I/2)
    curve_Ip = (curve_I[0]+.5,amp_Ip)

    curve_II = (peak_II, amp_II)
    curve_IIp = (curve_II[0]+.3,curve_II[1]-.02)

    curve_III = (peak_III,amp_III)
    curve_IIIp = (curve_III[0]+.9,amp_IIIp)

    #curve_III = (peak_III,amp_III)
    #curve_IIIp = (curve_III[0]+.9,0)


    VrefIII = (random.uniform(-.1,.1)) + curve_III[1]
    curve_V = (peak_V,VrefIII)

    amp_IV = VrefIII-.05
    amp_IV = max(amp_IV, 0)
    amp_IVp = amp_IV-.05
    amp_IVp = max(amp_IVp, 0)
    sn10refV = curve_V[1] - amp_V
    sn10refV = min(sn10refV, 0)
    sn10 = (curve_V[0]+1,sn10refV)

    curve_IV = (peak_IV, amp_IV)
    curve_IVp = (curve_IV[0]+.05, amp_IVp)

    curve_VI = (sn10[0]+1.5, amp_VI)
    curve_VIp = (curve_VI[0]+1.5, curve_VI[1]-.3)
    curve_VII = (curve_VIp[0]+1.5, curve_VIp[1]+.6)

    #print(sn10refV)

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
            [end,0]        
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
    return px, y_new, x, y

#px, y_new = ABR_Curve()

if __name__ == '__main__':
    window = MainWindow()
    window.show()
    exit_code = context.app.exec()
    sys.exit(exit_code)
