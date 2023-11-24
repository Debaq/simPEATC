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
from lib.AbrControl import AbrControl
from lib.AbrDetail import AbrDetail
from lib.AbrDetailAllCurves import AbrDetailAllCurves
from lib.AbrGraph import AbrGraph
from lib.AbrLatIntGraph import GraphLatInt
from lib.AbrReport import AbrReport
from lib.AbrTable import AbrTable
from lib.EEG import EEG
from lib.FSP import FSP
from lib.PdfCreator import PDFCreator
from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtWidgets import QDialog, QMainWindow, QSizePolicy, QSpacerItem, QVBoxLayout, QComboBox, QPushButton
from UI.AbrAdvanceSettings_ui import Ui_AdvanceSettings
from UI.AbrMain_ui import Ui_MainWindow
from lib.ABR_generator_2 import ABR_Curve

tr = QCoreApplication.translate


class PopupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Selección de casos')

        # Hacer que la ventana sea modal
        self.setModal(True)

        # Crear el ComboBox y el botón dentro de la ventana de diálogo
        layout = QVBoxLayout(self)

        self.combo_box = QComboBox()
        self.create_list()
        layout.addWidget(self.combo_box)

        self.accept_button = QPushButton("Aceptar")
        self.accept_button.clicked.connect(self.on_accept_clicked)
        layout.addWidget(self.accept_button)



    def create_list(self):
        for i in range(26):
            self.combo_box.addItem(f'Caso {i+1}')

    def on_accept_clicked(self):
        chosen_option = self.combo_box.currentText()
        print(f"Has seleccionado: {chosen_option}")
        self.accept()  # Esto cerrará la ventana de diálogo
        return self.combo_box.currentIndex()


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
        self.detail_all = AbrDetailAllCurves()
        self.graph_r = AbrGraph(0)
        self.graph_l = AbrGraph(1)
        self.graph_lat_int = GraphLatInt()

        self.layout_abr.addWidget(self.graph_r)
        self.layout_abr.addWidget(self.graph_l)
        self.layout_lat_int.addWidget(self.graph_lat_int)
        self.layout_report.addWidget(self.report)
        self.detail.layout_tab1_secction1.addWidget(self.eeg)
        self.detail.layout_tab1_secction2.addWidget(self.fmp)
        self.detail.layout_tab2.addWidget(self.detail_all)
        self.layout_dock_parameter_content.addWidget(self.control)
        self.layout_dock_test_contents.addWidget(self.detail)
        self.layout_dock_values_contents.addWidget(self.table_r)
        self.layout_dock_values_contents.addWidget(self.table_l)
        self.layout_dock_values_contents.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        ########Conexiones de slots
        self.actionP_rametros_Avanzados.triggered.connect(self.active_advance_setting)
        self.actionCambiar_Caso.triggered.connect(self.open_modal)
        self.table_r.sig_measure_value.connect(self.measure_action)
        self.table_l.sig_measure_value.connect(self.measure_action)
        self.graph_r.sig_data_info.connect(self.measure_data)
        self.graph_l.sig_data_info.connect(self.measure_data)
        self.graph_r.sig_change_value_mark.connect(self.table_r.change_value_lat)
        self.graph_l.sig_change_value_mark.connect(self.table_l.change_value_lat)
        self.graph_r.sig_curve_selected.connect(self.curve_selected)
        self.graph_l.sig_curve_selected.connect(self.curve_selected)
        self.graph_r.sig_del_curve.connect(self.update_delete_curve)
        self.graph_l.sig_del_curve.connect(self.update_delete_curve)
        self.report.sig_update_pdf.connect(self.report_svg)

        self.tabWidget.currentChanged.connect(self.tab_change)
        self.detail_all.sig_selected_curve.connect(self.selected_)
        self.btn_scale_minus.clicked.connect(self.scale_graph)
        self.btn_scale_plus.clicked.connect(self.scale_graph)

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
        self.current_curve_r = ""
        self.current_curve_l = ""
        self.current_setting = {}
        self.total_averages = 20
        self.current_measuring = [None, None]
        self.memory = {}
        self.donde = False

        #########TEMP TEST
        self.count_averages = 0

        self.open_modal()

    def open_modal(self):
        # Esta función crea y abre la ventana de diálogo
        dialog = PopupDialog(self)
        dialog.exec()
        self.case = dialog.combo_box.currentIndex()
        self.report.case = self.case

    def update_delete_curve(self, curve):
        if curve in self.memory:
            table_letter = 'r' if curve[0] == 'R' else 'l'
            table = f'table_{table_letter}'
            getattr(self, table).clear_all()
            self.detail_all.delete_row_by_header(curve)
            del self.memory[curve]
        
    def curve_selected(self, curve):
        table_letter = 'r' if curve[0] == 'R' else 'l'
        try:
            table = f'table_{table_letter}'
            data = self.memory[curve]
            getattr(self, table).update_latamp_table(data)
        except KeyError:
            pass

    def scale_graph(self):
        _,_,direction = self.sender().objectName().split('_')
        value = self.graph_r.scale(direction)
        self.graph_l.scale(direction)
        value = int(round(value,0))
        value = f"{value}µV"
        self.lbl_scale.setText(value)

    def selected_(self, curve):
        letter = 'r' if curve[0] == 'R' else 'l'
        graph = f'graph_{letter}'
        getattr(self, graph).active_curve(curve) 
        
    def tab_change(self, sender):
        if sender == 1:
            self.dock_values.setVisible(False)
            self.dock_parameter.setVisible(False)
            self.detail.tabWidget.setCurrentIndex(1)
            self.dock_test.setFixedHeight(400)
            self.graph_lat_int.plot_data(self.memory)
        elif sender == 2:
            self.dock_values.setVisible(False)
            self.dock_parameter.setVisible(False)
            self.detail.tabWidget.setCurrentIndex(1)
            self.dock_test.setFixedHeight(300)
            self.report_svg()

        else:
            self.dock_values.setVisible(True)
            self.dock_parameter.setVisible(True)
            self.detail.tabWidget.setCurrentIndex(0)
            self.dock_test.setFixedHeight(150)
            self.graph_lat_int.clear_graph()


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
            self.memory_curves()
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
        table=f"table_{side_letter.lower()}"
        getattr(self, table).clear_all()
        self.selected_(curve)
        self.current_capture_curve = curve
        return curve

    def graph(self, side):
        self.done = False
        if self.count_averages == 0:
            self.new_curve(side)
            self.count_averages = 1
        elif self.count_averages < self.total_averages:
            self.count_averages +=1
        else:
            self.done = True
            self.count_averages = 0
            self.control.stop_capture()
        i_xy, c_xy, a, b, repro = self.test_test(side)
        intencity = self.current_setting['int']

        data_line = {self.current_capture_curve:{"ipsi_xy":i_xy,"contra_xy":c_xy, "a":a, "b":b, "gap":1.8, 
                                                 "repro" : repro, "intencity":intencity, "done" : self.done}}
        side_letter = 'r' if side == 'OD' else 'l'
        graph = f'graph_{side_letter}'
        getattr(self, graph).create_line(data_line, intencity)

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
        mark,command = request.split('_')
        side = int(side)
        if command == 'L':
            value = self.current_measuring[side]['lat_A']
        elif command == 'A':
            value = self.current_measuring[side]['amp_AB']
        self.memory_curves((mark,command,value), side_letter)
        data[str(side)][request] = value
        table = f'table_{side_letter}'
        graph = f'graph_{side_letter}'
        getattr(self, table).set_data(data)
        getattr(self, graph).create_marks(mark)

    def measure_data(self, data):
        side = data["curve"][0]
        side = 0 if side == 'R' else 1
        side_letter = 'r' if side == 0 else 'l'
        self.current_measuring[side] = data['data']
        label = f"lbl_coord_{side_letter}"

        for key in data['data']:
            if isinstance(data['data'][key], float):  # Solo redondear si el valor es un flotante
                data['data'][key] = round(data['data'][key], 1)

        getattr(self,label).setText(f'{data}')

    def active_advance_setting(self):
        self.dialog = QDialog(self)
        self.ui = Ui_AdvanceSettings()
        self.ui.setupUi(self.dialog)
        self.dialog.exec()

################INTERCAMBIO
    def memory_curves(self, value=None, side=None):
        if isinstance(value, tuple):
            c,cmd,val = value
            key = 'LatAmp' if cmd == 'L' or cmd == 'A' else 'InterPeaks'
            column = 0 if cmd == 'L' else 1
        model = {'LatAmp':{'I':[None,None], 'II':[None,None],'III':[None,None],'IV':[None,None],'V':[None,None]}}
        if side:
            graph = f'graph_{side}'
            name_curve = getattr(self,graph).act_curve
            if value is not None:
                self.memory[name_curve][key][c][column] = val
        else:
            name_curve = self.current_capture_curve
            sett = self.current_setting
            self.memory[name_curve] = dict(sett, **model)
        self.detail_all.process_and_fill_data(self.memory)

################Report
    def report_svg(self):
        self.graph_lat_int.export_()
        self.graph_r.export_()
        self.graph_l.export_()
        text1 = self.report.text_edit_1.toHtml()
        text2 = self.report.text_edit_2.toHtml()
        image_r = context.get_resource('temp/0.png')
        image_l = context.get_resource('temp/1.png')
        image_lat = context.get_resource('temp/LatInt.png')
        file_pdf = context.get_resource('temp/GFG.pdf')
        evaluator = self.report.le_eva.text()
        PDFCreator(title="PEATC", html1=text1, html2=text2, images=[image_r,image_l], image_lat=image_lat,data_dict=self.memory, output=file_pdf, evaluator=evaluator)



    def test_test(self, side):

        n_1 = {"lat": [1.6, 3.7, 5.6], "amp":[.5, 1], "repro": True, "morfo": [True, True, True], "th":20, "type" : "normal"}
        n_2 = {"lat": [1.7,3.8, 5.7], "amp":[.4, .5], "repro": True, "morfo": [True, True, True], "th":30, "type" : "normal"}
        n_3 = {"lat": [1.6, 3.5, 5.5], "amp":[.4, .4], "repro": True, "morfo": [True, True, True], "th":10, "type" : "normal"}
        c_1 = {"lat": [1.78, 3.79, 5.95], "amp":[.1, 1], "repro": True, "morfo": [False, True, True], "th":60, "type" : "coclear"}
        c_2 = {"lat": [1.78, 3.79, 5.95], "amp":[.2, 1], "repro": True, "morfo": [False, True, True], "th":70, "type" : "coclear"}
        c_3 = {"lat": [1.78, 3.79, 5.85], "amp":[1, 1], "repro": True, "morfo": [False, True, True], "th":40, "type" : "coclear"}
        t_1 = {"lat": [2.0, 4.4, 6.5], "amp":[.5, .5], "repro": True, "morfo": [True, True, True], "th":60, "type" : "transmission"}
        t_2 = {"lat": [3.1, 5.1, 6.9], "amp":[.4, .5], "repro": True, "morfo": [True, True, True], "th":70, "type" : "transmission"}
        m_1 = {"lat": [1.8, 3.5, 7.2], "amp":[.7, .9], "repro": True, "morfo": [True, True, True], "th":70, "type" : "neural"}
        m_2 = {"lat": [1.7, 4, 6], "amp":[.3, .8], "repro": False, "morfo": [True, False, True], "th":60, "type" : "neural"}
        m_3 = {"lat": [1.6, 4.4, 6.8], "amp":[.5, .9], "repro": False, "morfo": [False, True, True], "th":70, "type" : "neural"}

        cases = [[n_1,n_2],[n_1,m_2],[n_3,m_3],[c_1,m_1],[m_2,c_2],[c_3,m_3],[n_1,t_1],
                 [t_2,t_1],[n_1,c_1],[c_2,n_2],[n_3,c_3],[n_1,t_2],[t_2,n_2],[c_1,n_1],
                 [t_1,t_2],[m_1,n_3],[c_1,m_2],[m_3,n_1],[t_2,n_1],[c_2,n_3],[m_3,c_2],
                 [c_3,n_2],[n_2,m_1],[m_1,n_2],[n_1,m_2],[m_2,n_3]]

        #8, 10, 26
        
        case = cases[self.case][0] if side == "OD" else cases[self.case][1]
        if case["repro"] == False:
            side_letter = 'r' if side == 0 else 'l'
            graph = f"graph_{side_letter}"
            repro_prev = getattr(self, graph).get_data(self.current_setting["int"])
            if repro_prev == None:
                repro_prev = 0
        else:
            repro_prev = 0


        x,y, dx, dy, repro = ABR_Curve(self.current_setting["int"], self.current_setting, case, repro_prev, [(self.count_averages*self.total_averages)*2.5, self.current_setting['average']], done = self.done)
        return(x,y),(dx,dy),(0,0),(0,0), repro
    
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
