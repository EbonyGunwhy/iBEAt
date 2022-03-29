__all__ = ['app', 'doc', 'build', 'install']

import os
import sys
import logging

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

import weasel.wewidgets as widgets
from weasel.core import Main
from weasel.apps import WeaselWelcome

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class Weasel:

    def __init__(self):
        self.app = None
        self.log = logger()
        self.QApp = QApplication([])
        self.QApp.setWindowIcon(QIcon(widgets.icons.favicon))
        self.status = widgets.StatusBar()
        self.main = Main(self)
        self.main.setStatusBar(self.status)
        self.dialog = widgets.Dialog(self.main)
        self.app = WeaselWelcome(self)


def app():

    return Weasel().app

def activate():

    windows = (sys.platform == "win32") or (sys.platform == "win64") or (os.name == 'nt')
    if windows:
        return '.venv\\scripts\\activate'
    else: # MacOS and Linux
        return '.venv/bin/activate' 


def install():
    """Install requirements of weasel and current project"""

    print('Creating virtual environment..')
    os.system('py -3 -m venv .venv')

    print('Installing weasel requirements..')
    os.system(activate() + ' && ' + 'py -m pip install -r weasel\\requirements.txt')

    if os.path.exists('requirements.txt'):
        print('Installing project requirements..')
        os.system(activate() + ' && ' + 'py -m pip install -r requirements.txt')


def doc():
    """Generate weasel documentation"""

    # COMMAND LINE SCRIPT
    # py -3 -m venv .venv
    # .venv\\scripts\\activate
    # py -m pip install -r requirements.txt
    # pdoc --html -f -c sort_identifiers=False weasel  

    install()
    print('Generating documentation..')
    os.system(activate() + ' && ' + 'pdoc --html -f -c sort_identifiers=False weasel')
    

def build(project, onefile=True, terminal=False, data_folders=[]):
    """Generate project executable"""

    # COMMENT
    # subprocess.run() is recommended to call commands in python
    # but only works for creating the virtual environment.
    # For some reason pip install does not work with subprocess.
    # Using os.system() until this can be resolved.

    install()

#    hidden_modules = ['matplotlib']
#    hidden_imports = ' '.join(['--hidden-import '+ mod + ' ' for mod in hidden_modules])

    windows = (sys.platform == "win32") or (sys.platform == "win64") or (os.name == 'nt')

    if windows:
        all_data = [
            'weasel\\wewidgets\\icons\\my_icons;.\\weasel\\wewidgets\\icons\\my_icons',
            'weasel\\wewidgets\\icons\\fugue-icons-3.5.6;.\\weasel\\wewidgets\\icons\\fugue-icons-3.5.6',
            ]
    else:
        all_data = [
            'weasel/wewidgets/icons/my_icons;./weasel/wewidgets/icons/my_icons',
            'weasel/wewidgets/icons/fugue-icons-3.5.6;./weasel/wewidgets/icons/fugue-icons-3.5.6',
            ]
    all_data = all_data + data_folders
    add_data = ' '.join(['--add-data='+ mod + ' ' for mod in all_data])

    print('Creating executable..')
    cmd = activate() + ' && ' + 'pyinstaller --name "myproject"'
    if onefile: 
        cmd += ' --onefile'
    if not terminal: 
        cmd += ' --noconsole'
#    cmd += ' ' + hidden_imports
    cmd += ' ' + add_data
    cmd += ' ' + project + '.py'
    os.system(cmd)


def logger():
    
    LOG_FILE_NAME = "log.log"
    if os.path.exists(LOG_FILE_NAME):
        os.remove(LOG_FILE_NAME)
    LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(
        filename = LOG_FILE_NAME, 
        level = logging.INFO, 
        format = LOG_FORMAT)
    return logging.getLogger(__name__)

