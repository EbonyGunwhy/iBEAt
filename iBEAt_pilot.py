import weasel
from weasel.apps.dicom import Windows

from iBEAt.menus import pilot

wsl = weasel.app()
wsl.set_app(Windows)
wsl.set_menu(pilot)
wsl.show()