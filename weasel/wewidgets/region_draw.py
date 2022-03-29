__all__ = ['SeriesViewerROI']

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, 
                            QVBoxLayout, 
                            QHBoxLayout)

from .. import wewidgets as widgets

class SeriesViewerROI(QWidget):
    """
    GUI for drawing and editing Regions of Interest
    """

    dataWritten = pyqtSignal()

    def __init__(self, series): 
        super().__init__()

        #Faster access but loading times are prohibitive for large series
        #if series.on_disk(): 
        #    series.read()

        self._defineWidgets(series)
        self._defineLayout()
        self._defineConnections()
        self._setMaskViewTool()

    def _defineWidgets(self, series):

        self.imageSliders = widgets.ImageSliders(series)
        self.regionList = widgets.RegionList(series)

        image = self.imageSliders.getImage()
        mask = self.regionList.getMask(image)

        self.maskView = widgets.MaskView(image, mask)
        self.maskViewToolBox = widgets.MaskViewToolBox()
#        self.brightness = widgets.ImageBrightness(image)
#        self.contrast = widgets.ImageContrast(image)
        self.pixelValue = widgets.PixelValueLabel(image)
        
    def _defineLayout(self):

        toolBar = QHBoxLayout()
        toolBar.setContentsMargins(0, 0, 0, 0)
        toolBar.setSpacing(0)
        toolBar.setAlignment(Qt.AlignLeft  | Qt.AlignVCenter)
        toolBar.addWidget(self.maskViewToolBox)
        toolBar.addWidget(self.regionList)
#        toolBar.addWidget(self.brightness) 
#        toolBar.addWidget(self.contrast) 
        toolBar.addWidget(self.pixelValue)

        self.toolBar = QWidget() 
        self.toolBar.setStyleSheet("background-color: white")  
        self.toolBar.setLayout(toolBar)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toolBar)
        layout.addWidget(self.maskView) 
        layout.addWidget(self.imageSliders) 

        self.setLayout(layout)

    def _defineConnections(self):

        self.maskView.mousePositionMoved.connect(self._mouseMoved)
        self.maskView.newMask.connect(self._newMask)
        self.maskViewToolBox.newTool.connect(self._setMaskViewTool)
        self.regionList.currentRegionChanged.connect(self._currentRegionChanged)
        self.regionList.dataWritten.connect(self.dataWritten.emit)
        self.imageSliders.valueChanged.connect(self._currentImageChanged)
#        self.brightness.valueChanged.connect(self._imageHasChanged)
#        self.contrast.valueChanged.connect(self._imageHasChanged)

    def _setMaskViewTool(self):

        tool = self.maskViewToolBox.getTool()
        self.maskView.setEventHandler(tool)

    def _mouseMoved(self):

        tool = self.maskViewToolBox.getTool()
        self.pixelValue.setValue([tool.x, tool.y])
        
    def _currentImageChanged(self):

        image = self.imageSliders.getImage()
        mask = self.regionList.getMask(image)
        self.maskView.setData(image)
        self.maskView.setMask(mask)
        self.pixelValue.setData(image)

    def _currentRegionChanged(self):

        image = self.imageSliders.getImage()
        mask = self.regionList.getMask(image)
        self.maskView.setMask(mask)

    def _newMask(self):

        mask = self.maskView.getMask()
        region = self.regionList.getRegion()
        mask.move_to(region)