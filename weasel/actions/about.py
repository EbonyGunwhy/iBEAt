import webbrowser
from weasel.core import Action

from weasel.widgets.icons import question_mark


def menu(parent):

    #menu = parent.menu('About')
    parent.action(About, text='Weasel', icon=question_mark) 


class About(Action):

    def run(self, app):
        webbrowser.open("weasel.pro")
        #webbrowser.get('chrome').open("Weasel.pro")
