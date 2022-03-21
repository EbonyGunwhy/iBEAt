from weasel import Action
import weasel.actions as actions

def sillymenu(parent):
    
    menu = parent.menu('Silly')
    menu.action(HelloHull, text='Hello Hull')
    menu.action(HelloHull, text='Hello Hull 2')
    menu.action(actions.demo.HelloWorld, text='Hello World')
    menu.action(actions.demo.ToggleApp, text='Toggle application')

def improc(parent):
    
    actions.folder.menu(parent)
    actions.edit.menu(parent)
    actions.view.menu(parent)
    
    menu = parent.menu("Silly")
    menu.action(HelloHull, text='Hello Hull')
    menu.action(HelloHull, text='Hello Hull 2')
    menu.action(actions.demo.ToggleApp, text='Toggle application')
    
    actions.about.menu(parent)

class HelloHull(Action):

    def run(self, app):

        app.dialog.information("Hello Hull!", title = 'My first pipeline!')