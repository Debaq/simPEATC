# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AbrTableInfo.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHeaderView, QLabel,
    QSizePolicy, QSpacerItem, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_TableData(object):
    def setupUi(self, TableData):
        if not TableData.objectName():
            TableData.setObjectName(u"TableData")
        TableData.resize(288, 422)
        self.verticalLayout = QVBoxLayout(TableData)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(TableData)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.tw_latamp = QTableWidget(TableData)
        if (self.tw_latamp.columnCount() < 2):
            self.tw_latamp.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tw_latamp.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tw_latamp.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        if (self.tw_latamp.rowCount() < 5):
            self.tw_latamp.setRowCount(5)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tw_latamp.setVerticalHeaderItem(0, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tw_latamp.setVerticalHeaderItem(1, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tw_latamp.setVerticalHeaderItem(2, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tw_latamp.setVerticalHeaderItem(3, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tw_latamp.setVerticalHeaderItem(4, __qtablewidgetitem6)
        self.tw_latamp.setObjectName(u"tw_latamp")
        self.tw_latamp.setMinimumSize(QSize(165, 0))
        self.tw_latamp.setMaximumSize(QSize(165, 150))
        font = QFont()
        font.setPointSize(8)
        self.tw_latamp.setFont(font)
        self.tw_latamp.setAutoScroll(False)
        self.tw_latamp.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tw_latamp.horizontalHeader().setMinimumSectionSize(55)
        self.tw_latamp.horizontalHeader().setDefaultSectionSize(55)
        self.tw_latamp.verticalHeader().setMinimumSectionSize(25)
        self.tw_latamp.verticalHeader().setDefaultSectionSize(25)

        self.verticalLayout.addWidget(self.tw_latamp)

        self.tw_inter = QTableWidget(TableData)
        if (self.tw_inter.columnCount() < 1):
            self.tw_inter.setColumnCount(1)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tw_inter.setHorizontalHeaderItem(0, __qtablewidgetitem7)
        if (self.tw_inter.rowCount() < 4):
            self.tw_inter.setRowCount(4)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tw_inter.setVerticalHeaderItem(0, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tw_inter.setVerticalHeaderItem(1, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tw_inter.setVerticalHeaderItem(2, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tw_inter.setVerticalHeaderItem(3, __qtablewidgetitem11)
        self.tw_inter.setObjectName(u"tw_inter")
        self.tw_inter.setMaximumSize(QSize(165, 130))
        self.tw_inter.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tw_inter.setGridStyle(Qt.SolidLine)
        self.tw_inter.horizontalHeader().setMinimumSectionSize(55)
        self.tw_inter.horizontalHeader().setDefaultSectionSize(55)
        self.tw_inter.verticalHeader().setMinimumSectionSize(25)
        self.tw_inter.verticalHeader().setDefaultSectionSize(25)

        self.verticalLayout.addWidget(self.tw_inter)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(TableData)

        QMetaObject.connectSlotsByName(TableData)
    # setupUi

    def retranslateUi(self, TableData):
        TableData.setWindowTitle(QCoreApplication.translate("TableData", u"Form", None))
        self.label.setText(QCoreApplication.translate("TableData", u"Side", None))
        ___qtablewidgetitem = self.tw_latamp.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("TableData", u"Latencia", None));
        ___qtablewidgetitem1 = self.tw_latamp.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("TableData", u"Amplitud", None));
        ___qtablewidgetitem2 = self.tw_latamp.verticalHeaderItem(0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("TableData", u"Onda I", None));
        ___qtablewidgetitem3 = self.tw_latamp.verticalHeaderItem(1)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("TableData", u"Onda II", None));
        ___qtablewidgetitem4 = self.tw_latamp.verticalHeaderItem(2)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("TableData", u"Onda III", None));
        ___qtablewidgetitem5 = self.tw_latamp.verticalHeaderItem(3)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("TableData", u"Onda IV", None));
        ___qtablewidgetitem6 = self.tw_latamp.verticalHeaderItem(4)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("TableData", u"Onda V", None));
        ___qtablewidgetitem7 = self.tw_inter.horizontalHeaderItem(0)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("TableData", u"Variables", None));
        ___qtablewidgetitem8 = self.tw_inter.verticalHeaderItem(0)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("TableData", u"Latencia I-V", None));
        ___qtablewidgetitem9 = self.tw_inter.verticalHeaderItem(1)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("TableData", u"Latencia III-V", None));
        ___qtablewidgetitem10 = self.tw_inter.verticalHeaderItem(2)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("TableData", u"Latencia I-III", None));
        ___qtablewidgetitem11 = self.tw_inter.verticalHeaderItem(3)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("TableData", u"Relaci\u00f3n V/I", None));
    # retranslateUi

