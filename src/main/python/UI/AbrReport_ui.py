# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AbrReport.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QTextEdit, QVBoxLayout, QWidget)

class Ui_AbrReport(object):
    def setupUi(self, AbrReport):
        if not AbrReport.objectName():
            AbrReport.setObjectName(u"AbrReport")
        AbrReport.resize(951, 620)
        self.gridLayout = QGridLayout(AbrReport)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, -1, -1, 0)
        self.tabWidget = QTabWidget(AbrReport)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.South)
        self.tabWidget.setTabShape(QTabWidget.Triangular)
        self.tabWidget.setDocumentMode(True)
        self.tab_1 = QWidget()
        self.tab_1.setObjectName(u"tab_1")
        self.verticalLayout = QVBoxLayout(self.tab_1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.lbl_date = QLabel(self.tab_1)
        self.lbl_date.setObjectName(u"lbl_date")

        self.horizontalLayout.addWidget(self.lbl_date)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.label = QLabel(self.tab_1)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.label_2 = QLabel(self.tab_1)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_2)

        self.text_edit = QTextEdit(self.tab_1)
        self.text_edit.setObjectName(u"text_edit")

        self.verticalLayout.addWidget(self.text_edit)

        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_2 = QVBoxLayout(self.tab_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.layout_pdf = QVBoxLayout()
        self.layout_pdf.setObjectName(u"layout_pdf")

        self.verticalLayout_2.addLayout(self.layout_pdf)

        self.frame = QFrame(self.tab_3)
        self.frame.setObjectName(u"frame")
        self.frame.setMaximumSize(QSize(16777215, 30))
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.pushButton = QPushButton(self.frame)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_2.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.frame)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout_2.addWidget(self.pushButton_2)


        self.verticalLayout_2.addWidget(self.frame)

        self.tabWidget.addTab(self.tab_3, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)


        self.retranslateUi(AbrReport)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AbrReport)
    # setupUi

    def retranslateUi(self, AbrReport):
        AbrReport.setWindowTitle(QCoreApplication.translate("AbrReport", u"Form", None))
        self.lbl_date.setText(QCoreApplication.translate("AbrReport", u"TextLabel", None))
        self.label.setText(QCoreApplication.translate("AbrReport", u"POTENCIALES EVOCADOS AUDITIVOS DE TRONCO CEREBRAL", None))
        self.label_2.setText(QCoreApplication.translate("AbrReport", u"PEATC", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), QCoreApplication.translate("AbrReport", u"Conclusiones", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("AbrReport", u"Imagenes", None))
        self.pushButton.setText(QCoreApplication.translate("AbrReport", u"Imprimir", None))
        self.pushButton_2.setText(QCoreApplication.translate("AbrReport", u"Guardar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("AbrReport", u"Previsualizaci\u00f3n", None))
    # retranslateUi

