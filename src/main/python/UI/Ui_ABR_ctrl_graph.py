# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ABR_ctrl_graph.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_ABR_control_curve(object):
    def setupUi(self, ABR_control_curve):
        if not ABR_control_curve.objectName():
            ABR_control_curve.setObjectName(u"ABR_control_curve")
        ABR_control_curve.resize(296, 477)
        font = QFont()
        font.setPointSize(8)
        ABR_control_curve.setFont(font)
        self.verticalLayout_4 = QVBoxLayout(ABR_control_curve)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 10)
        self.label = QLabel(ABR_control_curve)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(40, 16777215))
        font1 = QFont()
        font1.setPointSize(8)
        font1.setBold(True)
        self.label.setFont(font1)

        self.verticalLayout_4.addWidget(self.label)

        self.line = QFrame(ABR_control_curve)
        self.line.setObjectName(u"line")
        self.line.setMaximumSize(QSize(25, 16777215))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_4.addWidget(self.line)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lbl_unit = QLabel(ABR_control_curve)
        self.lbl_unit.setObjectName(u"lbl_unit")
        self.lbl_unit.setMaximumSize(QSize(25, 16777215))
        font2 = QFont()
        font2.setPointSize(6)
        self.lbl_unit.setFont(font2)
        self.lbl_unit.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.lbl_unit)

        self.btn_scale_plus = QPushButton(ABR_control_curve)
        self.btn_scale_plus.setObjectName(u"btn_scale_plus")
        self.btn_scale_plus.setMaximumSize(QSize(25, 25))
        self.btn_scale_plus.setFont(font)

        self.verticalLayout.addWidget(self.btn_scale_plus)

        self.lbl_scale = QLabel(ABR_control_curve)
        self.lbl_scale.setObjectName(u"lbl_scale")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_scale.sizePolicy().hasHeightForWidth())
        self.lbl_scale.setSizePolicy(sizePolicy)
        self.lbl_scale.setMaximumSize(QSize(25, 16777215))
        self.lbl_scale.setFont(font2)
        self.lbl_scale.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.lbl_scale)

        self.btn_scale_minus = QPushButton(ABR_control_curve)
        self.btn_scale_minus.setObjectName(u"btn_scale_minus")
        self.btn_scale_minus.setMaximumSize(QSize(25, 25))
        self.btn_scale_minus.setFont(font)

        self.verticalLayout.addWidget(self.btn_scale_minus)


        self.verticalLayout_4.addLayout(self.verticalLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.frame_curves = QGroupBox(ABR_control_curve)
        self.frame_curves.setObjectName(u"frame_curves")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_curves.sizePolicy().hasHeightForWidth())
        self.frame_curves.setSizePolicy(sizePolicy1)
        self.frame_curves.setMinimumSize(QSize(25, 0))
        self.frame_curves.setMaximumSize(QSize(25, 16777215))
        self.frame_curves.setFont(font1)
        self.frame_curves.setStyleSheet(u"border-style: outset;\n"
"border-width: 0px;")
        self.frame_curves.setFlat(True)
        self.layout_curves = QVBoxLayout(self.frame_curves)
        self.layout_curves.setSpacing(2)
        self.layout_curves.setObjectName(u"layout_curves")
        self.layout_curves.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_4.addWidget(self.frame_curves)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.btn_contra = QPushButton(ABR_control_curve)
        self.btn_contra.setObjectName(u"btn_contra")
        self.btn_contra.setEnabled(False)
        self.btn_contra.setMaximumSize(QSize(25, 25))
        self.btn_contra.setFont(font)

        self.verticalLayout_2.addWidget(self.btn_contra)

        self.btn_up = QPushButton(ABR_control_curve)
        self.btn_up.setObjectName(u"btn_up")
        self.btn_up.setMaximumSize(QSize(25, 25))
        self.btn_up.setFont(font1)

        self.verticalLayout_2.addWidget(self.btn_up)

        self.btn_down = QPushButton(ABR_control_curve)
        self.btn_down.setObjectName(u"btn_down")
        self.btn_down.setMaximumSize(QSize(25, 25))
        self.btn_down.setFont(font1)

        self.verticalLayout_2.addWidget(self.btn_down)

        self.btn_del = QPushButton(ABR_control_curve)
        self.btn_del.setObjectName(u"btn_del")
        self.btn_del.setMaximumSize(QSize(25, 25))
        font3 = QFont()
        font3.setPointSize(7)
        self.btn_del.setFont(font3)

        self.verticalLayout_2.addWidget(self.btn_del)


        self.verticalLayout_4.addLayout(self.verticalLayout_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)


        self.retranslateUi(ABR_control_curve)

        QMetaObject.connectSlotsByName(ABR_control_curve)
    # setupUi

    def retranslateUi(self, ABR_control_curve):
        ABR_control_curve.setWindowTitle(QCoreApplication.translate("ABR_control_curve", u"Form", None))
        self.label.setText("")
        self.lbl_unit.setText(QCoreApplication.translate("ABR_control_curve", u" \u03bcV", None))
        self.btn_scale_plus.setText(QCoreApplication.translate("ABR_control_curve", u"+", None))
        self.lbl_scale.setText(QCoreApplication.translate("ABR_control_curve", u"0.25", None))
        self.btn_scale_minus.setText(QCoreApplication.translate("ABR_control_curve", u"-", None))
        self.frame_curves.setTitle("")
        self.btn_contra.setText(QCoreApplication.translate("ABR_control_curve", u"C/I", None))
        self.btn_up.setText(QCoreApplication.translate("ABR_control_curve", u"\u23f6", None))
        self.btn_down.setText(QCoreApplication.translate("ABR_control_curve", u"\u23f7", None))
        self.btn_del.setText(QCoreApplication.translate("ABR_control_curve", u"Del", None))
    # retranslateUi

