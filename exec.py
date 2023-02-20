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
from menu.kanishka import coreg_menu
from menu.steven import dummy_menu


def iBEAT_dev(parent): 

    wezel.menu.folder.all(parent.menu('File'))
    wezel.menu.edit.all(parent.menu('Edit'))
    wezel.menu.view.all(parent.menu('View'))
    wezel.menu.filter.all(parent.menu('Filter'))
    wezel.menu.segment.all(parent.menu('Segment'))
    wezel.menu.transform.all(parent.menu('Transform'))
    coreg_menu(parent.menu('iBEAt-reg'))
    dummy_menu(parent.menu('iBEAt-seg'))
    wezel.menu.about.all(parent.menu('About'))


if __name__ == "__main__":

    # Main program
    wzl = wezel.app()
    wzl.set_menu(iBEAT_dev)
    wzl.show()