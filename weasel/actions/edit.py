import weasel.dbdicom as db
from weasel.core import Action

def menu(parent):

    parent.action(Copy)
    parent.action(Delete)
    parent.action(Merge)
    parent.action(Group)


class Copy(Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return app.nr_selected(3) != 0

    def run(self, app):

        app.status.message("Copying..")
        series_list = app.get_selected(3)        
        for j, series in enumerate(series_list):
            app.status.progress(j, len(series_list), 'Copying..')
            series.copy()               
        app.status.hide()
        app.refresh()


class Delete(Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return app.nr_selected(3) != 0

    def run(self, app):

        app.status.message("Deleting..")
        series_list = app.get_selected(3)        
        for j, series in enumerate(series_list):
            app.status.progress(j, len(series_list), 'Deleting..')
            series.remove()               
        app.status.hide()
        app.refresh()


class Merge(Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return app.nr_selected(3) != 0

    def run(self, app): 

        app.status.message('Merging..')
        series_list = app.get_selected(3)
        db.merge(series_list, status=app.status)
        app.status.hide()
        app.refresh()


class Group(Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return app.nr_selected(3) != 0

    def run(self, app): 

        app.status.message('Grouping..')
        series_list = app.get_selected(3)
        study = series_list[0].new_pibling(SeriesDescription='Grouped series')
        nr = str(len(series_list))
        for j, series in enumerate(series_list):
            msg = 'Grouping series ' + series.label() + ' (' + str(j+1) + ' of ' + nr + ')'
            series.copy_to(study, message=msg)
        app.status.hide()
        app.refresh()