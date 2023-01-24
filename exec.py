# To set up a virtual environment
# -------------------------------
# Create virtual environment and activate it
# py -3 -m venv .venv           
# .venv/Scripts/activate 

# Install editable versions of requirements under development
# pip install -e C:\Users\steve\Dropbox\Software\QIB-Sheffield\dbdicom
# pip install -e C:\Users\steve\Dropbox\Software\QIB-Sheffield\wezel
# pip install -e C:\Users\steve\Dropbox\Software\QIB-Sheffield\mdreg

# Install other requirements
# pip install -r requirements.txt

# to build an executable:
# -----------------------
# distribution mode: splash screen, single file and no console
# pyinstaller --name wezel --clean --onefile --noconsole --additional-hooks-dir=. --splash wezel.jpg exec.py

# debugging mode: multiple files & no splash & console included
# pyinstaller --name wezel --clean --additional-hooks-dir=. exec.py


import wezel
from menu.kanishka import iBEAT_dev


if __name__ == "__main__":

    # Main program
    wzl = wezel.app()
    wzl.set_menu(iBEAT_dev)
    wzl.show()