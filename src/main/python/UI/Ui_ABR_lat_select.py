# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ABR_lat_select.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_ABR_lat_select(object):
    def setupUi(self, ABR_lat_select):
        if not ABR_lat_select.objectName():
            ABR_lat_select.setObjectName(u"ABR_lat_select")
        ABR_lat_select.resize(422, 110)
        self.horizontalLayout = QHBoxLayout(ABR_lat_select)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox = QGroupBox(ABR_lat_select)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMaximumSize(QSize(120, 16777215))
        font = QFont()
        font.setPointSize(8)
        self.groupBox.setFont(font)
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, -1, -1, 0)
        self.btn_AB = QPushButton(self.groupBox)
        self.btn_AB.setObjectName(u"btn_AB")
        self.btn_AB.setFont(font)
        self.btn_AB.setCheckable(False)
        self.btn_AB.setChecked(False)

        self.horizontalLayout_4.addWidget(self.btn_AB)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_4.addWidget(self.label_3)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.btn_wave_I = QPushButton(self.groupBox)
        self.btn_wave_I.setObjectName(u"btn_wave_I")
        self.btn_wave_I.setMaximumSize(QSize(25, 22))
        font1 = QFont()
        font1.setPointSize(8)
        font1.setBold(False)
        self.btn_wave_I.setFont(font1)

        self.horizontalLayout_2.addWidget(self.btn_wave_I)

        self.btn_wave_II = QPushButton(self.groupBox)
        self.btn_wave_II.setObjectName(u"btn_wave_II")
        self.btn_wave_II.setMaximumSize(QSize(25, 22))
        self.btn_wave_II.setFont(font1)

        self.horizontalLayout_2.addWidget(self.btn_wave_II)

        self.btn_wave_III = QPushButton(self.groupBox)
        self.btn_wave_III.setObjectName(u"btn_wave_III")
        self.btn_wave_III.setMaximumSize(QSize(25, 22))
        self.btn_wave_III.setFont(font1)

        self.horizontalLayout_2.addWidget(self.btn_wave_III)

        self.btn_wave_IV = QPushButton(self.groupBox)
        self.btn_wave_IV.setObjectName(u"btn_wave_IV")
        self.btn_wave_IV.setMaximumSize(QSize(25, 22))
        self.btn_wave_IV.setFont(font1)

        self.horizontalLayout_2.addWidget(self.btn_wave_IV)

        self.btn_wave_V = QPushButton(self.groupBox)
        self.btn_wave_V.setObjectName(u"btn_wave_V")
        self.btn_wave_V.setMaximumSize(QSize(25, 22))
        self.btn_wave_V.setFont(font1)

        self.horizontalLayout_2.addWidget(self.btn_wave_V)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.btn_wave_Ip = QPushButton(self.groupBox)
        self.btn_wave_Ip.setObjectName(u"btn_wave_Ip")
        self.btn_wave_Ip.setMaximumSize(QSize(25, 22))
        self.btn_wave_Ip.setFont(font1)

        self.horizontalLayout_3.addWidget(self.btn_wave_Ip)

        self.btn_wave_IIp = QPushButton(self.groupBox)
        self.btn_wave_IIp.setObjectName(u"btn_wave_IIp")
        self.btn_wave_IIp.setMaximumSize(QSize(25, 22))
        self.btn_wave_IIp.setFont(font1)

        self.horizontalLayout_3.addWidget(self.btn_wave_IIp)

        self.btn_wave_IIIp = QPushButton(self.groupBox)
        self.btn_wave_IIIp.setObjectName(u"btn_wave_IIIp")
        self.btn_wave_IIIp.setMaximumSize(QSize(25, 22))
        self.btn_wave_IIIp.setFont(font1)

        self.horizontalLayout_3.addWidget(self.btn_wave_IIIp)

        self.btn_wave_IVp = QPushButton(self.groupBox)
        self.btn_wave_IVp.setObjectName(u"btn_wave_IVp")
        self.btn_wave_IVp.setMaximumSize(QSize(25, 22))
        self.btn_wave_IVp.setFont(font1)

        self.horizontalLayout_3.addWidget(self.btn_wave_IVp)

        self.btn_wave_Vp = QPushButton(self.groupBox)
        self.btn_wave_Vp.setObjectName(u"btn_wave_Vp")
        self.btn_wave_Vp.setMaximumSize(QSize(25, 22))
        self.btn_wave_Vp.setFont(font1)

        self.horizontalLayout_3.addWidget(self.btn_wave_Vp)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.horizontalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(ABR_lat_select)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setFont(font)
        self.gridLayout = QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(1)
        self.gridLayout.setContentsMargins(1, 1, 1, 1)
        self.lbl_3 = QLabel(self.groupBox_2)
        self.lbl_3.setObjectName(u"lbl_3")

        self.gridLayout.addWidget(self.lbl_3, 0, 2, 1, 1)

        self.lbl_4 = QLabel(self.groupBox_2)
        self.lbl_4.setObjectName(u"lbl_4")

        self.gridLayout.addWidget(self.lbl_4, 2, 0, 1, 1)

        self.lbl_6 = QLabel(self.groupBox_2)
        self.lbl_6.setObjectName(u"lbl_6")

        self.gridLayout.addWidget(self.lbl_6, 2, 2, 1, 1)

        self.lbl_8 = QLabel(self.groupBox_2)
        self.lbl_8.setObjectName(u"lbl_8")

        self.gridLayout.addWidget(self.lbl_8, 3, 1, 1, 1)

        self.lbl_2 = QLabel(self.groupBox_2)
        self.lbl_2.setObjectName(u"lbl_2")

        self.gridLayout.addWidget(self.lbl_2, 0, 1, 1, 1)

        self.lbl_7 = QLabel(self.groupBox_2)
        self.lbl_7.setObjectName(u"lbl_7")

        self.gridLayout.addWidget(self.lbl_7, 3, 0, 1, 1)

        self.lbl_1 = QLabel(self.groupBox_2)
        self.lbl_1.setObjectName(u"lbl_1")

        self.gridLayout.addWidget(self.lbl_1, 0, 0, 1, 1)

        self.lbl_5 = QLabel(self.groupBox_2)
        self.lbl_5.setObjectName(u"lbl_5")

        self.gridLayout.addWidget(self.lbl_5, 2, 1, 1, 1)

        self.lbl_9 = QLabel(self.groupBox_2)
        self.lbl_9.setObjectName(u"lbl_9")

        self.gridLayout.addWidget(self.lbl_9, 4, 0, 1, 1)

        self.lbl_10 = QLabel(self.groupBox_2)
        self.lbl_10.setObjectName(u"lbl_10")

        self.gridLayout.addWidget(self.lbl_10, 4, 1, 1, 1)

        self.lbl_11 = QLabel(self.groupBox_2)
        self.lbl_11.setObjectName(u"lbl_11")

        self.gridLayout.addWidget(self.lbl_11, 4, 2, 1, 1)


        self.horizontalLayout.addWidget(self.groupBox_2)


        self.retranslateUi(ABR_lat_select)

        QMetaObject.connectSlotsByName(ABR_lat_select)
    # setupUi

    def retranslateUi(self, ABR_lat_select):
        ABR_lat_select.setWindowTitle(QCoreApplication.translate("ABR_lat_select", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("ABR_lat_select", u"Marcar Latencias", None))
        self.btn_AB.setText(QCoreApplication.translate("ABR_lat_select", u"|A", None))
        self.label_3.setText("")
        self.btn_wave_I.setText(QCoreApplication.translate("ABR_lat_select", u"I", None))
        self.btn_wave_II.setText(QCoreApplication.translate("ABR_lat_select", u"II", None))
        self.btn_wave_III.setText(QCoreApplication.translate("ABR_lat_select", u"III", None))
        self.btn_wave_IV.setText(QCoreApplication.translate("ABR_lat_select", u"IV", None))
        self.btn_wave_V.setText(QCoreApplication.translate("ABR_lat_select", u"V", None))
        self.btn_wave_Ip.setText(QCoreApplication.translate("ABR_lat_select", u"I'", None))
        self.btn_wave_IIp.setText(QCoreApplication.translate("ABR_lat_select", u"II'", None))
        self.btn_wave_IIIp.setText(QCoreApplication.translate("ABR_lat_select", u"III'", None))
        self.btn_wave_IVp.setText(QCoreApplication.translate("ABR_lat_select", u"IV'", None))
        self.btn_wave_Vp.setText(QCoreApplication.translate("ABR_lat_select", u"V'", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("ABR_lat_select", u"Medidas", None))
        self.lbl_3.setText(QCoreApplication.translate("ABR_lat_select", u"A<>B:", None))
        self.lbl_4.setText(QCoreApplication.translate("ABR_lat_select", u"I: I': ", None))
        self.lbl_6.setText(QCoreApplication.translate("ABR_lat_select", u"III: III':", None))
        self.lbl_8.setText(QCoreApplication.translate("ABR_lat_select", u"V: V':", None))
        self.lbl_2.setText(QCoreApplication.translate("ABR_lat_select", u"A-B:", None))
        self.lbl_7.setText(QCoreApplication.translate("ABR_lat_select", u"IV: IV':", None))
        self.lbl_1.setText(QCoreApplication.translate("ABR_lat_select", u"A: B:", None))
        self.lbl_5.setText(QCoreApplication.translate("ABR_lat_select", u"II: II':", None))
        self.lbl_9.setText(QCoreApplication.translate("ABR_lat_select", u"I-III:", None))
        self.lbl_10.setText(QCoreApplication.translate("ABR_lat_select", u"III-V:", None))
        self.lbl_11.setText(QCoreApplication.translate("ABR_lat_select", u"I-V:", None))
    # retranslateUi

