# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AbrDetailAllCurves.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QSizePolicy, QTableWidget, QTableWidgetItem, QWidget)

class Ui_DetailAllCurves(object):
    def setupUi(self, DetailAllCurves):
        if not DetailAllCurves.objectName():
            DetailAllCurves.setObjectName(u"DetailAllCurves")
        DetailAllCurves.resize(677, 330)
        self.horizontalLayout = QHBoxLayout(DetailAllCurves)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.tw_curves_list = QTableWidget(DetailAllCurves)
        if (self.tw_curves_list.columnCount() < 16):
            self.tw_curves_list.setColumnCount(16)
        __qtablewidgetitem = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(8, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(9, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(10, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(11, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(12, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(13, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(14, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tw_curves_list.setHorizontalHeaderItem(15, __qtablewidgetitem15)
        self.tw_curves_list.setObjectName(u"tw_curves_list")
        self.tw_curves_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.horizontalLayout.addWidget(self.tw_curves_list)


        self.retranslateUi(DetailAllCurves)

        QMetaObject.connectSlotsByName(DetailAllCurves)
    # setupUi

    def retranslateUi(self, DetailAllCurves):
        DetailAllCurves.setWindowTitle(QCoreApplication.translate("DetailAllCurves", u"Form", None))
        ___qtablewidgetitem = self.tw_curves_list.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("DetailAllCurves", u"O\u00eddo", None));
        ___qtablewidgetitem1 = self.tw_curves_list.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("DetailAllCurves", u"Intensidad (MKg)", None));
        ___qtablewidgetitem2 = self.tw_curves_list.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("DetailAllCurves", u"Polaridad", None));
        ___qtablewidgetitem3 = self.tw_curves_list.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("DetailAllCurves", u"Est\u00edmulo", None));
        ___qtablewidgetitem4 = self.tw_curves_list.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("DetailAllCurves", u"Tasa", None));
        ___qtablewidgetitem5 = self.tw_curves_list.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("DetailAllCurves", u"Filtros", None));
        ___qtablewidgetitem6 = self.tw_curves_list.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("DetailAllCurves", u"Promediaciones", None));
        ___qtablewidgetitem7 = self.tw_curves_list.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("DetailAllCurves", u"I:lat(amp)", None));
        ___qtablewidgetitem8 = self.tw_curves_list.horizontalHeaderItem(8)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("DetailAllCurves", u"II:lat(amp)", None));
        ___qtablewidgetitem9 = self.tw_curves_list.horizontalHeaderItem(9)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("DetailAllCurves", u"III:lat(amp)", None));
        ___qtablewidgetitem10 = self.tw_curves_list.horizontalHeaderItem(10)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("DetailAllCurves", u"IV:lat(amp)", None));
        ___qtablewidgetitem11 = self.tw_curves_list.horizontalHeaderItem(11)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("DetailAllCurves", u"V:lat(amp)", None));
        ___qtablewidgetitem12 = self.tw_curves_list.horizontalHeaderItem(12)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("DetailAllCurves", u"Interpeak I-III", None));
        ___qtablewidgetitem13 = self.tw_curves_list.horizontalHeaderItem(13)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("DetailAllCurves", u"Interpeak III-V", None));
        ___qtablewidgetitem14 = self.tw_curves_list.horizontalHeaderItem(14)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("DetailAllCurves", u"Interpeak I-V", None));
        ___qtablewidgetitem15 = self.tw_curves_list.horizontalHeaderItem(15)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("DetailAllCurves", u"Relaci\u00f3n V/I", None));
    # retranslateUi

