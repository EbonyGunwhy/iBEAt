import os
import numpy as np
import weasel

# These attributes are used frequently in iBEAt.
# They are loaded up front to avoid rereading 
# the folder every time they are needed.
attributes = [
    'SliceLocation', 'AcquisitionTime', 
    'FlipAngle', 'EchoTime', 'InversionTime',   
    'DiffusionBValue',                          
]


class Open(weasel.Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return True

    def run(self, app):
        """
        Open a DICOM folder and update display.
        """

        app.status.message("Opening DICOM folder..")
        path = app.dialog.directory("Select a DICOM folder")
        if path == '':
            app.status.message('') 
            return
        app.status.cursorToHourglass()
        app.close()
        app.folder.set_attributes(attributes, scan=False)
        app.open(path)
        app.status.cursorToNormal()


class OpenSubFolders(weasel.Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return True

    def run(self, app):
        """
        Open a DICOM folder and update display.
        """
        app.status.message("Opening DICOM folder..")
        path = app.dialog.directory("Select the top folder..")
        if path == '':
            app.status.message('') 
            return
        subfolders = next(os.walk(path))[1]
        subfolders = [os.path.join(path, f) for f in subfolders]
        app.close()
        app.status.cursorToHourglass()
        app.folder.set_attributes(attributes, scan=False)
        for i, path in enumerate(subfolders):
            msg = 'Reading folder ' + str(i+1) + ' of ' + str(len(subfolders))
            app.folder.open(path, message=msg)
            app.folder.save()
        app.status.cursorToNormal()
        app.display(app.folder)


class RegionDraw(weasel.Action):

    def enable(self, app):
        
        if app.__class__.__name__ != 'Windows':
            return False
        return app.nr_selected(3) != 0

    def run(self, app):

        for series in app.get_selected(3):

            viewer = weasel.widgets.SeriesViewerROI(series, dimensions=attributes + ['StudyDate'])
            viewer.dataWritten.connect(app.treeView.setFolder)
            app.addAsSubWindow(viewer, title=series.label())


class FourDimArrayDisplay(weasel.Action):

    def enable(self, app):
        return app.nr_selected(3) != 0

    def run(self, app):
        series = app.get_selected(3)[0]
        array = series.load_npy()
        no_array = array is None
        if no_array:
            array, _ = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
            array = np.squeeze(array[...,0])
        if array.ndim != 4:
            app.dialog.information("Please select a 4D array for this viewer")
            return
        viewer = weasel.widgets.FourDimViewer(app.status, array)
        app.addAsSubWindow(viewer, title=series.label())
        app.status.message('Saving array for rapid access..')
        if no_array:
            series.save_npy(array=array)
        app.status.message('')


class TimeMIP(weasel.Action):
    """Previously known as DCE_create_AIF_button"""

    def run(self, app, series=None):

        if series is None:
            series = app.get_selected(3)[0]

        array, header = series.array(['SliceLocation', 'AcquisitionTime'])

        max = np.amax(array, axis=1)
        hdr = np.squeeze(header[:,0,:])

        mip = series.SeriesDescription + '_time_mip'
        mip = series.new_sibling(SeriesDescription = mip)
        mip.set_array(max, hdr)

        app.refresh() 