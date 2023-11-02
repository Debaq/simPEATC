# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AbrAdvanceSettings.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QGridLayout, QLabel, QSizePolicy,
    QSpinBox, QWidget)

class Ui_AdvanceSettings(object):
    def setupUi(self, AdvanceSettings):
        if not AdvanceSettings.objectName():
            AdvanceSettings.setObjectName(u"AdvanceSettings")
        AdvanceSettings.resize(400, 300)
        self.gridLayout = QGridLayout(AdvanceSettings)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(AdvanceSettings)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.comboBox = QComboBox(AdvanceSettings)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.gridLayout.addWidget(self.comboBox, 0, 2, 1, 1)

        self.label_2 = QLabel(AdvanceSettings)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.spinBox = QSpinBox(AdvanceSettings)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setMinimum(12)
        self.spinBox.setMaximum(600)

        self.gridLayout.addWidget(self.spinBox, 1, 2, 1, 1)

        self.label_3 = QLabel(AdvanceSettings)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.comboBox_2 = QComboBox(AdvanceSettings)
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName(u"comboBox_2")

        self.gridLayout.addWidget(self.comboBox_2, 2, 2, 1, 1)

        self.label_4 = QLabel(AdvanceSettings)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)

        self.comboBox_3 = QComboBox(AdvanceSettings)
        self.comboBox_3.addItem("")
        self.comboBox_3.setObjectName(u"comboBox_3")

        self.gridLayout.addWidget(self.comboBox_3, 3, 2, 1, 1)

        self.label_5 = QLabel(AdvanceSettings)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)

        self.comboBox_4 = QComboBox(AdvanceSettings)
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.setObjectName(u"comboBox_4")

        self.gridLayout.addWidget(self.comboBox_4, 4, 2, 1, 1)

        self.label_6 = QLabel(AdvanceSettings)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)

        self.comboBox_5 = QComboBox(AdvanceSettings)
        self.comboBox_5.addItem("")
        self.comboBox_5.addItem("")
        self.comboBox_5.addItem("")
        self.comboBox_5.addItem("")
        self.comboBox_5.addItem("")
        self.comboBox_5.setObjectName(u"comboBox_5")

        self.gridLayout.addWidget(self.comboBox_5, 5, 2, 1, 1)

        self.label_7 = QLabel(AdvanceSettings)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)

        self.comboBox_6 = QComboBox(AdvanceSettings)
        self.comboBox_6.addItem("")
        self.comboBox_6.addItem("")
        self.comboBox_6.addItem("")
        self.comboBox_6.addItem("")
        self.comboBox_6.addItem("")
        self.comboBox_6.setObjectName(u"comboBox_6")

        self.gridLayout.addWidget(self.comboBox_6, 6, 2, 1, 1)

        self.label_8 = QLabel(AdvanceSettings)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 7, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(AdvanceSettings)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 1)

        self.comboBox_7 = QComboBox(AdvanceSettings)
        self.comboBox_7.addItem("")
        self.comboBox_7.addItem("")
        self.comboBox_7.addItem("")
        self.comboBox_7.addItem("")
        self.comboBox_7.addItem("")
        self.comboBox_7.setObjectName(u"comboBox_7")

        self.gridLayout.addWidget(self.comboBox_7, 7, 2, 1, 1)


        self.retranslateUi(AdvanceSettings)
        self.buttonBox.accepted.connect(AdvanceSettings.accept)
        self.buttonBox.rejected.connect(AdvanceSettings.reject)

        QMetaObject.connectSlotsByName(AdvanceSettings)
    # setupUi

    def retranslateUi(self, AdvanceSettings):
        AdvanceSettings.setWindowTitle(QCoreApplication.translate("AdvanceSettings", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("AdvanceSettings", u"Transductor", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("AdvanceSettings", u"Fono inserci\u00f3n", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("AdvanceSettings", u"Fono de copa", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("AdvanceSettings", u"Vibrador \u00f3seo", None))

        self.label_2.setText(QCoreApplication.translate("AdvanceSettings", u"Ventana", None))
        self.label_3.setText(QCoreApplication.translate("AdvanceSettings", u"FSP", None))
        self.comboBox_2.setItemText(0, QCoreApplication.translate("AdvanceSettings", u"Detecci\u00f3n 99% y FSP de 3.1", None))

        self.label_4.setText(QCoreApplication.translate("AdvanceSettings", u"Ruido residual", None))
        self.comboBox_3.setItemText(0, QCoreApplication.translate("AdvanceSettings", u"40nV", None))

        self.label_5.setText(QCoreApplication.translate("AdvanceSettings", u"Electrodo Vertex", None))
        self.comboBox_4.setItemText(0, QCoreApplication.translate("AdvanceSettings", u"A1", None))
        self.comboBox_4.setItemText(1, QCoreApplication.translate("AdvanceSettings", u"A2", None))
        self.comboBox_4.setItemText(2, QCoreApplication.translate("AdvanceSettings", u"Cz", None))
        self.comboBox_4.setItemText(3, QCoreApplication.translate("AdvanceSettings", u"Ceja izquierda", None))
        self.comboBox_4.setItemText(4, QCoreApplication.translate("AdvanceSettings", u"No Conectado", None))

        self.label_6.setText(QCoreApplication.translate("AdvanceSettings", u"Electrodo Derecho", None))
        self.comboBox_5.setItemText(0, QCoreApplication.translate("AdvanceSettings", u"A1", None))
        self.comboBox_5.setItemText(1, QCoreApplication.translate("AdvanceSettings", u"A2", None))
        self.comboBox_5.setItemText(2, QCoreApplication.translate("AdvanceSettings", u"Cz", None))
        self.comboBox_5.setItemText(3, QCoreApplication.translate("AdvanceSettings", u"Ceja izquierda", None))
        self.comboBox_5.setItemText(4, QCoreApplication.translate("AdvanceSettings", u"No Conectado", None))

        self.label_7.setText(QCoreApplication.translate("AdvanceSettings", u"Electrodo Izquierdo", None))
        self.comboBox_6.setItemText(0, QCoreApplication.translate("AdvanceSettings", u"A1", None))
        self.comboBox_6.setItemText(1, QCoreApplication.translate("AdvanceSettings", u"A2", None))
        self.comboBox_6.setItemText(2, QCoreApplication.translate("AdvanceSettings", u"Cz", None))
        self.comboBox_6.setItemText(3, QCoreApplication.translate("AdvanceSettings", u"Ceja izquierda", None))
        self.comboBox_6.setItemText(4, QCoreApplication.translate("AdvanceSettings", u"No Conectado", None))

        self.label_8.setText(QCoreApplication.translate("AdvanceSettings", u"Electrodo Tierra", None))
        self.comboBox_7.setItemText(0, QCoreApplication.translate("AdvanceSettings", u"A1", None))
        self.comboBox_7.setItemText(1, QCoreApplication.translate("AdvanceSettings", u"A2", None))
        self.comboBox_7.setItemText(2, QCoreApplication.translate("AdvanceSettings", u"Cz", None))
        self.comboBox_7.setItemText(3, QCoreApplication.translate("AdvanceSettings", u"Ceja izquierda", None))
        self.comboBox_7.setItemText(4, QCoreApplication.translate("AdvanceSettings", u"No Conectado", None))

    # retranslateUi

