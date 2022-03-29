import os
import numpy as np

from weasel import Action
from mdreg import MDReg
from mdreg.models import (
    T2star, T2, T1_simple, DWI, DTI, DCE_2CFM, constant,
)

# TODO: set fixed colour scales for exported parameter maps

elastix_pars = os.path.join(os.path.dirname(__file__), 'elastix')


class MDRegT2star(Action):

    def run(weasel, series=None):

        if series is None:
            series = weasel.folder.series(checked=True)[0]

        array, header = series.array(['SliceLocation', 'EchoTime'], pixels_first=True)
        slice = 2

        signal_pars = [hdr.EchoTime for hdr in header[slice,:,0]]
        signal_model = T2star
        elastix_file = 'BSplines_T2.txt'

        _mdr(weasel, series, slice, array, header, signal_model, signal_pars, elastix_file)


class MDRegT2(Action):

    def run(weasel, series=None):

        if series is None:
            series = weasel.folder.series(checked=True)[0]

        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
        slice = 2

        signal_pars = [0,30,40,50,60,70,80,90,100,110,120]
        signal_model = T2
        elastix_file = 'BSplines_T2.txt'

        _mdr(weasel, series, slice, array, header, signal_model, signal_pars, elastix_file)


class MDRegT1(Action):

    def run(weasel, series=None):

        if series is None:
            series = weasel.folder.series(checked=True)[0]

        array, header = series.array(['SliceLocation', 'InversionTime'], pixels_first=True)
        slice = 2

        signal_pars = [hdr.InversionTime for hdr in header[slice,:,0]]
        signal_model = T1_simple
        elastix_file = 'BSplines_T1.txt'

        _mdr(weasel, series, slice, array, header, signal_model, signal_pars, elastix_file)


class MDRegDWI(Action):

    def run(weasel, series=None):

        if series is None:
            series = weasel.folder.series(checked=True)[0]

        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
        slice = 15

        signal_pars = [0,10.000086, 19.99908294, 30.00085926, 50.00168544, 80.007135, 100.0008375, 199.9998135, 300.0027313, 600.0]
        signal_model = DWI
        elastix_file = 'BSplines_IVIM.txt'

        _mdr(weasel, series, slice, array, header, signal_model, signal_pars, elastix_file)

class MDRegDTI(Action):

    def run(weasel, series=None):

        if series is None:
            series = weasel.folder.series(checked=True)[0]

        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
        slice = 15

        b_values = [float(hdr[(0x19, 0x100c)]) for hdr in header[slice,:,0]]
        b_vectors = [hdr[(0x19, 0x100e)] for hdr in header[slice,:,0]]
        orientation = [hdr.ImageOrientationPatient for hdr in header[slice,:,0]] 

        signal_pars = [b_values, b_vectors, orientation]
        signal_model = DTI
        elastix_file = 'BSplines_DTI.txt'

        _mdr(weasel, series, slice, array, header, signal_model, signal_pars, elastix_file)

class MDRegMT(Action):

    def run(weasel):

        all_series = weasel.folder.series()
        for sery in all_series:
            if sery.SeriesDescription == 'MT_OFF_kidneys_cor-oblique_bh':
                source = sery
                array_off, header_off = sery.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
                break
        for sery in all_series:
            if sery.SeriesDescription == 'MT_ON_kidneys_cor-oblique_bh':
                array_on, header_on = sery.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
                break
        array = np.concatenate((array_off, array_on), axis=3)
        header = np.concatenate((header_off, header_on), axis=1)

        slice = 7

        signal_pars = []
        signal_model = constant
        elastix_file = 'BSplines_MT.txt'

        _mdr(weasel, source, slice, array, header, signal_model, signal_pars, elastix_file)

class MDRegDCE(Action):

    def run(weasel, series=None):

        if series is None:
            series = weasel.folder.series(checked=True)[0]
        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

        slice = 4

        # GET AIF
        for sery in weasel.folder.series():
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
        signal_model = DCE_2CFM
        elastix_file = 'BSplines_DCE.txt'

        _mdr(weasel, series, slice, array, header, signal_model, signal_pars, elastix_file)


def _mdr(weasel, series, slice, array, header, signal_model, signal_pars, elastix_file):

    # PERFORM MDR
    mdr = MDReg()
    mdr.set_array(np.squeeze(array[:,:,slice,:,0]))
    mdr.signal_parameters = signal_pars
    mdr.pixel_spacing = header[slice,0,0].PixelSpacing
    mdr.signal_model = signal_model
    mdr.read_elastix(os.path.join(elastix_pars, elastix_file))
    mdr.set_elastix(MaximumNumberOfIterations = 256)
    mdr.precision = 1
    mdr.fit()   # Add status bar option like in dbdicom
    
    # SAVE RESULTS AS DICOM
    parameters = signal_model.par()
    for p in range(len(parameters)):
        par = series.new_sibling().set_array(mdr.par[...,p], np.squeeze(header[slice,...]))
        par.SeriesDescription = series.SeriesDescription + '_mdr_par_' + parameters[p]
    fit = series.new_sibling().set_array(mdr.model_fit)
    fit.SeriesDescription = series.SeriesDescription + '_mdr_fit'
    moco = series.new_sibling().set_array(mdr.coreg)
    moco.SeriesDescription = series.SeriesDescription + '_mdr_moco'

    # DISPLAY RESULTS
    weasel.display(moco) 
    weasel.refresh()   