import weasel
from iBEAt.pilot import menu

wsl = weasel.app()
wsl.set_app(weasel.apps.DicomWindows)
wsl.set_menu(menu)
wsl.show()