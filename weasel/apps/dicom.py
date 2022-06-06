__all__ = ['DicomWindows', 'DicomSeries']

from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtCore import Qt

import dbdicom as db
import weasel as wsl

from weasel import widgets
from weasel import actions


class Windows(wsl.App):

    def __init__(self, weasel): 
        """Creates the default main window."""

        super().__init__(weasel)

        self.treeView = None
        self.folder = db.Folder(status=self.status, dialog=self.dialog)
        self.central = widgets.MainMultipleDocumentInterface()
        self.main.setCentralWidget(self.central)
        self.set_menu(actions.demo.menu)

    def set_data(self, folder):

        if self.folder.close():
            self.central.closeAllSubWindows()
        else:
            return
        self.folder = folder
        if self.treeView is None:
            self.display(folder)
        else:
            self.treeView.setFolder(folder)
        self.menubar.enable()

    def open(self, path, message='Opening folder..'):
        self.folder.open(path, message=message)
        self.display(self.folder)

    def close(self):
        """Closes the application."""

        accept = self.folder.close()
        if accept:
            self.central.closeAllSubWindows()
            for dockwidget in self.main.findChildren(QDockWidget):
                self.main.removeDockWidget(dockwidget)
            self.menubar.enable()
        #    self.set_app(apps.WeaselWelcome)
        return accept

    def refresh(self):
        """
        Refreshes the Weasel display.
        """
        self.status.message('Refreshing display..')
        self.treeView.setFolder()
        self.menubar.enable()
        self.status.message()

    def addAsDockWidget(self, widget, title=''):

        dockwidget = QDockWidget(title, self.main, Qt.SubWindow)
        dockwidget.setAllowedAreas(Qt.LeftDockWidgetArea)
        dockwidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        dockwidget.setObjectName(widget.__class__.__name__)
        dockwidget.setWidget(widget)

        self.main.addDockWidget(Qt.LeftDockWidgetArea, dockwidget)

    def addAsSubWindow(self, widget, title=None, icon=None):
        """
        displays a widget as a subwindow in the MDI. 
        
        Returns the subwindow
        """ 
        return self.central.addWidget(widget, title=title, icon=icon)

    def addSubWindow(self, subWindow):

        self.central.addSubWindow(subWindow) 

    def closeAllSubWindows(self):
        """
        Closes all open windows.
        """
        self.central.closeAllSubWindows()

    def closeSubWindow(self, subWindowName):
        """
        Closes all subwindows with a given name
        """   
        self.central.closeSubWindow(subWindowName)  

    def tileSubWindows(self):
        """
        Tiles all open windows.
        """
        self.central.tileSubWindows()

    def display(self, object):

        if object.generation == 0:
            self.treeView = widgets.DICOMFolderTree(object, self.status)
            self.treeView.itemSelectionChanged.connect(self.menubar.enable)
            self.addAsDockWidget(self.treeView, title=object.path)
            self.menubar.enable()
        elif object.generation == 1: # No Patient Viewer yet
            pass
        elif object.generation == 2: # No Study Viewer yet
            pass
        elif object.generation == 3:
            viewer = widgets.SeriesViewer(object)
            self.addAsSubWindow(viewer, title=object.label())
        elif object.generation == 4:
            viewer = widgets.ImageViewer(object)
            self.addAsSubWindow(viewer, title=object.label())

    def get_selected(self, generation):
        
        if self.treeView is None: return []
        if generation == 4: return []
        selected = self.treeView.get_selected(generation)
        return [self.folder.object(row, generation) for row in selected]

    def nr_selected(self, generation):

        if self.treeView is None: return 0
        if generation == 4: return 0
        selected = self.treeView.get_selected(generation)
        return len(selected)

class Series(wsl.App):

    def __init__(self, weasel): 
        """Creates a central window showing series only."""

        super().__init__(weasel)

        self.folder = db.Folder(status=weasel.status, dialog=weasel.dialog)
        self.central = widgets.SeriesViewer()
        self.main.setCentralWidget(self.central)
        self.set_menu(actions.demo.menu) 

    def close(self):
        """Closes the Weasel display"""

        accept = self.folder.close()
        if accept:
            for dockwidget in self.main.findChildren(QDockWidget):
                self.main.removeDockWidget(dockwidget)
            self.main.menuBar().enable()
        return accept

    def refresh(self):
        """
        Refreshes the Weasel display.
        """
        self.weasel.status.message('Refreshing display..')
        self.treeView.setFolder()
        self.weasel.menubar.enable()
        self.weasel.status.message()

    def addAsDockWidget(self, widget, title=''):

        dockwidget = QDockWidget(title, self, Qt.SubWindow)
        dockwidget.setAllowedAreas(Qt.LeftDockWidgetArea)
        dockwidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        dockwidget.setObjectName(widget.__class__.__name__)
        dockwidget.setWidget(widget)

        self.main.addDockWidget(Qt.LeftDockWidgetArea, dockwidget)

    def display(self, object=None):

        if object is None:
            self.treeView = widgets.DICOMFolderTree(self.folder, self.weasel.status)
            self.treeView.itemSelectionChanged.connect(self.weasel.menubar.enable)
            self.addAsDockWidget(self.treeView, title=self.folder.path)
        elif object.generation == 1: # No Patient Viewer yet
            pass
        elif object.generation == 2: # No Study Viewer yet
            pass
        elif object.generation == 3:
            self.central.setData(object)
        elif object.generation == 4:
            pass