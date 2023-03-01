import wezel
from wezel.widgets import TableDisplay
from dbdicom.wrappers import sklearn, skimage, scipy, dipy


def segment_menu(parent): 

    parent.action(WholeKidneyMask, text="Presegment whole kidneys")
    parent.action(RenalSinusFat, text="Renal sinus fat")


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



class RenalSinusFat(wezel.gui.Action):

    def run(self, app):
        all_series = app.database().series()
        features = app.selected('Series')

        series_labels = [s.label() for s in all_series]
        if features == []:
            selected = 0
            all_selected = []
        else:
            selected = all_series.index(features[0])
            all_selected = [all_series.index(f) for f in features]
        cancel, f = app.dialog.input(
            {"label":"Post-contrast DIXON: Fat image", "type":"dropdownlist", "list": series_labels, 'value':selected},
            {"label":"Whole-kidney regions", "type":"listview", "list": series_labels, 'value':all_selected},
            title = "Please select input for renal sinus fat processing")
        if cancel:
            return
        fat_image = all_series[f[0]['value']]
        kidneys = [all_series[i] for i in f[1]['value']]

        sf_series = []
        fat_image_masked, fat_mask = dipy.median_otsu(fat_image, median_radius=2, numpass=1)
        for kidney in kidneys:
            #   Calculate Convex Hull 3D
            kidney_hull = skimage.convex_hull_image_3d(kidney)
            #   Subtract Convex Hull - selected series
            sinus = scipy.image_calculator(kidney_hull, kidney, 'series 1 - series 2', integer=True)
            #   Remove bright spots 3D (IS THIS NECESSARY?)
            # sinus_open = skimage.opening_3d(sinus)
            #   Extract largest cluster (IS THIS NECESSARY?)
            # sinus_open_largest = scipy.extract_largest_cluster_3d(sinus_open)
            #   Multiply with fat otsu image to remove vessels, cysts, tissue (otsu)
            # sinus_fat = scipy.image_calculator(fat_mask, sinus_open_largest, 'series 1 * series 2', integer=True)
            sinus_fat = scipy.image_calculator(fat_mask, sinus, 'series 1 * series 2', integer=True)
            #   Extract largest cluster
            sinus_fat_largest = scipy.extract_largest_cluster_3d(sinus_fat)
            #   Rename
            sinus_fat_largest.SeriesDescription = kidney.instance().SeriesDescription + 'SF'
            #   Append
            sf_series.append(sinus_fat_largest)
            #   Display
            app.display(sinus_fat_largest, view='Surface')
            #   Remove intermediate steps
            kidney_hull.remove()
            sinus.remove()
            #sinus_open.remove()
            #sinus_open_largest.remove()
            sinus_fat.remove()
        fat_image_masked.remove()
        fat_mask.remove()
        #   Collect features & display
        df = skimage.volume_features(sf_series)
        app.addWidget(TableDisplay(df), 'ROI statistics')
        app.refresh()

