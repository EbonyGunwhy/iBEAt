import wezel
from dbdicom.wrappers import sklearn


def segment_menu(parent): 

    parent.action(WholeKidneyMask, text="Presegment whole kidneys")
    #parent.action(RenalSinusFatPreSegment, text="Pre-segment renal sinus fat")
    #parent.action(RenalSinusFatPostSegment, text="Post-segment renal sinus fat")


class WholeKidneyMask(wezel.gui.Action): 

    def run(self, app):
        all_series = app.database().series()
        series_labels = [s.label() for s in all_series]
        features = app.selected('Series')
        if features == []:
            selected = 0
        else:
            selected = all_series.index(features[0])
        cancel, f = app.dialog.input(
            {"label":"Post-contrast DIXON: Fat image", "type":"dropdownlist", "list": series_labels, 'value':selected},
            {"label":"Post-contrast DIXON: Opposed phase image", "type":"dropdownlist", "list": series_labels, 'value':selected},
            title = "Please select input for whole kidney preprocessing")
        if cancel:
            return
        features = [all_series[f[0]['value']], all_series[f[1]['value']]]
        clusters = sklearn.sequential_kmeans(features, n_clusters=2, multiple_series=True)
        app.display(clusters)
        app.refresh()



class RenalSinusFatPreSegment(wezel.gui.Action):
    # For each selected series (RK, LK)
    #   Calculate Convex Hull
    #   Subtract Convex Hull - selected series
    #   
    pass


class RenalSinusFatPostSegment(wezel.gui.Action):
    # For each selected series (RK, LK)
    # Multiply with fat image
    # Label in 3D
    # Split up in masks
    # Display surface
    pass