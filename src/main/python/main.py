# -*- coding: utf-8 -*-
#################################################################
#                                                               #
#                  NOMBRE PROYECTO : LabSim                     #
#                          VER. 0.7.5                           #
#               CREADOR : NICOLÁS QUEZADA QUEZADA               #
#                                                               #
#################################################################

import sys

import numpy as np
from base import context
from lib.AbrGraph import AbrGraph
from lib.AbrLatIntGraph import GraphLatInt
from lib.AbrControl import AbrControl
from lib.AbrDetail import AbrDetail
from lib.AbrTable import AbrTable
from lib.AbrReport import AbrReport
from UI.Ui_AbrAdvanceSettings import Ui_AdvanceSettings
from lib.EEG import EEG
from lib.FSP import FSP

from PySide6.QtWidgets import QMainWindow, QDialog
from PySide6.QtCore import QCoreApplication, QTimer, Slot
from PySide6.QtWidgets import QSpacerItem, QSizePolicy
from UI.Ui_MainABR import Ui_MainWindow

tr = QCoreApplication.translate

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("simPeatc")

        self.control = AbrControl()
        self.detail = AbrDetail()
        self.report = AbrReport()
        self.table_l = AbrTable(1)
        self.table_r = AbrTable(0)
        self.eeg = EEG()
        self.fmp = FSP()
        self.graph_r = AbrGraph(0)
        self.graph_l = AbrGraph(1)
        self.graph_lat_int = GraphLatInt()

        self.layout_abr.addWidget(self.graph_r)
        self.layout_abr.addWidget(self.graph_l)
        self.layout_lat_int.addWidget(self.graph_lat_int)
        self.layout_report.addWidget(self.report)
        self.detail.layout_tab1_secction1.addWidget(self.eeg)
        self.detail.layout_tab1_secction2.addWidget(self.fmp)
        self.layout_dock_parameter_content.addWidget(self.control)
        self.layout_dock_test_contents.addWidget(self.detail)
        self.layout_dock_values_contents.addWidget(self.table_r)
        self.layout_dock_values_contents.addWidget(self.table_l)
        self.layout_dock_values_contents.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))


        ########Conexiones de slots
        self.actionP_rametros_Avanzados.triggered.connect(self.active_advance_setting)
        self.table_r.measure_value.connect(self.measure_action)
        self.table_l.measure_value.connect(self.measure_action)
        self.graph_r.data_info.connect(self.measure_data)
        self.graph_l.data_info.connect(self.measure_data)
        self.graph_r.change_value_mark.connect(self.table_r.change_value_lat)
        self.graph_l.change_value_mark.connect(self.table_l.change_value_lat)



        ######Variables de Estado
        self.control.capture.connect(self.capture_state)
        self.state_capture = "stopped"
        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.capture)

        ######Variables de almacenamiento
        self.setting_current = {}
        self.curves_R = []
        self.curves_L = []
        self.current_capture_curve = ""
        self.current_setting = {}
        self.total_averages = 20
        self.current_measuring = [None, None]


        #########TEMP
        self.count_averages = 0

    def capture_state(self, state:str) -> None:
        if state == 'record':
            self.state_capture = state
            self.current_setting = self.control.get_data()
            self.total_averages = self.fake_averages(self.current_setting["average"])
            self.capture_timer.start(500)
        elif state == 'stopped':
            self.state_capture = state
            self.capture_timer.stop()
            print('me detuve')
        else:
            self.state_capture = state

    def capture(self) -> None:
        if self.state_capture == 'record':
            side = self.current_setting["side"]
            self.graph(side)
        elif self.state_capture == 'pause':
            print("detenido")

    def get_curve(self, presets):
        pass

    def new_curve(self, side:str) -> str:
        side_letter = 'R' if side == 'OD' else 'L'
        side = f'curves_{side_letter}'
        db_curves = getattr(self, side) 
        if not db_curves:
            curve = f'{side_letter}1'
        else:
            number_last_curve = int(db_curves[-1].strip(side_letter))
            curve =  f'{side_letter}{number_last_curve+1}'
        
        getattr(self, side).append(curve)
        self.current_capture_curve = curve
        return curve

    def graph(self, side):
        if self.count_averages == 0:
            self.new_curve(side)
            self.count_averages = 1
        elif self.count_averages < self.total_averages:
            self.count_averages +=1
        else:
            self.count_averages = 0
            self.control.stop_capture()
            return
        i_xy, c_xy, a, b = self.generar_puntos(48)
        data_line = {self.current_capture_curve:{"ipsi_xy":i_xy,"contra_xy":c_xy, "a":a, "b":b, "gap":1.8}}
        side_letter = 'r' if side == 'OD' else 'l'
        graph = f'graph_{side_letter}'
        getattr(self, graph).create_line(data_line)

    def fake_averages(self, averages, fake = True, express = False):
        if isinstance(averages , str):
            averages = int(averages)
        if not express:
            if fake:
                a = 0.52991151  # Parámetro a obtenido del ajuste
                b = 0.52207181  # Parámetro b obtenido del ajuste
                return a * (averages**b)
            self.total_averages = averages
        else:
            return 1
        
    def measure_action(self, data):
        side =  list(data.keys())[0]
        side_letter = 'r' if side == '0' else 'l'
        request = list(data[side].keys())[0]
        curve,command = request.split('_')
        side = int(side)
        if command == 'L':
            value = self.current_measuring[side]['lat_A']
        elif command == 'A':
            value = self.current_measuring[side]['amp_AB']
        data[str(side)][request] = value
        table = f'table_{side_letter}'
        graph = f'graph_{side_letter}'
        getattr(self, table).set_data(data)
        getattr(self, graph).create_marks(curve)



    def measure_data(self, data):
        side = data["curve"][0]
        side = 0 if side == 'R' else 1
        self.current_measuring[side] = data['data']

    def active_advance_setting(self):
        self.dialog = QDialog(self)
        self.ui = Ui_AdvanceSettings()
        self.ui.setupUi(self.dialog)
        self.dialog.exec()



################TEST
    def generar_puntos(self, num_puntos=12):
        """
        Genera puntos aleatorios en el rango:
        x: [1, 12]
        y: [-2, 2]
        
        Args:
            num_puntos (int): Número de puntos a generar.

        Returns:
            tuple: Arrays de x e y con los puntos generados.
        """

        step = 12/num_puntos
        lista = np.arange(0, 12, step)
        a_x = lista
        b_x = lista
        
        a = np.random.uniform(-2, 2, num_puntos)
        b = np.random.uniform(-2, 2, num_puntos)
        a = a.tolist()
        b = b.tolist()

        x = lista
        x_contra = lista
        y = np.random.uniform(-1, 1, num_puntos)
        y_contra = np.random.uniform(-2, 2, num_puntos)
        y_contra = y_contra.tolist()
        
        return (x,y),(x_contra, y_contra),(a_x,a), (b_x,b)
    



if __name__ == '__main__':
    window = MainWindow()
    style_file = context.get_resource('qss/style_base.qss')
    line = ""
    with open(style_file, 'r') as f:
        style = f.read()
            
    window.setStyleSheet(style)
    window.show()
    
    exit_code = context.app.exec()
    
    sys.exit(exit_code)
