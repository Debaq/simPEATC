
import pyqtgraph as pg


class GraphLatInt(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        super(GraphLatInt, self).__init__(parent)

        self.configure_pyqtgraph()
        self.setup_ui_elements()
        self.filled_area()

    def configure_pyqtgraph(self):
        color_background = pg.mkColor(255, 255, 255, 255)
        self.color_pen = pg.mkColor(0, 0, 0, 255)
        self.setBackground(color_background)
    
    def setup_ui_elements(self):
        """Set up UI elements for the graph"""
        self.pw = self.addPlot(row=1,col=0)

        self.pw.setRange(yRange=(0, 12), xRange=(0, 100), disableAutoRange=True)
        self.pw.setLabels(left='ms', bottom='dBnHL')
        grid = pg.GridItem(textPen='white')
        self.pw.addItem(grid)
        grid.setTickSpacing(x=[10], y=[1.0])

        self.pw.setMouseEnabled(x=False, y=False)
        self.pw.setMenuEnabled(False)
        self.pw.hideButtons()
        ay = self.pw.getAxis('left')
        ay.setStyle(showValues=False)
    
    def filled_area(self):
        # Valores para crear el área sombreada
        x_vals = [35, 45, 55, 75, 75, 55, 45, 35]
        y_bottom_vals = [6.5, 6.0, 6.0, 5.9, 8.9, 9.2, 9.5, 10.5]
        y_top_vals = [10.5, 9.5, 9.2, 8.9, 5.9, 6.0, 6.0, 6.5]

        curve_top = self.pw.plot(x_vals, y_top_vals)
        curve_bottom = self.pw.plot(x_vals, y_bottom_vals)

        fill_between = pg.FillBetweenItem()
        fill_between.setCurves(curve_top, curve_bottom)
        fill_between.setBrush(pg.mkColor(100, 100, 250, 80))

        self.pw.addItem(fill_between)
        #self.pw.fillBetween(x_vals, y_bottom_vals, y_top_vals, brush=fill_color)

    
    def legend_(self):
        legend = pg.LegendItem((80,60), offset=(70,20))
        legend.setParentItem(self.pw.graphicsItem())
        legend.addItem(bg1, 'bar')
        legend.addItem(c1, 'curve1')
        legend.addItem(c2, 'curve2')
        legend.addItem(s1, 'scatter')

if __name__ == '__main__':

    import pyqtgraph.examples
    pyqtgraph.examples.run()