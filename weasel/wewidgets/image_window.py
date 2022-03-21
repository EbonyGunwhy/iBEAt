__all__ = ['ImageBrightness', 'ImageContrast']

from PyQt5.QtCore import  Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QDoubleSpinBox, QLabel, QHBoxLayout)

from . import icons


class ImageContrast(QWidget):

    valueChanged = pyqtSignal(float)

    def __init__(self, image=None):
        super().__init__()

        self.label = QLabel()
        self.label.setPixmap(QPixmap(icons.contrast))
        self.label.setFixedSize(24, 24)

        self.spinBox = QDoubleSpinBox()
        self.spinBox.valueChanged.connect(self.spinBoxValueChanged)
        self.spinBox.setToolTip("Adjust Contrast")
        self.spinBox.setMinimum(-100000.00)
        self.spinBox.setMaximum(1000000000.00)
        self.spinBox.setWrapping(True)
        self.spinBox.setFixedWidth(75)

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignLeft  | Qt.AlignVCenter)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(2)
        self.layout.addWidget(self.spinBox)
        self.layout.addWidget(self.label)

        self.setMaximumWidth(120)
        self.setLayout(self.layout)

        self.setData(image)

    def setData(self, image):

        self.image = image
        if self.image is None: 
            width = 1
        else:
            width = self.image.WindowWidth 
        self.setValue(width) 
        self.setSpinBoxStepSize() 
    
    def setSpinBoxStepSize(self):

        if self.image is None: return

        centre, width = self.image.window()
        minimumValue = centre - width/2
        maximumValue = centre + width/2
        if (minimumValue < 1 and minimumValue > -1) and (maximumValue < 1 and maximumValue > -1):
            spinBoxStep = float(width / 200) # It takes 100 clicks to walk through the middle 50% of the signal range
        else:
            spinBoxStep = int(width / 200) # It takes 100 clicks to walk through the middle 50% of the signal range
        self.spinBox.setSingleStep(spinBoxStep)

    def setValue(self, width=None):

        if width is None:
            width = self.image.WindowWidth
        self.spinBox.blockSignals(True)
        self.spinBox.setValue(width)
        self.spinBox.blockSignals(False)

    def spinBoxValueChanged(self):
        """Update Window Width of the image."""
        
        if self.image is None:
            return
        width = self.spinBox.value()
        self.image.WindowWidth = width
        self.valueChanged.emit(width)


class ImageBrightness(QWidget):

    valueChanged = pyqtSignal(float)

    def __init__(self, image=None):

        super().__init__() 

        self.label = QLabel()
        self.label.setPixmap(QPixmap(icons.brightness))
        self.label.setFixedSize(24, 24)

        self.spinBox = QDoubleSpinBox()
        self.spinBox.valueChanged.connect(self.spinBoxValueChanged)
        self.spinBox.setToolTip("Adjust Brightness")
        self.spinBox.setMinimum(-100000.00)
        self.spinBox.setMaximum(1000000000.00)
        self.spinBox.setWrapping(True)
        self.spinBox.setFixedWidth(75)

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignLeft  | Qt.AlignVCenter)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(2)
        self.layout.addWidget(self.spinBox)
        self.layout.addWidget(self.label)

        self.setMaximumWidth(120)
        self.setLayout(self.layout)

        self.setData(image)

    def setData(self, image):

        self.image = image
        if self.image is None:
            center = 0
        else:
            center = self.image.WindowCenter
        self.setValue(center)
        self.setSpinBoxStepSize()
    
    def setSpinBoxStepSize(self):

        if self.image is None: return

        centre, width = self.image.window()
        minimumValue = centre - width/2
        maximumValue = centre + width/2
        if (minimumValue < 1 and minimumValue > -1) and (maximumValue < 1 and maximumValue > -1):
            spinBoxStep = float(width / 200) # It takes 100 clicks to walk through the middle 50% of the signal range
        else:
            spinBoxStep = int(width / 200) # It takes 100 clicks to walk through the middle 50% of the signal range
        self.spinBox.setSingleStep(spinBoxStep)

    def spinBoxValueChanged(self):
        """Update Window Width of the image."""
        
        if self.image is None:
            return
        center = self.spinBox.value()
        self.image.WindowCenter = center
        self.valueChanged.emit(center)

    def setValue(self, center=None):

        if center is None: 
            center = self.image.WindowCenter
        self.spinBox.blockSignals(True)
        self.spinBox.setValue(center)
        self.spinBox.blockSignals(False)