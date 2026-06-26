from PySide6.QtWidgets import QWidget
from UI.AbrConfig_ui import Ui_Abr_Config
from PySide6.QtCore import QCoreApplication, Signal

tr = QCoreApplication.translate

class AbrControl(QWidget, Ui_Abr_Config):
    capture = Signal(str)
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.config_btn()
        # ESTACIÓN 3 OSCE: Todos los estímulos están habilitados
        # self.disable_unimplemented_stimuli()


    def disable_unimplemented_stimuli(self) -> None:
        """Desactiva estímulos no implementados (chirp, lschirp, burst)
        NOTA: Este método está deshabilitado para la Estación 3 del OSCE
        donde los estudiantes deben poder seleccionar todos los estímulos.
        """
        model = self.cb_stim.model()

        # Buscar y desactivar items específicos
        for i in range(self.cb_stim.count()):
            item_text = self.cb_stim.itemText(i).lower()

            # Desactivar chirp, lschirp y burst
            if any(stim in item_text for stim in ['chirp', 'lschirp', 'burst', 'tone']):
                item = model.item(i)
                item.setEnabled(False)
                # Opcional: agregar tooltip explicativo
                item.setToolTip("Estímulo en desarrollo - Próximamente disponible")


    def get_data(self) -> dict:
        stim = self.cb_stim.currentText()
        pol = self.cb_pol.currentText()
        inty = self.sb_intencity.value()
        mkg = self.sb_mskg.value()
        rate = self.sb_rate.value()
        filter_passdown = self.cb_filter_down.currentText()
        filter_passhigh =self.cb_filter_up.currentText()
        average = self.sb_prom.value()
        side = self.cb_side.currentText()
        atten = self.ch_atten.isChecked()

        return {"stim":stim, "pol":pol, "int":inty, "mkg":mkg,
                "rate":rate, "filter_down":filter_passdown,
                "filter_passhigh": filter_passhigh, "average" : average,
                "side":side, "atten":atten}

    def set_data(self, config: dict) -> None:
        """Aplica configuración a los widgets del control"""
        if 'stim' in config:
            idx = self.cb_stim.findText(config['stim'])
            if idx >= 0:
                self.cb_stim.setCurrentIndex(idx)

        if 'pol' in config:
            idx = self.cb_pol.findText(config['pol'])
            if idx >= 0:
                self.cb_pol.setCurrentIndex(idx)

        if 'int' in config:
            self.sb_intencity.setValue(config['int'])

        if 'mkg' in config:
            self.sb_mskg.setValue(config['mkg'])

        if 'rate' in config:
            self.sb_rate.setValue(config['rate'])

        if 'filter_down' in config:
            idx = self.cb_filter_down.findText(config['filter_down'])
            if idx >= 0:
                self.cb_filter_down.setCurrentIndex(idx)

        if 'filter_passhigh' in config:
            idx = self.cb_filter_up.findText(config['filter_passhigh'])
            if idx >= 0:
                self.cb_filter_up.setCurrentIndex(idx)

        if 'average' in config:
            self.sb_prom.setValue(config['average'])

        if 'side' in config:
            idx = self.cb_side.findText(config['side'])
            if idx >= 0:
                self.cb_side.setCurrentIndex(idx)

        if 'atten' in config:
            self.ch_atten.setChecked(config['atten'])

    def disabled_all(self, value:bool=True) -> None:
        self.cb_stim.setDisabled(value)
        self.cb_pol.setDisabled(value)
        self.sb_intencity.setDisabled(value)
        self.sb_mskg.setDisabled(value)
        self.sb_rate.setDisabled(value)
        self.cb_filter_down.setDisabled(value)
        self.cb_filter_up.setDisabled(value)
        self.sb_prom.setDisabled(value)
        self.cb_side.setDisabled(value)
        self.ch_atten.setDisabled(value)

    def config_btn(self) -> None:
        self.btn_start.clicked.connect(self.start_capture)
        self.btn_stop.clicked.connect(self.stop_capture)

    def start_capture(self) -> None:
        self.btn_start.setText(tr("Abr_Config", u"Pausar", None))
        self.btn_start.setStatusTip(tr("Abr_Config", u"Pausar prueba", None))
        self.btn_start.clicked.disconnect()
        self.btn_start.clicked.connect(self.pause_capture)
        self.disabled_all(True)
        self.capture.emit("record")

    def pause_capture(self) -> None:
        self.btn_start.setText(tr("Abr_Config", u"Continuar", None))
        self.btn_start.setStatusTip(tr("Abr_Config", u"Continuar prueba", None))
        self.btn_start.clicked.disconnect()
        self.btn_start.clicked.connect(self.start_capture)
        self.capture.emit("pause")

    def stop_capture(self) -> None:
        self.btn_start.setText(tr("Abr_Config", u"Iniciar", None))
        self.btn_start.setStatusTip(tr("Abr_Config", u"Iniciar prueba", None))
        self.btn_start.clicked.disconnect()
        self.btn_start.clicked.connect(self.start_capture)
        self.disabled_all(False)
        self.capture.emit("stopped")
