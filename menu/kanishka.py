import wezel
from dbdicom.wrappers import elastix


def iBEAT_dev(parent): 

    wezel.menu.folder.all(parent.menu('File'))
    wezel.menu.edit.all(parent.menu('Edit'))
    wezel.menu.view.all(parent.menu('View'))
    wezel.menu.filter.all(parent.menu('Filter'))
    wezel.menu.segment.all(parent.menu('Segment'))
    wezel.menu.transform.all(parent.menu('Transform'))
    coreg_menu(parent.menu('iBEAt-dev'))
    wezel.menu.about.all(parent.menu('About'))



def coreg_menu(parent): 

    parent.action(CoregisterToElastix, text='Coregister to (elastix)')

    



class CoregisterToElastix(wezel.Action): 

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):
        for series in app.selected('Series'):
            seriesList = series.parent().children()
            seriesLabels = [s.instance().SeriesDescription for s in seriesList]
            transform = ['Rigid', 'Affine', 'Freeform']
            metric = ["AdvancedMeanSquares", "NormalizedMutualInformation", "AdvancedMattesMutualInformation"]
            input = wezel.widgets.UserInput(
                {"label":"Coregister to which fixed series?", "type":"dropdownlist", "list": seriesLabels, 'value':0},
                {"label":"Transformation: ", "type":"dropdownlist", "list": transform, 'value':1},
                {"label":"Metric: ", "type":"dropdownlist", "list": metric, 'value':1},
                {"label":"Final grid spacing (mm)", "type":"float", 'value':25.0, 'minimum':1.0},
                title = "Please select coregistration settings")
            if input.cancel:
                return
            fixed = seriesList[input.values[0]["value"]]
            coregistered = elastix.coregister(series, fixed,
                transformation = transform[input.values[1]["value"]],
                metric = metric[input.values[2]["value"]],
                final_grid_spacing = input.values[3]["value"],
            )
            app.display(coregistered)
        app.refresh()


