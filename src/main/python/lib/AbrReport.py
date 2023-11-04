import sys
from datetime import datetime

import fitz
from base import context
from PySide6.QtCore import QCoreApplication, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QWidget
from UI.AbrReport_ui import Ui_AbrReport
import lib.PdfCreator 

tr = QCoreApplication.translate

class AbrReport(QWidget, Ui_AbrReport):
    measure = Signal(str)
    def __init__(self) -> None:
        QWidget.__init__(self)
        self.setupUi(self)
        self.lbl_date.setText(self.date_current())
        self.pdf_view()


    def date_current(self):
        current_date = datetime.now().strftime("%d/%m/%Y")
        return current_date



    def pdf_view(self):
        pdf = context.get_resource('temp/GFG.pdf')
        self.pdf_widget = PDFViewer()
        self.pdf_widget.load_pdf(pdf)
        self.layout_pdf.addWidget(self.pdf_widget)


class PDFViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.scale_factor = 1.0
        self.doc = None
        self.current_page = 0
        self.verticalScrollBar().valueChanged.connect(self.check_scroll_borders)

    def load_pdf(self, pdf_path):
        # Abrir el documento PDF con PyMuPDF
        self.doc = fitz.open(pdf_path)
        self.show_page(self.current_page)

    def show_page(self, page_number):
        if self.doc is None or page_number < 0 or page_number >= len(self.doc):
            return  # Verificar límites de la página
        page = self.doc.load_page(page_number)
        pix = page.get_pixmap()
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        self.scene.clear()  # Limpiar la escena antes de mostrar una nueva página
        self.scene.addPixmap(pixmap)
        self.setSceneRect(pixmap.rect())
        self.current_page = page_number

    def check_scroll_borders(self, value):
        bar = self.verticalScrollBar()
        max_value = bar.maximum()
        if value == max_value and self.current_page < len(self.doc) - 1:
            # Moverse a la siguiente página
            self.show_page(self.current_page + 1)
        elif value == bar.minimum() and self.current_page > 0:
            # Moverse a la página anterior
            self.show_page(self.current_page - 1)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.show_page(self.current_page - 1)

        else:
            self.show_page(self.current_page + 1)

        #self.scale(self.scale_factor, self.scale_factor)