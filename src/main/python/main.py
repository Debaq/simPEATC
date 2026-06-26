# -*- coding: utf-8 -*-
#################################################################
#                                                               #
#                  NOMBRE PROYECTO : LabSim                     #
#                          VER. 0.7.5                           #
#               CREADOR : NICOLÁS QUEZADA QUEZADA               #
#                                                               #
#################################################################

import argparse
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
from PySide6.QtWidgets import (QComboBox, QDialog, QFrame, QGroupBox,
                               QFormLayout, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QSizePolicy,
                               QSpacerItem, QTextEdit, QVBoxLayout,
                               QMessageBox)
from UI.AbrAdvanceSettings_ui import Ui_AdvanceSettings
from UI.AbrMain_ui import Ui_MainWindow
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from lib.conbinaciones import elegir_combinacion_especifica, casos, namecasos, combinaciones
from lib.casos_estacion_3 import CASOS_ESTACION_3, get_descripcion_caso, validar_configuracion
from lib.InformeEstacion5 import DialogoInformeEstacion5
from lib.GeneradorInformeOSCE import GeneradorInformeOSCE
from lib.EnviarPDFServidor import enviar_pdf_osce
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
    def __init__(self, parent=None, modo_desarrollo=False):
        super().__init__(parent)
        self.setWindowTitle('Evaluación OSCE - PEATC')

        # Hacer que la ventana sea modal y no se pueda cerrar
        self.setModal(True)
        self.setFixedSize(450, 450)

        # Variables de estado
        self.estaciones_completadas = []
        self.estacion_seleccionada = None
        self.datos_estudiante = {'nombre': '', 'numero': ''}
        self.modo_desarrollo = modo_desarrollo

        # Layout principal
        layout = QVBoxLayout(self)

        # Título
        titulo = QLabel("<h2 style='text-align: center;'>Evaluación OSCE - PEATC</h2>")
        layout.addWidget(titulo)

        # === SECCIÓN DE DATOS DEL ESTUDIANTE ===
        grupo_datos = QGroupBox("Datos del Estudiante")
        grupo_datos.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout_datos = QVBoxLayout()

        # Nombre del estudiante
        lbl_nombre = QLabel("Nombre Completo:")
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ej: Juan Pérez López")
        layout_datos.addWidget(lbl_nombre)
        layout_datos.addWidget(self.txt_nombre)

        # Número de estudiante
        lbl_numero = QLabel("Número de Estudiante:")
        self.txt_numero = QLineEdit()
        self.txt_numero.setPlaceholderText("Ej: 2021234567")
        layout_datos.addWidget(lbl_numero)
        layout_datos.addWidget(self.txt_numero)

        grupo_datos.setLayout(layout_datos)
        layout.addWidget(grupo_datos)

        # Instrucciones
        instrucciones = QLabel(
            "<p style='text-align: center;'><b>Complete sus datos y seleccione la estación</b><br>"
            "Cada estación tiene 5 minutos de duración</p>"
        )
        instrucciones.setWordWrap(True)
        layout.addWidget(instrucciones)

        # Espacio
        layout.addSpacing(10)

        # Botones de estaciones
        self.btn_estacion_3 = QPushButton("ESTACIÓN 3: Configuración del Equipo")
        self.btn_estacion_3.setFixedHeight(50)
        self.btn_estacion_3.clicked.connect(lambda: self.seleccionar_estacion(3))
        layout.addWidget(self.btn_estacion_3)

        self.btn_estacion_4 = QPushButton("ESTACIÓN 4: Obtención del Registro")
        self.btn_estacion_4.setFixedHeight(50)
        self.btn_estacion_4.setEnabled(False)  # Deshabilitado inicialmente
        self.btn_estacion_4.clicked.connect(lambda: self.seleccionar_estacion(4))
        layout.addWidget(self.btn_estacion_4)

        self.btn_estacion_5 = QPushButton("ESTACIÓN 5: Interpretación e Informe")
        self.btn_estacion_5.setFixedHeight(50)
        self.btn_estacion_5.setEnabled(False)  # Deshabilitado inicialmente
        self.btn_estacion_5.clicked.connect(lambda: self.seleccionar_estacion(5))
        layout.addWidget(self.btn_estacion_5)

        # Label de estado
        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("color: green; font-weight: bold;")
        self.lbl_estado.setWordWrap(True)
        layout.addWidget(self.lbl_estado)

        # MODO DESARROLLO: Habilitar todas las estaciones y poner datos de prueba
        if self.modo_desarrollo:
            # Poner datos de prueba
            self.txt_nombre.setText("DESARROLLO_TEST")
            self.txt_numero.setText("999999")

            # Habilitar todos los botones de estación
            self.btn_estacion_3.setEnabled(True)
            self.btn_estacion_4.setEnabled(True)
            self.btn_estacion_5.setEnabled(True)

            # Cambiar estilos para indicar modo desarrollo
            self.setWindowTitle('Evaluación OSCE - PEATC [MODO DESARROLLO]')
            self.lbl_estado.setText("⚠️ MODO DESARROLLO: Todas las estaciones habilitadas")
            self.lbl_estado.setStyleSheet("color: orange; font-weight: bold;")

            print("\n" + "="*80)
            print("🔧 MODO DESARROLLO ACTIVADO")
            print("="*80)
            print("✅ Todas las estaciones están habilitadas")
            print("✅ Datos de prueba pre-cargados (DESARROLLO_TEST / 999999)")
            print("✅ Puedes acceder a cualquier estación directamente")
            print("="*80 + "\n")

        self.center_on_screen()

    def seleccionar_estacion(self, numero_estacion):
        """Maneja la selección de una estación"""
        # Validar que los datos del estudiante estén completos antes de iniciar
        if not self.txt_nombre.text().strip():
            QMessageBox.warning(
                self,
                "Datos Incompletos",
                "Por favor, ingrese su nombre completo antes de continuar."
            )
            self.txt_nombre.setFocus()
            return

        if not self.txt_numero.text().strip():
            QMessageBox.warning(
                self,
                "Datos Incompletos",
                "Por favor, ingrese su número de estudiante antes de continuar."
            )
            self.txt_numero.setFocus()
            return

        # Guardar datos del estudiante
        self.datos_estudiante['nombre'] = self.txt_nombre.text().strip()
        self.datos_estudiante['numero'] = self.txt_numero.text().strip()

        # Deshabilitar edición de datos después de iniciar
        self.txt_nombre.setEnabled(False)
        self.txt_numero.setEnabled(False)

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
    def __init__(self, modo_desarrollo=False) -> None:
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.estacion_desarrollo = modo_desarrollo
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
        # CRÍTICO: También conectar las marcas del gráfico para actualizar la memoria
        self.graph_r.sig_change_value_mark.connect(self.update_memory_from_graph_mark)
        self.graph_l.sig_change_value_mark.connect(self.update_memory_from_graph_mark)
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

        # Botón de desarrollo para saltar tiempo
        self.btn_skip_time_dev.clicked.connect(self.skip_time_dev)
        if self.estacion_desarrollo:
            self.btn_skip_time_dev.show()
            print("🔧 DEV: Botón 'Saltar Tiempo' habilitado")

        # Inicializar botones de navegación OSCE (se crearán después)
        self.btn_caso_anterior = None
        self.btn_caso_siguiente = None

        # Crear botones de navegación OSCE
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
        self.datos_estudiante_osce = {'nombre': '', 'numero': ''}  # Datos del estudiante para OSCE

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

        self.open_modal()
        self.inicializar_observador()

    def force_next(self):
        self.segundos_restantes = 1

    def skip_time_dev(self):
        """Método de desarrollo para saltar el tiempo directamente a 0"""
        if self.estacion_desarrollo:
            print("🔧 DEV: Saltando tiempo a 0...")
            self.segundos_restantes = 0

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
        """Limpia completamente los gráficos y la memoria de curvas"""
        print("\n🔄 RESET: Limpiando gráficos y memoria...")

        # Limpiar completamente ambos gráficos usando el nuevo método
        self.graph_r.limpiar_todo()
        self.graph_l.limpiar_todo()

        # Limpiar listas de curvas
        self.curves_R = []
        self.curves_L = []

        # Limpiar memoria
        self.memory = {}

        # Limpiar tablas
        self.table_r.clear_all()
        self.table_l.clear_all()
        self.detail_all.clear_all()

        print("   ✓ Reset completado\n")


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
            # En Estación 5 OSCE no hay previsualización de PDF, solo Conclusiones
            if not (self.modo_osce and self.estacion_actual == 5):
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

            # En Estación 4: mostrar curva final directamente sin animación
            if hasattr(self, 'estacion_actual') and self.estacion_actual == 4:
                self.total_averages = self.fake_averages(self.current_setting["average"], express=True)
                self.capture_timer.start(10)  # Mínimo delay para procesamiento
                print("   ⚡ Modo rápido Estación 4: curva final sin animación")
            else:
                # Estaciones 3 y 5: animación normal con promediaciones
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

    def update_memory_from_graph_mark(self, data):
        """
        Actualiza la memoria cuando se marca una onda directamente en el gráfico

        Args:
            data: dict con formato {curva: {onda: [x, y]}} o {curva: {onda: None}}
        """
        for curve_name, marks_dict in data.items():
            # Verificar que la curva existe en memoria
            if curve_name not in self.memory:
                return

            # Asegurar que existe la estructura LatAmp
            if 'LatAmp' not in self.memory[curve_name]:
                self.memory[curve_name]['LatAmp'] = {
                    'I': [None, None],
                    'II': [None, None],
                    'III': [None, None],
                    'IV': [None, None],
                    'V': [None, None]
                }

            # Actualizar cada marca
            for wave, coords in marks_dict.items():
                if coords is None:
                    # Marca eliminada
                    self.memory[curve_name]['LatAmp'][wave] = [None, None]
                    print(f"   🗑️  Marca eliminada: {curve_name} - Onda {wave}")
                else:
                    # Marca creada/actualizada
                    latencia, amplitud = coords
                    self.memory[curve_name]['LatAmp'][wave] = [latencia, amplitud]
                    print(f"   ✓ Marca guardada: {curve_name} - Onda {wave}: Lat={latencia:.2f}ms, Amp={amplitud:.2f}μV")

            # Actualizar la tabla de detalle de todas las curvas
            self.detail_all.process_and_fill_data(self.memory)

    def active_advance_setting(self):
        self.dialog = QDialog(self)
        self.ui = Ui_AdvanceSettings()
        self.ui.setupUi(self.dialog)

        # Determinar si debemos cargar configuración guardada o valores predeterminados
        if hasattr(self, 'estacion_actual') and hasattr(self, 'caso_actual') and hasattr(self, 'datos_estaciones'):
            estacion = self.estacion_actual
            caso = self.caso_actual

            if estacion in self.datos_estaciones and caso in self.datos_estaciones[estacion]['casos']:
                caso_data = self.datos_estaciones[estacion]['casos'][caso]
                config_guardada = caso_data.get('configuracion', {})

                if config_guardada and len(config_guardada) > 0:
                    # Caso con configuración guardada: restaurarla
                    if 'transductor' in config_guardada:
                        idx = self.ui.comboBox.findText(config_guardada['transductor'])
                        if idx >= 0:
                            self.ui.comboBox.setCurrentIndex(idx)

                    if 'ventana' in config_guardada:
                        self.ui.spinBox.setValue(config_guardada['ventana'])

                    if 'fsp' in config_guardada:
                        idx = self.ui.comboBox_2.findText(config_guardada['fsp'])
                        if idx >= 0:
                            self.ui.comboBox_2.setCurrentIndex(idx)

                    if 'ruido_residual' in config_guardada:
                        idx = self.ui.comboBox_3.findText(config_guardada['ruido_residual'])
                        if idx >= 0:
                            self.ui.comboBox_3.setCurrentIndex(idx)

                    if 'electrodo_vertex' in config_guardada:
                        idx = self.ui.comboBox_4.findText(config_guardada['electrodo_vertex'])
                        if idx >= 0:
                            self.ui.comboBox_4.setCurrentIndex(idx)

                    if 'electrodo_derecho' in config_guardada:
                        idx = self.ui.comboBox_5.findText(config_guardada['electrodo_derecho'])
                        if idx >= 0:
                            self.ui.comboBox_5.setCurrentIndex(idx)

                    if 'electrodo_izquierdo' in config_guardada:
                        idx = self.ui.comboBox_6.findText(config_guardada['electrodo_izquierdo'])
                        if idx >= 0:
                            self.ui.comboBox_6.setCurrentIndex(idx)

                    if 'electrodo_tierra' in config_guardada:
                        idx = self.ui.comboBox_7.findText(config_guardada['electrodo_tierra'])
                        if idx >= 0:
                            self.ui.comboBox_7.setCurrentIndex(idx)

                    print(f"   ↻ Parámetros avanzados restaurados en el diálogo para Caso {caso}")
                else:
                    # Caso nuevo: aplicar valores predeterminados según estación
                    if estacion == 3:
                        # Valores predeterminados Estación 3
                        self.ui.comboBox.setCurrentText('Fono de copa')
                        self.ui.spinBox.setValue(20)
                        self.ui.comboBox_2.setCurrentText('Desactivado')
                        self.ui.comboBox_3.setCurrentText('100nV')
                        self.ui.comboBox_4.setCurrentText('A1')  # Vertex
                        self.ui.comboBox_5.setCurrentText('A1')  # Derecho
                        self.ui.comboBox_6.setCurrentText('A1')  # Izquierdo
                        self.ui.comboBox_7.setCurrentText('A1')  # Tierra
                        print(f"   ⚙️  Parámetros avanzados default Estación 3 en diálogo para Caso {caso}")
                    elif estacion == 4:
                        # Valores predeterminados Estación 4
                        self.ui.comboBox.setCurrentText('Fono inserción')
                        self.ui.spinBox.setValue(12)
                        self.ui.comboBox_2.setCurrentText('Detección 99% y FSP de 3.1')
                        self.ui.comboBox_3.setCurrentText('40nV')
                        self.ui.comboBox_4.setCurrentText('Cz')   # Vertex
                        self.ui.comboBox_5.setCurrentText('A2')   # Derecho
                        self.ui.comboBox_6.setCurrentText('A1')   # Izquierdo
                        self.ui.comboBox_7.setCurrentText('Ceja izquierda')  # Tierra
                        print(f"   ⚙️  Parámetros avanzados default Estación 4 en diálogo para Caso {caso}")

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
        print("\n🔧 CREANDO BOTONES DE NAVEGACIÓN OSCE...")
        try:
            # El horizontalLayout ya existe como atributo después de setupUi()
            # Lo accedemos directamente
            layout = self.horizontalLayout

            if layout is None:
                print("   ❌ Error: horizontalLayout es None")
                self.btn_caso_anterior = None
                self.btn_caso_siguiente = None
                return

            # Crear botón "Caso Anterior"
            self.btn_caso_anterior = QPushButton("◀ Anterior", self.centralwidget)
            self.btn_caso_anterior.setFixedHeight(30)
            self.btn_caso_anterior.setMaximumWidth(100)
            self.btn_caso_anterior.clicked.connect(self.ir_caso_anterior)
            print(f"   ✓ btn_caso_anterior creado: {self.btn_caso_anterior is not None}")

            # Crear botón "Caso Siguiente"
            self.btn_caso_siguiente = QPushButton("Siguiente ▶", self.centralwidget)
            self.btn_caso_siguiente.setFixedHeight(30)
            self.btn_caso_siguiente.setMaximumWidth(100)
            self.btn_caso_siguiente.clicked.connect(self.ir_caso_siguiente)
            print(f"   ✓ btn_caso_siguiente creado: {self.btn_caso_siguiente is not None}")

            # Insertar botones en el layout (después de lbl_time y antes de btn_next_case)
            # El orden será: [lbl_info] [spacer] [lbl_time] [btn_caso_anterior] [btn_caso_siguiente] [btn_next_case] [spacer]
            index = layout.indexOf(self.btn_next_case)
            if index >= 0:
                layout.insertWidget(index, self.btn_caso_anterior)
                layout.insertWidget(index + 1, self.btn_caso_siguiente)
                print(f"   ✓ Botones insertados en layout en índice {index}")
            else:
                # Si no encuentra btn_next_case, agregar al final
                layout.addWidget(self.btn_caso_anterior)
                layout.addWidget(self.btn_caso_siguiente)
                print(f"   ✓ Botones agregados al final del layout")

            # Ocultar botones inicialmente (se mostrarán solo en modo OSCE estaciones 3 y 4)
            self.btn_caso_anterior.hide()
            self.btn_caso_siguiente.hide()
            print(f"   ✓ Botones ocultados inicialmente")
            print(f"   ✅ Botones de navegación OSCE creados exitosamente\n")

        except Exception as e:
            print(f"   ❌ Error al crear botones de navegación OSCE: {e}")
            import traceback
            traceback.print_exc()
            self.btn_caso_anterior = None
            self.btn_caso_siguiente = None

    def actualizar_botones_navegacion(self):
        """Actualiza el estado de los botones de navegación según el caso actual"""
        print(f"\n🔍 DEBUG actualizar_botones_navegacion:")
        print(f"   - Estación actual: {self.estacion_actual}")
        print(f"   - Caso actual: {self.caso_actual}")
        print(f"   - Modo OSCE: {self.modo_osce}")
        print(f"   - btn_caso_anterior existe: {self.btn_caso_anterior is not None}")
        print(f"   - btn_caso_siguiente existe: {self.btn_caso_siguiente is not None}")

        # Verificar que los botones existen
        if self.btn_caso_anterior is None or self.btn_caso_siguiente is None:
            print("   ⚠️ Botones no existen, saliendo...")
            return

        if not self.modo_osce or self.estacion_actual is None:
            print("   ⚠️ No modo OSCE o estación None, ocultando botones...")
            self.btn_caso_anterior.hide()
            self.btn_caso_siguiente.hide()
            return

        # Estación 5 solo tiene 1 caso, no hay navegación
        if self.estacion_actual == 5:
            print("   🚫 ESTACIÓN 5 DETECTADA - OCULTANDO BOTONES")
            print(f"      - Visible antes (anterior): {self.btn_caso_anterior.isVisible()}")
            print(f"      - Visible antes (siguiente): {self.btn_caso_siguiente.isVisible()}")

            # Ocultar los botones
            self.btn_caso_anterior.setVisible(False)
            self.btn_caso_siguiente.setVisible(False)
            self.btn_caso_anterior.setEnabled(False)
            self.btn_caso_siguiente.setEnabled(False)

            # Remover los botones del layout para que realmente desaparezcan
            if hasattr(self, 'horizontalLayout'):
                layout = self.horizontalLayout
                if layout is not None:
                    layout.removeWidget(self.btn_caso_anterior)
                    layout.removeWidget(self.btn_caso_siguiente)
                    print("      - Botones removidos del layout")

            print(f"      - Visible después (anterior): {self.btn_caso_anterior.isVisible()}")
            print(f"      - Visible después (siguiente): {self.btn_caso_siguiente.isVisible()}")
            print(f"      - Habilitado después (anterior): {self.btn_caso_anterior.isEnabled()}")
            print(f"      - Habilitado después (siguiente): {self.btn_caso_siguiente.isEnabled()}")

            # Mostrar info en btn_next_case (solo informativo, no clickeable)
            self.btn_next_case.setText(f"Estación {self.estacion_actual} - Caso 3")
            self.btn_next_case.setVisible(True)
            self.btn_next_case.setEnabled(False)  # Deshabilitar para que no sea clickeable
            self.btn_next_case.setStyleSheet("QPushButton:disabled { color: #888; }")  # Estilo de texto deshabilitado
            print("   ✅ Botones de navegación ocultados y removidos del layout (Estación 5 - solo Caso 3)")
            print("   ✅ Botón info deshabilitado (solo informativo)")
            return

        # Estaciones 3 y 4: Mostrar botones de navegación
        print(f"   📍 Estaciones 3 o 4 - MOSTRANDO botones de navegación")
        self.btn_caso_anterior.setVisible(True)
        self.btn_caso_siguiente.setVisible(True)

        # Habilitar/deshabilitar según caso actual
        if self.caso_actual == 1:
            self.btn_caso_anterior.setEnabled(False)
            self.btn_caso_siguiente.setEnabled(True)
            print(f"   ◀ Anterior: DESHABILITADO (Caso 1)")
            print(f"   ▶ Siguiente: HABILITADO")
        elif self.caso_actual == 3:
            self.btn_caso_anterior.setEnabled(True)
            self.btn_caso_siguiente.setEnabled(False)
            print(f"   ◀ Anterior: HABILITADO")
            print(f"   ▶ Siguiente: DESHABILITADO (Caso 3)")
        else:  # caso 2
            self.btn_caso_anterior.setEnabled(True)
            self.btn_caso_siguiente.setEnabled(True)
            print(f"   ◀ Anterior: HABILITADO")
            print(f"   ▶ Siguiente: HABILITADO (Caso 2)")

        print(f"   ✓ Botones visibles (anterior): {self.btn_caso_anterior.isVisible()}")
        print(f"   ✓ Botones visibles (siguiente): {self.btn_caso_siguiente.isVisible()}")

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

        # Guardar datos de gráficos (para poder restaurar las curvas visuales)
        caso_data['graph_data_r'] = copy.deepcopy(self.graph_r.data) if hasattr(self.graph_r, 'data') else {}
        caso_data['graph_data_l'] = copy.deepcopy(self.graph_l.data) if hasattr(self.graph_l, 'data') else {}
        caso_data['graph_marks_r'] = copy.deepcopy(self.graph_r.marks) if hasattr(self.graph_r, 'marks') else {}
        caso_data['graph_marks_l'] = copy.deepcopy(self.graph_l.marks) if hasattr(self.graph_l, 'marks') else {}
        caso_data['graph_curve_int_r'] = copy.deepcopy(self.graph_r.curve_int) if hasattr(self.graph_r, 'curve_int') else {}
        caso_data['graph_curve_int_l'] = copy.deepcopy(self.graph_l.curve_int) if hasattr(self.graph_l, 'curve_int') else {}

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
                # Solo considerar ondas con al menos un valor real (no None)
                ondas_marcadas = [onda for onda in ['I', 'II', 'III', 'IV', 'V']
                                 if onda in lat_amp and lat_amp[onda] and
                                 (lat_amp[onda][0] is not None or lat_amp[onda][1] is not None)]
                print(f"      • Ondas marcadas: {ondas_marcadas}")
                for onda in ondas_marcadas:
                    if lat_amp[onda] and lat_amp[onda][0] is not None and lat_amp[onda][1] is not None:
                        print(f"         - Onda {onda}: Lat={lat_amp[onda][0]:.2f}ms, Amp={lat_amp[onda][1]:.2f}μV")
                    elif lat_amp[onda]:
                        print(f"         - Onda {onda}: Marcada (sin valores de latencia/amplitud)")

        # En estación 3, guardar configuración de parámetros
        if self.estacion_actual == 3:
            config = self.control.get_data()
            advance_config = self.get_advance_settings_data()

            # Combinar configuración básica y avanzada
            configuracion_completa = {**config, **advance_config}
            caso_data['configuracion'] = configuracion_completa

            # Validar configuración contra parámetros correctos
            validacion = validar_configuracion(self.caso_actual, configuracion_completa)
            caso_data['validacion'] = validacion

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

            print(f"\n📊 VALIDACIÓN DE CONFIGURACIÓN:")
            print(f"   - Correcto: {validacion['correcto']}")
            print(f"   - Puntaje: {validacion['puntaje']}/{validacion['total']}")
            if validacion['errores']:
                print(f"   - Errores detectados: {len(validacion['errores'])}")
                for error in validacion['errores']:
                    print(f"      • {error}")
            if validacion['advertencias']:
                print(f"   - Advertencias: {len(validacion['advertencias'])}")
                for adv in validacion['advertencias']:
                    print(f"      • {adv}")

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
            # Estación 4: Asignar casos específicos (solo cambia el case_id)
            self.configurar_caso_estacion_4(caso)
            # NO resetear parámetros - se mantienen entre casos
            # Los estudiantes modifican parámetros según necesiten (intensidad, lado, etc.)
            print(f"   ✓ Caso {caso} cargado - Parámetros mantenidos (pueden modificarse)")
        elif estacion == 5:
            # Estación 5: Heredar datos de estación 4 caso 3
            self.heredar_datos_estacion_4()

        # Actualizar UI
        self.actualizar_ui_caso(estacion, caso)
        self.actualizar_botones_navegacion()

        print(f"Cargado: Estación {estacion} - Caso {caso}")

    def restaurar_curvas_desde_memoria(self):
        """Restaura las curvas en los gráficos desde la memoria"""
        print(f"\n{'='*80}")
        print(f"🔄 RESTAURANDO CURVAS DESDE MEMORIA")
        print(f"{'='*80}")

        # Reconstruir listas de curvas
        self.curves_R = [k for k in self.memory.keys() if k.startswith('R')]
        self.curves_L = [k for k in self.memory.keys() if k.startswith('L')]

        # Actualizar tablas
        self.detail_all.process_and_fill_data(self.memory)

        # Obtener datos guardados del caso actual
        caso_data = self.datos_estaciones[self.estacion_actual]['casos'][self.caso_actual]

        # Restaurar datos de gráficos
        graph_data_r = caso_data.get('graph_data_r', {})
        graph_data_l = caso_data.get('graph_data_l', {})
        graph_marks_r = caso_data.get('graph_marks_r', {})
        graph_marks_l = caso_data.get('graph_marks_l', {})
        graph_curve_int_r = caso_data.get('graph_curve_int_r', {})
        graph_curve_int_l = caso_data.get('graph_curve_int_l', {})

        # Variable para rastrear la última curva restaurada
        ultima_curva_r = None
        ultima_curva_l = None

        # Restaurar gráfico derecho (OD)
        if graph_data_r:
            print(f"\n   📈 Restaurando curvas OD:")
            self.graph_r.data = graph_data_r
            self.graph_r.marks = graph_marks_r
            self.graph_r.curve_int = graph_curve_int_r

            # Recrear las líneas visuales en el gráfico
            for curve_name, curve_data in graph_data_r.items():
                print(f"      • {curve_name} @ {graph_curve_int_r.get(curve_name, 'N/A')} dB")
                # Recrear la línea
                y = curve_data['ipsi_xy'][1] + curve_data.get('gap', 1.8)
                self.graph_r.pw.plot(x=curve_data['ipsi_xy'][0], y=y, pen=self.graph_r.active_color, name=curve_name)

                # Recrear el label
                label = self.graph_r.create_label(curve_name, graph_curve_int_r.get(curve_name, 0), curve_data.get('gap', 1.8))
                self.graph_r.pw.addItem(label)

                # Recrear las marcas de ondas
                if curve_name in graph_marks_r:
                    marcas_recreadas = []
                    for mark_name, mark_data in graph_marks_r[curve_name].items():
                        self.graph_r.recreate_mark(curve_name, mark_name, mark_data)
                        marcas_recreadas.append(mark_name)
                    if marcas_recreadas:
                        print(f"         └─ Marcas restauradas: {', '.join(marcas_recreadas)}")

                # Guardar última curva
                ultima_curva_r = curve_name

            # Establecer la última curva como activa
            if ultima_curva_r:
                self.graph_r.act_curve = ultima_curva_r
                print(f"   ✓ Curva activa OD: {ultima_curva_r}")

        # Restaurar gráfico izquierdo (OI)
        if graph_data_l:
            print(f"\n   📈 Restaurando curvas OI:")
            self.graph_l.data = graph_data_l
            self.graph_l.marks = graph_marks_l
            self.graph_l.curve_int = graph_curve_int_l

            # Recrear las líneas visuales en el gráfico
            for curve_name, curve_data in graph_data_l.items():
                print(f"      • {curve_name} @ {graph_curve_int_l.get(curve_name, 'N/A')} dB")
                # Recrear la línea
                y = curve_data['ipsi_xy'][1] + curve_data.get('gap', 1.8)
                self.graph_l.pw.plot(x=curve_data['ipsi_xy'][0], y=y, pen=self.graph_l.active_color, name=curve_name)

                # Recrear el label
                label = self.graph_l.create_label(curve_name, graph_curve_int_l.get(curve_name, 0), curve_data.get('gap', 1.8))
                self.graph_l.pw.addItem(label)

                # Recrear las marcas de ondas
                if curve_name in graph_marks_l:
                    marcas_recreadas = []
                    for mark_name, mark_data in graph_marks_l[curve_name].items():
                        self.graph_l.recreate_mark(curve_name, mark_name, mark_data)
                        marcas_recreadas.append(mark_name)
                    if marcas_recreadas:
                        print(f"         └─ Marcas restauradas: {', '.join(marcas_recreadas)}")

                # Guardar última curva
                ultima_curva_l = curve_name

            # Establecer la última curva como activa
            if ultima_curva_l:
                self.graph_l.act_curve = ultima_curva_l
                print(f"   ✓ Curva activa OI: {ultima_curva_l}")

        # Actualizar gráfico de latencia-intensidad
        if self.memory:
            print(f"\n   📊 Actualizando gráfico latencia-intensidad...")
            self.graph_lat_int.plot_data(self.memory)

        # Actualizar tablas de latencia/amplitud con la última curva de cada lado
        print(f"\n   📋 Actualizando tablas de latencia/amplitud...")

        # Tabla OD (derecha)
        if self.curves_R:
            # Buscar la última curva con datos de latencia/amplitud
            curva_od_con_datos = None
            for curve_name in reversed(self.curves_R):
                if curve_name in self.memory and 'LatAmp' in self.memory[curve_name]:
                    lat_amp = self.memory[curve_name]['LatAmp']
                    # Verificar si tiene al menos una onda marcada
                    tiene_datos = any(lat_amp.get(onda, [None, None])[0] is not None
                                     for onda in ['I', 'II', 'III', 'IV', 'V'])
                    if tiene_datos:
                        curva_od_con_datos = curve_name
                        break

            if curva_od_con_datos:
                self.table_r.update_latamp_table(self.memory[curva_od_con_datos])
                print(f"      • Tabla OD actualizada con curva: {curva_od_con_datos}")
            else:
                self.table_r.clear_all()
                print(f"      • Tabla OD limpiada (sin curvas marcadas)")
        else:
            self.table_r.clear_all()
            print(f"      • Tabla OD limpiada (sin curvas)")

        # Tabla OI (izquierda)
        if self.curves_L:
            # Buscar la última curva con datos de latencia/amplitud
            curva_oi_con_datos = None
            for curve_name in reversed(self.curves_L):
                if curve_name in self.memory and 'LatAmp' in self.memory[curve_name]:
                    lat_amp = self.memory[curve_name]['LatAmp']
                    # Verificar si tiene al menos una onda marcada
                    tiene_datos = any(lat_amp.get(onda, [None, None])[0] is not None
                                     for onda in ['I', 'II', 'III', 'IV', 'V'])
                    if tiene_datos:
                        curva_oi_con_datos = curve_name
                        break

            if curva_oi_con_datos:
                self.table_l.update_latamp_table(self.memory[curva_oi_con_datos])
                print(f"      • Tabla OI actualizada con curva: {curva_oi_con_datos}")
            else:
                self.table_l.clear_all()
                print(f"      • Tabla OI limpiada (sin curvas marcadas)")
        else:
            self.table_l.clear_all()
            print(f"      • Tabla OI limpiada (sin curvas)")

        print(f"\n✅ Restauración completada")
        print(f"   - Curvas OD restauradas: {len(graph_data_r)}")
        print(f"   - Curvas OI restauradas: {len(graph_data_l)}")
        print(f"{'='*80}\n")

    def configurar_caso_estacion_4(self, caso):
        """Configura los casos específicos de la Estación 4"""
        from lib.conbinaciones import combinaciones

        # Buscar casos por tipo en combinaciones
        if caso == 1:
            # Caso 1: OD Normal, OI Conductivo (Transmisión)
            case_od_id = self.buscar_caso_por_tipo('normal', indice=0)
            case_oi_id = self.buscar_caso_por_tipo('conductivo', indice=0)
        elif caso == 2:
            # Caso 2: OD Coclear, OI Normal
            case_od_id = self.buscar_caso_por_tipo('coclear', indice=1)
            case_oi_id = self.buscar_caso_por_tipo('normal', indice=1)
        elif caso == 3:
            # Caso 3: OD Neural (schwannoma), OI Neural (diferente)
            case_od_id = self.buscar_caso_por_tipo('neural', indice=3)  # Schwannoma vestibular
            case_oi_id = self.buscar_caso_por_tipo('neural', indice=4)  # Schwannoma mediano
        else:
            case_od_id = 'normal_1'
            case_oi_id = 'normal_1'

        # Buscar o crear combinación en la lista
        combo_buscada = (case_od_id, case_oi_id)

        # Buscar índice de esta combinación en la lista
        try:
            case_index = combinaciones.index(combo_buscada)
        except ValueError:
            # Si no existe, usar la primera normal
            case_index = 0
            print(f"   ⚠️  Combinación ({case_od_id}, {case_oi_id}) no encontrada, usando índice 0")

        # Guardar configuración
        self.datos_estaciones[4]['casos'][caso]['case_id'] = case_index
        self.case = case_index

        print(f"Estación 4 Caso {caso}:")
        print(f"   - OD: {case_od_id}")
        print(f"   - OI: {case_oi_id}")
        print(f"   - Índice combinación: {case_index}")

    def buscar_caso_por_tipo(self, tipo, indice=0):
        """Busca un caso por tipo en las combinaciones

        Args:
            tipo: 'normal', 'coclear', 'neural', 'conductivo'
            indice: índice del caso dentro del tipo (0, 1, 2, etc.)

        Returns:
            ID del caso en DICT_CASES (string) o el primer caso normal por defecto
        """
        from lib.conbinaciones import DICT_CASES

        # Mapeo de tipos a patologías en DICT_CASES
        tipo_mapping = {
            'normal': 'normal',
            'coclear': 'cochlear',
            'conductivo': 'conductive',
            'neural': 'neural'
        }

        patologia_buscar = tipo_mapping.get(tipo.lower(), 'normal')

        # Buscar casos por patología
        casos_encontrados = [
            caso_id for caso_id, caso_data in DICT_CASES.items()
            if caso_data.get('patologia') == patologia_buscar
        ]

        # Retornar el caso según índice
        if casos_encontrados and indice < len(casos_encontrados):
            return casos_encontrados[indice]

        # Por defecto retornar el primer caso normal
        return 'normal_1'

    def heredar_datos_estacion_4(self):
        """Hereda todos los datos del caso 3 de la estación 4 a la estación 5"""
        import copy

        print("\n" + "="*80)
        print("🔄 HEREDANDO DATOS: Estación 4 Caso 3 → Estación 5")
        print("="*80)

        # Copiar todos los datos del caso 3 de estación 4
        caso_4_3 = self.datos_estaciones[4]['casos'][3]
        caso_5_3 = self.datos_estaciones[5]['casos'][3]

        # Copiar memoria completa
        self.memory = copy.deepcopy(caso_4_3['memory'])
        caso_5_3['memory'] = copy.deepcopy(caso_4_3['memory'])

        # Copiar datos de gráficos
        caso_5_3['graph_data_r'] = copy.deepcopy(caso_4_3.get('graph_data_r', {}))
        caso_5_3['graph_data_l'] = copy.deepcopy(caso_4_3.get('graph_data_l', {}))
        caso_5_3['graph_marks_r'] = copy.deepcopy(caso_4_3.get('graph_marks_r', {}))
        caso_5_3['graph_marks_l'] = copy.deepcopy(caso_4_3.get('graph_marks_l', {}))
        caso_5_3['graph_curve_int_r'] = copy.deepcopy(caso_4_3.get('graph_curve_int_r', {}))
        caso_5_3['graph_curve_int_l'] = copy.deepcopy(caso_4_3.get('graph_curve_int_l', {}))

        # Copiar case_id
        if caso_4_3.get('case_id'):
            self.case = caso_4_3['case_id']
            caso_5_3['case_id'] = caso_4_3['case_id']
            print(f"   ✓ Case ID heredado: {caso_4_3['case_id']}")

        print(f"   ✓ Memoria heredada: {len(self.memory)} curvas")
        print(f"   ✓ Datos de gráficos OD: {len(caso_5_3.get('graph_data_r', {}))} curvas")
        print(f"   ✓ Datos de gráficos OI: {len(caso_5_3.get('graph_data_l', {}))} curvas")

        # Restaurar curvas
        self.restaurar_curvas_desde_memoria()

        print("\n✅ Estación 5: Datos heredados de Estación 4 - Caso 3")
        print("="*80 + "\n")

    def actualizar_ui_caso(self, estacion, caso):
        """Actualiza la interfaz para mostrar info del caso actual"""
        if estacion == 5:
            texto = f"ESTACIÓN {estacion} - Interpretación Caso 3"
        else:
            texto = f"ESTACIÓN {estacion} - Caso {caso}/3"

        self.lbl_info.setText(texto)

        # Si es estación 3, mostrar instrucciones del caso
        if estacion == 3:
            desc_caso = get_descripcion_caso(caso)
            if desc_caso:
                # Mostrar diálogo con instrucciones del caso
                msg = QMessageBox(self)
                msg.setWindowTitle(f"Estación 3 - Caso {caso}")
                msg.setIcon(QMessageBox.Information)
                msg.setText(f"<h3>{desc_caso['nombre']}</h3>")
                msg.setInformativeText(desc_caso['instrucciones'])
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setStyleSheet("QLabel{min-width: 400px;}")
                msg.exec()

        # Si es estación 5, mostrar instrucciones
        elif estacion == 5:
            msg = QMessageBox(self)
            msg.setWindowTitle("Estación 5 - Interpretación e Informe")
            msg.setIcon(QMessageBox.Information)
            msg.setText("<h3>Estación 5: Interpretación, Informe y Decisiones</h3>")
            msg.setInformativeText(
                "📊 A continuación podrá ver todas las curvas y mediciones del Caso 3.\n\n"
                "✓ Revise las curvas con sus marcas de ondas (I, II, III, IV, V)\n"
                "✓ Revise las tablas de latencias y amplitudes\n"
                "✓ Revise el gráfico de latencia-intensidad\n"
                "✓ Analice los valores obtenidos\n\n"
                "📝 Cuando esté listo para elaborar el informe:\n"
                "   → Presione el botón 'Elaborar Informe' en el menú superior\n\n"
                "El informe debe incluir:\n"
                "• Descripción de hallazgos (latencias, intervalos interpicos, etc.)\n"
                "• Comparación con valores normativos\n"
                "• Conclusión diagnóstica según protocolo\n\n"
                "⏱️ Tiempo disponible: 5 minutos"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet("QLabel{min-width: 500px;}")
            msg.exec()

            # NO abrir automáticamente el diálogo de informe
            # El estudiante debe ver primero las curvas y valores
            # Y luego abrir el informe manualmente cuando esté listo

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

        # DESHABILITAR pestaña de Conclusiones (solo configuración)
        if hasattr(self, 'tabWidget'):
            self.tabWidget.setTabEnabled(2, False)  # Índice 2 = Conclusiones
            # Asegurar que está en pestaña de Gráficos
            if self.tabWidget.currentIndex() == 2:
                self.tabWidget.setCurrentIndex(0)

        print("Estación 3: Captura deshabilitada, parámetros habilitados, Conclusiones DESHABILITADAS")

    def habilitar_captura_estacion_4(self):
        """Habilita el botón Grabar en estación 4"""
        # Habilitar botones de captura
        if hasattr(self.control, 'btn_start'):
            self.control.btn_start.setEnabled(True)
            self.control.btn_start.setToolTip("")

        if hasattr(self.control, 'btn_stop'):
            self.control.btn_stop.setEnabled(True)

        # HABILITAR todos los controles de parámetros (necesitan poder cambiarlos durante la estación)
        if hasattr(self.control, 'disabled_all'):
            self.control.disabled_all(False)

        # DESHABILITAR pestaña de Conclusiones (solo captura, no interpretación)
        if hasattr(self, 'tabWidget'):
            self.tabWidget.setTabEnabled(2, False)  # Índice 2 = Conclusiones
            # Asegurar que está en pestaña de Gráficos
            if self.tabWidget.currentIndex() == 2:
                self.tabWidget.setCurrentIndex(0)

        print("Estación 4: Captura habilitada, parámetros HABILITADOS, Conclusiones DESHABILITADAS")

    def habilitar_conclusiones_estacion_5(self):
        """Habilita la pestaña de Conclusiones para Estación 5 (interpretación e informe)"""
        # Deshabilitar botones de captura (solo interpretación)
        if hasattr(self.control, 'btn_start'):
            self.control.btn_start.setEnabled(False)
            self.control.btn_start.setToolTip("Deshabilitado en Estación 5 - Solo interpretación")

        if hasattr(self.control, 'btn_stop'):
            self.control.btn_stop.setEnabled(False)

        # Deshabilitar parámetros (no deben modificarse en Estación 5)
        if hasattr(self.control, 'disabled_all'):
            self.control.disabled_all(True)

        # Mostrar vista de todas las curvas en el panel de detalles
        if hasattr(self.detail, 'tabWidget'):
            # Cambiar a pestaña de "Todas las curvas" (índice 1)
            self.detail.tabWidget.setCurrentIndex(1)
            print("   ✓ Vista 'Todas las curvas' activada")

        # Expandir el dock de detalles para ver mejor todas las curvas
        if hasattr(self, 'dock_test'):
            self.dock_test.setFixedHeight(400)
            print("   ✓ Panel de detalles expandido")

        # Asegurar que el dock de valores esté visible (tablas de latencia/amplitud)
        if hasattr(self, 'dock_values'):
            self.dock_values.setVisible(True)
            print("   ✓ Tablas de latencias/amplitudes visibles")

        # ESTACIÓN 5 OSCE: Activar modo especial en AbrReport
        # - Oculta pestañas Esquema y Previsualización
        # - Solo muestra Conclusiones para escribir el informe
        if hasattr(self.report, 'activar_modo_estacion_5'):
            self.report.activar_modo_estacion_5()
            print("   ✓ Modo Estación 5 activado en Conclusiones (solo esa pestaña visible)")

        # HABILITAR pestaña de Conclusiones (para el informe)
        if hasattr(self, 'tabWidget'):
            self.tabWidget.setTabEnabled(2, True)  # Índice 2 = Conclusiones
            # Cambiar DIRECTAMENTE a la pestaña de Conclusiones para escribir el informe
            self.tabWidget.setCurrentIndex(2)
            print("   ✓ Pestaña Conclusiones habilitada y mostrada directamente")

        # Asegurar que los botones de navegación estén ocultos
        self.actualizar_botones_navegacion()

        print("\n✅ Estación 5: Modo informe activado")
        print("   - Vista directa de Conclusiones para escribir informe")
        print("   - Puede alternar a Gráficos para revisar curvas")
        print("   - Puede ver tablas de latencias/amplitudes")
        print("   - Puede ver gráfico latencia-intensidad")
        print("   - Informe se enviará automáticamente al finalizar el tiempo")
        print("   - Sin navegación entre casos (solo Caso 3)")

    def reset_parametros_default(self):
        """Resetea los parámetros del control a sus valores por defecto (Estación 3)"""
        # Configuración por defecto para Estación 3
        default_config = {
            'stim': 'Click',
            'pol': 'Alternante',
            'int': 80,
            'mkg': 10,          # Cambio: era 0
            'rate': 3.3,        # Cambio: era 21.1
            'filter_down': '100',
            'filter_passhigh': '4000',  # Cambio: era '3000'
            'average': 1000,    # Cambio: era 2000
            'side': 'OI',       # Cambio: era 'OD'
            'atten': False
        }

        # Aplicar configuración por defecto al control básico
        if hasattr(self.control, 'set_data'):
            self.control.set_data(default_config)

        # Habilitar todos los estímulos (Click, Tone burst, etc.) para que puedan elegir
        if hasattr(self.control, 'cb_stim'):
            self.control.cb_stim.setEnabled(True)

        # Aplicar configuración por defecto a parámetros avanzados (Estación 3)
        default_advance_config = {
            'transductor': 'Fono de copa',     # Cambio: era 'Fono inserción'
            'ventana': 20,                     # Cambio: era 12
            'fsp': 'Desactivado',              # Cambio: era 'Detección 99% y FSP de 3.1'
            'ruido_residual': '100nV',         # Cambio: era '40nV'
            'electrodo_vertex': 'A1',          # Cambio: era 'Cz'
            'electrodo_derecho': 'A1',         # Mantenido
            'electrodo_izquierdo': 'A1',       # Cambio: era 'A2'
            'electrodo_tierra': 'A1'           # Cambio: era 'Cz'
        }

        self.set_advance_settings_data(default_advance_config)

        print("⚙️  Parámetros reseteados a default Estación 3")
        print("   Básicos: Click, Alternante, 80dB, 10dB mask, 1000 prom, 3.3 rate, 4000Hz, OI")
        print("   Avanzados: Fono de copa, Ventana 20ms, FSP Desactivado, 100nV, Electrodos A1")

    def configurar_parametros_estacion_4(self):
        """Configura los parámetros específicos para Estación 4"""
        # Configuración específica para Estación 4
        config_estacion_4 = {
            'stim': 'Click',
            'pol': 'Rarefacción',  # Cambio importante
            'int': 80,
            'mkg': 0,
            'rate': 21.1,
            'filter_down': '100',
            'filter_passhigh': '3000',
            'average': 2000,
            'side': 'OD',
            'atten': False
        }

        # Aplicar configuración al control básico
        if hasattr(self.control, 'set_data'):
            self.control.set_data(config_estacion_4)

        # Configuración avanzada específica para Estación 4
        config_avanzada_estacion_4 = {
            'transductor': 'Fono inserción',
            'ventana': 12,
            'fsp': 'Detección 99% y FSP de 3.1',
            'ruido_residual': '40nV',
            'electrodo_vertex': 'Cz',
            'electrodo_derecho': 'A2',  # Cambio: era A1
            'electrodo_izquierdo': 'A1',  # Cambio: era A2
            'electrodo_tierra': 'Ceja izquierda'  # Cambio: era Cz
        }

        self.set_advance_settings_data(config_avanzada_estacion_4)

        print("⚙️  Parámetros configurados para Estación 4 (Rarefacción, A2/A1, Ceja izquierda)")

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

    def abrir_dialogo_informe_estacion5(self):
        """
        MÉTODO DESACTIVADO - Ya no se usa diálogo separado

        En la nueva implementación, el informe se escribe directamente
        en la pestaña Conclusiones y se guarda automáticamente al finalizar el tiempo.
        """
        # Ya no abrimos diálogo, el informe está en la pestaña Conclusiones
        QMessageBox.information(
            self,
            "Estación 5 - Informe",
            "El informe se completa directamente en la pestaña 'Conclusiones'.\n\n"
            "Los campos 'Descripción' y 'Conclusión' se guardarán automáticamente "
            "cuando finalice el tiempo de la estación."
        )

        # Cambiar a la pestaña de Conclusiones si no está ahí
        if hasattr(self, 'tabWidget'):
            self.tabWidget.setCurrentIndex(2)  # Índice 2 = Conclusiones

        return

        # ===== CÓDIGO ANTERIOR (comentado) =====
        # if self.estacion_actual != 5:
        #     QMessageBox.warning(
        #         self,
        #         "Acción no disponible",
        #         "El formulario de informe solo está disponible en la Estación 5."
        #     )
        #     return
        #
        # caso_3_data = self.datos_estaciones[5]['casos'][3]
        # case_id = caso_3_data.get('case_id', None)
        # dialogo = DialogoInformeEstacion5(self, caso_id=case_id, memory=self.memory)
        #
        # if 'informe' in caso_3_data:
        #     dialogo.cargar_informe(caso_3_data['informe'])
        #
        # def guardar_informe_completo(informe_data):
        #     self.datos_estaciones[5]['casos'][3]['informe'] = informe_data
        #
        # dialogo.informe_completado.connect(guardar_informe_completo)
        # dialogo.exec()

    def abrir_dialogo_osce(self):
        """Abre o reabre el diálogo de selección de estaciones OSCE"""
        if self.dialog_osce is None:
            # Verificar si estamos en modo desarrollo
            modo_desarrollo = hasattr(self, 'estacion_desarrollo') and self.estacion_desarrollo
            self.dialog_osce = CuadroDialogoOSCE(self, modo_desarrollo=modo_desarrollo)

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
            # Capturar datos del estudiante (solo la primera vez)
            if not self.datos_estudiante_osce['nombre']:
                self.datos_estudiante_osce = self.dialog_osce.datos_estudiante.copy()
                print(f"\n{'='*80}")
                print(f"👤 DATOS DEL ESTUDIANTE REGISTRADOS")
                print(f"{'='*80}")
                print(f"Nombre: {self.datos_estudiante_osce['nombre']}")
                print(f"Número: {self.datos_estudiante_osce['numero']}")
                print(f"{'='*80}\n")

            self.iniciar_estacion(self.dialog_osce.estacion_seleccionada)

    def iniciar_estacion(self, numero_estacion):
        """Inicia una estación específica del OSCE"""
        self.estacion_actual = numero_estacion

        # Configurar parámetros según estación
        if numero_estacion == 3:
            # Estación 3: Parámetros default con Alternante
            self.reset_parametros_default()
        elif numero_estacion == 4:
            # Estación 4: Parámetros específicos con Rarefacción
            self.configurar_parametros_estacion_4()
        # Estación 5: No resetear (hereda de Estación 4)

        # Cargar el primer caso de la estación
        if numero_estacion == 5:
            # Estación 5: Solo tiene caso 3 (heredado)
            self.caso_actual = 3
            # Heredar datos de estación 4 caso 3
            self.heredar_datos_estacion_4()
            self.actualizar_ui_caso(5, 3)
        else:
            # Estaciones 3 y 4: Reiniciar al caso 1
            self.caso_actual = 1
            # Cargar caso 1
            self.cargar_caso(numero_estacion, 1)

        # Configurar según estación
        if numero_estacion == 3:
            # Estación 3: Deshabilitar botón Grabar y Conclusiones
            self.deshabilitar_captura_estacion_3()
        elif numero_estacion == 4:
            # Estación 4: Habilitar botón Grabar, deshabilitar Conclusiones
            self.habilitar_captura_estacion_4()
        elif numero_estacion == 5:
            # Estación 5: Habilitar Conclusiones para informe, deshabilitar captura
            self.habilitar_conclusiones_estacion_5()

        # Actualizar botones de navegación
        self.actualizar_botones_navegacion()

        # Configurar timer para 5 minutos
        self.segundos_restantes = TIEMPO_ESTACION_OSCE * 60
        self.timer.start(1000)

        print(f"Iniciando Estación {numero_estacion} - Caso {self.caso_actual}")

    def guardar_datos_estacion(self):
        """Guarda los datos de la estación actual al finalizar el tiempo"""
        if self.estacion_actual is not None:
            # ESTACIÓN 5: Guardar automáticamente el informe de Conclusiones
            if self.estacion_actual == 5:
                if hasattr(self.report, 'obtener_informe_estacion_5'):
                    informe_data = self.report.obtener_informe_estacion_5()
                    self.datos_estaciones[5]['casos'][3]['informe'] = informe_data
                    print("\n" + "="*80)
                    print("📄 INFORME ESTACIÓN 5 GUARDADO AUTOMÁTICAMENTE")
                    print("="*80)
                    print(f"Identificación: {informe_data['datos_caso']['identificacion']}")
                    print(f"Fecha: {informe_data['datos_caso']['fecha']}")
                    print(f"Timestamp: {informe_data['timestamp']}")
                    print(f"Caracteres descripción: {len(informe_data['hallazgos'])}")
                    print(f"Caracteres conclusión: {len(informe_data['conclusion'])}")
                    print("="*80 + "\n")

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
        # Usar context.get_resource para el directorio base, luego construir la ruta
        base_dir = context.get_resource('')
        resultados_dir = os.path.join(base_dir, 'resultados_osce')
        if not os.path.exists(resultados_dir):
            os.makedirs(resultados_dir)

        # Timestamp para el archivo
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_json = os.path.join(resultados_dir, f"osce_completo_{timestamp}.json")

        # Crear directorio para imágenes de este OSCE
        imagenes_dir = os.path.join(resultados_dir, f"imagenes_{timestamp}")
        if not os.path.exists(imagenes_dir):
            os.makedirs(imagenes_dir)

        # Guardar datos en JSON
        datos_completos = {
            'fecha': datetime.datetime.now().isoformat(),
            'estudiante': self.datos_estudiante_osce,
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

        # Exportar gráficos de cada caso de Estación 4
        print("\n" + "="*80)
        print("📊 EXPORTANDO GRÁFICOS DE CURVAS ABR")
        print("="*80)

        imagenes_casos = {}

        # Guardar memoria actual antes del loop
        memory_backup = self.memory.copy()

        # Exportar gráficos para cada caso de la Estación 4
        for num_caso in [1, 2, 3]:
            print(f"\nExportando gráficos del Caso {num_caso}...")

            caso_data = self.datos_estaciones[4]['casos'][num_caso]
            memory_caso = caso_data.get('memory', {})

            if memory_caso:
                # CRÍTICO: Cambiar temporalmente caso_actual para que restaurar_curvas_desde_memoria use los datos correctos
                caso_actual_original = self.caso_actual
                estacion_actual_original = self.estacion_actual

                self.caso_actual = num_caso
                self.estacion_actual = 4

                # Cargar memoria del caso
                self.memory = memory_caso

                # Limpiar gráficos completamente antes de restaurar
                self.graph_r.pw.clear()
                self.graph_l.pw.clear()
                self.graph_lat_int.clear_graph()

                # Restaurar curvas en los gráficos
                self.restaurar_curvas_desde_memoria()

                # Actualizar gráfico de latencia-intensidad
                self.graph_lat_int.plot_data(self.memory)

                # CRÍTICO: Forzar procesamiento de eventos Qt MÚLTIPLES VECES para actualizar gráficos
                from PySide6.QtWidgets import QApplication
                for _ in range(3):  # Procesar eventos varias veces
                    QApplication.processEvents()

                # Exportar gráficos (ahora que están actualizados visualmente)
                self.graph_r.export_()
                self.graph_l.export_()
                self.graph_lat_int.export_()

                # Restaurar caso_actual y estacion_actual
                self.caso_actual = caso_actual_original
                self.estacion_actual = estacion_actual_original

                # Copiar imágenes exportadas al directorio del OSCE
                import shutil
                temp_dir = context.get_resource('temp')

                img_od = os.path.join(temp_dir, '0.png')
                img_oi = os.path.join(temp_dir, '1.png')
                img_lat = os.path.join(temp_dir, 'LatInt.png')

                dest_od = os.path.join(imagenes_dir, f'caso{num_caso}_OD.png')
                dest_oi = os.path.join(imagenes_dir, f'caso{num_caso}_OI.png')
                dest_lat = os.path.join(imagenes_dir, f'caso{num_caso}_LatInt.png')

                if os.path.exists(img_od):
                    shutil.copy(img_od, dest_od)
                    print(f"  ✓ Gráfico OD exportado: {dest_od}")

                if os.path.exists(img_oi):
                    shutil.copy(img_oi, dest_oi)
                    print(f"  ✓ Gráfico OI exportado: {dest_oi}")

                if os.path.exists(img_lat):
                    shutil.copy(img_lat, dest_lat)
                    print(f"  ✓ Gráfico Lat-Int exportado: {dest_lat}")

                # Guardar rutas de imágenes
                imagenes_casos[num_caso] = {
                    'OD': dest_od if os.path.exists(dest_od) else None,
                    'OI': dest_oi if os.path.exists(dest_oi) else None,
                    'LatInt': dest_lat if os.path.exists(dest_lat) else None
                }

                # Restaurar memoria original
                self.memory = memory_backup

            else:
                print(f"  ⚠ Caso {num_caso} sin datos de memoria")
                imagenes_casos[num_caso] = {'OD': None, 'OI': None, 'LatInt': None}

        print("\n✓ Exportación de gráficos completada")
        print("="*80 + "\n")

        # Generar informe HTML/PDF para evaluación docente
        nombre_estudiante = self.datos_estudiante_osce.get('nombre', 'Estudiante')
        numero_estudiante = self.datos_estudiante_osce.get('numero', 'N/A')

        generador = GeneradorInformeOSCE(
            self.datos_estaciones,
            nombre_estudiante=nombre_estudiante,
            numero_estudiante=numero_estudiante,
            imagenes_casos=imagenes_casos
        )

        # Generar HTML
        archivo_html = os.path.join(resultados_dir, f"informe_osce_{timestamp}.html")
        generador.guardar_html(archivo_html)

        # Intentar generar PDF
        archivo_pdf = os.path.join(resultados_dir, f"informe_osce_{timestamp}.pdf")
        try:
            generador.guardar_pdf(archivo_pdf)
            archivo_final = archivo_pdf
        except Exception as e:
            print(f"No se pudo generar PDF: {e}")
            print("Se guardó como HTML en su lugar.")
            archivo_final = archivo_html

        # Mostrar mensaje al usuario con ambos archivos
        QMessageBox.information(
            self,
            "OSCE Completado",
            f"¡Las 3 estaciones han sido completadas exitosamente!\n\n"
            f"Archivos generados:\n\n"
            f"📋 Informe para evaluación docente:\n{archivo_final}\n\n"
            f"💾 Datos completos (JSON):\n{archivo_json}\n\n"
            f"El informe HTML/PDF contiene toda la información necesaria "
            f"para la evaluación del docente según las pautas OSCE."
        )

        # Enviar PDF automáticamente al servidor (silencioso, sin confirmación)
        if archivo_final.endswith('.pdf'):
            self.enviar_pdf_a_servidor_automatico(archivo_final, nombre_estudiante, numero_estudiante)

    def enviar_pdf_a_servidor_automatico(self, ruta_pdf, nombre_estudiante, numero_estudiante):
        """
        Envía el PDF al servidor automáticamente sin preguntar al usuario.
        Si falla, solo continúa sin mostrar errores.

        Args:
            ruta_pdf: Ruta al archivo PDF
            nombre_estudiante: Nombre del estudiante
            numero_estudiante: Número del estudiante
        """
        import os

        # URL hardcodeada del servidor
        url_servidor = "https://tmeduca.org/osce/recibir_pdf.php"

        print(f"\n{'='*80}")
        print(f"📤 ENVIANDO PDF AL SERVIDOR")
        print(f"{'='*80}")
        print(f"Estudiante: {nombre_estudiante}")
        print(f"Número: {numero_estudiante}")
        print(f"Servidor: {url_servidor}")
        print(f"Archivo: {os.path.basename(ruta_pdf)}")

        try:
            # Importar módulo de envío
            from lib.EnviarPDFServidor import enviar_pdf_osce

            # Enviar el PDF
            resultado = enviar_pdf_osce(
                ruta_pdf=ruta_pdf,
                nombre_estudiante=nombre_estudiante,
                numero_estudiante=numero_estudiante,
                url_servidor=url_servidor
            )

            # Mostrar resultado solo en consola
            if resultado['exito']:
                print(f"✓ PDF enviado exitosamente")
                print(f"Mensaje: {resultado['mensaje']}")
                if resultado.get('url_pdf'):
                    print(f"URL PDF: {resultado['url_pdf']}")
                print(f"{'='*80}\n")
            else:
                # Error al enviar, pero continuar sin mostrar ventana al usuario
                print(f"⚠ No se pudo enviar el PDF al servidor")
                print(f"Error: {resultado.get('error', 'Desconocido')}")
                print(f"El archivo se guardó localmente en: {ruta_pdf}")
                print(f"{'='*80}\n")

        except ImportError:
            # Si no está el módulo de envío, solo continuar
            print(f"⚠ Módulo de envío no disponible")
            print(f"El archivo se guardó localmente en: {ruta_pdf}")
            print(f"{'='*80}\n")
        except Exception as e:
            # Cualquier otro error, continuar silenciosamente
            print(f"⚠ Error al enviar PDF: {str(e)}")
            print(f"El archivo se guardó localmente en: {ruta_pdf}")
            print(f"{'='*80}\n")

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
    # Parsear argumentos de línea de comandos (para desarrollo/testing)
    parser = argparse.ArgumentParser(description='Simulador PEATC - OSCE')
    parser.add_argument('--dev', '--desarrollo', action='store_true',
                        help='Activar modo desarrollo: habilita todas las estaciones OSCE desde el inicio')
    parser.add_argument('--skip-verificacion', action='store_true',
                        help='Saltar verificación de activación - Solo para desarrollo')
    args = parser.parse_args()

    # Verificar activación (a menos que se use --skip-verificacion o --dev)
    if not args.skip_verificacion and not args.dev:
        if not verificar_activacion():
            sys.exit(1)  # Cerrar aplicación si no está activada
    else:
        print("⚠️  MODO DESARROLLO: Verificación de activación deshabilitada")

    # Crear ventana principal con flag de desarrollo
    window = MainWindow(modo_desarrollo=args.dev)

    style_file = context.get_resource('qss/style_base.qss')

    with open(style_file, 'r', encoding='utf-8') as f:
        style = f.read()

    window.setStyleSheet(style)
    window.show()

    exit_code = context.app.exec()

    sys.exit(exit_code)
