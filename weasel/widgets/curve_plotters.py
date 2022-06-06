__all__ = ['PlotCurve']

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from PyQt5.QtWidgets import QWidget, QVBoxLayout

class PlotCurve(QWidget):

    def __init__(self):
        super().__init__()

        self.figure = plt.figure()
        self.figure.set_visible(True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.xLabel = 't-axis'
        self.yLabel = 'signal'
       
        self.subPlot = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def clear(self):

        self.subPlot.clear()
        self.canvas.draw()

    def setData(self, x, y, index=None):

        self.subPlot.clear()
        self.subPlot.tick_params(
            axis='both', 
            which='major', 
            labelsize=4)
        self.subPlot.set_xlabel(
            self.xLabel, loc='center', 
            va='top', fontsize=4)
        self.subPlot.set_ylabel(
            self.yLabel, loc='center', 
            fontsize=4)
        self.subPlot.grid()
        self.subPlot.plot(x, y)
        if index is not None:
            self.subPlot.plot(x[index], y[index], 'bo')
        self.canvas.draw()
