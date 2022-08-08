""" MDR for Siemens T1,T2,T2*,DWI,DTI,DCE,MT mapping sequences.

This program runs MDR (Model Driven Registration) for acquired Siemens 
MRI mapping data (e.g. T1, T2, T2*, DWI, DTI, DCE, and MT) and displays
the results:
    - Calculated parameters (e.g. S0 and T2 - for T2 mapping)
    - Fit model
    - Co-registered images
into wezel GUI and strores them into DICOM files (with the 
appropriated headers)

Main Steps (for each mapping sequence):

1. DICOMs with weighted MRI data and headers are imported from wezel GUI
2. Images and headers are sorted using DICOM headers: "slice location" and "acquisition time"
3. Important signal parameters are either hardcoded (e.g. T2, DWI) or imported via DICOM headers
4. "_mdr" function is called to apply MDR to all slices
5. _mdr results (parameters, fitmodel and coreg images) are stored into DICOM files (with headers) and displayed into wezel

This script is called everytime the user select a mapable dataset and presses one of the MDR buttons (Siemens) of the iBEAt-MDR menu
"""

import os
import numpy as np

import wezel
import mdreg
import mdreg.models.T2star_simple
import mdreg.models.T2_simple
import mdreg.models.T1_simple
import mdreg.models.DWI_simple
import mdreg.models.DTI
import mdreg.models.DCE_2CFM
import actions.reggrow as reg
import cv2
import matplotlib.pyplot as plt
import actions.autoaif




# TODO: set fixed colour scales for exported parameter maps

elastix_pars = os.path.join(os.path.join(os.path.dirname(__file__)).split("actions")[0], 'elastix')

class MDRegConst(wezel.Action):
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


class MDRegT2star(wezel.Action):
    """Perform MDR on all slices using a T2star mono-exp model"""
    
    def run(self, app, series=None,study=None):

        if series is None:
            series = app.get_selected(3)[0]

        array, header = series.array(['SliceLocation', 'EchoTime'], pixels_first=True)
        signal_pars = 0
        signal_model = mdreg.models.T2star_simple
        elastix_file = 'BSplines_T2star.txt'
        number_slices = array.shape[2]

        _mdr(app, series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='EchoTime',study=study)



class MDRegT2(wezel.Action):
    """Perform MDR on all slices using a T2 mono-exp model"""

    def run(self, app, series=None, study=None):

        if series is None:
            series = app.get_selected(3)[0]

        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

        signal_pars = [0,30,40,50,60,70,80,90,100,110,120]
        signal_model = mdreg.models.T2_simple
        elastix_file = 'BSplines_T2.txt'
        number_slices = array.shape[2]
        
        _mdr(app, series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='None', study=study)


class MDRegT1(wezel.Action):
    """Perform MDR on all slices using a T1 mono-exp model"""

    def run(self, app, series=None, study=None):

        if series is None:
            series = app.get_selected(3)[0]

        array, header = series.array(['SliceLocation', 'InversionTime'], pixels_first=True)

        signal_pars = 0
        signal_model = mdreg.models.T1_simple
        #signal_model = mdreg.models.constant
        elastix_file = 'BSplines_T1.txt'
        number_slices = array.shape[2]

        _mdr(app, series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='InversionTime', study=study)


class MDRegDWI(wezel.Action):
    """Perform MDR on all slices using a DWI mono-exp model"""

    def run(self, app, series=None,study=None):

        if series is None:
            series = app.get_selected(3)[0]

        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

        signal_pars = [0,10.000086, 19.99908294, 30.00085926, 50.00168544, 80.007135, 100.0008375, 199.9998135, 300.0027313, 600.0]
        signal_model = mdreg.models.DWI_simple
        elastix_file = 'BSplines_IVIM.txt'

        number_slices = array.shape[2]
        _mdr(app, series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='None',study=study)

class MDRegDTI(wezel.Action):
    """Perform MDR on all slices using a DTI model"""

    def run(self, app, series=None,study=None):

        if series is None:
            series = app.get_selected(3)[0]

        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

        signal_pars = 0
        signal_model = mdreg.models.DTI
        elastix_file = 'BSplines_DTI.txt'
        number_slices = array.shape[2]

        _mdr(app, series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='DTI',study=study)


class MDRegMT(wezel.Action):
    """Perform MDR on all slices using a MT model"""

    def run(self, app, series=None,study=None):

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

        #slice = 7

        signal_pars = []
        signal_model = mdreg.models.constant
        elastix_file = 'BSplines_MT.txt'

        number_slices = array.shape[2]
        _mdr(app, mt_on, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='None',study=study)

        #add MTR = ( MT_off - MT_on ) / MT_off * 100 then save 


class MDRegDCE(wezel.Action):
    """Perform MDR on all slices using a DCE linear model"""

    def run(self, app, series=None, study=None):

        if series is None:
            series = app.get_selected(3)[0]
        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

        signal_pars = 0
        signal_model = mdreg.models.DCE_2CFM
        elastix_file = 'BSplines_DCE.txt'

        number_slices = array.shape[2]
        _mdr(app, series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='DCE', study=study)


def _mdr(app, series, number_slices, array, header, signal_model, elastix_file, signal_pars,sort_by, study=None):
    """ MDR fit function.  

    Args:
    ----
    app             (wezel)
    series          (wezel series): contains the user selected series in wezel GUI
    number_slices   (numpy.1darray): number of total slices (third dimention of the parameter "array")
    array           (numpy.ndarray): DICOM data with shape [x-dim, y-dim, z-dim (slice), t-dim (time series)]
    header          list containing all DICOM headers  
    signal_model    python script with the model fit for the differents mapping techniques
    elastix_file    (.txt file): elaxtix text file: BSplines_*mapping technique*.txt 
    signal_pars     (numpy.ndarray): either contains an hardcoded parameter not visible in DICOM headers (e.g.: T2 - EchoTime or DWI - b-values), or is 0 triggers the extraction of the relevant mapping parameter from DICOM headers
    sort by         (string array): either specifies the needed variable in DICOM headers (e.g.: EchoTime, IversionTime) or triggers a specific pre-process step (e.g.: DTI, DCE) 


    Returns
    -------
    model_fit       (numpy.ndarray): signal model fit at all time-series with shape [x-dim, y-dim, z-dim (slice), t-dim (time series), parameter (e.g.: S0, T2)].
    par             (numpy.ndarray): signal model fit at all time-series with shape [x-dim, y-dim, z-dim (slice), t-dim (time series), parameter (e.g.: S0, T2)].
    moco            (numpy.ndarray): signal model fit at all time-series with shape [x-dim, y-dim, z-dim (slice), t-dim (time series), parameter (e.g.: S0, T2)].
    """

    # PERFORM MDR
    parameters = signal_model.pars()

    # PARAMETER VARIABLES INITIALIZATION
    model_fit = np.empty(array.shape)
    coreg = np.empty(array.shape)
    pars = np.empty(array.shape[:3] + (len(parameters),) )

    # LOOP THROUGH SLICES
    for slice in range(number_slices):

        mdr = mdreg.MDReg()

        if signal_pars!=0:                                                                          #if condition for hardcoded parameters e.g.: T2 "EchoTime"
            mdr.signal_parameters = signal_pars
        else:
            if sort_by == "DTI":                                                                    #extracting DTI relevant parameters from DICOM headers                                              
                        b_values = [float(hdr[(0x19, 0x100c)]) for hdr in header[slice,:,0]]
                        b_vectors = [hdr[(0x19, 0x100e)] for hdr in header[slice,:,0]]
                        orientation = [hdr.ImageOrientationPatient for hdr in header[slice,:,0]] 
                        mdr.signal_parameters = [b_values, b_vectors, orientation]
            elif sort_by =="DCE" and signal_pars==0:                                                
                        
                        # GET AIF
                        cutRatio=0.25             #create a window around the center of the image where the aorta is
                        filter_kernel=(15,15)     #gaussian kernel for smoothing the image to destroy any noisy single high intensity filter
                        regGrow_threshold = 2     #threshold for the region growing algorithm
                        aortaslice = 9

                        aif = actions.autoaif.DCEautoAIF.run(app, array, header, series, aortaslice, cutRatio, filter_kernel, regGrow_threshold)

                        time = [float(hdr.AcquisitionTime) for hdr in header[slice,:,0]]
                        time = np.array(time)
                        time -= time[0] 
                        #
                        # time = time[1:]
               
                        baseline = 15
                        hematocrit = 0.45
                        signal_pars = [aif, time, baseline, hematocrit]
                        mdr.signal_parameters = signal_pars

            else:
                mdr.signal_parameters = [hdr[sort_by] for hdr in (header[slice,:,0])]                #extracting relevant parameters from DICOM headers using the string sort_by
        
        #STORING RESULTS
        mdr.set_array(np.squeeze(array[:,:,slice,:,0]))     
        mdr.pixel_spacing = header[slice,0,0].PixelSpacing
        mdr.signal_model = signal_model
        mdr.read_elastix(os.path.join(elastix_pars, elastix_file))
        mdr.status = app.status
        mdr.pinned_message = 'MDR for slice ' + str(slice+1)
        mdr.fit()
        
        model_fit[:,:,slice,:,0] = mdr.model_fit
        coreg[:,:,slice,:,0] = mdr.coreg
        pars[:,:,slice,:] = mdr.pars


   # array = [x,y,z,TE]
   # pars = [x,y,z,2]
   # model_fit = [x,y,z,TE]
   # coreg = [x,y,z,TE]
    if study is None:
        study = series.parent
    #EXPORT RESULTS TO wezel GUI USING DICOM
    for p in range(len(parameters)):
        par = series.SeriesDescription + '_mdr_par_' + parameters[p]
        par = study.new_series(SeriesDescription=par)
        #par = series.new_sibling(SeriesDescription=par)
        par.set_array(np.squeeze(pars[...,p]), np.squeeze(header[:,0]), pixels_first=True)
    fit = series.SeriesDescription + '_mdr_fit'
    fit = study.new_series(SeriesDescription=fit)
    fit.set_array(model_fit, np.squeeze(header[:,:]), pixels_first=True)
    moco = series.SeriesDescription + '_mdr_moco'
    moco = study.new_series(SeriesDescription = moco)
    moco.set_array(coreg, np.squeeze(header[:,:]), pixels_first=True)

    # DISPLAY RESULTS
    #app.display(moco) 
    app.refresh()   