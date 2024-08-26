import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, 
                               QGraphicsView, QGraphicsScene, QTextEdit, QGraphicsProxyWidget, 
                               QLabel, QFrame, QHBoxLayout, QGraphicsRectItem, QScrollBar)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QCursor, QBrush, QColor, QPainter, QPen

class MovableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.title_bar = QLabel("Mover desde aquí")
        self.title_bar.setStyleSheet("background-color: lightgray;")
        self.text_edit = QTextEdit()

        self.layout.addWidget(self.title_bar)
        self.layout.addWidget(self.text_edit)

class GraphicsApp(QMainWindow):
    def __init__(self):
        super(GraphicsApp, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('QGraphicsView Widget Example')
        self.showMaximized()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.view = QGraphicsView(self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        # Ajustar el tamaño del QGraphicsView para que parezca una página
        self.view.setFixedSize(700, 1000)
        self.view.setSceneRect(QRectF(0, 0, 700, 3000))  # Aumentamos la altura para tener espacio adicional
        self.scene.addRect(QRectF(0, 0, 700, 3000), QPen(QColor(0, 0, 0)), QBrush(QColor(255, 255, 255)))

        self.add_btn = QPushButton("Agregar QTextEdit", self)
        self.add_btn.clicked.connect(self.addTextEdit)

        self.layout.addWidget(self.view, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.add_btn)
        self.show()

    def addTextEdit(self):
        widget = MovableWidget()
        proxy_widget = self.scene.addWidget(widget)
        
        # Establecer una restricción de movimiento
        last_item = self.scene.items()[-2] if len(self.scene.items()) > 1 else None
        if last_item and isinstance(last_item, QGraphicsProxyWidget):
            y_position = last_item.y() + last_item.boundingRect().height() + 10
        else:
            y_position = 0

        mouse_pos = self.view.mapFromGlobal(QCursor.pos())
        scene_pos = self.view.mapToScene(mouse_pos)
        proxy_widget.setPos(scene_pos.x(), y_position)

        # Establecer el flag para hacerlo movible
        proxy_widget.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemIsMovable)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GraphicsApp()
    sys.exit(app.exec())
