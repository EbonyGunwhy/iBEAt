import wezel
from dbdicom.wrappers import elastix
from wrappers import mdreg
import dbdicom as db


# def iBEAT_dev(parent): 

#     wezel.menu.folder.all(parent.menu('File'))
#     wezel.menu.edit.all(parent.menu('Edit'))
#     wezel.menu.view.all(parent.menu('View'))
#     wezel.menu.filter.all(parent.menu('Filter'))
#     wezel.menu.segment.all(parent.menu('Segment'))
#     wezel.menu.transform.all(parent.menu('Transform'))
#     coreg_menu(parent.menu('iBEAt-dev'))

#     wezel.menu.about.all(parent.menu('About'))

def coreg_menu(parent): 

    parent.action(CoregisterToElastix, text="Coregister to (elastix)")
    parent.action(DTIModelFit, text="DTI model fit")
    parent.action(DTIMDReg, text="DTI MDReg")
    parent.action(T1ModelFit, text="T1 model fit")
    parent.action(T2ModelFit, text="T2 model fit")
    parent.action(T2starModelFit, text="T2star model fit")
    parent.action(IVIMModelFit, text="IVIM model fit")
    parent.action(MTModelFit, text="MT model fit") # TBC multi-series selection
    parent.action(DCEModelFit, text="DCE model fit")
    
class CoregisterToElastix(wezel.gui.Action): 

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):
        # Get input parameters including target for coregistration
        for series in app.selected('Series'):
            seriesList = series.parent().parent().series()
            seriesLabels = [s.label() for s in seriesList]
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

        # Loop over selected sources and perform coregistration
        fixed = seriesList[input.values[0]["value"]]
        for source in app.selected('Series'):
            coregistered = elastix.coregister(source, fixed,
                transformation = transform[input.values[1]["value"]],
                metric = metric[input.values[2]["value"]],
                final_grid_spacing = input.values[3]["value"],
            )
            app.display(coregistered)
        app.refresh()

class DTIModelFit(wezel.gui.Action): 

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):
        # Get input parameters including target for coregistration
        for series in app.selected('Series'):
            fit, par = mdreg.fit_DTI(series)
            app.display(fit)
            for p in par:
                app.display(p)
        app.refresh()

class T1ModelFit(wezel.gui.Action): 

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):
        # Get input parameters including target for coregistration
        for series in app.selected('Series'):
            fit, par = mdreg.fit_T1(series)
            app.display(fit)
            for p in par:
                app.display(p)
        app.refresh()

class T2ModelFit(wezel.gui.Action): 

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):
        # Get input parameters including target for coregistration
        for series in app.selected('Series'):
            fit, par = mdreg.fit_T2(series)
            app.display(fit)
            for p in par:
                app.display(p)
        app.refresh()

class T2starModelFit(wezel.gui.Action): 

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):
        # Get input parameters including target for coregistration
        for series in app.selected('Series'):
            fit, par = mdreg.fit_T2star(series)
            app.display(fit)
            for p in par:
                app.display(p)
        app.refresh()

class IVIMModelFit(wezel.gui.Action): 

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):
        # Get input parameters including target for coregistration
        for series in app.selected('Series'):
            fit, par = mdreg.fit_IVIM(series)
            app.display(fit)
            for p in par:
                app.display(p)
        app.refresh()

class DTIMDReg(wezel.gui.Action): 

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):
        # Get input parameters including target for coregistration
        for series in app.selected('Series'):
            mdr, fit, par = mdreg.process_DTI(series)
            app.display(mdr)
            app.display(fit)
            for p in par:
                app.display(p)
        app.refresh()

class MTModelFit(wezel.gui.Action): #TBC MULTI-SERIES SELECTION

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):
        # Get input parameters including target for coregistration
        for series in app.selected('Series'):
            fit, par = mdreg.fit_MT(series)
            app.display(fit)
            for p in par:
                app.display(p)
        app.refresh()

class DCEModelFit(wezel.gui.Action): 

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):
        # Get input parameters including target for coregistration
        for series in app.selected('Series'):
            fit, par = mdreg.fit_DCE(series)
            app.display(fit)
            for p in par:
                app.display(p)
        app.refresh()