from PySide6.QtCore import QCoreApplication, Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QTableWidgetItem
from UI.AbrDetailAllCurves_ui import Ui_DetailAllCurves

tr = QCoreApplication.translate

class AbrDetailAllCurves(QWidget, Ui_DetailAllCurves):
    sig_selected_curve = Signal(str)
    def __init__(self) -> None:
        QWidget.__init__(self)
        self.setupUi(self)
        self.data = {}
        # Conectar la señal cellClicked a la función on_cell_clicked
        self.tw_curves_list.cellClicked.connect(self.on_cell_clicked)
    
    def del_register(self):
        pass
    
    def process_and_fill_data (self, data_dict):
        for i in data_dict:
            data = {i:data_dict[i]}
            self.process_and_fill(data)

    def process_and_fill(self, data_dict):
        # La clave principal del diccionario (p. ej., 'R1') se usa como cabecera horizontal
        main_key = next(iter(data_dict))  # Obtener la primera clave del diccionario
        data = data_dict[main_key]

        # Crear un diccionario con el mapeo de la columna y el valor correspondiente
        row_data = {
            'Oído': data['side'],
            'Intensidad (MKg)': f"{data['int']}({data['mkg']})",
            'Polaridad': data['pol'],
            'Estímulo': data['stim'],
            'Tasa': data['rate'],
            'Filtros': f"{data['filter_passhigh']}-{data['filter_down']}",
            'Promediaciones': data['average'],
            'I:lat(amp)': self.format_lat_amp(data['LatAmp']['I']),
            'II:lat(amp)': self.format_lat_amp(data['LatAmp']['II']),
            'III:lat(amp)': self.format_lat_amp(data['LatAmp']['III']),
            'IV:lat(amp)': self.format_lat_amp(data['LatAmp']['IV']),
            'V:lat(amp)': self.format_lat_amp(data['LatAmp']['V']),
            'Interpeak I-III': self.cal_interpeak(data['LatAmp']['I'], data['LatAmp']['III']),
            'Interpeak III-V': self.cal_interpeak(data['LatAmp']['III'], data['LatAmp']['V']),
            'Interpeak I-V': self.cal_interpeak(data['LatAmp']['I'], data['LatAmp']['V']),
            'Relación V/I': self.calculate_ratio(data['LatAmp'])
        }
        

        header_labels = [self.tw_curves_list.horizontalHeaderItem(i).text() for i in range(self.tw_curves_list.columnCount())]

        existing_row = self.find_row_by_header(main_key)

        if existing_row is not None:  # Si existe, actualizar esa fila
            current_row = existing_row
        else:  # Si no existe, añadir una nueva fila
            current_row = self.tw_curves_list.rowCount()
            self.tw_curves_list.insertRow(current_row)
            self.tw_curves_list.setVerticalHeaderItem(current_row, QTableWidgetItem(main_key))

       # Llenar las celdas con los datos
        for header in header_labels:
            col = header_labels.index(header)
            value = row_data.get(header, '')
            self.tw_curves_list.setItem(current_row, col, QTableWidgetItem(str(value)))


    @staticmethod
    def format_lat_amp(lat_amp):
        # Formatear la latencia y amplitud
        return f"{round(lat_amp[0],2) if lat_amp[0] is not None else ''}" \
               f"({'{:.2f}'.format(lat_amp[1]) if lat_amp[1] is not None else ''})"

    @staticmethod
    def calculate_ratio(lat_amp_dict):
        # Calcular la relación V/I
        try:
            return round(lat_amp_dict['V'][1] / lat_amp_dict['I'][1],2)
        except (TypeError, ZeroDivisionError):
            return None

    @staticmethod
    def cal_interpeak(val_a:int, val_b:int) ->None:
        try:
            interpeak = abs(val_a[0] - val_b[0])
            interpeak = round(interpeak, 3)
            return interpeak
        except (TypeError, ZeroDivisionError):
            return None

    def find_row_by_header(self, header_name):
        # Buscar la fila por el encabezado vertical
        for row in range(self.tw_curves_list.rowCount()):
            vertical_header_item = self.tw_curves_list.verticalHeaderItem(row)
            if vertical_header_item and vertical_header_item.text() == header_name:
                return row
        return None

    def delete_row_by_header(self, header_name):
        # Elimina una fila por su nombre
        row = self.find_row_by_header(header_name)
        if row is not None:
            self.tw_curves_list.removeRow(row)
    
    def on_cell_clicked(self, row, column):
        # Esta función se llama cuando se hace clic en una celda
        curve_name = self.tw_curves_list.verticalHeaderItem(row).text()
        self.sig_selected_curve.emit(curve_name)
    