__all__ = [
    'RestoreImageButton', 
    'SaveImageButton', 
    'ExportImageButton', 
    'DeleteImageButton', 
]

from PyQt5.QtCore import  pyqtSignal
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon

from . import icons

class DeleteImageButton(QPushButton):

    buttonClicked = pyqtSignal()

    def __init__(self, image=None):
        super().__init__()

    #    self.image = image
        
        self.setFixedSize(24, 24)
        self.setIcon(QIcon(icons.bin_metal))
        self.setToolTip('Delete image')
        self.clicked.connect(self.delete) 

        self.setData(image)

    def delete(self):
 
        if self.image is None:
            return
        self.image.remove()
        self.buttonClicked.emit()

    def setData(self, image):
        self.image = image


class ExportImageButton(QPushButton):

    def __init__(self, object=None):
        super().__init__()

    #    self.object = object
 
        self.setFixedSize(24, 24)
        self.setIcon(QIcon(icons.blue_document_export))
        self.setToolTip('Export as .png')
        self.clicked.connect(self.exportObject)

        self.setData(object)

    def setData(self, object):
        self.object = object

    def setObject(self, object): # obsolete
        self.object = object

    def exportObject(self):
        """Export as png."""

        if self.object is None: return
        fileName = self.object.dialog.file_to_save(filter = "*.png")
        if fileName == None: return
        fileName = fileName[:-4]
        instances = self.object.instances()
        self.object.status.message('Exporting as png..')
        for i, image in enumerate(instances):
            image.export_as_png(fileName)
            self.object.status.progress(i, len(instances))
        self.object.status.hide()


class RestoreImageButton(QPushButton):

    buttonClicked = pyqtSignal()

    def __init__(self, image=None):
        super().__init__()

    #    self.image = image
         
        self.setFixedSize(24, 24)
        self.setIcon(QIcon(icons.arrow_curve_180_left))
        self.setToolTip('Undo changes')
        self.clicked.connect(self.restore) 

        self.setData(image)

    def setData(self, image):
        self.image = image

    def restore(self):

        if self.image is None: return
        self.image.restore()
        self.buttonClicked.emit()


class SaveImageButton(QPushButton):

    buttonClicked = pyqtSignal()

    def __init__(self, image=None):
        super().__init__()

        self.setFixedSize(24, 24)
        self.setIcon(QIcon(icons.disk))
        self.setToolTip('Save changes')
        self.clicked.connect(self.save) 

        self.setData(image)

    def save(self):
 
        if self.image is None:
            return
        self.image.save()
        self.buttonClicked.emit()

    def setData(self, image):
        self.image = image