import pyqtgraph as pg
from PySide6.QtWidgets import QApplication

class FSP(pg.GraphicsLayoutWidget):
    def __init__(self, mean=1000):
        super().__init__()
        self.mean = mean
        self.setBackground('w')  # Fondo blanco
        self.pw1 = self.addPlot(row=0, col=0)

        # Segundo eje y (ViewBox)
        self.pw2 = pg.ViewBox()
        self.pw1.scene().addItem(self.pw2)
        self.pw1.getAxis('right').linkToView(self.pw2)
        self.pw2.setXLink(self.pw1)

        # Actualizar el ViewBox cuando cambie el tamaño
        self.pw1.getViewBox().sigResized.connect(self.update_views)

        # Configuraciones de grilla y rango
        self.pw1.showGrid(x=False, y=True)
        self.pw1.setYRange(0, 100)
        self.pw1.setXRange(0, self.mean)
        self.pw2.setYRange(0, 200)

        # Deshabilitar auto rango y habilitar menú contextual
        self.pw1.setMouseEnabled(x=False, y=False)
        self.pw1.setMenuEnabled(False)
        self.pw2.setMenuEnabled(False)

        self.pw1.disableAutoRange()
        self.pw2.disableAutoRange()

        # Estilo de ejes
        ax = self.pw1.getAxis('bottom')
        ay = self.pw1.getAxis('left')
        ax.setStyle(showValues=False)

        # Agregar título
        self.title()

    def update_views(self):
        self.pw2.setGeometry(self.pw1.getViewBox().sceneBoundingRect())
        self.pw2.disableAutoRange()
        self.pw1.disableAutoRange()


    def title(self):
        text = pg.TextItem(text='FSP')
        self.pw1.addItem(text)
        text.setPos(self.pw1.getViewBox().viewRange()[0][0], self.pw1.getViewBox().viewRange()[1][1])

    def set_mean(self, value):
        self.mean = value
        self.pw1.setXRange(0, self.mean)



