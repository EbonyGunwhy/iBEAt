__all__ = ['Main', 'App', 'Action', 'MenuBar', 'Menu']

from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QMenuBar
from PyQt5.QtGui import QIcon

import weasel.widgets as widgets


class Main(QMainWindow):

    def __init__(self, weasel): 
        """Creates the main window."""

        super().__init__()

        self.weasel = weasel
        self.setWindowTitle("Weasel")
        self.setWindowIcon(QIcon(widgets.icons.favicon))

    def closeEvent(self, event): # dummy for now
        accept = self.weasel.app.close()
        if accept:
            event.accept()
        else:
            event.ignore()


class App:
    """Base class for all Weasel applications"""

    def __init__(self, weasel):
        self.weasel = weasel

    @property
    def QApp(self):
        return self.weasel.QApp

    @property
    def main(self):
        return self.weasel.main

    @property
    def log(self):
        return self.weasel.log

    @property
    def dialog(self):
        return self.weasel.dialog

    @property
    def menubar(self):
        return self.main.menuBar()

    @property
    def status(self):
        return self.main.statusBar()

    def show(self):    
        self.log.info('Launching Weasel!')
        try:
            self.main.show()
            self.QApp.exec()
            #sys.exit(app.exec())
        except Exception as e:
            self.log.exception('Error: ' + str(e))

    def set_menu(self, menu):
        menubar = MenuBar(self, menu)
        self.main.setMenuBar(menubar)

    def set_central(self, widget):
        self.main.setCentralWidget(widget)

    def set_status(self, message):
        self.status.message(message)

    def set_data(self, data=None):
        pass

    def get_data(self):
        pass

    def set_app(self, App):
        weasel = self.weasel
        weasel.app = App(weasel) 
        self.__class__ = App 
        self.__dict__ = weasel.app.__dict__
        return weasel.app   

    def close(self):
        """
        Called when the user attemps to close the main window.

        Returns: True if the window can be closed, False if not.
        """
        return True


class MenuBar(QMenuBar):
    """
    Programming interfaces for the Weasel menus. 
    """

    def __init__(self, app, menu):
        super().__init__()

        self._menus = []
        self.app = app
        menu(self)
        self.enable()

    def addMenu(self, menu):
        super().addMenu(menu)
        self._menus.append(menu)
        
    def menu(self, label = "Menu"):
        """
        Creates a top level menu in the menuBar.
        """
        return Menu(self, label)

    def enable(self):
        """
        Refreshes the enabled status of each menu item.
        """
        for menu in self._menus:
            menu.enable()


class Menu(QMenu):

    def __init__(self, parent=None, title='Menu'):
        super().__init__()

        self._actions = []
        self._menus = []
        self.setTitle(title)
        self.app = parent.app
        if parent is not None:
            parent.addMenu(self)

    def addMenu(self, menu):
        super().addMenu(menu)
        self._menus.append(menu)

    def menu(self, title='Submenu'):
        return Menu(self, title)

    def action(self, action, **kwargs):
        return action(self, **kwargs)
        
    def separator(self):
        self.addSeparator() 

    def enable(self):
        """
        Refreshes the enabled status of each menu item.
        """
        for submenu in self._menus:
            submenu.enable()
        for action in self._actions:
            enable = action.enable(action.app)
            action.setEnabled(enable)


class Action(QAction):
    """Base class for all weasel actions"""

    def __init__(self, parent,
        text = None,
        shortcut = None,
        tooltip = None, 
        icon = None):
        """parent: App, Menu or MenuBar"""
        super().__init__()

        if hasattr(parent, 'app'):
            self.app = parent.app
            parent.addAction(self)
            parent._actions.append(self)
        else:
            self.app = parent
        if text is None:
            text = self.__class__.__name__
        self.setText(text)
        self.triggered.connect(lambda: self.run(self.app))
    
        if icon is not None: self.setIcon(QIcon(icon))
        if shortcut is not None: self.setShortcut(shortcut)
        if tooltip is not None: self.setToolTip(tooltip)

    def enable(self, app):
        return True

    def run(self, app):
        pass

