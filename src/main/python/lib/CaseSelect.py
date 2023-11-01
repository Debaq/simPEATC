import json

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMessageBox, QSpinBox, QVBoxLayout


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

    def retrieve_data(self, json_data, index):
        if index < 0 or index >= len(json_data["cases_preset"]):
            return None  # Indice no existe en cases_preset

        # Obteniendo los nombres (keys) de los tipos en base al índice dado
        od_type_name = json_data["cases_preset"][index][0]
        oi_type_name = json_data["cases_preset"][index][1]

        # Obteniendo los datos correspondientes a esos nombres
        od_data = json_data["types"].get(od_type_name, None)
        oi_data = json_data["types"].get(oi_type_name, None)

        if od_data is None or oi_data is None:
            return None  # Alguno de los nombres no existe en types

        return {"OD": od_data, "OI": oi_data}

    

    def load_json_to_dict(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data


