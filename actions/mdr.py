import os
import numpy as np

import weasel
import mdreg

# TODO: set fixed colour scales for exported parameter maps

elastix_pars = os.path.join(os.path.dirname(__file__), 'elastix')


class MDRegConst(weasel.Action):
    """Perform MDR on all slices using a constant model"""

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return True

    def run(self, app): 
        """
        Perform model-driven motion correction
        """
        series = app.get_selected(3)[0]
        array, dataset = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

        mdr = mdreg.MDReg()
        mdr.set_elastix(MaximumNumberOfIterations = 256)
        mdr.status = app.status

        for z in range(array.shape[2]):
            mdr.pinned_message = 'MDR for slice ' + str(z+1) + ' of ' + str(array.shape[2])
            mdr.pixel_spacing = dataset[z,0,0].PixelSpacing
            mdr.set_array(np.squeeze(array[:,:,z,:,0]))
            mdr.fit()  
            array[:,:,z,:,0] = mdr.coreg

        fit = series.new_cousin(SeriesDescription = series.SeriesDescription + '_coreg')
        fit.set_array(array, dataset, pixels_first=True)

        app.refresh() 


class MDRegT2star(weasel.Action):

    def run(self, app, series=None):

        if series is None:
            series = app.get_selected(3)[0]

        array, header = series.array(['SliceLocation', 'EchoTime'], pixels_first=True)
        slice = 2

        signal_pars = [hdr.EchoTime for hdr in header[slice,:,0]]
        signal_model = mdreg.models.T2star
        elastix_file = 'BSplines_T2.txt'

        _mdr(app, series, slice, array, header, signal_model, signal_pars, elastix_file)


class MDRegT2(weasel.Action):

    def run(self, app, series=None):

        if series is None:
            series = app.get_selected(3)[0]

        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
        slice = 2

        signal_pars = [0,30,40,50,60,70,80,90,100,110,120]
        signal_model = mdreg.models.T2
        elastix_file = 'BSplines_T2.txt'

        _mdr(app, series, slice, array, header, signal_model, signal_pars, elastix_file)


class MDRegT1(weasel.Action):

    def run(self, app, series=None):

        if series is None:
            series = app.get_selected(3)[0]

        array, header = series.array(['SliceLocation', 'InversionTime'], pixels_first=True)
        slice = 2

        signal_pars = [hdr.InversionTime for hdr in header[slice,:,0]]
        signal_model = mdreg.models.T1_simple
        elastix_file = 'BSplines_T1.txt'

        _mdr(app, series, slice, array, header, signal_model, signal_pars, elastix_file)


class MDRegDWI(weasel.Action):

    def run(self, app, series=None):

        if series is None:
            series = app.get_selected(3)[0]

        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
        slice = 15

        signal_pars = [0,10.000086, 19.99908294, 30.00085926, 50.00168544, 80.007135, 100.0008375, 199.9998135, 300.0027313, 600.0]
        signal_model = mdreg.models.DWI
        elastix_file = 'BSplines_IVIM.txt'

        _mdr(app, series, slice, array, header, signal_model, signal_pars, elastix_file)

class MDRegDTI(weasel.Action):

    def run(self, app, series=None):

        if series is None:
            series = app.get_selected(3)[0]

        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
        slice = 15

        b_values = [float(hdr[(0x19, 0x100c)]) for hdr in header[slice,:,0]]
        b_vectors = [hdr[(0x19, 0x100e)] for hdr in header[slice,:,0]]
        orientation = [hdr.ImageOrientationPatient for hdr in header[slice,:,0]] 

        signal_pars = [b_values, b_vectors, orientation]
        signal_model = mdreg.models.DTI
        elastix_file = 'BSplines_DTI.txt'

        _mdr(app, series, slice, array, header, signal_model, signal_pars, elastix_file)


class MDRegMT(weasel.Action):

    def run(self, app, series=None):

        if series is None:
            all_series = app.get_selected(3)
            for sery in all_series:
                if sery.SeriesDescription == 'MT_OFF_kidneys_cor-oblique_bh':
                    source = sery
                    mt_off = sery
                    break
            for sery in all_series:
                if sery.SeriesDescription == 'MT_ON_kidneys_cor-oblique_bh':
                    mt_on = sery
                    break
        else:
            source = series[0]
            mt_off = series[0]
            mt_on = series[1]

        array_off, header_off = mt_off.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
        array_on, header_on = mt_on.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

        array = np.concatenate((array_off, array_on), axis=3)
        header = np.concatenate((header_off, header_on), axis=1)

        slice = 7

        signal_pars = []
        signal_model = mdreg.models.constant
        elastix_file = 'BSplines_MT.txt'

        _mdr(app, source, slice, array, header, signal_model, signal_pars, elastix_file)


class MDRegDCE(weasel.Action):

    def run(self, app, series=None):

        if series is None:
            series = app.get_selected(3)[0]
        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

        slice = 4

        # GET AIF
        for sery in app.folder.series():
            if sery.SeriesDescription == 'DCE_ART':
                mask, _ = sery.array()
                loc = sery.SliceLocation
                break
        aif = []
        for z in range(array.shape[2]):
            if header[z,0,0].SliceLocation == loc:
                for t in range(array.shape[3]): #loop to average ROIs
                    tmask = np.squeeze(array[:,:,:,t,0]) * np.squeeze(mask)
                    aif.append = np.median(tmask[tmask!=0])
        time = [hdr.AcquisitionTime for hdr in header[slice,:,0]]
        time -= time[0]
               
        baseline = 15
        hematocrit = 0.45

        signal_pars = [aif, time, baseline, hematocrit]
        signal_model = mdreg.models.DCE_2CFM
        elastix_file = 'BSplines_DCE.txt'

        _mdr(app, series, slice, array, header, signal_model, signal_pars, elastix_file)


def _mdr(app, series, slice, array, header, signal_model, signal_pars, elastix_file):

    # PERFORM MDR
    mdr = mdreg.MDReg()
    mdr.set_array(np.squeeze(array[:,:,slice,:,0]))
    mdr.signal_parameters = signal_pars
    mdr.pixel_spacing = header[slice,0,0].PixelSpacing
    mdr.signal_model = signal_model
    mdr.read_elastix(os.path.join(elastix_pars, elastix_file))
    mdr.status = app.status
    mdr.pinned_message = 'MDR for slice ' + str(slice+1)
    mdr.fit()   
    
    # SAVE RESULTS AS DICOM
    parameters = signal_model.par()
    for p in range(len(parameters)):
        par = series.SeriesDescription + '_mdr_par_' + parameters[p]
        par = series.new_sibling(SeriesDescription=par)
        par.set_array(np.squeeze(mdr.par[...,p]), np.squeeze(header[slice,...]), pixels_first=True)
    fit = series.SeriesDescription + '_mdr_fit'
    fit = series.new_sibling(SeriesDescription=fit)
    fit.set_array(mdr.model_fit, np.squeeze(header[slice,...]), pixels_first=True)
    moco = series.SeriesDescription + '_mdr_moco'
    moco = series.new_sibling(SeriesDescription = moco)
    moco.set_array(mdr.coreg, np.squeeze(header[slice,...]), pixels_first=True)

    # DISPLAY RESULTS
    #app.display(moco) 
    app.refresh()   