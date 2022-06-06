__all__ = ['Dialog', 'StatusBar']

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QApplication,                          
    QStatusBar, 
    QProgressBar, 
    QFileDialog, 
    QMessageBox, 
)

from .UserInput import userInput

 
class Dialog():

    def __init__(self, parent=None):

        self.parent = parent

    def information(self, message="Message in the box", title="Window Title"):
        """
        Information message. Press 'OK' to continue.
        """
        QMessageBox.information(self.parent, title, message)

    def warning(self, message="Message in the box", title="Window Title"):
        """
        Warning message. Press 'OK' to continue.
        """
        QMessageBox.warning(self.parent, title, message)

    def error(self, message="Message in the box", title="Window Title"):
        """
        Error message. Press 'OK' to continue.
        """
        QMessageBox.critical(self.parent, title, message)

    def directory(self, message='Please select a folder', datafolder=None):
        """
        Select a directory.
        """
        return QFileDialog.getExistingDirectory(
            parent = self.parent, 
            caption = message, 
            directory = datafolder, 
            options = QFileDialog.ShowDirsOnly)

    def question(self, message="Do you wish to proceed?", title="Question for the user", cancel=False):
        """
        Displays a question window in the User Interface.
        
        The user has to click either "OK" or "Cancel" in order to continue using the interface.
        Returns False if reply is "Cancel" and True if reply is "OK".
        """
        if cancel:
            reply = QMessageBox.question(
                self.parent, title, message,
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, 
                QMessageBox.No)
        else:
            reply = QMessageBox.question(
                self.parent, title, message,
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No)
        if reply == QMessageBox.Yes: return "Yes"
        elif reply == QMessageBox.No: return "No"
        elif reply == QMessageBox.Cancel: return "Cancel"

    def file_to_open(self, 
        title = 'Open file..', 
        initial_folder = None, 
        extension = "All files (*.*)", 
        datafolder = None):
        """
        Select a file to read.
        """
        if initial_folder is None:
            initial_folder = datafolder
        filename, _ = QFileDialog.getOpenFileName(title, initial_folder, extension)
        if filename == '': return None
        return filename

    def file_to_save(self, title='Save as ...', directory=None, filter="All files (*.*)", datafolder=None):
        """
        Select a filename to save.
        """
        if directory is None:
            directory = datafolder
        filename, _ = QFileDialog.getSaveFileName(caption=title, directory=directory, filter=filter)
        if filename == '': return None
        return filename

    def input(self, *fields, title="User input window"):
        """
        Collect user input of various types.
        """
        return userInput(*fields, title=title)



class StatusBar(QStatusBar):

    def __init__(self):
        super().__init__()

        self.progressBar = QProgressBar()
        self.progressBar.setFixedHeight(10)
        self.addPermanentWidget(self.progressBar)
        self.hide()

    def hide(self):

        self.message('')
        self.progressBar.hide()
        QApplication.processEvents() # allow gui to update

    def message(self, message=None):

        if message == None: 
            message = ''
        self.showMessage(message)
        QApplication.processEvents() # allow gui to update

    def progress(self, value, total, message=None):

        if message is not None: self.message(message)
        self.progressBar.show()
        self.progressBar.setRange(0, total)
        self.progressBar.setValue(value)
        QApplication.processEvents() # allow gui to update

    def cursorToHourglass(self):
        """
        Turns the arrow shape for the cursor into an hourglass. 
        """   
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

    def cursorToNormal(self):
        """
        Restores the cursor into an arrow after it was set to hourglass 
        """   
        QApplication.restoreOverrideCursor() 