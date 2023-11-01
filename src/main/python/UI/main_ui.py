# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QDockWidget, QHBoxLayout, QMainWindow,
    QMenu, QMenuBar, QSizePolicy, QStatusBar,
    QTabWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1016, 600)
        MainWindow.setDocumentMode(True)
        MainWindow.setDockNestingEnabled(True)
        self.actionSalir = QAction(MainWindow)
        self.actionSalir.setObjectName(u"actionSalir")
        self.actionP_rametros_Avanzados = QAction(MainWindow)
        self.actionP_rametros_Avanzados.setObjectName(u"actionP_rametros_Avanzados")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(2, 0, 2, 0)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setMinimumSize(QSize(500, 0))
        self.tabWidget.setUsesScrollButtons(True)
        self.abr = QWidget()
        self.abr.setObjectName(u"abr")
        self.layout_abr = QHBoxLayout(self.abr)
        self.layout_abr.setObjectName(u"layout_abr")
        self.tabWidget.addTab(self.abr, "")
        self.lat = QWidget()
        self.lat.setObjectName(u"lat")
        self.layout_lat_int = QHBoxLayout(self.lat)
        self.layout_lat_int.setObjectName(u"layout_lat_int")
        self.tabWidget.addTab(self.lat, "")
        self.conc = QWidget()
        self.conc.setObjectName(u"conc")
        self.layout_report = QHBoxLayout(self.conc)
        self.layout_report.setSpacing(0)
        self.layout_report.setObjectName(u"layout_report")
        self.layout_report.setContentsMargins(-1, -1, -1, 0)
        self.tabWidget.addTab(self.conc, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1016, 22))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        MainWindow.setMenuBar(self.menubar)
        self.dock_parameter = QDockWidget(MainWindow)
        self.dock_parameter.setObjectName(u"dock_parameter")
        self.dock_parameter.setMinimumSize(QSize(180, 143))
        self.dock_parameter.setFloating(False)
        self.dock_parameter.setFeatures(QDockWidget.DockWidgetMovable)
        self.dock_parameter_contents = QWidget()
        self.dock_parameter_contents.setObjectName(u"dock_parameter_contents")
        self.layout_dock_parameter_content = QVBoxLayout(self.dock_parameter_contents)
        self.layout_dock_parameter_content.setObjectName(u"layout_dock_parameter_content")
        self.layout_dock_parameter_content.setContentsMargins(3, 3, 3, 3)
        self.dock_parameter.setWidget(self.dock_parameter_contents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dock_parameter)
        self.dock_values = QDockWidget(MainWindow)
        self.dock_values.setObjectName(u"dock_values")
        self.dock_values.setMaximumSize(QSize(180, 524287))
        self.dock_values.setFeatures(QDockWidget.DockWidgetMovable)
        self.dock_values_contents = QWidget()
        self.dock_values_contents.setObjectName(u"dock_values_contents")
        self.layout_dock_values_contents = QVBoxLayout(self.dock_values_contents)
        self.layout_dock_values_contents.setObjectName(u"layout_dock_values_contents")
        self.layout_dock_values_contents.setContentsMargins(3, 3, 3, 3)
        self.dock_values.setWidget(self.dock_values_contents)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dock_values)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dock_test = QDockWidget(MainWindow)
        self.dock_test.setObjectName(u"dock_test")
        self.dock_test.setMinimumSize(QSize(100, 100))
        self.dock_test.setMaximumSize(QSize(524287, 150))
        self.dock_test.setFeatures(QDockWidget.DockWidgetFloatable|QDockWidget.DockWidgetMovable)
        self.dock_test.setAllowedAreas(Qt.BottomDockWidgetArea|Qt.TopDockWidgetArea)
        self.dock_test_contents = QWidget()
        self.dock_test_contents.setObjectName(u"dock_test_contents")
        self.layout_dock_test_contents = QHBoxLayout(self.dock_test_contents)
        self.layout_dock_test_contents.setSpacing(0)
        self.layout_dock_test_contents.setObjectName(u"layout_dock_test_contents")
        self.layout_dock_test_contents.setContentsMargins(0, 0, 0, 0)
        self.dock_test.setWidget(self.dock_test_contents)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dock_test)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menuArchivo.addAction(self.actionP_rametros_Avanzados)
        self.menuArchivo.addSeparator()
        self.menuArchivo.addAction(self.actionSalir)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSalir.setText(QCoreApplication.translate("MainWindow", u"Salir", None))
        self.actionP_rametros_Avanzados.setText(QCoreApplication.translate("MainWindow", u"P\u00e1rametros Avanzados", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.abr), QCoreApplication.translate("MainWindow", u"Gr\u00e1ficos", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.lat), QCoreApplication.translate("MainWindow", u"Latencia/Intencidad", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.conc), QCoreApplication.translate("MainWindow", u"Conclusiones", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("MainWindow", u"Archivo", None))
#if QT_CONFIG(statustip)
        self.dock_parameter.setStatusTip(QCoreApplication.translate("MainWindow", u"Par\u00e1metros", None))
#endif // QT_CONFIG(statustip)
        self.dock_parameter.setWindowTitle(QCoreApplication.translate("MainWindow", u"Par\u00e1metros", None))
#if QT_CONFIG(statustip)
        self.dock_values.setStatusTip(QCoreApplication.translate("MainWindow", u"Valores de las curvas", None))
#endif // QT_CONFIG(statustip)
        self.dock_values.setWindowTitle(QCoreApplication.translate("MainWindow", u"Valores", None))
#if QT_CONFIG(statustip)
        self.dock_test.setStatusTip(QCoreApplication.translate("MainWindow", u"Prueba Actual", None))
#endif // QT_CONFIG(statustip)
        self.dock_test.setWindowTitle(QCoreApplication.translate("MainWindow", u"Prueba", None))
    # retranslateUi

