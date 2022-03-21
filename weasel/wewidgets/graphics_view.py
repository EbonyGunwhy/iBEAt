__all__ = ['GraphicsView']

import numpy as np
import math
import time

from matplotlib import cm
from PyQt5.QtCore import  pyqtSignal, QObject
from PyQt5.QtGui import QFont

import pyqtgraph as pg

class GraphicsView(QObject):

    sigLevelsChanged = pyqtSignal(float, float)
    sigMouseMoved = pyqtSignal(list)

    def __init__(self, image=None):
        super().__init__()

        self.coordinates = []

        font = QFont()
        font.setPixelSize(9)

        plotItem = pg.PlotItem()
        plotItem.hideButtons()
        plotItem.getAxis('left').tickFont = font
        plotItem.getAxis('bottom').tickFont = font

        self.imageView = pg.ImageView(view=plotItem) #view=pg.PlotItem() adds axes to image
        self.imageView.ui.roiBtn.hide()
        self.imageView.ui.menuBtn.hide()
        self.imageView.getView().scene().sigMouseMoved.connect(
            lambda pos: self._getPixelCoordinates(pos)
        )

        self.histogram = self.imageView.getHistogramWidget().item
        self.histogram.sigLevelsChanged.connect(self._setSigLevels)
        self.histogram.axis.setTickFont(font) 
        # self.histogram.vb.setFixedWidth(15) 

        self.setData(image)

    @property
    def widget(self):
        return self.imageView

    def setData(self, image):

        if image is not None: 
            if image.on_disk(): 
                image.read()
        self.image = image
        self.show()

    def _setSigLevels(self):
        """
        Update window center and width.
        """
        if self.image is None: return
        minLevel, maxLevel = self.imageView.getLevels()
        width = maxLevel - minLevel
        centre = minLevel + (width/2)
        self.image.WindowCenter = centre
        self.image.WindowWidth = width
        self.sigLevelsChanged.emit(centre, width)

    def _getPixelCoordinates(self, pos):
        """
        Emit a signal with coordinates of the pixel under the cursor.
        """
        if self.image is None: return
        self.coordinates = []
        container = self.imageView.getView()
        if container.sceneBoundingRect().contains(pos): 
            mousePoint = container.getViewBox().mapSceneToView(pos) 
            x_i = math.floor(mousePoint.x())
            y_i = math.floor(mousePoint.y()) 
            over_image = (0 <= y_i < self.image.Rows) and (0 <= x_i < self.image.Columns)
            if over_image: self.coordinates = [x_i, y_i]  
        self.sigMouseMoved.emit(self.coordinates) 


    def show(self):
        """Displays an image's pixel array in a pyqtGraph imageView widget 
        & sets its colour table, contrast and intensity levels. 
        Also, sets the contrast and intensity in the associated histogram.
        """
        if self.image is None:
            self.imageView.clear()
            return
        pixelArray = self.image.array()
        center, width = self.image.window()
        colormap, lut = self.image.get_colormap() 
        pgMap = colorMap(colormap, lut) 
#        print(center-width/2, center+width/2)
        self.imageView.setColorMap(pgMap)
        self.imageView.setImage(pixelArray, 
            autoHistogramRange = True, 
            levels = (center - width/2, center + width/2))
        self.imageView.show()

def colorMap(colormap, lut):
    """Converts a matplotlib colour map into
        a colour map that can be used by the pyqtGraph imageView widget.
    """
        
    if colormap == 'custom':
        colors = lut
    elif colormap == 'gray':
        colors = [[0.0, 0.0, 0.0, 1.0], [1.0, 1.0, 1.0, 1.0]]
    else:
        cmMap = cm.get_cmap(colormap)
        colourClassName = cmMap.__class__.__name__
        if colourClassName == 'ListedColormap':
            colors = cmMap.colors
        elif colourClassName == 'LinearSegmentedColormap':
            colors = cmMap(np.linspace(0, 1))
    
    positions = np.linspace(0, 1, len(colors))
    return pg.ColorMap(positions, colors)