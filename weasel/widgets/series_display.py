__all__ = ['SeriesViewer']

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout, 
    QToolBar, 
)                          

from .. import widgets

class SeriesViewer(QWidget):
    """Display a single series."""

    closed = pyqtSignal()

    def __init__(self, series=None): 
        super().__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)
 
        self._setWidgets()
        self._setConnections()
        self._setLayout()
        self.setData(series)

    def _setWidgets(self):

        self.settings = widgets.LockUnlockButton(toolTip = 'Lock image settings')
        self.colors = widgets.SelectImageColorTable() 
        self.brightness = widgets.ImageBrightness()
        self.contrast = widgets.ImageContrast()
        self.export = widgets.ExportImageButton()
        self.restore = widgets.RestoreImageButton()
        self.save = widgets.SaveImageButton()
        self.delete = widgets.DeleteImageButton()
        self.pixelValue = widgets.PixelValueLabel()
        self.graphics = widgets.GraphicsView()
        self.imageSliders = widgets.ImageSliders()

    def _setConnections(self):

        self.colors.newColorTable.connect(self._imageHasChanged)
        self.restore.buttonClicked.connect(self._restoreClicked)
        self.save.buttonClicked.connect(self._saveClicked)
        self.delete.buttonClicked.connect(self._imageDeleted)
        self.brightness.valueChanged.connect(self._imageHasChanged)
        self.contrast.valueChanged.connect(self._imageHasChanged)
        self.graphics.sigLevelsChanged.connect(self._setWindowValue)
        self.graphics.sigMouseMoved.connect(self._graphicsMouseMoved)
        self.imageSliders.valueChanged.connect(self._imageSlidersValueChanged)

    def _setLayout(self):

        self.toolBar = QToolBar()
        self.toolBar.addWidget(self.restore) 
        self.toolBar.addWidget(self.save)  
        self.toolBar.addWidget(self.delete)
        self.toolBar.addWidget(self.export)
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.settings) 
        self.toolBar.addWidget(self.colors) 
        self.toolBar.addWidget(self.brightness) 
        self.toolBar.addWidget(self.contrast) 
        self.toolBar.addWidget(self.pixelValue)
        self.toolBar.setStyleSheet("background-color: white")

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.toolBar)
        layout.addWidget(self.graphics.widget)
        layout.addWidget(self.imageSliders)
        
        self.setLayout(layout)

    def setData(self, series=None):

        self.setEnabled(series is not None)
        self.series = series
        if series is None:
            self.image = None
        else:
            if series.on_disk():
                series.read()
            self.image = series.children(0)
        self.image_has_changed = False

        self._setImage()
        self.imageSliders.setData(self.series, self.image)

    def _setImage(self):

        self.colors.setData(self.image)
        self.export.setData(self.image)
        self.restore.setData(self.image)
        self.save.setData(self.image)
        self.delete.setData(self.image)
        self.brightness.setData(self.image)
        self.contrast.setData(self.image)
        self.pixelValue.setData(self.image)
        self.graphics.setData(self.image)
        
    def _imageHasChanged(self):

        self.image_has_changed = True
        self.graphics.show()

    def _restoreClicked(self):

        self.image_has_changed = False
        self.series.restore(
            message="Restoring all images of the series to last saved state..")
        self.brightness.setValue()
        self.contrast.setValue()
        self.colors.setValue()
        self.graphics.show()

    def _saveClicked(self):

        self.image_has_changed = False
        center = self.image.WindowCenter
        width = self.image.WindowWidth
        colormap, _ = self.image.get_colormap()
        instances = self.series.instances()
        self.series.status.message('Saving all images of the series..')
        for i, image in enumerate(instances):
            image.WindowCenter = center
            image.WindowWidth = width 
            image.set_colormap(colormap=colormap)
            image.save()
            self.series.status.progress(i, len(instances))
        self.series.status.hide()

    def _imageDeleted(self):

        self.imageSliders.blockSignals(True)       
        self.imageSliders.setSeries(self.series)
        self.imageSliders.blockSignals(False)
        self.image = self.imageSliders.getImage()
        self._setImage()
        
    def _setWindowValue(self):

        self.image_has_changed = True
        self.brightness.setValue()
        self.contrast.setValue()

    def _graphicsMouseMoved(self):

        xy = self.graphics.coordinates
        self.pixelValue.setValue(xy)

    def _imageSlidersValueChanged(self):

        image_on_display = self.image is not None
        if self.image_has_changed: 
            if image_on_display:
                self.image.write() 
        if self.settings.isLocked:
            if image_on_display:
                center = self.image.WindowCenter
                width = self.image.WindowWidth
                colormap, _ = self.image.get_colormap()

        self.image = self.imageSliders.getImage()
        self.image_has_changed = False

        if self.settings.isLocked:
            if self.image is not None:
                if image_on_display:
                    self.image.WindowCenter = center 
                    self.image.WindowWidth = width 
                    self.image.set_colormap(colormap=colormap)
                    self.image_has_changed = True

        self._setImage()