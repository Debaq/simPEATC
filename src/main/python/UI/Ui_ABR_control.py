# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ABR_control.ui'
##
## Created by: Qt User Interface Compiler version 6.2.0
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_ABRSim(object):
    def setupUi(self, ABRSim):
        if not ABRSim.objectName():
            ABRSim.setObjectName(u"ABRSim")
        ABRSim.resize(1238, 493)
        self.horizontalLayout = QHBoxLayout(ABRSim)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.control = QFrame(ABRSim)
        self.control.setObjectName(u"control")
        self.control.setMinimumSize(QSize(170, 0))
        self.control.setMaximumSize(QSize(170, 16777215))
        font = QFont()
        font.setPointSize(8)
        self.control.setFont(font)
        self.layout_left = QVBoxLayout(self.control)
        self.layout_left.setObjectName(u"layout_left")

        self.horizontalLayout.addWidget(self.control)

        self.line = QFrame(ABRSim)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout.addWidget(self.line)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.layourt_ctrl_R = QHBoxLayout()
        self.layourt_ctrl_R.setSpacing(0)
        self.layourt_ctrl_R.setObjectName(u"layourt_ctrl_R")
        self.layourt_ctrl_R.setContentsMargins(4, 0, 4, -1)

        self.verticalLayout_2.addLayout(self.layourt_ctrl_R)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalFrame_2 = QFrame(ABRSim)
        self.verticalFrame_2.setObjectName(u"verticalFrame_2")
        self.verticalFrame_2.setMinimumSize(QSize(30, 0))
        self.verticalFrame_2.setMaximumSize(QSize(30, 16777215))
        font1 = QFont()
        font1.setPointSize(6)
        self.verticalFrame_2.setFont(font1)
        self.layout_ctrl_curve_R = QVBoxLayout(self.verticalFrame_2)
        self.layout_ctrl_curve_R.setSpacing(0)
        self.layout_ctrl_curve_R.setObjectName(u"layout_ctrl_curve_R")
        self.layout_ctrl_curve_R.setContentsMargins(1, 0, 1, 6)

        self.horizontalLayout_3.addWidget(self.verticalFrame_2)

        self.verticalFrame_3 = QFrame(ABRSim)
        self.verticalFrame_3.setObjectName(u"verticalFrame_3")
        self.layout_graph_R = QVBoxLayout(self.verticalFrame_3)
        self.layout_graph_R.setSpacing(0)
        self.layout_graph_R.setObjectName(u"layout_graph_R")
        self.layout_graph_R.setContentsMargins(0, 6, 6, 6)

        self.horizontalLayout_3.addWidget(self.verticalFrame_3)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.layourt_ctrl_L = QHBoxLayout()
        self.layourt_ctrl_L.setSpacing(0)
        self.layourt_ctrl_L.setObjectName(u"layourt_ctrl_L")
        self.layourt_ctrl_L.setContentsMargins(4, -1, 4, -1)

        self.verticalLayout_4.addLayout(self.layourt_ctrl_L)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalFrame_4 = QFrame(ABRSim)
        self.verticalFrame_4.setObjectName(u"verticalFrame_4")
        self.verticalFrame_4.setMinimumSize(QSize(30, 0))
        self.verticalFrame_4.setMaximumSize(QSize(30, 16777215))
        self.verticalFrame_4.setFont(font1)
        self.layout_ctrl_curve_L = QVBoxLayout(self.verticalFrame_4)
        self.layout_ctrl_curve_L.setSpacing(0)
        self.layout_ctrl_curve_L.setObjectName(u"layout_ctrl_curve_L")
        self.layout_ctrl_curve_L.setContentsMargins(1, 0, 1, 6)

        self.horizontalLayout_2.addWidget(self.verticalFrame_4)

        self.verticalFrame_5 = QFrame(ABRSim)
        self.verticalFrame_5.setObjectName(u"verticalFrame_5")
        self.layout_graph_L = QVBoxLayout(self.verticalFrame_5)
        self.layout_graph_L.setSpacing(0)
        self.layout_graph_L.setObjectName(u"layout_graph_L")
        self.layout_graph_L.setContentsMargins(0, 6, 6, 6)

        self.horizontalLayout_2.addWidget(self.verticalFrame_5)


        self.verticalLayout_4.addLayout(self.horizontalLayout_2)


        self.horizontalLayout.addLayout(self.verticalLayout_4)


        self.retranslateUi(ABRSim)

        QMetaObject.connectSlotsByName(ABRSim)
    # setupUi

    def retranslateUi(self, ABRSim):
        ABRSim.setWindowTitle(QCoreApplication.translate("ABRSim", u"ABRSim", None))
    # retranslateUi

