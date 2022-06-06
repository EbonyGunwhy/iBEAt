__all__ = ['MaskViewToolBox']

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

from .. import widgets as widgets

class MaskViewToolBox(QWidget):

    newTool = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.button = {}
        self.current = "ImageViewCursor"
        self.defineWidgets()
        self.defineLayout()
        self.setTool(self.current) 
        
    def defineWidgets(self):

        self.defineButton(widgets.ImageViewCursor())
        self.defineButton(widgets.ImageViewZoom())
        self.defineButton(widgets.MaskViewBrush())
        self.defineButton(widgets.MaskViewPenFreehand())
        self.defineButton(widgets.MaskViewPenPolygon())
        self.defineButton(widgets.MaskViewPenRectangle())
        self.defineButton(widgets.MaskViewPenCircle())

    def defineButton(self, tool):

        key = tool.__class__.__name__
        self.button[key] = QPushButton()
        self.button[key].setToolTip(tool.toolTip)
        self.button[key].setCheckable(True)
        self.button[key].setIcon(tool.icon)
        self.button[key].tool = tool
        self.button[key].clicked.connect(lambda: self.buttonClicked(key))     
        
    def defineLayout(self):

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        for button in self.button.values():
            layout.addWidget(button, alignment=Qt.AlignLeft)
        self.setLayout(layout)

    def buttonClicked(self, key):

        self.setTool(key)
        self.newTool.emit()

    def setTool(self, key):

        self.button[self.current].setChecked(False)
        self.current = key
        self.button[self.current].setChecked(True)

    def getTool(self):

        return self.button[self.current].tool