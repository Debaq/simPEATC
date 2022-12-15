import pyqtgraph as pg
import numpy as np
from PySide6.QtWidgets import QWidget


class EEG(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        color_backgorund = pg.mkColor(255, 255, 255, 255)
        self.color_pen = pg.mkColor(0, 0, 0, 255)
        pg.setConfigOption('background', color_backgorund)
        pg.setConfigOption('foreground', self.color_pen)

        self.pw = pg.PlotWidget(name='Plot1', background='default')
        self.pw.setRange(yRange=(-2, 2), xRange=(0, 12),
                          disableAutoRange=True)
        self.pw.showGrid(x=True, y=True)
        self.pw.setMouseEnabled(x=False, y=False)
        self.pw.setMenuEnabled(False)
        ax = self.pw.getAxis('bottom')
        ay = self.pw.getAxis('left')
        ax.setStyle(showValues=False)
        self.x = 0
        self.y = 0
        self.marks = {'I': None, 'II':None, 'III':None, 'IV':None, 'V':None,
                      'Ip': None, 'IIp':None, 'IIIp':None, 'IVp':None, 'Vp':None}
        self.change_mark = False
