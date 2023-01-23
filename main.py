# To develop the application
# --------------------------
# py -3 -m venv .venv           # create virtual environment
# .venv/Scripts/activate        # activate virtual environment

import wezel
from wezel.apps.dicom import Windows
from menus import pilot

import wezel
if __name__ == "__main__":
    wsl = wezel.app()
    wsl.set_app(Windows)
    wsl.set_menu(pilot)
    wsl.show() 
