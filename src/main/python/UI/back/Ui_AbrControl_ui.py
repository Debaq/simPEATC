# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_AbrControl.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QLabel,
    QSizePolicy, QSpinBox, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 257)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lbl_mkg = QLabel(Form)
        self.lbl_mkg.setObjectName(u"lbl_mkg")

        self.gridLayout.addWidget(self.lbl_mkg, 3, 2, 1, 1)

        self.lbl_rate = QLabel(Form)
        self.lbl_rate.setObjectName(u"lbl_rate")

        self.gridLayout.addWidget(self.lbl_rate, 4, 0, 1, 1)

        self.lbl_pol = QLabel(Form)
        self.lbl_pol.setObjectName(u"lbl_pol")

        self.gridLayout.addWidget(self.lbl_pol, 2, 0, 1, 1)

        self.sb_intencity = QSpinBox(Form)
        self.sb_intencity.setObjectName(u"sb_intencity")

        self.gridLayout.addWidget(self.sb_intencity, 3, 1, 1, 1)

        self.cb_filter_down = QComboBox(Form)
        self.cb_filter_down.setObjectName(u"cb_filter_down")

        self.gridLayout.addWidget(self.cb_filter_down, 5, 1, 1, 1)

        self.lbl_stim = QLabel(Form)
        self.lbl_stim.setObjectName(u"lbl_stim")

        self.gridLayout.addWidget(self.lbl_stim, 0, 0, 1, 1)

        self.lbl_int = QLabel(Form)
        self.lbl_int.setObjectName(u"lbl_int")

        self.gridLayout.addWidget(self.lbl_int, 3, 0, 1, 1)

        self.sb_rate = QSpinBox(Form)
        self.sb_rate.setObjectName(u"sb_rate")

        self.gridLayout.addWidget(self.sb_rate, 4, 1, 1, 1)

        self.lbl_passdown = QLabel(Form)
        self.lbl_passdown.setObjectName(u"lbl_passdown")

        self.gridLayout.addWidget(self.lbl_passdown, 5, 0, 1, 1)

        self.sb_mskg = QSpinBox(Form)
        self.sb_mskg.setObjectName(u"sb_mskg")

        self.gridLayout.addWidget(self.sb_mskg, 3, 3, 1, 1)

        self.cb_pol = QComboBox(Form)
        self.cb_pol.setObjectName(u"cb_pol")

        self.gridLayout.addWidget(self.cb_pol, 2, 1, 1, 3)

        self.cb_stim = QComboBox(Form)
        self.cb_stim.setObjectName(u"cb_stim")

        self.gridLayout.addWidget(self.cb_stim, 0, 1, 1, 3)

        self.lbl_passhigh = QLabel(Form)
        self.lbl_passhigh.setObjectName(u"lbl_passhigh")

        self.gridLayout.addWidget(self.lbl_passhigh, 5, 2, 1, 1)

        self.cb_filter_up = QComboBox(Form)
        self.cb_filter_up.setObjectName(u"cb_filter_up")

        self.gridLayout.addWidget(self.cb_filter_up, 5, 3, 1, 1)

        self.label_8 = QLabel(Form)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 7, 0, 1, 1)

        self.sb_prom = QSpinBox(Form)
        self.sb_prom.setObjectName(u"sb_prom")

        self.gridLayout.addWidget(self.sb_prom, 7, 1, 1, 1)

        self.label_9 = QLabel(Form)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 7, 2, 1, 1)

        self.cb_side = QComboBox(Form)
        self.cb_side.setObjectName(u"cb_side")

        self.gridLayout.addWidget(self.cb_side, 7, 3, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.lbl_mkg.setText(QCoreApplication.translate("Form", u"Masking :", None))
        self.lbl_rate.setText(QCoreApplication.translate("Form", u"Tasa :", None))
        self.lbl_pol.setText(QCoreApplication.translate("Form", u"Polaridad :", None))
        self.lbl_stim.setText(QCoreApplication.translate("Form", u"Est\u00edmulo :", None))
        self.lbl_int.setText(QCoreApplication.translate("Form", u"Intensidad :", None))
        self.lbl_passdown.setText(QCoreApplication.translate("Form", u"Pasa Bajo :", None))
        self.lbl_passhigh.setText(QCoreApplication.translate("Form", u"Pasa Alto :", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"Promediaci\u00f3n :", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"Lado :", None))
    # retranslateUi

