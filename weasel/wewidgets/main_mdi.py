__all__ = ['MainMultipleDocumentInterface', 'Message']

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QBrush
from PyQt5.QtWidgets import (                         
    QMdiArea, QWidget, QVBoxLayout, 
    QMdiSubWindow, QLabel,
)

class MainMultipleDocumentInterface(QMdiArea):

    def __init__(self):
        super().__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setBackground(QBrush(Qt.black))

    def addSubWindow(self, subWindow):

        super().addSubWindow(subWindow) 
        height = self.height()
        width = self.width()
        subWindow.setGeometry(0, 0, width, height)
        self.tileSubWindows()
        subWindow.show() 

    def addWidget(self, widget, title=None, icon=None):
        """This method takes a composite widget created by an external 
        application, makes it the central widget of an MDI subwindow 
        and displays that subwindow in the Weasel MDI""" 

        subWindow = QMdiSubWindow()
        subWindow.setWidget(widget)
        subWindow.setObjectName(widget.__class__.__name__)
        subWindow.setWindowFlags(
            Qt.CustomizeWindowHint | 
            Qt.WindowCloseButtonHint | 
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint)
        if title is not None:
            subWindow.setWindowTitle(title)
        if icon is not None:
            subWindow.setWindowIcon(QIcon(icon))
        self.addSubWindow(subWindow)
        if hasattr(widget, 'closed'):
            widget.closed.connect(subWindow.close)
        return subWindow
        
    def closeSubWindow(self, subWindowName):
        """
        Closes all subwindows of a given Class

        objectName (string): the value set by setObjectName(objectName)
            when the SubWindow was created
        """   
        for subWindow in self.subWindowList():
            if subWindow.objectName() == subWindowName:
                subWindow.close() 


class Message(QMdiSubWindow):

    def __init__(self, message=None, title=None):
            
        super().__init__()

        self.label = QLabel()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.widget = QWidget()
        self.widget.setLayout(layout)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWidget(self.widget)

        if message is not None:
            self.display(message, title=title)

    def display(self, message, title=None):

        self.label.setText(message)
        self.label.adjustSize() 
        if title is not None:
            self.setWindowTitle(title)
        self.show()


