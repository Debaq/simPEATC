# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_AbrDetails.ui'
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
    QLabel, QSizePolicy, QSpacerItem, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_AbrDetails(object):
    def setupUi(self, AbrDetails):
        if not AbrDetails.objectName():
            AbrDetails.setObjectName(u"AbrDetails")
        AbrDetails.resize(924, 197)
        AbrDetails.setMinimumSize(QSize(0, 110))
        self.horizontalLayout = QHBoxLayout(AbrDetails)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(AbrDetails)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QSize(0, 100))
        self.tabWidget.setTabPosition(QTabWidget.South)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayout_2 = QHBoxLayout(self.tab)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(3, 3, 3, 3)
        self.layout_tab1_secction1 = QVBoxLayout()
        self.layout_tab1_secction1.setObjectName(u"layout_tab1_secction1")
        self.layout_tab1_secction1.setContentsMargins(0, -1, -1, -1)

        self.horizontalLayout_2.addLayout(self.layout_tab1_secction1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.layout_tab1_secction2 = QVBoxLayout()
        self.layout_tab1_secction2.setObjectName(u"layout_tab1_secction2")
        self.layout_tab1_secction2.setContentsMargins(0, -1, -1, -1)

        self.horizontalLayout_2.addLayout(self.layout_tab1_secction2)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.formFrame = QFrame(self.tab)
        self.formFrame.setObjectName(u"formFrame")
        self.formFrame.setMaximumSize(QSize(300, 80))
        self.gridLayout = QGridLayout(self.formFrame)
        self.gridLayout.setSpacing(1)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, -1, 15, -1)
        self.lbl_info_estim = QLabel(self.formFrame)
        self.lbl_info_estim.setObjectName(u"lbl_info_estim")

        self.gridLayout.addWidget(self.lbl_info_estim, 0, 1, 1, 1)

        self.label_5 = QLabel(self.formFrame)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)

        self.label_3 = QLabel(self.formFrame)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.label_2 = QLabel(self.formFrame)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.lbl_info_int = QLabel(self.formFrame)
        self.lbl_info_int.setObjectName(u"lbl_info_int")

        self.gridLayout.addWidget(self.lbl_info_int, 2, 1, 1, 1)

        self.lbl_info_mkg = QLabel(self.formFrame)
        self.lbl_info_mkg.setObjectName(u"lbl_info_mkg")

        self.gridLayout.addWidget(self.lbl_info_mkg, 3, 1, 1, 1)

        self.label_6 = QLabel(self.formFrame)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)

        self.lbl_info_pol = QLabel(self.formFrame)
        self.lbl_info_pol.setObjectName(u"lbl_info_pol")

        self.gridLayout.addWidget(self.lbl_info_pol, 1, 1, 1, 1)

        self.label_9 = QLabel(self.formFrame)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 0, 2, 1, 1)

        self.lbl_info_rate = QLabel(self.formFrame)
        self.lbl_info_rate.setObjectName(u"lbl_info_rate")

        self.gridLayout.addWidget(self.lbl_info_rate, 0, 3, 1, 1)

        self.label_11 = QLabel(self.formFrame)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout.addWidget(self.label_11, 1, 2, 1, 1)

        self.lbl_info_filter = QLabel(self.formFrame)
        self.lbl_info_filter.setObjectName(u"lbl_info_filter")

        self.gridLayout.addWidget(self.lbl_info_filter, 1, 3, 1, 1)

        self.label_13 = QLabel(self.formFrame)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout.addWidget(self.label_13, 2, 2, 1, 1)

        self.lbl_info_aver = QLabel(self.formFrame)
        self.lbl_info_aver.setObjectName(u"lbl_info_aver")

        self.gridLayout.addWidget(self.lbl_info_aver, 2, 3, 1, 1)

        self.label_15 = QLabel(self.formFrame)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout.addWidget(self.label_15, 3, 2, 1, 1)

        self.lbl_info_side = QLabel(self.formFrame)
        self.lbl_info_side.setObjectName(u"lbl_info_side")

        self.gridLayout.addWidget(self.lbl_info_side, 3, 3, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 4, 1, 1, 1)


        self.horizontalLayout_2.addWidget(self.formFrame)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")

        self.horizontalLayout.addWidget(self.tabWidget)


        self.retranslateUi(AbrDetails)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AbrDetails)
    # setupUi

    def retranslateUi(self, AbrDetails):
        AbrDetails.setWindowTitle(QCoreApplication.translate("AbrDetails", u"Form", None))
        self.lbl_info_estim.setText("")
        self.label_5.setText(QCoreApplication.translate("AbrDetails", u"Intensidad:", None))
        self.label_3.setText(QCoreApplication.translate("AbrDetails", u"Polaridad:", None))
        self.label_2.setText(QCoreApplication.translate("AbrDetails", u"Est\u00edmulo :", None))
        self.lbl_info_int.setText("")
        self.lbl_info_mkg.setText("")
        self.label_6.setText(QCoreApplication.translate("AbrDetails", u"Masking:", None))
        self.lbl_info_pol.setText("")
        self.label_9.setText(QCoreApplication.translate("AbrDetails", u"Tasa:", None))
        self.lbl_info_rate.setText("")
        self.label_11.setText(QCoreApplication.translate("AbrDetails", u"Filtros:", None))
        self.lbl_info_filter.setText("")
        self.label_13.setText(QCoreApplication.translate("AbrDetails", u"Promediaciones:", None))
        self.lbl_info_aver.setText("")
        self.label_15.setText(QCoreApplication.translate("AbrDetails", u"Lado :", None))
        self.lbl_info_side.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("AbrDetails", u"Curva Seleccionada", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("AbrDetails", u"Resumen de Curvas", None))
    # retranslateUi

