"""
Interfaz de informe para Estación 5 del OSCE
Permite al estudiante escribir la interpretación del caso 3 de Estación 4
Versión 1.0
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QTextEdit, QPushButton, QGroupBox, QFormLayout,
                               QLineEdit, QMessageBox, QScrollArea, QWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import datetime


class DialogoInformeEstacion5(QDialog):
    """
    Diálogo para que el estudiante complete el informe de interpretación
    de PEATC para la Estación 5 del OSCE
    """

    informe_completado = Signal(dict)  # Señal con el informe completo

    def __init__(self, parent=None, caso_id=None, memory=None):
        super().__init__(parent)
        self.caso_id = caso_id
        self.memory = memory or {}
        self.informe_data = {}

        self.setWindowTitle("Estación 5 - Interpretación e Informe PEATC")
        self.setModal(True)
        self.resize(800, 700)

        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        main_layout = QVBoxLayout(self)

        # Título
        titulo = QLabel("<h2>Estación 5: Interpretación, Informe y Decisiones</h2>")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        # Instrucciones
        instrucciones = QLabel(
            "<p><b>Instrucciones:</b> Complete el informe de PEATC del Caso 3 "
            "de la estación anterior. Incluya todos los elementos requeridos.</p>"
        )
        instrucciones.setWordWrap(True)
        main_layout.addWidget(instrucciones)

        # Área de scroll para el formulario
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # === SECCIÓN 1: DATOS DEL CASO ===
        grupo_datos = QGroupBox("1. Datos del Caso")
        grupo_datos_layout = QFormLayout()

        self.txt_identificacion = QLineEdit()
        self.txt_identificacion.setPlaceholderText("Ej: Caso 3, Paciente simulado")
        grupo_datos_layout.addRow("Identificación:", self.txt_identificacion)

        self.txt_fecha = QLineEdit()
        self.txt_fecha.setText(datetime.datetime.now().strftime("%Y-%m-%d"))
        grupo_datos_layout.addRow("Fecha:", self.txt_fecha)

        self.txt_condiciones = QTextEdit()
        self.txt_condiciones.setMaximumHeight(60)
        self.txt_condiciones.setPlaceholderText("Ej: Registro realizado en condiciones de simulación...")
        grupo_datos_layout.addRow("Condiciones:", self.txt_condiciones)

        grupo_datos.setLayout(grupo_datos_layout)
        scroll_layout.addWidget(grupo_datos)

        # === SECCIÓN 2: DESCRIPCIÓN DE HALLAZGOS ===
        grupo_hallazgos = QGroupBox("2. Descripción de Hallazgos")
        grupo_hallazgos_layout = QVBoxLayout()

        lbl_hallazgos = QLabel(
            "Describa los hallazgos del registro (latencias absolutas, intervalos "
            "interpicos, diferencias interaurales, morfología, umbral):"
        )
        lbl_hallazgos.setWordWrap(True)
        grupo_hallazgos_layout.addWidget(lbl_hallazgos)

        self.txt_hallazgos = QTextEdit()
        self.txt_hallazgos.setMinimumHeight(150)
        self.txt_hallazgos.setPlaceholderText(
            "Ejemplo:\n\n"
            "OÍDO DERECHO:\n"
            "- Onda I: 1.6 ms\n"
            "- Onda III: 3.7 ms\n"
            "- Onda V: 5.6 ms\n"
            "- I-III: 2.1 ms\n"
            "- III-V: 1.9 ms\n"
            "- I-V: 4.0 ms\n\n"
            "OÍDO IZQUIERDO:\n"
            "- Onda I: 1.6 ms\n"
            "- Onda III: 4.2 ms\n"
            "- Onda V: 6.3 ms\n"
            "- I-III: 2.6 ms (prolongado)\n"
            "- III-V: 2.1 ms\n"
            "- I-V: 4.7 ms (prolongado)\n\n"
            "DIFERENCIAS INTERAURALES:\n"
            "- I-III: 0.5 ms (>0.4 ms, significativo)\n"
            "- I-V: 0.7 ms (>0.4 ms, significativo)\n\n"
            "MORFOLOGÍA:\n"
            "- OD: Ondas bien definidas\n"
            "- OI: Onda III de baja amplitud y morfología pobre\n\n"
            "UMBRAL DE ONDA V:\n"
            "- OD: 20 dB nHL\n"
            "- OI: 30 dB nHL"
        )
        grupo_hallazgos_layout.addWidget(self.txt_hallazgos)

        grupo_hallazgos.setLayout(grupo_hallazgos_layout)
        scroll_layout.addWidget(grupo_hallazgos)

        # === SECCIÓN 3: COMPARACIÓN CON NORMATIVOS ===
        grupo_normativos = QGroupBox("3. Comparación con Valores Normativos")
        grupo_normativos_layout = QVBoxLayout()

        lbl_normativos = QLabel(
            "Compare los hallazgos con valores normativos e identifique alteraciones:"
        )
        lbl_normativos.setWordWrap(True)
        grupo_normativos_layout.addWidget(lbl_normativos)

        self.txt_normativos = QTextEdit()
        self.txt_normativos.setMinimumHeight(120)
        self.txt_normativos.setPlaceholderText(
            "Ejemplo:\n\n"
            "VALORES NORMATIVOS (a 75 dB nHL):\n"
            "- Latencias absolutas: I=1.6±0.2ms, III=3.7±0.2ms, V=5.6±0.2ms\n"
            "- Intervalos interpicos: I-III=2.0±0.4ms, III-V=1.8±0.4ms, I-V=3.8±0.4ms\n"
            "- Diferencia interaural: <0.4ms\n\n"
            "HALLAZGOS FUERA DE RANGO:\n"
            "- OI: I-III prolongado (2.6 ms vs 2.0±0.4 ms)\n"
            "- OI: I-V prolongado (4.7 ms vs 3.8±0.4 ms)\n"
            "- Diferencia interaural I-III significativa (0.5 ms > 0.4 ms)\n"
            "- Diferencia interaural I-V significativa (0.7 ms > 0.4 ms)"
        )
        grupo_normativos_layout.addWidget(self.txt_normativos)

        grupo_normativos.setLayout(grupo_normativos_layout)
        scroll_layout.addWidget(grupo_normativos)

        # === SECCIÓN 4: CONCLUSIÓN DIAGNÓSTICA ===
        grupo_conclusion = QGroupBox("4. Conclusión Diagnóstica")
        grupo_conclusion_layout = QVBoxLayout()

        lbl_conclusion = QLabel(
            "Establezca la conclusión diagnóstica según protocolo (clasificación del "
            "patrón, alteraciones específicas, correlación clínica):"
        )
        lbl_conclusion.setWordWrap(True)
        grupo_conclusion_layout.addWidget(lbl_conclusion)

        self.txt_conclusion = QTextEdit()
        self.txt_conclusion.setMinimumHeight(120)
        self.txt_conclusion.setPlaceholderText(
            "Ejemplo:\n\n"
            "CLASIFICACIÓN: Patrón compatible con lesión neural/retrococlear izquierda\n\n"
            "ALTERACIONES ESPECÍFICAS:\n"
            "- Prolongación significativa del intervalo I-III en oído izquierdo\n"
            "- Prolongación del intervalo I-V izquierdo\n"
            "- Diferencias interaurales significativas\n"
            "- Morfología alterada de onda III izquierda\n\n"
            "CORRELACIÓN CLÍNICA:\n"
            "Los hallazgos son compatibles con patología retrococlear izquierda, "
            "sugestivo de schwannoma vestibular o lesión del VIII par craneal. "
            "Se recomienda imagen por resonancia magnética con contraste para "
            "descartar lesión ocupante de espacio."
        )
        grupo_conclusion_layout.addWidget(self.txt_conclusion)

        grupo_conclusion.setLayout(grupo_conclusion_layout)
        scroll_layout.addWidget(grupo_conclusion)

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # Botones
        botones_layout = QHBoxLayout()

        btn_guardar = QPushButton("Guardar Borrador")
        btn_guardar.clicked.connect(self.guardar_borrador)
        botones_layout.addWidget(btn_guardar)

        botones_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(btn_cancelar)

        btn_finalizar = QPushButton("Finalizar Informe")
        btn_finalizar.clicked.connect(self.finalizar_informe)
        btn_finalizar.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        botones_layout.addWidget(btn_finalizar)

        main_layout.addLayout(botones_layout)

    def guardar_borrador(self):
        """Guarda un borrador del informe sin cerrar el diálogo"""
        self.recopilar_datos()
        QMessageBox.information(
            self,
            "Borrador Guardado",
            "El borrador del informe ha sido guardado. Puede continuar editando."
        )

    def finalizar_informe(self):
        """Finaliza y envía el informe completo"""
        # Validar que los campos críticos estén completos
        if not self.txt_hallazgos.toPlainText().strip():
            QMessageBox.warning(
                self,
                "Informe Incompleto",
                "Debe completar la sección de 'Descripción de Hallazgos' (campo crítico)."
            )
            return

        if not self.txt_normativos.toPlainText().strip():
            QMessageBox.warning(
                self,
                "Informe Incompleto",
                "Debe completar la 'Comparación con Valores Normativos' (campo crítico)."
            )
            return

        if not self.txt_conclusion.toPlainText().strip():
            QMessageBox.warning(
                self,
                "Informe Incompleto",
                "Debe establecer una 'Conclusión Diagnóstica' (campo crítico)."
            )
            return

        # Recopilar datos completos
        self.recopilar_datos()

        # Confirmar finalización
        respuesta = QMessageBox.question(
            self,
            "Finalizar Informe",
            "¿Está seguro de finalizar el informe? No podrá editarlo después.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            self.informe_completado.emit(self.informe_data)
            self.accept()

    def recopilar_datos(self):
        """Recopila todos los datos del formulario"""
        self.informe_data = {
            'datos_caso': {
                'identificacion': self.txt_identificacion.text(),
                'fecha': self.txt_fecha.text(),
                'condiciones': self.txt_condiciones.toPlainText()
            },
            'hallazgos': self.txt_hallazgos.toPlainText(),
            'normativos': self.txt_normativos.toPlainText(),
            'conclusion': self.txt_conclusion.toPlainText(),
            'caso_id': self.caso_id,
            'timestamp': datetime.datetime.now().isoformat()
        }

    def cargar_informe(self, informe_data):
        """Carga un informe previo (para edición)"""
        if not informe_data:
            return

        datos_caso = informe_data.get('datos_caso', {})
        self.txt_identificacion.setText(datos_caso.get('identificacion', ''))
        self.txt_fecha.setText(datos_caso.get('fecha', ''))
        self.txt_condiciones.setPlainText(datos_caso.get('condiciones', ''))

        self.txt_hallazgos.setPlainText(informe_data.get('hallazgos', ''))
        self.txt_normativos.setPlainText(informe_data.get('normativos', ''))
        self.txt_conclusion.setPlainText(informe_data.get('conclusion', ''))


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    dialogo = DialogoInformeEstacion5()

    def mostrar_informe(informe):
        print("="*80)
        print("INFORME COMPLETADO")
        print("="*80)
        print(f"\nDAT OS DEL CASO:")
        print(f"  Identificación: {informe['datos_caso']['identificacion']}")
        print(f"  Fecha: {informe['datos_caso']['fecha']}")
        print(f"\nHALLAZGOS:")
        print(informe['hallazgos'])
        print(f"\nNORMATIVOS:")
        print(informe['normativos'])
        print(f"\nCONCLUSIÓN:")
        print(informe['conclusion'])

    dialogo.informe_completado.connect(mostrar_informe)
    dialogo.exec()

    sys.exit(app.exec())
