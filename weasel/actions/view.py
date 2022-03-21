from weasel.core import Action
from weasel.wewidgets import SeriesViewerROI

def menu(parent):
   
    parent.action(Image)
    parent.action(Series)
    parent.separator()
    parent.action(Region)
    parent.separator()
    parent.action(CloseWindows, text='Close windows')
    parent.action(TileWindows, text='Tile windows')


class Series(Action):

    def enable(self, app):
        
        if not hasattr(app, 'folder'):
            return False
        data = app.folder.data()
        if data.empty:
            return False
        return data.checked.any()

    def run(self, app):

        for series in app.folder.series(checked=True):
            app.display(series)
      

class Image(Action):

    def enable(self, app):
        
        if not hasattr(app, 'folder'):
            return False
        data = app.folder.data()
        if data.empty: 
            return False
        return data.checked.any()

    def run(self, app):

        for image in app.folder.instances(checked = True):
            app.display(image)


class Region(Action):

    def enable(self, app):
        
        if app.__class__.__name__ != 'DicomWindows':
            return False
        data = app.folder.data()
        if data.empty: 
            return False
        return data.checked.any()

    def run(self, app):

        for series in app.folder.series(checked = True):

            viewer = SeriesViewerROI(series)
            viewer.dataWritten.connect(app.treeView.setFolder)
            app.addAsSubWindow(viewer, title=series.label())

class CloseWindows(Action):

    def enable(self, app):
        
        if app.__class__.__name__ != 'DicomWindows':
            return False
        return True

    def run(self, app):

        app.central.closeAllSubWindows()

class TileWindows(Action):

    def enable(self, app):
        
        if app.__class__.__name__ != 'DicomWindows':
            return False
        return True

    def run(self, app):

        app.central.tileSubWindows()

