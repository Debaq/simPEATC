# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AbrConfig.ui'
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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QDoubleSpinBox, QGridLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QWidget)

class Ui_Abr_Config(object):
    def setupUi(self, Abr_Config):
        if not Abr_Config.objectName():
            Abr_Config.setObjectName(u"Abr_Config")
        Abr_Config.resize(198, 418)
        self.gridLayout = QGridLayout(Abr_Config)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(3)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.lbl_int = QLabel(Abr_Config)
        self.lbl_int.setObjectName(u"lbl_int")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_int.sizePolicy().hasHeightForWidth())
        self.lbl_int.setSizePolicy(sizePolicy)
        self.lbl_int.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbl_int, 2, 0, 1, 1)

        self.cb_side = QComboBox(Abr_Config)
        self.cb_side.addItem("")
        self.cb_side.addItem("")
        self.cb_side.setObjectName(u"cb_side")

        self.gridLayout.addWidget(self.cb_side, 11, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 14, 1, 1, 1)

        self.lbl_pol = QLabel(Abr_Config)
        self.lbl_pol.setObjectName(u"lbl_pol")
        sizePolicy.setHeightForWidth(self.lbl_pol.sizePolicy().hasHeightForWidth())
        self.lbl_pol.setSizePolicy(sizePolicy)
        self.lbl_pol.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbl_pol, 1, 0, 1, 1)

        self.lbl_stim = QLabel(Abr_Config)
        self.lbl_stim.setObjectName(u"lbl_stim")
        sizePolicy.setHeightForWidth(self.lbl_stim.sizePolicy().hasHeightForWidth())
        self.lbl_stim.setSizePolicy(sizePolicy)
        self.lbl_stim.setLayoutDirection(Qt.LeftToRight)
        self.lbl_stim.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbl_stim, 0, 0, 1, 1)

        self.cb_filter_down = QComboBox(Abr_Config)
        self.cb_filter_down.addItem("")
        self.cb_filter_down.addItem("")
        self.cb_filter_down.addItem("")
        self.cb_filter_down.addItem("")
        self.cb_filter_down.addItem("")
        self.cb_filter_down.addItem("")
        self.cb_filter_down.addItem("")
        self.cb_filter_down.addItem("")
        self.cb_filter_down.setObjectName(u"cb_filter_down")

        self.gridLayout.addWidget(self.cb_filter_down, 6, 1, 1, 1)

        self.lbl_passhigh = QLabel(Abr_Config)
        self.lbl_passhigh.setObjectName(u"lbl_passhigh")
        sizePolicy.setHeightForWidth(self.lbl_passhigh.sizePolicy().hasHeightForWidth())
        self.lbl_passhigh.setSizePolicy(sizePolicy)
        self.lbl_passhigh.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbl_passhigh, 7, 0, 1, 1)

        self.sb_intencity = QSpinBox(Abr_Config)
        self.sb_intencity.setObjectName(u"sb_intencity")
        self.sb_intencity.setMaximum(120)
        self.sb_intencity.setSingleStep(5)
        self.sb_intencity.setValue(70)

        self.gridLayout.addWidget(self.sb_intencity, 2, 1, 1, 1)

        self.cb_filter_up = QComboBox(Abr_Config)
        self.cb_filter_up.addItem("")
        self.cb_filter_up.addItem("")
        self.cb_filter_up.addItem("")
        self.cb_filter_up.addItem("")
        self.cb_filter_up.addItem("")
        self.cb_filter_up.addItem("")
        self.cb_filter_up.addItem("")
        self.cb_filter_up.addItem("")
        self.cb_filter_up.setObjectName(u"cb_filter_up")

        self.gridLayout.addWidget(self.cb_filter_up, 7, 1, 1, 1)

        self.cb_stim = QComboBox(Abr_Config)
        self.cb_stim.addItem("")
        self.cb_stim.addItem("")
        self.cb_stim.addItem("")
        self.cb_stim.addItem("")
        self.cb_stim.addItem("")
        self.cb_stim.addItem("")
        self.cb_stim.addItem("")
        self.cb_stim.setObjectName(u"cb_stim")

        self.gridLayout.addWidget(self.cb_stim, 0, 1, 1, 1)

        self.label_9 = QLabel(Abr_Config)
        self.label_9.setObjectName(u"label_9")
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_9, 11, 0, 1, 1)

        self.btn_stop = QPushButton(Abr_Config)
        self.btn_stop.setObjectName(u"btn_stop")

        self.gridLayout.addWidget(self.btn_stop, 13, 0, 1, 2)

        self.lbl_passdown = QLabel(Abr_Config)
        self.lbl_passdown.setObjectName(u"lbl_passdown")
        sizePolicy.setHeightForWidth(self.lbl_passdown.sizePolicy().hasHeightForWidth())
        self.lbl_passdown.setSizePolicy(sizePolicy)
        self.lbl_passdown.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbl_passdown, 6, 0, 1, 1)

        self.label_8 = QLabel(Abr_Config)
        self.label_8.setObjectName(u"label_8")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy1)
        self.label_8.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_8, 10, 0, 1, 1)

        self.sb_mskg = QSpinBox(Abr_Config)
        self.sb_mskg.setObjectName(u"sb_mskg")
        self.sb_mskg.setMaximum(100)
        self.sb_mskg.setSingleStep(5)

        self.gridLayout.addWidget(self.sb_mskg, 3, 1, 1, 1)

        self.ch_atten = QCheckBox(Abr_Config)
        self.ch_atten.setObjectName(u"ch_atten")

        self.gridLayout.addWidget(self.ch_atten, 4, 1, 1, 1)

        self.lbl_mkg = QLabel(Abr_Config)
        self.lbl_mkg.setObjectName(u"lbl_mkg")
        sizePolicy.setHeightForWidth(self.lbl_mkg.sizePolicy().hasHeightForWidth())
        self.lbl_mkg.setSizePolicy(sizePolicy)
        self.lbl_mkg.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbl_mkg, 3, 0, 1, 1)

        self.lbl_rate = QLabel(Abr_Config)
        self.lbl_rate.setObjectName(u"lbl_rate")
        sizePolicy.setHeightForWidth(self.lbl_rate.sizePolicy().hasHeightForWidth())
        self.lbl_rate.setSizePolicy(sizePolicy)
        self.lbl_rate.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbl_rate, 5, 0, 1, 1)

        self.btn_start = QPushButton(Abr_Config)
        self.btn_start.setObjectName(u"btn_start")

        self.gridLayout.addWidget(self.btn_start, 12, 0, 1, 2)

        self.sb_prom = QSpinBox(Abr_Config)
        self.sb_prom.setObjectName(u"sb_prom")
        self.sb_prom.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.sb_prom.setAccelerated(True)
        self.sb_prom.setMaximum(8000)
        self.sb_prom.setSingleStep(10)

        self.gridLayout.addWidget(self.sb_prom, 10, 1, 1, 1)

        self.sb_rate = QDoubleSpinBox(Abr_Config)
        self.sb_rate.setObjectName(u"sb_rate")
        self.sb_rate.setDecimals(1)

        self.gridLayout.addWidget(self.sb_rate, 5, 1, 1, 1)

        self.cb_pol = QComboBox(Abr_Config)
        self.cb_pol.addItem("")
        self.cb_pol.addItem("")
        self.cb_pol.addItem("")
        self.cb_pol.setObjectName(u"cb_pol")

        self.gridLayout.addWidget(self.cb_pol, 1, 1, 1, 1)


        self.retranslateUi(Abr_Config)

        QMetaObject.connectSlotsByName(Abr_Config)
    # setupUi

    def retranslateUi(self, Abr_Config):
        Abr_Config.setWindowTitle(QCoreApplication.translate("Abr_Config", u"Form", None))
        self.lbl_int.setText(QCoreApplication.translate("Abr_Config", u"Intensidad :", None))
        self.cb_side.setItemText(0, QCoreApplication.translate("Abr_Config", u"OD", None))
        self.cb_side.setItemText(1, QCoreApplication.translate("Abr_Config", u"OI", None))

#if QT_CONFIG(statustip)
        self.cb_side.setStatusTip(QCoreApplication.translate("Abr_Config", u"Lado de estimulaci\u00f3n", None))
#endif // QT_CONFIG(statustip)
        self.lbl_pol.setText(QCoreApplication.translate("Abr_Config", u"Polaridad : ", None))
        self.lbl_stim.setText(QCoreApplication.translate("Abr_Config", u"Est\u00edmulo : ", None))
        self.cb_filter_down.setItemText(0, QCoreApplication.translate("Abr_Config", u"1000", None))
        self.cb_filter_down.setItemText(1, QCoreApplication.translate("Abr_Config", u"1500", None))
        self.cb_filter_down.setItemText(2, QCoreApplication.translate("Abr_Config", u"2000", None))
        self.cb_filter_down.setItemText(3, QCoreApplication.translate("Abr_Config", u"2500", None))
        self.cb_filter_down.setItemText(4, QCoreApplication.translate("Abr_Config", u"3000", None))
        self.cb_filter_down.setItemText(5, QCoreApplication.translate("Abr_Config", u"3500", None))
        self.cb_filter_down.setItemText(6, QCoreApplication.translate("Abr_Config", u"4000", None))
        self.cb_filter_down.setItemText(7, QCoreApplication.translate("Abr_Config", u"4500", None))

#if QT_CONFIG(statustip)
        self.cb_filter_down.setStatusTip(QCoreApplication.translate("Abr_Config", u"Filtro pasa bajo", None))
#endif // QT_CONFIG(statustip)
        self.lbl_passhigh.setText(QCoreApplication.translate("Abr_Config", u"Pasa Alto : ", None))
#if QT_CONFIG(statustip)
        self.sb_intencity.setStatusTip(QCoreApplication.translate("Abr_Config", u"Intensidad del est\u00edmulo", None))
#endif // QT_CONFIG(statustip)
        self.cb_filter_up.setItemText(0, QCoreApplication.translate("Abr_Config", u"3.3", None))
        self.cb_filter_up.setItemText(1, QCoreApplication.translate("Abr_Config", u"10", None))
        self.cb_filter_up.setItemText(2, QCoreApplication.translate("Abr_Config", u"33", None))
        self.cb_filter_up.setItemText(3, QCoreApplication.translate("Abr_Config", u"50", None))
        self.cb_filter_up.setItemText(4, QCoreApplication.translate("Abr_Config", u"100", None))
        self.cb_filter_up.setItemText(5, QCoreApplication.translate("Abr_Config", u"150", None))
        self.cb_filter_up.setItemText(6, QCoreApplication.translate("Abr_Config", u"200", None))
        self.cb_filter_up.setItemText(7, QCoreApplication.translate("Abr_Config", u"250", None))

#if QT_CONFIG(statustip)
        self.cb_filter_up.setStatusTip(QCoreApplication.translate("Abr_Config", u"Filtro pasa alto", None))
#endif // QT_CONFIG(statustip)
        self.cb_stim.setItemText(0, QCoreApplication.translate("Abr_Config", u"Click", None))
        self.cb_stim.setItemText(1, QCoreApplication.translate("Abr_Config", u"Ls-chirp", None))
        self.cb_stim.setItemText(2, QCoreApplication.translate("Abr_Config", u"Chirp", None))
        self.cb_stim.setItemText(3, QCoreApplication.translate("Abr_Config", u"Burst 500Hz", None))
        self.cb_stim.setItemText(4, QCoreApplication.translate("Abr_Config", u"Burst 1kHz", None))
        self.cb_stim.setItemText(5, QCoreApplication.translate("Abr_Config", u"Burst 2kHz", None))
        self.cb_stim.setItemText(6, QCoreApplication.translate("Abr_Config", u"Burst 4kHz", None))

#if QT_CONFIG(statustip)
        self.cb_stim.setStatusTip(QCoreApplication.translate("Abr_Config", u"Tipo de est\u00edmulo", None))
#endif // QT_CONFIG(statustip)
        self.label_9.setText(QCoreApplication.translate("Abr_Config", u"Lado : ", None))
#if QT_CONFIG(statustip)
        self.btn_stop.setStatusTip(QCoreApplication.translate("Abr_Config", u"Detener Prueba", None))
#endif // QT_CONFIG(statustip)
        self.btn_stop.setText(QCoreApplication.translate("Abr_Config", u"Detener", None))
        self.lbl_passdown.setText(QCoreApplication.translate("Abr_Config", u"Pasa Bajo : ", None))
        self.label_8.setText(QCoreApplication.translate("Abr_Config", u"Promediaci\u00f3n : ", None))
#if QT_CONFIG(statustip)
        self.sb_mskg.setStatusTip(QCoreApplication.translate("Abr_Config", u"Intensidad del enmascaramiento", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(statustip)
        self.ch_atten.setStatusTip(QCoreApplication.translate("Abr_Config", u"Activar atenuador de intensidad en el inicio", None))
#endif // QT_CONFIG(statustip)
        self.ch_atten.setText(QCoreApplication.translate("Abr_Config", u"Atenuador", None))
        self.lbl_mkg.setText(QCoreApplication.translate("Abr_Config", u"Masking : ", None))
        self.lbl_rate.setText(QCoreApplication.translate("Abr_Config", u"Tasa : ", None))
#if QT_CONFIG(statustip)
        self.btn_start.setStatusTip(QCoreApplication.translate("Abr_Config", u"Iniciar Prueba", None))
#endif // QT_CONFIG(statustip)
        self.btn_start.setText(QCoreApplication.translate("Abr_Config", u"Iniciar", None))
#if QT_CONFIG(statustip)
        self.sb_prom.setStatusTip(QCoreApplication.translate("Abr_Config", u"N\u00famero de promediaciones", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(statustip)
        self.sb_rate.setStatusTip(QCoreApplication.translate("Abr_Config", u"Tasa de estimulaci\u00f3n", None))
#endif // QT_CONFIG(statustip)
        self.cb_pol.setItemText(0, QCoreApplication.translate("Abr_Config", u"Alternada", None))
        self.cb_pol.setItemText(1, QCoreApplication.translate("Abr_Config", u"Condensaci\u00f3n", None))
        self.cb_pol.setItemText(2, QCoreApplication.translate("Abr_Config", u"Rarefacci\u00f3n", None))

#if QT_CONFIG(statustip)
        self.cb_pol.setStatusTip(QCoreApplication.translate("Abr_Config", u"Polaridad del est\u00edmulo", None))
#endif // QT_CONFIG(statustip)
    # retranslateUi

