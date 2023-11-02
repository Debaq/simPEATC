from PySide6.QtCore import QCoreApplication, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget
from UI.AbrReport_ui import Ui_AbrReport
from datetime import datetime
tr = QCoreApplication.translate

class AbrReport(QWidget, Ui_AbrReport):
    measure = Signal(str)
    def __init__(self) -> None:
        QWidget.__init__(self)
        self.setupUi(self)
        self.lbl_date.setText(self.date_current())


    def date_current(self):
        current_date = datetime.now().strftime("%d/%m/%Y")
        return current_date
    

    def pdf_view(self):
        self.webEngineView.load()





