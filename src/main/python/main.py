# -*- coding: utf-8 -*-
#################################################################
#                                                               #
#                  NOMBRE PROYECTO : LabSim                     #
#                          VER. 0.7.5                           #
#               CREADOR : NICOLÁS QUEZADA QUEZADA               #
#                                                               #
#################################################################

import json
import random
import sys

from base import context
from lib.ABR_generator_2 import ABR_Curve
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
from PySide6.QtCore import QCoreApplication, Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QComboBox, QDialog, QFrame, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QSizePolicy,
                               QSpacerItem, QTextEdit, QVBoxLayout,
                               QMessageBox)
from UI.AbrAdvanceSettings_ui import Ui_AdvanceSettings
from UI.AbrMain_ui import Ui_MainWindow
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from lib.convinaciones import elegir_combinacion_especifica, casos, namecasos

tr = QCoreApplication.translate

STATE_INIT = "exam"


class JSONFileHandler(FileSystemEventHandler):
    def __init__(self, json_file_path, callback):
        super().__init__()
        self.json_file_path = json_file_path
        self.callback = callback

    def on_modified(self, event):
        if event.src_path == self.json_file_path:
            print(f"El archivo JSON ha sido modificado: {event.src_path}")
            self.callback()



class IsOver(QDialog):
    def __init__(self, parent=None):
        super(IsOver, self).__init__(parent)

        # Configuraciones de la ventana modal
        self.setWindowTitle("Tiempo Acabado")
        self.setModal(True)  # Hace la ventana modal
        self.setFixedSize(300, 100)  # Tamaño fijo de la ventana

        # Inicialización de Widgets
        layout = QVBoxLayout(self)
        label = QLabel("El tiempo se ha acabado, verifique con el docente su caso", self)
        next_case_button = QPushButton("Siguiente caso", self)
        next_case_button.clicked.connect(self.on_next_case)

        # Agregar Widgets al layout
        layout.addWidget(label)
        layout.addWidget(next_case_button)

    def on_next_case(self):
        # Acción cuando se hace clic en 'Siguiente caso'
        #print("Preparando el siguiente caso...")
        self.accept()  # Cierra la ventana modal



class ModeP(QDialog):
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
        self.center_on_screen()


    def center_on_screen(self):
        # Obtener la resolución de la pantalla
        screen_resolution = QGuiApplication.primaryScreen().geometry()

        # Calcular la posición central para el diálogo
        x = (screen_resolution.width() - self.width()) / 2
        y = (screen_resolution.height() - self.height()) / 2

        # Establecer la posición del diálogo en el centro de la pantalla
        self.move(x, y)

    def create_list(self):
        for i in range(26):
            self.combo_box.addItem(f'Caso {i+1}')

    def on_accept_clicked(self):
        chosen_option = self.combo_box.currentText()
        print(f"Has seleccionado: {chosen_option}")
        self.accept()  # Esto cerrará la ventana de diálogo
        return self.combo_box.currentIndex()


class ModeEva(QDialog):
    def __init__(self, parent=None, x_numero = None):
        super().__init__(parent)
        self.setWindowTitle('Comenzar Evaluación')

        # Hacer que la ventana sea modal
        self.setModal(True)

        # Crear el ComboBox y el botón dentro de la ventana de diálogo
        layout = QVBoxLayout(self)
        text = QTextEdit("""<p style="text-align: center;"><strong>Incio de evaluaci&oacute;n </strong></p>
<p style="text-align: justify;">A continuaci&oacute;n posee 35 minutos para la realizaci&oacute;n de un caso cl&iacute;nico aleatorio.</p>
<p style="text-align: justify;">Favor ponga su nombre a continuaci&oacute;n:</p>
<p style="text-align: justify;">&nbsp;</p>
<p style="text-align: justify;">*el numero debajo es el caso seleccionado automaticamente para esta prueba, si este fuese el mismo favor solicitar el cambio al docente</p>
                         """)
        text.setReadOnly(True)
        text.setFrameShape(QFrame.NoFrame)
        text.setReadOnly(True)
        text.setTextInteractionFlags(Qt.NoTextInteraction)
        layout.addWidget(text)
        self.name = QLineEdit()
        self.name.setPlaceholderText("Nombre Completo")
        layout.addWidget(self.name)
        
        #self.case = self.generar_numero_aleatorio(x_numeros=x_numero)
        self.case = elegir_combinacion_especifica()
        case = self.actualizar_label()
        layout.addWidget(case)

        self.accept_button = QPushButton("Iniciar")
        self.accept_button.clicked.connect(self.on_accept_clicked)
        layout.addWidget(self.accept_button)
        self.center_on_screen()

    def actualizar_label(self):
        # Convertir todos los elementos a string y sumar 1 a cada uno
        casos_formato = [str(caso + 1) for caso in self.case]

        if len(casos_formato) > 1:
            # Si hay más de un elemento, inserta 'y' antes del último elemento
            casos_texto = ", ".join(casos_formato[:-1]) + " y " + casos_formato[-1]
        else:
            # Si solo hay un elemento, solo usa ese elemento
            casos_texto = casos_formato[0]

        return QLabel(f"Casos: {casos_texto}")


    def center_on_screen(self):
        # Obtener la resolución de la pantalla
        screen_resolution = QGuiApplication.primaryScreen().geometry()

        # Calcular la posición central para el diálogo
        x = (screen_resolution.width() - self.width()) / 2
        y = (screen_resolution.height() - self.height()) / 2

        # Establecer la posición del diálogo en el centro de la pantalla
        self.move(x, y)


    def generar_numero_aleatorio(self, minimo=0, maximo=1,  x_numeros=2):
        if minimo > maximo:
            minimo, maximo = maximo, minimo  # Intercambiar los valores si minimo es mayor que maximo

        if x_numeros > (maximo - minimo + 1):
            raise ValueError("No es posible generar la cantidad solicitada de números únicos en el rango dado")

        numeros_generados = set()

        while len(numeros_generados) < x_numeros:
            numero = random.randint(minimo, maximo)
            numeros_generados.add(numero)

        return list(numeros_generados)

    def create_list(self):
        for i in range(26):
            self.combo_box.addItem(f'Caso {i+1}')

    def on_accept_clicked(self):
        if not self.name.text().strip():
            # Si el campo 'name' está vacío, mostrar un mensaje de error
            QMessageBox.warning(self, "Error", "Por favor, ingrese su nombre.")
        else:
            # Si 'name' tiene un valor, cerrar la ventana
            self.accept()  # Esto cerrará la ventana de diálogo
            return self.case
    
    def reject(self):
        # Se llama cuando se presiona Escape. Evita que la ventana se cierre.
        # Puedes dejarlo vacío o mostrar un mensaje, según tus necesidades.
        pass

    def closeEvent(self, event):
        # Se llama cuando se intenta cerrar la ventana (p. ej., con Alt+F4).
        if not self.name.text().strip():
            # Si el campo 'name' está vacío, rechazar el evento de cierre
            QMessageBox.warning(self, "Error", "Por favor, ingrese su nombre antes de cerrar.")
            event.ignore()  # Ignora el evento de cierre
        else:
            event.accept()  # Acepta el evento de cierre


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("simPeatc")
        self.showFullScreen()

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

        self.btn_next_case.hide()
        self.btn_next_case.clicked.connect(self.force_next)

        ######Variables de Estado
        self.control.capture.connect(self.capture_state)
        self.state_capture = "stopped"
        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.capture)
        self.timer = QTimer()
        self.time_eva = 35*60
        self.segundos_restantes = self.time_eva
        self.timer.timeout.connect(self.actualizar_tiempo)
        self.n_cases = 2
        self.current_case = 0

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

        ##########Data Base
        self.json_file_path = 'cases.json'
        self.data = self.cargar_json(self.json_file_path)

        #########TEMP TEST
        self.count_averages = 0

        self.open_modal()
        self.inicializar_observador()

    def force_next(self):
        self.segundos_restantes = 1

    def actualizar_tiempo(self):
        minutos = self.segundos_restantes // 60
        segundos = self.segundos_restantes % 60
        tiempo_formateado = f"{minutos:02}:{segundos:02}"

        if self.segundos_restantes <= 300:  # Menos de 5 minutos (300 segundos)
            self.lbl_time.setStyleSheet("color: red;")
        else:
            self.lbl_time.setStyleSheet("")  # Restablecer el estilo por defecto

        if self.segundos_restantes <= 1200:
            self.btn_next_case.show()

        self.lbl_time.setText(tiempo_formateado)

        if self.segundos_restantes == 0:
            self.timer.stop()
            next = IsOver(self)
            self.autosave()
            next.exec()
            self.reset()
            self.reset_and_reload()
            self.case = self.cases[1]
            self.report.case = self.cases[1]

        else:
            self.segundos_restantes -= 1

    def autosave(self):
        self.report_svg()
        self.report.save_file_auto()

    def reset(self):
        for i in self.curves_R:
            self.update_delete_curve(i)
            letter = 'r' if i[0] == 'R' else 'l'
            graph = f'graph_{letter}'
            getattr(self, graph).active_curve(i)
            getattr(self, graph).delete_curve()
        for i in self.curves_L:
            self.update_delete_curve(i)
            letter = 'r' if i[0] == 'R' else 'l'
            graph = f'graph_{letter}'
            getattr(self, graph).active_curve(i)
            getattr(self, graph).delete_curve()


    def reset_and_reload(self):
        self.current_case += 1 
        if self.current_case < len(self.cases): 
            self.lbl_info.setText(f"Estamos evaluando el caso {self.cases[self.current_case]+1}")
            self.segundos_restantes = self.time_eva
            self.btn_next_case.hide()
            self.timer.start()


        else:
            self.lbl_info.setText(f"Se acabaron los casos, fin de la partida")
            

    def open_modal(self):
        # Esta función crea y abre la ventana de diálogo
        if STATE_INIT == "exam":
            dialog = ModeEva(self, x_numero=self.n_cases)
            exam = True
        else:
            dialog = ModeP(self)
            exam = False

        dialog.exec()

        if exam:
            self.cases = dialog.case
            name_user = dialog.name.text()
            self.report.set_le_eva(name_user)
        
        else:
            self.case = dialog.combo_box.currentIndex()
        
        self.report.case = self.cases[0]
        self.case = self.cases[0]
        self.lbl_info.setText(f"Estamos evaluando el caso {self.cases[self.current_case]+1}")
        self.timer.start(1000)


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
            self.capture_timer.start(200)
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

        """
        morfología : presencia de ondas I,III,V
        replicabilidad : +- 0.1 ms
        Latencias Absolutas a 75: +-0.2ms
            - I : 1.6 ms
            -III: 3.7 ms
            -V: 5.6 ms
        Interonda +-0.4 ms
            -I-III : 2.0ms
            -III-V : 1.8ms
            -I-V : 3.8 ms

        desviación de latencias sobre los 50dB: 0.3ms / 10dB
        desviación de latencia onda V en cambio de tasa: desde los 0.6 a 0.8
        Ratio V/I  : mayor a 1
        interaural diferencia : menor que 0.4

        """


        #8, 10, 26
        side = 0 if side == "OD" else 1

        case = casos(self.case, side)
        #case = casos(27, side)
        #print(namecasos(26))

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
    
################data

    def cargar_json(self, json_file_path):
        data = context.get_resource(f'cases/{json_file_path}')
        with open(data, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)


    def inicializar_observador(self):
        # Inicializar el observador de cambios
        self.observer = Observer()
        data = context.get_resource(f'cases/{self.json_file_path}')

        handler = JSONFileHandler(data, self.actualizar_datos)
        self.observer.schedule(handler, path='.', recursive=False)
        self.observer.start()
    
    def actualizar_datos(self):
        self.data = self.cargar_json(self.json_file_path)
        if self.data:
            print("se actualizo")

    #########EVENTS
    def closeEvent(self, event):
        # Detener el observador de cambios cuando se cierre la ventana
        self.observer.stop()
        self.observer.join()
        event.accept()



if __name__ == '__main__':
    window = MainWindow()
    style_file = context.get_resource('qss/style_base.qss')

    with open(style_file, 'r', encoding='utf-8') as f:
        style = f.read()
           
    window.setStyleSheet(style)
    window.show()
    
    exit_code = context.app.exec()
    
    sys.exit(exit_code)
