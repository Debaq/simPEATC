from pyqtgraph import GraphicsLayoutWidget
import pyqtgraph as pg
import numpy as np


class EEG(GraphicsLayoutWidget):
    def __init__(self):
        GraphicsLayoutWidget.__init__(self)
        color_background = pg.mkColor(255, 255, 255, 255)
        self.color_pen = pg.mkColor(0, 0, 0, 255)
        self.setBackground(color_background)
        self.pw = self.addPlot(row=0,col=0)
        self.pw.setRange(yRange=(-2, 2), xRange=(0, 12),
                          disableAutoRange=True)
        self.pw.showGrid(x=False, y=True)
        self.pw.setMouseEnabled(x=False, y=False)
        self.pw.setMenuEnabled(False)
        ax = self.pw.getAxis('bottom')
        ay = self.pw.getAxis('left')
        ax.setStyle(showValues=False)
        self.x = 0
        self.y = 0
        self.title()
        self.side_text()

    def title(self):
        text = pg.TextItem(text='EEG')
        text.setPos(10, 2)
        self.pw.addItem(text)

    def side_text(self):
        text_r = pg.TextItem(text='R', color='r')
        text_r.setPos(0,2)
        text_l = pg.TextItem(text='L', color='b')
        text_l.setPos(0,0)
        self.pw.addItem(text_l)
        self.pw.addItem(text_r)