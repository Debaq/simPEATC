from PySide6.QtCore import QCoreApplication, Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QTableWidgetItem
from UI.Ui_AbrTable import Ui_TableData

tr = QCoreApplication.translate

class AbrTable(QWidget, Ui_TableData):
    measure_value = Signal(dict)
    def __init__(self, side) -> None:
        QWidget.__init__(self)
        self.setupUi(self)
        self.side = side
        self.set_table()
        self.data =   [ ['', ''],
                        ['', ''],
                        ['', ''],
                        ['', ''],
                        ['', '']]

    def set_table(self)->None:
        tables = [self.tw_latamp, self.tw_inter]
        color = self.get_color_table()
        s = f"QTableWidget::item{{ background-color:{color}; }}"
        for i in tables:
            i.cellClicked.connect(self.on_cell_clicked)
            i.setStyleSheet(s)

        self.label.setText("")

    def get_color_table(self) -> QColor:
        if self.side == 0:
            color = 'rgba(255, 0, 127, 30)'
        else:
            color = '#9965f4'
        return color

    def get_cols_rows(self, table) -> (int,int):
        cols = table.columnCount()
        rows = table.rowCount()
        return cols,rows

    def on_cell_clicked(self, row:int, column:int) -> None:
        table = self.sender().objectName()
        if table == 'tw_latamp':
            coord = (row, column)
            str_coords = self.curve_coord(coord)
            self.request_values(str_coords)

    def curve_coord(self, coord:str|tuple) -> str|tuple:
        coords_text =   [['I_L', 'I_A'],
                        ['II_L', 'II_A'],
                        ['III_L', 'III_A'],
                        ['IV_L', 'IV_A'],
                        ['V_L', 'V_A']]

        if isinstance(coord, str):
            for fila, lista in enumerate(coords_text):
                if coord in lista:
                    return (fila, lista.index(coord))
        else:
            return coords_text[coord[0]][coord[1]]

    def request_values(self, data:str) -> None:
        request = {f'{self.side}':{f'{data}':None}}
        self.measure_value.emit(request)

    def set_data(self, data):
        command = list(data[str(self.side)].keys())[0]
        coords = self.curve_coord(command)
        value = data[str(self.side)][command]
        self.data[coords[0]][coords[1]] = value
        value = round(value,2)
        item = QTableWidgetItem(str(value))
        self.tw_latamp.setItem(coords[0], coords[1], item)
        #print(f"command {command} ,  row {coords[0]}, column {coords[1]}")
        self.calcule_others()

    def calcule_others(self)->None:
        ##I-V column 1, i:row 0 v:row 4
        ##III-V column 1, iii:row 2 v:row 4
        ##I-III column 1, i:row 0 iii:row 2
        if self.data[0][0] and self.data[4][0]:
            self.cal_interpeak(0,4,0)
        if self.data[2][0] and self.data[4][0]:
            self.cal_interpeak(2,4,1)
        if self.data[0][0] and self.data[2][0]:
            self.cal_interpeak(0,2,2)
        if self.data[0][1] and self.data[4][1]:
            self.cal_rel_v_i()

    def reset_others(self)->None:
        if self.data[0][0] is None:
            self.tw_inter.setItem(0, 0, QTableWidgetItem(""))
            self.tw_inter.setItem(2, 0, QTableWidgetItem(""))
            self.tw_inter.setItem(3, 0, QTableWidgetItem(""))
        if self.data[2][0] is None:
            self.tw_inter.setItem(1, 0, QTableWidgetItem(""))
            self.tw_inter.setItem(2, 0, QTableWidgetItem(""))
        if self.data[4][0] is None:
            self.tw_inter.setItem(0, 0, QTableWidgetItem(""))
            self.tw_inter.setItem(1, 0, QTableWidgetItem(""))
            self.tw_inter.setItem(3, 0, QTableWidgetItem(""))
        if self.data[4][1] is None or self.data[0][1] is None:
            self.tw_inter.setItem(3, 0, QTableWidgetItem(""))

    def cal_rel_v_i(self,)->None:
        ##column 0, i:row 0 v:row 4
        value_i = self.data[0][1]
        value_v = self.data[4][1]
        relation = value_v/value_i
        relation = round(relation,2)
        item = QTableWidgetItem(str(relation))
        self.tw_inter.setItem(3,0, item)
        
    def cal_interpeak(self, pos_a:int, pos_b:int, cell:int) ->None:
        value_a = self.data[pos_a][0]
        value_b = self.data[pos_b][0]
        interpeak = abs(value_a - value_b)
        interpeak = round(interpeak, 3)
        item = QTableWidgetItem(str(interpeak))
        self.tw_inter.setItem(cell,0, item)

    def change_value_lat(self, data:dict):
        for i in data:
            for t in data[i]:
                coord = self.curve_coord(f"{t}_L")
                if data[i][t] is None:
                    self.tw_latamp.setItem(coord[0], 0, QTableWidgetItem(""))
                    self.tw_latamp.setItem(coord[0], 1, QTableWidgetItem(""))
                    self.data[coord[0]][0] = None
                    self.data[coord[0]][1] = None
                else:
                    print(data[i][t])
                    #self.data[coord[0]][0] = None
                    #self.data[coord[0]][1] = None

                self.reset_others()



    def get_data(self):
        return self.data



        







def hex_to_rgba(hex_value):
###ya no lo uso pero lo dejare por aquí
    """
    Convierte un color en formato hexadecimal a una tupla RGBA.

    Argumentos:
    - hex_value (str): Color en formato hexadecimal. Debe empezar con '#' y puede ser de 7 o 9 caracteres
    (por ejemplo: #FF5733 o #AAFF5733).

    Retorna:
    - Tupla con cuatro valores int que representan los valores RGBA del color.
    """
    if len(hex_value) == 7:  # Formato #RRGGBB
        r = int(hex_value[1:3], 16)
        g = int(hex_value[3:5], 16)
        b = int(hex_value[5:7], 16)
        a = 255
    elif len(hex_value) == 9:  # Formato #AARRGGBB
        a = int(hex_value[1:3], 16)
        r = int(hex_value[3:5], 16)
        g = int(hex_value[5:7], 16)
        b = int(hex_value[7:9], 16)
    else:
        raise ValueError("El valor hexadecimal no tiene un formato válido.")
    
    return (r, g, b, a)

                
