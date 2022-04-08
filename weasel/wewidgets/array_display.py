__all__ = ['FourDimViewer']

import numpy as np

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
)
from .. import wewidgets as widgets

class FourDimViewer(QSplitter):
    """
    GUI for displaying a 4D numpy array

    status : weasel status object
    array : numpy array with dimensions (x,y,z,t)
    zcoords : numpy array with dimensions (z,t)
    tcoords : numpy array with dimensions (z,t)
    zlabel : str
    tlabel : str
    """

    def __init__(self, status=None, array=None, zcoords=None, tcoords=None, zlabel='z', tlabel='t'): 
        super().__init__()

        self.status = status
        self._defineWidgets()
        self._defineConnections()
        self._defineLayout()
        self._setViewTool()
        self.setData(array=array, zcoords=zcoords, tcoords=tcoords, zlabel=zlabel, tlabel=tlabel, fit=True)
        
    def _defineWidgets(self):

        self.viewToolBox = widgets.ArrayViewToolBox()
        self.view = widgets.ArrayView()
        self.viewSlider = widgets.IndexSlider()
        self.plot = widgets.PlotCurve()
        self.plotSlider = widgets.IndexSlider()

    def _defineConnections(self):

        self.viewToolBox.newTool.connect(self._setViewTool)
        self.view.mousePositionMoved.connect(self._mouseMoved)
        self.viewSlider.valueChanged.connect(self._refresh)
        self.plotSlider.valueChanged.connect(self._refresh)

    def _defineLayout(self):

        # Left panel for viewing images

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft  | Qt.AlignVCenter)
        layout.addWidget(self.viewToolBox)

        self.toolBar = QWidget() 
        self.toolBar.setStyleSheet("background-color: white")  
        self.toolBar.setLayout(layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toolBar)
        layout.addWidget(self.view) 
        layout.addWidget(self.viewSlider) 

        leftPanel = QWidget() 
        leftPanel.setLayout(layout)

        # Right Panel for viewing curve plots

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.plot) 
        layout.addWidget(self.plotSlider) 

        rightPanel = QWidget() 
        rightPanel.setLayout(layout)

        # Putting both panels together

        self.addWidget(leftPanel)
        self.addWidget(rightPanel)

    def setData(self, array=None, 
        zcoords=None, tcoords=None, 
        zlabel='z', tlabel='z', 
        fit = False):

        self.zcoords = zcoords
        self.tcoords = tcoords
        self.zlabel = zlabel
        self.tlabel = tlabel

        if array is not None: 
            self.array = array
            self.viewSlider.setMaximum(array.shape[2])
            self.plotSlider.setMaximum(array.shape[3])

        d = self.array.shape

        if self.zcoords is None: # create z-index array
            self.zcoords = np.empty((d[2],d[3]))
            for z in range(d[2]):
                for t in range(d[3]):
                    self.zcoords[z,t] = z

        if self.tcoords is None: # create t-index array
            self.tcoords = np.empty((d[2],d[3]))
            for z in range(d[2]):
                for t in range(d[3]):
                    self.tcoords[z,t] = t

        self._refresh(fit=fit)

    def _setStatus(self):

        tool = self.viewToolBox.getTool()
        x = tool.x
        y = tool.y
        z = self.viewSlider.value()
        t = self.plotSlider.value()
        if (not (0 <= x < self.array.shape[0]) or
            not (0 <= y < self.array.shape[1])):
            msg = self.zlabel + ' = ' + str(self.zcoords[z,t])
            msg += ', ' + self.tlabel + ' = ' + str(self.tcoords[z,t])
        else:
            v = self.array[x,y,z,t]
            msg = 'x = ' + str(x)
            msg += ', y = ' + str(y)
            msg += ', ' + self.zlabel + ' = ' + str(self.zcoords[z,t])
            msg += ', ' + self.tlabel + ' = ' + str(self.tcoords[z,t])
            msg += ', signal = ' + str(v)
        self.status.message(msg)

    def _setViewTool(self):

        tool = self.viewToolBox.getTool()
        self.view.setEventHandler(tool)

    def _mouseMoved(self):

        self._setStatus()
        tool = self.viewToolBox.getTool()
        x = tool.x
        y = tool.y
        if (not (0 <= x < self.array.shape[0]) or
            not (0 <= y < self.array.shape[1])):
            self.plot.clear()
        else:
            z = self.viewSlider.value()
            t = self.plotSlider.value()
            #self.plot.setData(self.tcoords[z,:], np.squeeze(self.array[x,y,z,:]), index=t)
            self.plot.setData(self.tcoords[z,:], self.array[x,y,z,:], index=t)
        
    def _refresh(self, fit=False):

        self._setStatus()
        tool = self.viewToolBox.getTool()
        x = tool.x
        y = tool.y
        z = self.viewSlider.value()
        t = self.plotSlider.value()
        self.view.setData(self.array[:,:,z,t], fit=fit)
        #self.view.setData(np.squeeze(self.array[:,:,z,t]))
        if (not (0 <= x < self.array.shape[0]) or
            not (0 <= y < self.array.shape[1])):
            self.plot.clear()
        else:
            #self.plot.setData(self.tcoords[z,:], np.squeeze(self.array[x,y,z,:]), index=t)
            self.plot.setData(self.tcoords[z,:], self.array[x,y,z,:], index=t)
