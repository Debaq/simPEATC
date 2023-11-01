from PySide6.QtCore import QCoreApplication, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget
from UI.Ui_AbrReport import Ui_AbrReport

tr = QCoreApplication.translate

class AbrReport(QWidget, Ui_AbrReport):
    measure = Signal(str)
    def __init__(self) -> None:
        QWidget.__init__(self)
        self.setupUi(self)






