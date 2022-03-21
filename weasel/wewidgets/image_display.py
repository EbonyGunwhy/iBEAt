__all__ = ['ImageViewer', 'ImageLabel']

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout, 
    QLabel, 
    QToolBar,
)
from .. import wewidgets as widget
from . import icons

class ImageViewer(QWidget):
    """Display a single image."""

    closed = pyqtSignal()

    def __init__(self, image=None): 
        super().__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)

        self._setWidgets()
        self._setConnections()
        self._setLayout()
        self.setData(image)

    def _setWidgets(self):

        self.colors = widget.SelectImageColorTable()
        self.brightness = widget.ImageBrightness()
        self.contrast = widget.ImageContrast()
        self.export = widget.ExportImageButton()
        self.restore = widget.RestoreImageButton()
        self.save = widget.SaveImageButton()
        self.pixelValue = widget.PixelValueLabel()
        self.graphics = widget.GraphicsView()
        
    def _setConnections(self):

        self.colors.newColorTable.connect(self.graphics.show)
        self.restore.buttonClicked.connect(self._restoreClicked)
        self.brightness.valueChanged.connect(self.graphics.show)
        self.contrast.valueChanged.connect(self.graphics.show)
        self.graphics.sigLevelsChanged.connect(self._setWindowValue)
        self.graphics.sigMouseMoved.connect(self._graphicsMouseMoved)

    def _setLayout(self):

        self.toolBar = QToolBar()
        self.toolBar.addWidget(self.restore)
        self.toolBar.addWidget(self.save)  
        self.toolBar.addWidget(self.export)
        self.toolBar.addSeparator()
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
        
        self.setLayout(layout)

    def setData(self, image=None):

        self.setEnabled(image is not None)
        if image is not None:
            if image.on_disk(): 
                image.read()
        self.image = image
        self.colors.setData(image)
        self.brightness.setData(image)
        self.contrast.setData(image)
        self.export.setData(image)
        self.restore.setData(image)
        self.save.setData(image)
        self.pixelValue.setData(image)
        self.graphics.setData(image)

    def _restoreClicked(self):

        self.colors.setValue()
        self.graphics.show()

    def _setWindowValue(self):

        self.brightness.setValue()
        self.contrast.setValue()

    def _graphicsMouseMoved(self):

        xy = self.graphics.coordinates
        self.pixelValue.setValue(xy)


class ImageLabel(QLabel):

    def __init__(self):
        super().__init__()

        self.setScaledContents(True)
        self.setData(icons.weasel)
        
    def setData(self, file):
        self.im = QPixmap(file).scaledToWidth(512)
        self.setPixmap(self.im)


