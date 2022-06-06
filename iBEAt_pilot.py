import weasel
from weasel.apps.dicom import Windows

from iBEAt.pilot import menu

wsl = weasel.app()
wsl.set_app(Windows)
wsl.set_menu(menu)
wsl.show()