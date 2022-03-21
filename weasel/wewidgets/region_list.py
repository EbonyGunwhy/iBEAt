__all__ = ['RegionList']

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, 
    QComboBox, 
    QHBoxLayout, 
    QPushButton, 
)
from .UserInput import userInput
from . import icons

class RegionList(QWidget):
    """Manages a list of regions on the same underlay series"""

    currentRegionChanged = pyqtSignal()
    dataWritten = pyqtSignal()

    def __init__(self, series, regions=None):
        super().__init__()

        self._defineWidgets()
        self._defineConnections()
        self._defineLayout()
        self.setSeries(series)
        self.setRegions(regions)

    def setSeries(self, series):

        self._underlay = series

    def getSeries(self):

        return self._underlay

    def setRegions(self, regions):

        if regions == None:
            region = self._underlay.parent.new_child()
            self.regions = [region]
        else:
            self.regions = regions
        for region in self.regions: 
            region.read()

        self.comboBox.blockSignals(True)
        self.comboBox.clear()
        self.comboBox.addItems(self._items())
        self.comboBox.setCurrentIndex(0)
        self.comboBox.blockSignals(False)

    def getRegions(self):

        return self.regions

    def getRegion(self):

        return self._currentRegion

    def getMask(self, image):
        """Get the mask corresponding to a given image"""
    
        if image is None: return
        maskList = self._currentRegion.children(SliceLocation=image.SliceLocation) # needs to be slice orientation
        if maskList != []: return maskList[0]


#    def remove(self, region_to_remove):

#        for index, region in enumerate(self.regions):
#            if region == region_to_remove:
#                self.regions.remove(region)
#                self.comboBox.removeItem(index)
#                return

    def _defineWidgets(self):

        self.comboBox = QComboBox()
        self.comboBox.setDuplicatesEnabled(False)
        self.comboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.comboBox.setToolTip("List of regions")
        self.comboBox.setEditable(True)
        self.comboBox.setInsertPolicy(QComboBox.InsertAtCurrent)
        self.comboBox.setDuplicatesEnabled(True)
#        self.comboBox.addItems(self._items())
#        self.comboBox.setCurrentIndex(0)

        self.btnLoad = QPushButton()
        self.btnLoad.setToolTip('Load new ROIs')
        self.btnLoad.setIcon(QIcon(icons.application_import))

        self.btnNew = QPushButton() 
        self.btnNew.setToolTip('Create a new ROI')
        self.btnNew.setIcon(QIcon(icons.plus))
        
        self.btnDelete = QPushButton() 
        self.btnDelete.setToolTip('Delete the current ROI')
        self.btnDelete.setIcon(QIcon(icons.minus))

#        self.btnReset = QPushButton()
#        self.btnReset.setToolTip('Erase the current ROI')
#        self.btnReset.setIcon(QIcon(icons.arrow_curve_180_left))

        self.btnWrite = QPushButton()
        self.btnWrite.setToolTip('Write the current ROI to disk')
        self.btnWrite.setIcon(QIcon(icons.disk))

    def _defineLayout(self):

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.comboBox, alignment=Qt.AlignLeft)
        layout.addWidget(self.btnLoad, alignment=Qt.AlignLeft)
        layout.addWidget(self.btnNew, alignment=Qt.AlignLeft)
        layout.addWidget(self.btnDelete, alignment=Qt.AlignLeft)
#        layout.addWidget(self.btnReset, alignment=Qt.AlignLeft)
        layout.addWidget(self.btnWrite, alignment=Qt.AlignLeft)

        self.setLayout(layout)

    def _defineConnections(self):

        self.comboBox.currentIndexChanged.connect(self.currentRegionChanged.emit)
        self.btnLoad.clicked.connect(self._loadRegion)
        self.btnNew.clicked.connect(self._newRegion)
        self.btnDelete.clicked.connect(self._deleteRegion)
    #    self.btnReset.clicked.connect(self.maskView.eraseMask)
        self.btnWrite.clicked.connect(self._writeCurrentRegion)
        self.btnWrite.clicked.connect(self.dataWritten.emit)
        
    @property
    def _currentRegion(self):

        return self.regions[self.comboBox.currentIndex()]

    def _items(self):

        items = []
        for region in self.regions:
            if region.data().empty:
                item = 'New Region'
            else:
                item = region.SeriesDescription
            items.append(item)
        return items

    def _writeCurrentRegion(self):

        text = self.comboBox.currentText()
        self._currentRegion.SeriesDescription = text
        self._currentRegion.write()

    def _newRegion(self):

        region = self._underlay.parent.new_child()
        region.read()
        self.regions.append(region) # add to the list
        description = "New Region"
        count = 2
        while -1 != self.comboBox.findText(description, flags=Qt.MatchContains):
            description = "New Region" + ' [' + str(count).zfill(2) + ']'
            count += 1
        self.comboBox.blockSignals(True) #update the widget
        self.comboBox.addItem(description)
        self.comboBox.setCurrentIndex(len(self.regions)-1)
        self.comboBox.blockSignals(False)
        self.currentRegionChanged.emit()
        
    def _deleteRegion(self): # deletes it from the list 

        currentIndex = self.comboBox.currentIndex()
        region = self._currentRegion

        # Drop from the list
        self.regions.remove(region) 

        # Update the widget
        self.comboBox.blockSignals(True) 
        self.comboBox.removeItem(currentIndex)
        if self.regions == []:
            region = self._underlay.parent.new_child()
            region.read()
            self.regions = [region]
            self.comboBox.addItems(self._items())
            self.comboBox.setCurrentIndex(0)
        else:
            if currentIndex >= len(self.regions)-1:
                newIndex = len(self.regions)-1
            else:
                newIndex = currentIndex+1
            self.comboBox.setCurrentIndex(newIndex)
        self.comboBox.blockSignals(False)
        self.currentRegionChanged.emit()

    def _loadRegion(self):

        # Build list of series for all series in the same study
        seriesList = self._underlay.parent.children()
        seriesLabels = [series.SeriesDescription for series in seriesList]

        # Ask the user to select series to import as regions
        cancel, input = userInput(
            {"label":"Series:", "type":"listview", "list": seriesLabels},
            title = "Please select series to import as Regions", 
        )
        if cancel: return
        selectedSeries = [seriesList[i] for i in input[0]["value"]]
        
        # Overlay each of the selected series on the displayed series
        self.comboBox.blockSignals(True)
        for series in selectedSeries:
            series.read()
            region = series.map_onto(self._underlay)
            self.regions.append(region)
            self.comboBox.addItem(region.SeriesDescription)
        self.comboBox.setCurrentIndex(len(self.regions)-1)
        self.comboBox.blockSignals(False)
        self.currentRegionChanged.emit()