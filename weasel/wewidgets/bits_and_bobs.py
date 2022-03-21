__all__ = ['LockUnlockButton']

from PyQt5.QtCore import  pyqtSignal
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon

from . import icons

class LockUnlockButton(QPushButton):

    toggled = pyqtSignal()

    def __init__(self, toolTip = 'Lock state'):
        super().__init__()

        self.isLocked = True
        self.icon_lock = QIcon(icons.lock) 
        self.icon_lock_unlock = QIcon(icons.lock_unlock) 
        self.setFixedSize(24, 24)
        self.setIcon(self.icon_lock)
        self.setToolTip(toolTip)
        self.clicked.connect(self.toggle) 

    def toggle(self):

        if self.isLocked == True:
            self.setIcon(self.icon_lock_unlock)
            self.isLocked = False
        elif self.isLocked == False:
            self.setIcon(self.icon_lock)
            self.isLocked = True
            
        self.toggled.emit()