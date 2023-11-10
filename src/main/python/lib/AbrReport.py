import shutil
import sys
from datetime import datetime

import fitz
from base import context
from PySide6.QtCore import QCoreApplication, Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (QFileDialog, QGraphicsDropShadowEffect,
                               QGraphicsRectItem, QGraphicsScene,
                               QGraphicsView, QWidget)
from UI.AbrReport_ui import Ui_AbrReport

tr = QCoreApplication.translate

class AbrReport(QWidget, Ui_AbrReport):
    sig_update_pdf = Signal(bool)
    def __init__(self) -> None:
        QWidget.__init__(self)
        self.setupUi(self)
        self.lbl_date.setText(self.date_current())
        self.pdf_widget = PDFViewer()
        self.pdf_view()
        self.tabWidget.currentChanged.connect(self.change_tab)
        self.btn_update.clicked.connect(self.update_pdf)
        self.btn_print.clicked.connect(self.print_pdf)
        self.btn_save.clicked.connect(self.open_save_as_dialog)
        self.case = ""

    def change_tab(self, tab):
        self.sig_update_pdf.emit(True)
        self.update_pdf()

    def date_current(self):
        current_date = datetime.now().strftime("%d/%m/%Y")
        return current_date

    def pdf_view(self):
        self.update_pdf()
        self.layout_pdf.addWidget(self.pdf_widget)
    
    def update_pdf(self):
        self.file_pdf = context.get_resource('temp/GFG.pdf')
        self.pdf_widget.load_pdf(self.file_pdf)
    
    def print_pdf(self):
        printer = QPrinter(QPrinter.HighResolution)
        print_dialog = QPrintDialog(printer, self)

        # Mostrar el cuadro de diálogo de impresión
        if print_dialog.exec() == QPrintDialog.Accepted:
            # Aquí asumimos que el PDF que deseas imprimir es el actualmente cargado en pdf_widget
            self.perform_print(printer)

    def open_save_as_dialog(self):
        # Esta función abre el diálogo 'Guardar Como'
        options = QFileDialog.Options()
        # Establecer el nombre de archivo predeterminado y la extensión de archivo
        defaultFileName = f"caso_{self.case+1}_{self.le_eva.text()}.pdf"
        fileName, _ = QFileDialog.getSaveFileName(self,
                                                  "Guardar Como",
                                                  defaultFileName,
                                                  "PDF Files (*.pdf)",
                                                  options=options)
        if fileName:
            #print(f"El archivo se guardará como: {fileName}")
            self.save_file(fileName)
            # Aquí podrías agregar la lógica para guardar el archivo PDF

    def save_file(self, new_path):
        try:
            shutil.copy(self.file_pdf, new_path)
            #print(f"Archivo copiado con éxito de {origen} a {destino}")
        except IOError as e:
            print(f"No se pudo copiar el archivo. {e}")
        except Exception as e:
            print(f"Error: {e}")

    def perform_print(self, printer):
        try:
            # Obtener el PDF actualmente visualizado
            pdf_path = self.file_pdf
            # Abrir el documento PDF con PyMuPDF
            doc = fitz.open(pdf_path)

            # Iniciar el pintor para el dibujo en el QPrinter
            painter = QPainter()
            painter.begin(printer)  # Asegúrate de que esto se llama antes de dibujar

            for page_num in range(len(doc)):
                if page_num > 0:  # Agregar una nueva página si no es la primera
                    printer.newPage()

                # Cargar la página
                page = doc.load_page(page_num)

                # Ajusta el factor de zoom para la resolución deseada. Un valor mayor significa una imagen más nítida.
                zoom_factor = 2.0  # Ejemplo: Aumenta esto para mejorar la calidad de la imagen.
                mat = fitz.Matrix(zoom_factor, zoom_factor)
                pix = page.get_pixmap(matrix=mat)

                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)

                # Calcular el tamaño y la posición para dibujar la imagen
                page_rect = printer.pageRect(QPrinter.DevicePixel).toRect()  # Obtener un QRect con el tamaño del área de dibujo

                # Calcular el factor de escala para ajustar la imagen al área imprimible de la página
                scale_factor = min(page_rect.width() / img.width(), page_rect.height() / img.height())
                scaled_img = img.scaled(img.width() * scale_factor, img.height() * scale_factor, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # Calcular la posición para centrar la imagen
                x = (page_rect.width() - scaled_img.width()) / 2 + page_rect.left()
                y = (page_rect.height() - scaled_img.height()) / 2 + page_rect.top()

                # Dibujar la imagen centrada en el pintor
                painter.drawImage(x, y, scaled_img)

            # Finalizar la impresión
            painter.end()
        except Exception as e:
            print(f"Se produjo un error durante la impresión: {e}")

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

         # Crear un rectángulo con el tamaño de la imagen y un borde
        border_rect = QGraphicsRectItem(pixmap.rect())
        border_rect.setPen(QColor(0, 0, 0))  # Color del borde, negro en este caso
        border_rect.setBrush(Qt.transparent)  # Fondo transparente

        # Crear y configurar la sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 100))  # Sombra semitransparente
        shadow.setOffset(5, 5)
        border_rect.setGraphicsEffect(shadow)

        # Añadir el borde con la sombra a la escena
        self.scene.addItem(border_rect)

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