import sys
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (QApplication, QMainWindow, QDockWidget, QTextEdit, 
                               QWidget, QVBoxLayout, QSplitter)

app = QApplication(sys.argv)
window = QMainWindow()

# Crear un contenedor principal y un QSplitter
central_widget = QWidget()
layout = QVBoxLayout(central_widget)
splitter = QSplitter(Qt.Vertical)
layout.addWidget(splitter)

# Crear y configurar el dock lateral
left_dock = QDockWidget("Lateral Dock")
left_edit = QTextEdit()
left_dock.setWidget(left_edit)

# Crear y configurar el dock inferior
bottom_dock = QDockWidget("Bottom Dock")
bottom_edit = QTextEdit()
bottom_dock.setWidget(bottom_edit)

# Agregar widgets al QSplitter
splitter.addWidget(left_dock)
splitter.addWidget(bottom_edit)  # Nota: Agregamos el QTextEdit directamente, pero podría ser otro QDockWidget si se desea

window.setCentralWidget(central_widget)
window.show()
sys.exit(app.exec())
