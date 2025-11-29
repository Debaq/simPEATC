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
from lib.ABR_generator_v2 import ABR_Curve
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
from PySide6.QtCore import QCoreApplication, Qt, QTimer, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QComboBox, QDialog, QFrame, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QSizePolicy,
                               QSpacerItem, QTextEdit, QVBoxLayout,
                               QMessageBox)
from UI.AbrAdvanceSettings_ui import Ui_AdvanceSettings
from UI.AbrMain_ui import Ui_MainWindow
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from lib.conbinaciones import elegir_combinacion_especifica, casos, namecasos, combinaciones
from verificacion import verificar_activacion

tr = QCoreApplication.translate

STATE_INIT = "osce"  # Cambiado a modo OSCE por defecto
TIEMPO_TEST = 40
TIEMPO_ESTACION_OSCE = 5  # 5 minutos por estación en modo OSCE
TIEMPO_ENTR_PROM = 300
N_CASES = 2
N_ESTACIONES = 3  # Número de estaciones OSCE

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
    def __init__(self, parent=None, modo_osce=False, estacion=None):
        super(IsOver, self).__init__(parent)

        # Configuraciones de la ventana modal
        self.setWindowTitle("Tiempo Acabado")
        self.setModal(True)  # Hace la ventana modal
        self.setFixedSize(350, 150)  # Tamaño fijo de la ventana
        self.modo_osce = modo_osce
        self.estacion = estacion

        # Inicialización de Widgets
        layout = QVBoxLayout(self)

        if modo_osce:
            if estacion:
                label = QLabel(f"Estación {estacion} completada.\n\n"
                              "Por favor, diríjase a la siguiente estación.", self)
            else:
                label = QLabel("Tiempo completado.", self)
            label.setWordWrap(True)
            next_case_button = QPushButton("Continuar", self)
        else:
            label = QLabel("El tiempo se ha acabado, verifique con el docente su caso", self)
            next_case_button = QPushButton("Siguiente caso", self)

        label.setAlignment(Qt.AlignCenter)
        next_case_button.clicked.connect(self.on_next_case)

        # Agregar Widgets al layout
        layout.addWidget(label)
        layout.addWidget(next_case_button)

    def on_next_case(self):
        # Acción cuando se hace clic en 'Siguiente caso'
        print("Preparando el siguiente caso...")
        self.accept()  # Cierra la ventana modal

    def reject(self):
        # Evita que se cierre con Escape
        pass

    def closeEvent(self, event):
        # Evita que se cierre con Alt+F4
        event.ignore()



class CuadroDialogoTest(QDialog):
    cambio_case = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Selección de casos')

        # Hacer que la ventana sea modal
        self.setModal(True)

        # Crear el ComboBox y el botón dentro de la ventana de diálogo
        layout = QVBoxLayout(self)

        self.combo_box = QComboBox()
        self.create_list(len(combinaciones))  # En lugar de N_CASES
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

    def create_list(self, n):
        for i in range(n):
            self.combo_box.addItem(f'Caso {i+1}')

    def on_accept_clicked(self):
        chosen_option = self.combo_box.currentText()
        print(f"Has seleccionado: {chosen_option}")
        self.accept()  # Esto cerrará la ventana de diálogo
        self.cambio_case.emit(self.combo_box.currentIndex())
        return self.combo_box.currentIndex()


class CuadroDialogoOSCE(QDialog):
    """Ventana de selección para evaluación OSCE con 3 estaciones"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Evaluación OSCE - PEATC')

        # Hacer que la ventana sea modal y no se pueda cerrar
        self.setModal(True)
        self.setFixedSize(400, 300)

        # Variables de estado
        self.estaciones_completadas = []
        self.estacion_seleccionada = None

        # Layout principal
        layout = QVBoxLayout(self)

        # Título
        titulo = QLabel("<h2 style='text-align: center;'>Evaluación OSCE - PEATC</h2>")
        layout.addWidget(titulo)

        # Instrucciones
        instrucciones = QLabel(
            "<p style='text-align: center;'>Seleccione la estación correspondiente<br>"
            "Cada estación tiene 5 minutos de duración</p>"
        )
        layout.addWidget(instrucciones)

        # Espacio
        layout.addSpacing(20)

        # Botones de estaciones
        self.btn_estacion_3 = QPushButton("ESTACIÓN 3")
        self.btn_estacion_3.setFixedHeight(50)
        self.btn_estacion_3.clicked.connect(lambda: self.seleccionar_estacion(3))
        layout.addWidget(self.btn_estacion_3)

        self.btn_estacion_4 = QPushButton("ESTACIÓN 4")
        self.btn_estacion_4.setFixedHeight(50)
        self.btn_estacion_4.setEnabled(False)  # Deshabilitado inicialmente
        self.btn_estacion_4.clicked.connect(lambda: self.seleccionar_estacion(4))
        layout.addWidget(self.btn_estacion_4)

        self.btn_estacion_5 = QPushButton("ESTACIÓN 5")
        self.btn_estacion_5.setFixedHeight(50)
        self.btn_estacion_5.setEnabled(False)  # Deshabilitado inicialmente
        self.btn_estacion_5.clicked.connect(lambda: self.seleccionar_estacion(5))
        layout.addWidget(self.btn_estacion_5)

        # Label de estado
        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.lbl_estado)

        self.center_on_screen()

    def seleccionar_estacion(self, numero_estacion):
        """Maneja la selección de una estación"""
        self.estacion_seleccionada = numero_estacion
        self.accept()

    def marcar_estacion_completada(self, numero_estacion):
        """Marca una estación como completada y habilita la siguiente"""
        if numero_estacion not in self.estaciones_completadas:
            self.estaciones_completadas.append(numero_estacion)

        # Actualizar botones
        if numero_estacion == 3:
            self.btn_estacion_3.setEnabled(False)
            self.btn_estacion_3.setText("ESTACIÓN 3 ✓")
            self.btn_estacion_4.setEnabled(True)
            self.lbl_estado.setText("Estación 3 completada. Continúe con Estación 4")
        elif numero_estacion == 4:
            self.btn_estacion_4.setEnabled(False)
            self.btn_estacion_4.setText("ESTACIÓN 4 ✓")
            self.btn_estacion_5.setEnabled(True)
            self.lbl_estado.setText("Estación 4 completada. Continúe con Estación 5")
        elif numero_estacion == 5:
            self.btn_estacion_5.setEnabled(False)
            self.btn_estacion_5.setText("ESTACIÓN 5 ✓")
            self.lbl_estado.setText("¡Todas las estaciones completadas!")

    def todas_completadas(self):
        """Verifica si todas las estaciones están completadas"""
        return len(self.estaciones_completadas) == 3

    def center_on_screen(self):
        # Obtener la resolución de la pantalla
        screen_resolution = QGuiApplication.primaryScreen().geometry()

        # Calcular la posición central para el diálogo
        x = (screen_resolution.width() - self.width()) / 2
        y = (screen_resolution.height() - self.height()) / 2

        # Establecer la posición del diálogo en el centro de la pantalla
        self.move(x, y)

    def reject(self):
        # Evita que se cierre con Escape
        pass

    def closeEvent(self, event):
        # Evita que se cierre con Alt+F4
        event.ignore()


class CuadroDialogoExamen(QDialog):
    def __init__(self, parent=None, x_numero = None):
        super().__init__(parent)
        self.setWindowTitle('Comenzar PEATC')

        # Hacer que la ventana sea modal
        self.setModal(True)

        # Crear el ComboBox y el botón dentro de la ventana de diálogo
        layout = QVBoxLayout(self)
        text = QTextEdit(f"""<p style="text-align: center;"><strong>Inicio de PEATC</strong></p>
<p style="text-align: justify;">A continuaci&oacute;n posee {TIEMPO_TEST} minutos para la realizaci&oacute;n de cada caso de un total de 2</p>
<p style="text-align: justify;">Favor ponga su nombre a continuaci&oacute;n:</p>
<p style="text-align: justify;">&nbsp;</p>
<p style="text-align: justify;">*estos casos no son aleatorios son los correspondientes al práctico</p>
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
        #self.showFullScreen()

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

        self.report.type_use = STATE_INIT

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

        # Crear botones de navegación OSCE (se crearán dinámicamente)
        self.crear_botones_navegacion_osce()

        ######Variables de Estado
        self.control.capture.connect(self.capture_state)
        self.state_capture = "stopped"
        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.capture)
        self.timer = QTimer()
        self.time_eva = TIEMPO_TEST*60
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

        ########## OSCE Variables
        self.modo_osce = (STATE_INIT == "osce")
        self.estacion_actual = None
        self.caso_actual = 1  # Caso actual dentro de la estación (1, 2 o 3)
        self.dialog_osce = None

        # Estructura: Estación -> Caso -> Datos
        self.datos_estaciones = {
            3: {
                'casos': {
                    1: {'memory': {}, 'configuracion': {}, 'completado': False},
                    2: {'memory': {}, 'configuracion': {}, 'completado': False},
                    3: {'memory': {}, 'configuracion': {}, 'completado': False}
                },
                'completada': False
            },
            4: {
                'casos': {
                    1: {'memory': {}, 'case_id': None, 'completado': False},  # OD:Normal OI:Transmisión
                    2: {'memory': {}, 'case_id': None, 'completado': False},  # OD:Coclear OI:Normal
                    3: {'memory': {}, 'case_id': None, 'completado': False}   # OD:Neural OI:Neural
                },
                'completada': False
            },
            5: {
                'casos': {
                    3: {'memory': {}, 'case_id': None, 'completado': False}   # Solo caso 3 de estación 4
                },
                'completada': False,
                'hereda_de_estacion_4': True
            }
        }

        # Botones de navegación OSCE
        self.btn_caso_anterior = None
        self.btn_caso_siguiente = None

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

        if self.segundos_restantes <= 1200 and not self.modo_osce:
            self.btn_next_case.show()

        self.lbl_time.setText(tiempo_formateado)

        if self.segundos_restantes == 0:
            self.timer.stop()

            if self.modo_osce:
                # Modo OSCE: guardar datos de la estación y mostrar ventana
                self.guardar_datos_estacion()
                next = IsOver(self, modo_osce=True, estacion=self.estacion_actual)
                next.exec()
                self.reset()
                # Volver a mostrar el diálogo de estaciones
                self.abrir_dialogo_osce()
            else:
                # Modo examen tradicional
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

        if STATE_INIT == "exam":
            self.current_case += 1 
            if self.current_case < len(self.cases): 
                self.lbl_info.setText(f"Estamos evaluando el caso {self.cases[self.current_case]+1}")
                self.segundos_restantes = self.time_eva
                self.btn_next_case.hide()
                self.timer.start()


            else:
                self.lbl_info.setText(f"Se acabaron los casos, fin de la partida")

        else:
            self.btn_next_case.setText(f"Estamos evaluando el caso {self.cases+1}")
            self.btn_next_case.setDisabled(True)
            self.reset()
            

                

    def open_modal(self):
        # Esta función crea y abre la ventana de diálogo
        if STATE_INIT == "osce":
            # Modo OSCE
            self.abrir_dialogo_osce()
        elif STATE_INIT == "exam":
            dialog = CuadroDialogoExamen(self, x_numero=self.n_cases)
            exam = True
            dialog.exec()
            self.cases = dialog.case
            name_user = dialog.name.text()
            self.report.set_le_eva(name_user)
            self.report.case = self.cases[0]
            self.case = self.cases[0]
            self.lbl_info.setText(f"Estamos evaluando el caso {self.cases[self.current_case]+1}")
            self.timer.start(1000)
        else:
            dialog = CuadroDialogoTest(self)
            dialog.cambio_case.connect(self.cambiodecaso)
            dialog.exec()
            self.case = dialog.combo_box.currentIndex()
            self.timer.start(1000)



    def cambiodecaso(self, data):
        self.cases= data
        self.reset_and_reload()

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
            self.capture_timer.start(TIEMPO_ENTR_PROM)
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

    def get_advance_settings_data(self):
        """Obtiene los datos de parámetros avanzados"""
        if hasattr(self, 'ui') and self.ui:
            return {
                'transductor': self.ui.comboBox.currentText(),
                'ventana': self.ui.spinBox.value(),
                'fsp': self.ui.comboBox_2.currentText(),
                'ruido_residual': self.ui.comboBox_3.currentText(),
                'electrodo_vertex': self.ui.comboBox_4.currentText(),
                'electrodo_derecho': self.ui.comboBox_5.currentText(),
                'electrodo_izquierdo': self.ui.comboBox_6.currentText(),
                'electrodo_tierra': self.ui.comboBox_7.currentText()
            }
        else:
            # Valores por defecto si no se han configurado
            return {
                'transductor': 'Fono inserción',
                'ventana': 12,
                'fsp': 'Detección 99% y FSP de 3.1',
                'ruido_residual': '40nV',
                'electrodo_vertex': 'Cz',
                'electrodo_derecho': 'A1',
                'electrodo_izquierdo': 'A2',
                'electrodo_tierra': 'Cz'
            }

    def set_advance_settings_data(self, config):
        """Aplica configuración a los parámetros avanzados"""
        if not hasattr(self, 'ui') or not self.ui:
            # Crear el diálogo si no existe
            self.dialog = QDialog(self)
            self.ui = Ui_AdvanceSettings()
            self.ui.setupUi(self.dialog)

        # Aplicar valores
        if 'transductor' in config:
            idx = self.ui.comboBox.findText(config['transductor'])
            if idx >= 0:
                self.ui.comboBox.setCurrentIndex(idx)

        if 'ventana' in config:
            self.ui.spinBox.setValue(config['ventana'])

        if 'fsp' in config:
            idx = self.ui.comboBox_2.findText(config['fsp'])
            if idx >= 0:
                self.ui.comboBox_2.setCurrentIndex(idx)

        if 'ruido_residual' in config:
            idx = self.ui.comboBox_3.findText(config['ruido_residual'])
            if idx >= 0:
                self.ui.comboBox_3.setCurrentIndex(idx)

        if 'electrodo_vertex' in config:
            idx = self.ui.comboBox_4.findText(config['electrodo_vertex'])
            if idx >= 0:
                self.ui.comboBox_4.setCurrentIndex(idx)

        if 'electrodo_derecho' in config:
            idx = self.ui.comboBox_5.findText(config['electrodo_derecho'])
            if idx >= 0:
                self.ui.comboBox_5.setCurrentIndex(idx)

        if 'electrodo_izquierdo' in config:
            idx = self.ui.comboBox_6.findText(config['electrodo_izquierdo'])
            if idx >= 0:
                self.ui.comboBox_6.setCurrentIndex(idx)

        if 'electrodo_tierra' in config:
            idx = self.ui.comboBox_7.findText(config['electrodo_tierra'])
            if idx >= 0:
                self.ui.comboBox_7.setCurrentIndex(idx)

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
        pass
        # Inicializar el observador de cambios
        #self.observer = Observer()
        #data = context.get_resource(f'cases/{self.json_file_path}')

        #handler = JSONFileHandler(data, self.actualizar_datos)
        #self.observer.schedule(handler, path='.', recursive=False)
        #self.observer.start()
    
    def actualizar_datos(self):
        self.data = self.cargar_json(self.json_file_path)
        if self.data:
            print("se actualizo")

    ################METODOS OSCE

    def crear_botones_navegacion_osce(self):
        """Crea los botones de navegación entre casos para OSCE"""
        try:
            # El horizontalLayout ya existe como atributo después de setupUi()
            # Lo accedemos directamente
            layout = self.horizontalLayout

            if layout is None:
                print("Error: horizontalLayout es None")
                return

            # Crear botón "Caso Anterior"
            self.btn_caso_anterior = QPushButton("◀ Anterior", self.centralwidget)
            self.btn_caso_anterior.setFixedHeight(30)
            self.btn_caso_anterior.setMaximumWidth(100)
            self.btn_caso_anterior.clicked.connect(self.ir_caso_anterior)

            # Crear botón "Caso Siguiente"
            self.btn_caso_siguiente = QPushButton("Siguiente ▶", self.centralwidget)
            self.btn_caso_siguiente.setFixedHeight(30)
            self.btn_caso_siguiente.setMaximumWidth(100)
            self.btn_caso_siguiente.clicked.connect(self.ir_caso_siguiente)

            # Insertar botones en el layout (después de lbl_time y antes de btn_next_case)
            # El orden será: [lbl_info] [spacer] [lbl_time] [btn_caso_anterior] [btn_caso_siguiente] [btn_next_case] [spacer]
            index = layout.indexOf(self.btn_next_case)
            if index >= 0:
                layout.insertWidget(index, self.btn_caso_anterior)
                layout.insertWidget(index + 1, self.btn_caso_siguiente)
            else:
                # Si no encuentra btn_next_case, agregar al final
                layout.addWidget(self.btn_caso_anterior)
                layout.addWidget(self.btn_caso_siguiente)

        except Exception as e:
            print(f"Error al crear botones de navegación OSCE: {e}")
            import traceback
            traceback.print_exc()

    def actualizar_botones_navegacion(self):
        """Actualiza el estado de los botones de navegación según el caso actual"""
        # Verificar que los botones existen
        if self.btn_caso_anterior is None or self.btn_caso_siguiente is None:
            return

        if not self.modo_osce or self.estacion_actual is None:
            self.btn_caso_anterior.hide()
            self.btn_caso_siguiente.hide()
            return

        # Estación 5 solo tiene 1 caso, no hay navegación
        if self.estacion_actual == 5:
            self.btn_caso_anterior.hide()
            self.btn_caso_siguiente.hide()
            # Mostrar info en btn_next_case
            self.btn_next_case.setText(f"Estación {self.estacion_actual}")
            self.btn_next_case.show()
            return

        # Estaciones 3 y 4: Mostrar botones de navegación
        self.btn_caso_anterior.show()
        self.btn_caso_siguiente.show()

        # Habilitar/deshabilitar según caso actual
        if self.caso_actual == 1:
            self.btn_caso_anterior.setEnabled(False)
            self.btn_caso_siguiente.setEnabled(True)
        elif self.caso_actual == 3:
            self.btn_caso_anterior.setEnabled(True)
            self.btn_caso_siguiente.setEnabled(False)
        else:  # caso 2
            self.btn_caso_anterior.setEnabled(True)
            self.btn_caso_siguiente.setEnabled(True)

        # Ocultar btn_next_case en modo OSCE (solo mostrar botones de navegación)
        self.btn_next_case.hide()

    def ir_caso_anterior(self):
        """Navega al caso anterior dentro de la estación"""
        if self.caso_actual > 1:
            self.guardar_caso_actual()
            self.caso_actual -= 1
            self.cargar_caso(self.estacion_actual, self.caso_actual)

    def ir_caso_siguiente(self):
        """Navega al caso siguiente dentro de la estación"""
        if self.caso_actual < 3:
            self.guardar_caso_actual()
            self.caso_actual += 1
            self.cargar_caso(self.estacion_actual, self.caso_actual)

    def guardar_caso_actual(self):
        """Guarda los datos del caso actual antes de cambiar"""
        if self.estacion_actual is None:
            return

        import copy

        print("\n" + "="*80)
        print(f"📦 GUARDANDO DATOS - Estación {self.estacion_actual} - Caso {self.caso_actual}")
        print("="*80)

        # Guardar memoria actual
        caso_data = self.datos_estaciones[self.estacion_actual]['casos'][self.caso_actual]
        caso_data['memory'] = copy.deepcopy(self.memory)
        caso_data['completado'] = True

        # Imprimir información de la memoria guardada
        print(f"\n📊 MEMORIA GUARDADA:")
        print(f"   - Curvas OD (R): {[k for k in self.memory.keys() if k.startswith('R')]}")
        print(f"   - Curvas OI (L): {[k for k in self.memory.keys() if k.startswith('L')]}")
        print(f"   - Total de curvas: {len(self.memory)}")

        # Detalles de cada curva
        for curve_id, curve_data in self.memory.items():
            print(f"\n   Curva {curve_id}:")
            print(f"      • Lado: {curve_data.get('side', 'N/A')}")
            print(f"      • Intensidad: {curve_data.get('int', 'N/A')} dB")
            print(f"      • Promediaciones: {curve_data.get('average', 'N/A')}")
            if 'LatAmp' in curve_data:
                lat_amp = curve_data['LatAmp']
                ondas_marcadas = [onda for onda in ['I', 'II', 'III', 'IV', 'V'] if onda in lat_amp and lat_amp[onda]]
                print(f"      • Ondas marcadas: {ondas_marcadas}")
                for onda in ondas_marcadas:
                    if lat_amp[onda]:
                        print(f"         - Onda {onda}: Lat={lat_amp[onda][0]:.2f}ms, Amp={lat_amp[onda][1]:.2f}μV")

        # En estación 3, guardar configuración de parámetros
        if self.estacion_actual == 3:
            config = self.control.get_data()
            advance_config = self.get_advance_settings_data()

            # Combinar configuración básica y avanzada
            caso_data['configuracion'] = {**config, **advance_config}

            print(f"\n⚙️  CONFIGURACIÓN GUARDADA (Estación 3):")
            print(f"   PARÁMETROS BÁSICOS:")
            print(f"   - Estímulo: {config.get('stim', 'N/A')}")
            print(f"   - Polaridad: {config.get('pol', 'N/A')}")
            print(f"   - Intensidad: {config.get('int', 'N/A')} dB")
            print(f"   - Masking: {config.get('mkg', 'N/A')} dB")
            print(f"   - Rate: {config.get('rate', 'N/A')} Hz")
            print(f"   - Promediaciones: {config.get('average', 'N/A')}")
            print(f"   - Lado: {config.get('side', 'N/A')}")
            print(f"   - Filtro paso bajo: {config.get('filter_down', 'N/A')} Hz")
            print(f"   - Filtro paso alto: {config.get('filter_passhigh', 'N/A')} Hz")
            print(f"   - Atenuación: {config.get('atten', 'N/A')}")

            print(f"\n   PARÁMETROS AVANZADOS:")
            print(f"   - Transductor: {advance_config.get('transductor', 'N/A')}")
            print(f"   - Ventana: {advance_config.get('ventana', 'N/A')} ms")
            print(f"   - FSP: {advance_config.get('fsp', 'N/A')}")
            print(f"   - Ruido residual: {advance_config.get('ruido_residual', 'N/A')}")
            print(f"   - Electrodo Vertex: {advance_config.get('electrodo_vertex', 'N/A')}")
            print(f"   - Electrodo Derecho: {advance_config.get('electrodo_derecho', 'N/A')}")
            print(f"   - Electrodo Izquierdo: {advance_config.get('electrodo_izquierdo', 'N/A')}")
            print(f"   - Electrodo Tierra: {advance_config.get('electrodo_tierra', 'N/A')}")

        # En estación 4 y 5, guardar case_id
        if self.estacion_actual in [4, 5]:
            if hasattr(self, 'case') and self.case:
                caso_data['case_id'] = self.case
                print(f"\n🔢 CASE ID GUARDADO (Estación {self.estacion_actual}):")
                print(f"   - Case ID: {self.case}")
                if isinstance(self.case, (list, tuple)) and len(self.case) == 2:
                    print(f"   - OD: Caso #{self.case[0]}")
                    print(f"   - OI: Caso #{self.case[1]}")

        print(f"\n✅ Datos guardados exitosamente")
        print("="*80 + "\n")

    def cargar_caso(self, estacion, caso):
        """Carga los datos de un caso específico"""
        # Limpiar curvas actuales
        self.reset()

        caso_data = self.datos_estaciones[estacion]['casos'][caso]

        # Restaurar memoria si existe
        if caso_data['memory']:
            import copy
            self.memory = copy.deepcopy(caso_data['memory'])
            # Restaurar curvas en los gráficos
            self.restaurar_curvas_desde_memoria()

        # Configurar caso específico según estación
        if estacion == 3:
            # Estación 3: Restaurar configuración si existe, o resetear a default
            if caso_data.get('configuracion'):
                # Caso ya visitado: restaurar configuración guardada
                self.aplicar_configuracion_completa(caso_data['configuracion'])
                print(f"   ↻ Restaurando configuración guardada del Caso {caso}")
            else:
                # Caso nuevo: resetear a valores por defecto
                self.reset_parametros_default()
                print(f"   ⚙️  Caso {caso} nuevo - Parámetros reseteados a default")
        elif estacion == 4:
            # Estación 4: Asignar casos específicos
            self.configurar_caso_estacion_4(caso)
            # Si el caso tiene configuración guardada, restaurarla
            if caso_data.get('configuracion'):
                self.aplicar_configuracion_completa(caso_data['configuracion'])
                print(f"   ↻ Restaurando configuración del Caso {caso}")
        elif estacion == 5:
            # Estación 5: Heredar datos de estación 4 caso 3
            self.heredar_datos_estacion_4()

        # Actualizar UI
        self.actualizar_ui_caso(estacion, caso)
        self.actualizar_botones_navegacion()

        print(f"Cargado: Estación {estacion} - Caso {caso}")

    def restaurar_curvas_desde_memoria(self):
        """Restaura las curvas en los gráficos desde la memoria"""
        # Reconstruir listas de curvas
        self.curves_R = [k for k in self.memory.keys() if k.startswith('R')]
        self.curves_L = [k for k in self.memory.keys() if k.startswith('L')]

        # Actualizar tablas y gráficos
        self.detail_all.process_and_fill_data(self.memory)

        # TODO: Restaurar curvas en los gráficos
        # Esto requiere recrear las líneas en pyqtgraph

    def configurar_caso_estacion_4(self, caso):
        """Configura los casos específicos de la Estación 4"""
        # Buscar casos por tipo en conbinaciones.py
        if caso == 1:
            # OD: Normal, OI: Transmisión (conductivo)
            case_od = self.buscar_caso_por_tipo('normal')
            case_oi = self.buscar_caso_por_tipo('conductivo')
        elif caso == 2:
            # OD: Coclear, OI: Normal
            case_od = self.buscar_caso_por_tipo('coclear')
            case_oi = self.buscar_caso_por_tipo('normal')
        elif caso == 3:
            # OD: Neural, OI: Neural (diferentes)
            case_od = self.buscar_caso_por_tipo('neural', indice=0)
            case_oi = self.buscar_caso_por_tipo('neural', indice=1)

        # Guardar configuración
        self.datos_estaciones[4]['casos'][caso]['case_id'] = (case_od, case_oi)
        self.case = (case_od, case_oi)

        print(f"Estación 4 Caso {caso}: OD={case_od}, OI={case_oi}")

    def buscar_caso_por_tipo(self, tipo, indice=0):
        """Busca un caso por tipo en las combinaciones"""
        from lib.conbinaciones import combinaciones

        casos_tipo = [i for i, combo in enumerate(combinaciones) if tipo in str(combo).lower()]

        if casos_tipo and indice < len(casos_tipo):
            return casos_tipo[indice]

        return 0  # Caso por defecto

    def heredar_datos_estacion_4(self):
        """Hereda todos los datos del caso 3 de la estación 4 a la estación 5"""
        import copy

        # Copiar memoria completa del caso 3 de estación 4
        caso_4_3 = self.datos_estaciones[4]['casos'][3]
        self.memory = copy.deepcopy(caso_4_3['memory'])

        # Copiar case_id
        if caso_4_3['case_id']:
            self.case = caso_4_3['case_id']
            self.datos_estaciones[5]['casos'][3]['case_id'] = caso_4_3['case_id']

        # Restaurar curvas
        self.restaurar_curvas_desde_memoria()

        print("Estación 5: Datos heredados de Estación 4 - Caso 3")

    def actualizar_ui_caso(self, estacion, caso):
        """Actualiza la interfaz para mostrar info del caso actual"""
        if estacion == 5:
            texto = f"ESTACIÓN {estacion} - Interpretación Caso 3"
        else:
            texto = f"ESTACIÓN {estacion} - Caso {caso}/3"

        self.lbl_info.setText(texto)

    def deshabilitar_captura_estacion_3(self):
        """Deshabilita el botón Grabar en estación 3 (solo configuración)"""
        # Deshabilitar botones de captura
        if hasattr(self.control, 'btn_start'):
            self.control.btn_start.setEnabled(False)
            self.control.btn_start.setToolTip("Deshabilitado en Estación 3 - Solo configuración de parámetros")

        if hasattr(self.control, 'btn_stop'):
            self.control.btn_stop.setEnabled(False)

        # Habilitar todos los controles de parámetros (incluyendo estímulos)
        if hasattr(self.control, 'disabled_all'):
            self.control.disabled_all(False)

        print("Estación 3: Captura deshabilitada, parámetros habilitados")

    def habilitar_captura_estacion_4(self):
        """Habilita el botón Grabar en estación 4"""
        # Habilitar botones de captura
        if hasattr(self.control, 'btn_start'):
            self.control.btn_start.setEnabled(True)
            self.control.btn_start.setToolTip("")

        if hasattr(self.control, 'btn_stop'):
            self.control.btn_stop.setEnabled(True)

        # Deshabilitar todos los controles de parámetros (no se pueden cambiar durante captura)
        if hasattr(self.control, 'disabled_all'):
            self.control.disabled_all(True)

        print("Estación 4: Captura habilitada, parámetros deshabilitados")

    def reset_parametros_default(self):
        """Resetea los parámetros del control a sus valores por defecto"""
        # Configuración por defecto
        default_config = {
            'stim': 'Click',
            'pol': 'Alternante',
            'int': 80,
            'mkg': 0,
            'rate': 21.1,
            'filter_down': '100',
            'filter_passhigh': '3000',
            'average': 2000,
            'side': 'OD',
            'atten': False
        }

        # Aplicar configuración por defecto al control básico
        if hasattr(self.control, 'set_data'):
            self.control.set_data(default_config)

        # Aplicar configuración por defecto a parámetros avanzados
        default_advance_config = {
            'transductor': 'Fono inserción',
            'ventana': 12,
            'fsp': 'Detección 99% y FSP de 3.1',
            'ruido_residual': '40nV',
            'electrodo_vertex': 'Cz',
            'electrodo_derecho': 'A1',
            'electrodo_izquierdo': 'A2',
            'electrodo_tierra': 'Cz'
        }

        self.set_advance_settings_data(default_advance_config)

        print("⚙️  Parámetros reseteados a default")

    def aplicar_configuracion_completa(self, config):
        """Aplica toda la configuración guardada (básica + avanzada) a los widgets"""
        # Separar configuración básica y avanzada
        basic_keys = ['stim', 'pol', 'int', 'mkg', 'rate', 'filter_down',
                     'filter_passhigh', 'average', 'side', 'atten']

        basic_config = {k: v for k, v in config.items() if k in basic_keys}
        advance_config = {k: v for k, v in config.items() if k not in basic_keys}

        # Aplicar configuración básica
        if basic_config and hasattr(self.control, 'set_data'):
            self.control.set_data(basic_config)

        # Aplicar configuración avanzada
        if advance_config:
            self.set_advance_settings_data(advance_config)

        print("✓ Configuración aplicada a widgets")

    def abrir_dialogo_osce(self):
        """Abre o reabre el diálogo de selección de estaciones OSCE"""
        if self.dialog_osce is None:
            self.dialog_osce = CuadroDialogoOSCE(self)

        # Marcar estaciones completadas en el diálogo
        for estacion, datos in self.datos_estaciones.items():
            if datos['completada']:
                self.dialog_osce.marcar_estacion_completada(estacion)

        # Si todas las estaciones están completadas, guardar todo y resetear
        if self.dialog_osce.todas_completadas():
            self.guardar_todas_estaciones()
            self.resetear_programa_completo()
            return

        # Mostrar diálogo
        self.dialog_osce.exec()

        # Cuando se selecciona una estación
        if self.dialog_osce.estacion_seleccionada:
            self.iniciar_estacion(self.dialog_osce.estacion_seleccionada)

    def iniciar_estacion(self, numero_estacion):
        """Inicia una estación específica del OSCE"""
        self.estacion_actual = numero_estacion

        # Reiniciar al caso 1
        self.caso_actual = 1

        # Resetear parámetros a default (excepto si es estación 5)
        if numero_estacion != 5:
            self.reset_parametros_default()

        # Cargar el primer caso de la estación
        if numero_estacion == 5:
            # Estación 5: Heredar datos de estación 4 caso 3
            self.heredar_datos_estacion_4()
            self.actualizar_ui_caso(5, 3)
        else:
            # Estaciones 3 y 4: Cargar caso 1
            self.cargar_caso(numero_estacion, 1)

        # Configurar según estación
        if numero_estacion == 3:
            # Estación 3: Deshabilitar botón Grabar
            self.deshabilitar_captura_estacion_3()
        elif numero_estacion == 4:
            # Estación 4: Habilitar botón Grabar
            self.habilitar_captura_estacion_4()
        elif numero_estacion == 5:
            # Estación 5: Deshabilitar botón Grabar (solo interpretación)
            self.deshabilitar_captura_estacion_3()

        # Actualizar botones de navegación
        self.actualizar_botones_navegacion()

        # Configurar timer para 5 minutos
        self.segundos_restantes = TIEMPO_ESTACION_OSCE * 60
        self.timer.start(1000)

        print(f"Iniciando Estación {numero_estacion} - Caso {self.caso_actual}")

    def guardar_datos_estacion(self):
        """Guarda los datos de la estación actual al finalizar el tiempo"""
        if self.estacion_actual is not None:
            # Guardar el caso actual antes de finalizar
            self.guardar_caso_actual()

            # Marcar estación como completada
            self.datos_estaciones[self.estacion_actual]['completada'] = True

            # Marcar en el diálogo
            if self.dialog_osce:
                self.dialog_osce.marcar_estacion_completada(self.estacion_actual)

            print(f"Estación {self.estacion_actual} completada - Todos los casos guardados")

    def guardar_todas_estaciones(self):
        """Guarda todos los datos de las 3 estaciones al finalizar"""
        import datetime
        import os

        # Crear directorio de resultados si no existe
        resultados_dir = context.get_resource('resultados_osce')
        if not os.path.exists(resultados_dir):
            os.makedirs(resultados_dir)

        # Timestamp para el archivo
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_json = os.path.join(resultados_dir, f"osce_completo_{timestamp}.json")

        # Guardar datos en JSON
        datos_completos = {
            'fecha': datetime.datetime.now().isoformat(),
            'estaciones': {}
        }

        for num_estacion, datos_estacion in self.datos_estaciones.items():
            estacion_info = {
                'completada': datos_estacion['completada'],
                'casos': {}
            }

            # Guardar cada caso de la estación
            for num_caso, datos_caso in datos_estacion['casos'].items():
                caso_info = {
                    'completado': datos_caso['completado'],
                    'memory': datos_caso['memory']
                }

                # Agregar campos específicos según estación
                if num_estacion == 3:
                    caso_info['configuracion'] = datos_caso.get('configuracion', {})
                elif num_estacion in [4, 5]:
                    caso_info['case_id'] = datos_caso.get('case_id', None)

                estacion_info['casos'][f'caso_{num_caso}'] = caso_info

            datos_completos['estaciones'][f'estacion_{num_estacion}'] = estacion_info

        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos_completos, f, indent=4, ensure_ascii=False)

        print(f"Datos completos guardados en: {archivo_json}")

        # Mostrar mensaje al usuario
        QMessageBox.information(
            self,
            "OSCE Completado",
            f"Las 3 estaciones han sido completadas exitosamente.\n\n"
            f"Datos guardados en:\n{archivo_json}"
        )

    def resetear_programa_completo(self):
        """Resetea completamente el programa después de completar las 3 estaciones"""
        # Limpiar todas las curvas
        self.reset()

        # Reiniciar datos de estaciones con nueva estructura
        self.datos_estaciones = {
            3: {
                'casos': {
                    1: {'memory': {}, 'configuracion': {}, 'completado': False},
                    2: {'memory': {}, 'configuracion': {}, 'completado': False},
                    3: {'memory': {}, 'configuracion': {}, 'completado': False}
                },
                'completada': False
            },
            4: {
                'casos': {
                    1: {'memory': {}, 'case_id': None, 'completado': False},
                    2: {'memory': {}, 'case_id': None, 'completado': False},
                    3: {'memory': {}, 'case_id': None, 'completado': False}
                },
                'completada': False
            },
            5: {
                'casos': {
                    3: {'memory': {}, 'case_id': None, 'completado': False}
                },
                'completada': False,
                'hereda_de_estacion_4': True
            }
        }

        # Reiniciar diálogo OSCE
        self.dialog_osce = None
        self.estacion_actual = None
        self.caso_actual = 1

        # Reiniciar memoria
        self.memory = {}
        self.curves_R = []
        self.curves_L = []

        # Ocultar botones de navegación
        if self.btn_caso_anterior:
            self.btn_caso_anterior.hide()
        if self.btn_caso_siguiente:
            self.btn_caso_siguiente.hide()

        # Actualizar UI
        self.lbl_info.setText("Programa reiniciado. Listo para nueva evaluación OSCE")

        print("Programa completamente reiniciado")

        # Volver a abrir el diálogo de selección
        self.abrir_dialogo_osce()

    #########EVENTS
    def closeEvent(self, event):
        # Detener el observador de cambios cuando se cierre la ventana
        if hasattr(self, 'observer'):
            self.observer.stop()
            self.observer.join()
        event.accept()



if __name__ == '__main__':
    if not verificar_activacion():
        sys.exit(1)  # Cerrar aplicación si no está activada
    
    window = MainWindow()
    style_file = context.get_resource('qss/style_base.qss')

    with open(style_file, 'r', encoding='utf-8') as f:
        style = f.read()
           
    window.setStyleSheet(style)
    window.show()
    
    exit_code = context.app.exec()
    
    sys.exit(exit_code)
