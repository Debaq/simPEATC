from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QApplication, QScrollBar
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtCore import Qt
import sys
import fitz


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    pdf_path = "uach.pdf"  # Reemplaza con la ruta a tu archivo PDF
    viewer.load_pdf(pdf_path)
    viewer.show()
    sys.exit(app.exec())
