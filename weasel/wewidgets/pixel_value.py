__all__ = ['PixelValueLabel']

from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import QLabel


class PixelValueLabel(QLabel):
    """
    Label showing the pixel value.
    """

    def __init__(self, image=None):
        super().__init__()

        self.image = image
        self.setMargin(0)
        self.setTextFormat(Qt.PlainText)

    def setData(self, image):
        self.image = image

    def setValue(self, coordinates):
        
        text = ""
        if self.image is not None:
            if len(coordinates) == 2:
                x = coordinates[0]
                y = coordinates[1]
                if 0 <= x < self.image.Rows:
                    if 0 <= y < self.image.Columns:
                        pixelArray = self.image.array()
                        pixelValue = pixelArray[x,y]
                        text = "Signal ({}, {}) = {}".format(x, y, pixelValue)
        self.setText(text)