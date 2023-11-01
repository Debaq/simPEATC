from PySide6.QtWidgets import  QWidget
from UI.Ui_AbrDetails import Ui_AbrDetails

class AbrDetail(QWidget, Ui_AbrDetails):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)