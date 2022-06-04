import os
import numpy as np

import mdreg.mdreg as mdreg
from mdreg.mdreg.models import constant

import weasel.dbdicom as db
from weasel.core import Action
import weasel.actions as actions
from weasel.wewidgets import SeriesViewerROI, FourDimViewer

#from iBEAt.xnat import Upload, Download
#from iBEAt.rename import Leeds
#import iBEAt.mdr as mdr

def menu(parent): 

    menu = parent.menu('File')
    menu.action(Open, shortcut='Ctrl+O')
    menu.action(actions.folder.Read)
    menu.action(actions.folder.Save, shortcut='Ctrl+S')
    menu.action(actions.folder.Restore, shortcut='Ctrl+R')
    menu.action(actions.folder.Close, shortcut='Ctrl+C')

    actions.edit.menu(parent.menu('Edit'))

    menu = parent.menu('View')
    menu.action(actions.view.Series)
    menu.action(Region, text='Draw ROI')
    menu.action(FourDimArrayDisplay, text='4D Array')
    menu.separator()
    menu.action(actions.view.CloseWindows, text='Close windows')
    menu.action(actions.view.TileWindows, text='Tile windows')

    menu = parent.menu('TRISTAN lab')
    #menu.action(RenameSeries, text='Rename series..')
    menu.action(OpenSubFolders, text='Read subfolders')
    menu.separator()
    menu.action(MergeDynamics, text='Merge all FA 15 dynamics')
    menu.action(MDRegDynamics, text='Motion-correct dynamics')
    

    menu = parent.menu('iBEAt pilot')
    #menu.action(Download, text='Download data from XNAT') # function download
    #menu.action(Leeds, text='Rename DICOMs (Siemens) iBEAt')
    menu.separator()
    #menu.action(mdr.MDRegT2star, text='T2* MDR (Siemens)')
    #menu.action(mdr.MDRegT2, text='T2 MDR (Siemens)')
    #menu.action(mdr.MDRegT1, text='T1 MDR (Siemens)')
    #menu.action(mdr.MDRegDWI, text='IVIM MDR (Siemens)')
    #menu.action(mdr.MDRegDTI, text='DTI MDR (Siemens)')
    #menu.action(mdr.MDRegDCE, text='DCE MDR (Siemens)')
    menu.action(MDR_iBEAt_MT_Button, text='MT MDR (Siemens)')
    menu.separator()
    menu.action(MDR_allSeries_iBEAt_Button, text='MDR ALL SERIES (Siemens) iBEAt')
    menu.action(MDR_allSeries_iBEAt_Button_NO_importing, text = 'MDR ALL SERIES (Siemens) iBEAt (No Import from XNAT)')
    menu.separator()
    menu.action(iBEAt_SiemensT1T2MapButton, text='Joint T1 & T2 Mapping (Siemens)')
    menu.action(iBEAt_SiemensT2sMapButton, text='T2* Mapping (Siemens)')
    menu.action(iBEAt_SiemensIVIMButton, text='IVIM: ADC Mapping (Siemens)')
    menu.action(iBEAt_SiemensDTIButton, text='DTI: FA Mapping (Siemens)')
    menu.separator()
    #menu.action(Upload, text = 'Upload results to XNAT') # function upload

    actions.about.menu(parent.menu('About'))


# These attributes are used frequently in iBEAt.
# They are loaded up front to avoid rereading 
# the folder every time they are needed.
attributes = [
    'SliceLocation', 'AcquisitionTime', 
    'FlipAngle', 'EchoTime', 'InversionTime',   
    'DiffusionBValue',                          
]


class Open(Action):

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


class OpenSubFolders(Action):

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


class MergeDynamics(Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return True

    def run(self, app): 
        """
        Merge the dynamics with FA 15 of all studies in the database.

        TODO: include merge of VFA data for T1-mapping
        """

        # Find all series with the correct SeriesDescriptions
        studies = app.folder.studies()
        desc = ['fl3d_fast_fb_fa15_W', 'fl3d_fast_fb_fa15_dynamic_W']
        dyn_series = db.find_series(studies, SeriesDescription=desc)
        sorted_series = []
        for i, series in enumerate(dyn_series):
            app.status.progress(i+1, len(dyn_series), 'Sorting dynamics..')
            sorted = series.dataset(['SliceLocation', 'AcquisitionTime'], status=False)
            sorted_series.append(sorted)
        
        # Create a new study & series to merge them in
        merged = dyn_series[0].new_cousin(
            StudyDescripton = 'list of merged series',
            SeriesDescription = 'fl3d_fast_fb_fa15_W_merged')

        # Merge with overwriting slice locations
        z_indices = range(sorted_series[0].shape[0])
        cnt = 1
        cntmax = len(sorted_series) * len(z_indices)
        for i, series in enumerate(sorted_series):
            for z in z_indices:
                app.status.progress(cnt, cntmax, 'Merging dynamics..')
                dynamics = np.squeeze(series[z,:,0]).tolist()
                db.set_value(dynamics, 
                    SliceLocation = z, 
                    PatientID = merged.UID[0],
                    StudyInstanceUID = merged.UID[1],
                    SeriesInstanceUID = merged.UID[2])
                cnt += 1
        app.refresh()

class MDRegDynamics(Action):

    def enable(self, weasel):

        if not hasattr(weasel, 'folder'):
            return False
        return True

    def run(self, weasel): 
        """
        Perform model-driven motion correction
        """
        series = weasel.get_selected(3)[0]
        array, dataset = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

    #    mdr = mdreg.MDReg()
    #    mdr.signal_parameters = []
    #    mdr.signal_model = constant
    #    #mdr.read_elastix(os.path.join(elastix_pars, elastix_file))
    #    #mdr.set_elastix(MaximumNumberOfIterations = 256)
    #    #mdr.precision = 1
    #    for z in range(array.shape[2]):
    #        tmp = np.squeeze(array[:,:,z,:,0])
    #        array[:,:,z,:,0] = tmp[:]
            #mdr.pixel_spacing = dataset[z,0,0].PixelSpacing
            #mdr.set_array(np.squeeze(array[:,:,z,:,0]))
            ##mdr.fit()   # Add status bar option like in dbdicom
            #mdr.fit_signal()
            #array[:,:,z,:,0] = mdr.model_fit[:]

    #    array[:,:,slice,:,0] = mdr.coreg
        fit = series.new_cousin(SeriesDescription = series.SeriesDescription + '_coreg')
        fit.set_array(array, dataset, pixels_first=True)

        #TO REPLACE BY:
        #xarray = db.array(series, sortby=['SliceLocation', 'AcquisitionTime'], pixels_first=True)
        #perform mdreg on dbarray.tonumpy()
        #fit = series.new_sibling(SeriesDescription = series.SeriesDescription + '_array')
        #fit.write_array(xarray, pixels_first=True)

        weasel.refresh() 

class RenameSeries(Action):

    def enable(self, app):
        if not hasattr(app, 'folder'):
            return False
        return app.nr_selected(3) != 0

    def run(self, app): 
        series_list = app.get_selected(3)
        for s in series_list:
            desc = s.SeriesDescription
            app.status.message('Renaming series ' + desc)
            db.set_value(s.instances(), SeriesDescription=desc+'_new_name')
        app.status.hide()
        app.refresh()


class Region(Action):

    def enable(self, app):
        
        if app.__class__.__name__ != 'DicomWindows':
            return False
        return app.nr_selected(3) != 0

    def run(self, app):

        for series in app.get_selected(3):

            viewer = SeriesViewerROI(series, dimensions=attributes + ['StudyDate'])
            viewer.dataWritten.connect(app.treeView.setFolder)
            app.addAsSubWindow(viewer, title=series.label())


class FourDimArrayDisplay(Action):

    def enable(self, weasel):
        return weasel.nr_selected(3) != 0

    def run(self, weasel):
        series = weasel.get_selected(3)[0]
        array = series.load_npy()
        no_array = array is None
        if no_array:
            array, _ = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
            array = np.squeeze(array[...,0])
        if array.ndim != 4:
            weasel.dialog.information("Please select a 4D array for this viewer")
            return
        viewer = FourDimViewer(weasel.status, array)
        weasel.addAsSubWindow(viewer, title=series.label())
        weasel.status.message('Saving array for rapid access..')
        if no_array:
            series.save_npy(array=array)
        weasel.status.message('')


class MDR_iBEAt_MT_Button(Action):
    pass

class MDR_allSeries_iBEAt_Button(Action):
    pass

class MDR_allSeries_iBEAt_Button_NO_importing(Action):
    pass

class iBEAt_SiemensT1T2MapButton(Action):
    pass

class iBEAt_SiemensT2sMapButton(Action):
    pass

class iBEAt_SiemensIVIMButton(Action):
    pass

class iBEAt_SiemensDTIButton(Action):
    pass



