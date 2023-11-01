# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_Report.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_AbrReport(object):
    def setupUi(self, AbrReport):
        if not AbrReport.objectName():
            AbrReport.setObjectName(u"AbrReport")
        AbrReport.resize(830, 620)
        self.horizontalLayout = QHBoxLayout(AbrReport)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.verticalFrame = QFrame(AbrReport)
        self.verticalFrame.setObjectName(u"verticalFrame")
        self.verticalFrame.setMinimumSize(QSize(800, 0))
        self.verticalFrame.setMaximumSize(QSize(800, 16777215))
        self.verticalFrame.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.verticalFrame.setFrameShape(QFrame.StyledPanel)
        self.verticalFrame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.verticalFrame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 10, -1, -1)
        self.label_2 = QLabel(self.verticalFrame)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.label_3 = QLabel(self.verticalFrame)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.label_3)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.label = QLabel(self.verticalFrame)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label)

        self.label_4 = QLabel(self.verticalFrame)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)
        self.label_4.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_4)

        self.textEdit = QTextEdit(self.verticalFrame)
        self.textEdit.setObjectName(u"textEdit")

        self.verticalLayout_2.addWidget(self.textEdit)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout.addWidget(self.verticalFrame)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.retranslateUi(AbrReport)

        QMetaObject.connectSlotsByName(AbrReport)
    # setupUi

    def retranslateUi(self, AbrReport):
        AbrReport.setWindowTitle(QCoreApplication.translate("AbrReport", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("AbrReport", u"Logo", None))
        self.label_3.setText(QCoreApplication.translate("AbrReport", u"date", None))
        self.label.setText(QCoreApplication.translate("AbrReport", u"Potenciales Evocados de Tronco Cerebral", None))
        self.label_4.setText(QCoreApplication.translate("AbrReport", u"PEATC", None))
    # retranslateUi

