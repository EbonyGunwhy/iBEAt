__all__ = ['SelectImageColorTable']

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox

listColors =  ['gray', 'cividis',  'magma', 'plasma', 'viridis', 
    'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
    'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
    'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
    'binary', 'gist_yarg', 'gist_gray', 'bone', 'pink',
    'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
    'hot', 'afmhot', 'gist_heat', 'copper',
    'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
    'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
    'twilight', 'twilight_shifted', 'hsv',
    'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
    'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'turbo',
    'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar', 'custom']

QComboBoxStyleSheet = """

QComboBox::drop-down 
{
    border: 0px; /* This seems to replace the whole arrow of the combo box */
}
QComboBox:down-arrow 
{
    image: url("weasel/widgets/icons/fugue-icons-3.5.6/spectrum.png");
}
"""


class SelectImageColorTable(QComboBox):  

    newColorTable = pyqtSignal(str)

    def __init__(self, image=None):
        super().__init__() 
                                         
        self.blockSignals(True)
        self.addItems(listColors)
        self.blockSignals(False)
        self.setToolTip('Change colors')
        #self.setFixedHeight(28)
        self.setMaximumWidth(120)
        self.setStyleSheet(QComboBoxStyleSheet)
        self.currentIndexChanged.connect(self.colorTableChanged)

        self.setData(image)
#        if image is None:
#            colorTable = 'gray'
#        else:
#            colorTable, _ = image.get_colormap()
#        self.image = image

    def setData(self, image):

        self.image = image
        self.setValue()
    
    def setValue(self):

        if self.image is None:
            colorTable = 'gray'
        else:
            colorTable, _ = self.image.get_colormap()
        self.blockSignals(True)
        self.setCurrentText(colorTable)
        self.blockSignals(False)
        
    def colorTableChanged(self):

        if self.image is None: return
        
        colorTable = self.currentText()
        if colorTable.lower() == 'custom':
            colorTable = 'gray'             
            self.blockSignals(True)
            self.setCurrentText(colorTable)
            self.blockSignals(False) 
        self.image.set_colormap(colormap=colorTable)
        self.newColorTable.emit(colorTable)


