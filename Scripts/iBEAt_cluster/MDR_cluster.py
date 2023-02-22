""" 
@author: Joao Periquito 
iBEAt MDR Scrpit
2022
Find iBEAt standard pulse sequence name  and execute MDR for: DCE, DTI, T1, T2, T2*, MT
"""
import psutil
import mdreg
import os
import datetime
import time
import numpy as np
import mdreg.models.T2star_parallel
import mdreg.models.T2_parallel
import mdreg.models.T1_parallel
import mdreg.models.DWI_monoexponential_parallel
import mdreg.models.DTI
import mdreg.models.DCE_2CFM
import actions.autoaif
import dbdicom as db
import os
import gc
import matplotlib.pyplot as plt
from skimage.transform import rescale
import nibabel as nib # unnecessary - remove
import scipy

elastix_pars = os.path.join(os.path.join(os.path.dirname(__file__)).split("actions")[0], 'elastix')

def zoom(array, header, zoom):
    """
    wrapper for scipy.ndimage.zoom.

    Parameters
    ----------
    input: dbdicom series

    Returns
    -------
    zoomed : dbdicom series
    """
    newDimX = int(np.shape(array)[0]*zoom)
    newDimY = int(np.shape(array)[1]*zoom)
    resized_array = np.zeros([newDimX, newDimY, array.shape[2], array.shape[3], array.shape[4]])
    
    for i in range (array.shape[2]):
        for j in range (array.shape[3]):
        
            pixel_spacing = header[i,j,:]['PixelSpacing']
            header[i,j,:]['PixelSpacing'] = [p/zoom for p in pixel_spacing]

            temp_array = np.squeeze(array[:,:,i,j,:])
            temp_array_resized = scipy.ndimage.zoom(temp_array, zoom)
            resized_array[:,:,i,j,0] = temp_array_resized

    return resized_array, header


def MDRegT2star(series=None,study=None):

    #series = zoom(series, 0.5)
    array, header = series.array(['SliceLocation', 'EchoTime'], pixels_first=True)

    signal_pars = 0
    signal_model = mdreg.models.T2star_parallel
    elastix_file = 'BSplines_T2star.txt'
    number_slices = array.shape[2]

    _mdr(series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='EchoTime',study=study)

def MDRegT1(series=None, study=None):

    if series.Manufacturer == 'SIEMENS':
        array, header = series.array(['SliceLocation', 'InversionTime'], pixels_first=True)

        signal_pars = 0
        signal_model = mdreg.models.T1_parallel
        elastix_file = 'BSplines_T1.txt'
        number_slices = array.shape[2]

        _mdr(series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='InversionTime', study=study)
    
    else:
        array, header = series.array(['SliceLocation',(0x2005, 0x1572)], pixels_first=True)

        signal_pars = 0
        signal_model = mdreg.models.T1_parallel
        elastix_file = 'BSplines_T1.txt'
        number_slices = array.shape[2]

        _mdr(series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by=(0x2005, 0x1572), study=study)




def MDRegT2(series=None, study=None):
    """Perform MDR on all slices using a T2 mono-exp model"""
    
    #series = zoom(series, 0.5)

    if series.Manufacturer == 'SIEMENS':
        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
        signal_pars = [0,30,40,50,60,70,80,90,100,110,120]
    else:
        array, header = series.array(['SliceLocation', 'EchoTime'], pixels_first=True)
        signal_pars = series.EchoTime

    signal_model = mdreg.models.T2_parallel
    elastix_file = 'BSplines_T2.txt'
    number_slices = array.shape[2]
    
    _mdr(series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='None', study=study)


def MDRegIVIM(series=None,study=None):
    """Perform MDR on all slices using a DWI mono-exp model"""

    #series = zoom(series, 0.5)
    array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

    signal_pars = [0,10.000086, 19.99908294, 30.00085926, 50.00168544, 80.007135, 100.0008375, 199.9998135, 300.0027313, 600.0]
    signal_model = mdreg.models.DWI_monoexponential_parallel
    elastix_file = 'BSplines_IVIM.txt'

    number_slices = array.shape[2]
    _mdr(series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='None',study=study)

def MDRegDTI(series=None,study=None):
    """Perform MDR on all slices using a DTI model"""

    if series.Manufacturer == 'SIEMENS':
        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
    else:
        array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
        array = np.transpose(array, (0, 1, 2, 4, 3))
        header = np.transpose(header, (0, 2, 1))

    print(array.shape)
    print(header.shape)

    signal_pars = 0
    signal_model = mdreg.models.DTI
    elastix_file = 'BSplines_DTI.txt'
    number_slices = array.shape[2]

    _mdr(series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='DTI',study=study)

def MDRegMT(series=None,study=None):
    """Perform MDR on all slices using a MT model"""

    mt_off =series[0]
    mt_on =series[1]

    array_off, header_off = mt_off.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
    array_on, header_on = mt_on.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

    #array_off = np.reshape(array_off,np.shape(array_off)+(1,))
    #array_on = np.reshape(array_on,np.shape(array_on)+(1,))
    array = np.concatenate((array_off, array_on), axis=3)
    header = np.concatenate((header_off, header_on), axis=1)
    
    #array = np.reshape(array,np.shape(array)+(1,))

    signal_pars = []
    signal_model = mdreg.models.constant
    elastix_file = 'BSplines_MT.txt'

    number_slices = array.shape[2]
    _mdr(mt_on, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='None',study=study)

def MDRegDCE(series=None, study=None):
    """Perform MDR on all slices using a DCE linear model"""

    #series = zoom(series, 0.5)
    array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

    signal_pars = 0
    signal_model = mdreg.models.DCE_2CFM
    elastix_file = 'BSplines_DCE.txt'

    number_slices = array.shape[2]
    _mdr(series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='DCE', study=study)

def _mdr(series, number_slices, array, header, signal_model, elastix_file, signal_pars,sort_by, study=None):
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
        #print("Part -8  before mdreg: " + str(psutil.virtual_memory()[3]/1000000000))
        mdr = mdreg.MDReg()
        #print("Part -7  after mdreg: " + str(psutil.virtual_memory()[3]/1000000000))

        if signal_pars!=0:                                                                          #if condition for hardcoded parameters e.g.: T2 "EchoTime"
            mdr.signal_parameters = signal_pars

        else:
            if sort_by == "DTI":                                                                    #extracting DTI relevant parameters from DICOM headers                                              
                        
                        if series.Manufacturer == 'SIEMENS':
                            b_values = [float(hdr[(0x19, 0x100c)]) for hdr in header[slice,:,0]]
                            b_vectors = [hdr[(0x19, 0x100e)] for hdr in header[slice,:,0]]
                            orientation = [hdr.ImageOrientationPatient for hdr in header[slice,:,0]]
                        else:
                            b_values = [float(hdr[(0x18, 0x9087)]) for hdr in header[slice,:,0]]
                            b_vectors = [hdr[(0x18, 0x9089)] for hdr in header[slice,:,0]]
                            orientation = [hdr.ImageOrientationPatient for hdr in header[slice,:,0]]
                        mdr.signal_parameters = [b_values, b_vectors, orientation]

            elif sort_by =="DCE" and signal_pars==0:                                                
                        
                        # GET AIF
                        cutRatio=0.25             #create a window around the center of the image where the aorta is
                        filter_kernel=(15,15)     #gaussian kernel for smoothing the image to destroy any noisy single high intensity filter
                        regGrow_threshold = 2     #threshold for the region growing algorithm

                        if series.Manufacturer == 'SIEMENS':
                            for i in range(header.shape[0]):
                                if (header[i,0,0]["ImageOrientationPatient"]== [1, 0, 0, 0, 1, 0]):
                                    aortaslice = int(i + 1)
                                    break
                                else:
                                    aortaslice = 9
                        else:
                            aortaslice = 1

                        aif = actions.autoaif.DCEautoAIF(array, header, series, aortaslice, cutRatio, filter_kernel, regGrow_threshold)

                        time = np.zeros(header.shape[1])
                        for i in range(header.shape[1]):
                            tempTime = header[slice,i,0]['AcquisitionTime']
                            tempH = int(tempTime[0:2])
                            tempM = int(tempTime[2:4])
                            tempS = int(tempTime[4:6])
                            tempRest = float("0." + tempTime[7:])
                            time[i] = tempH*3600+tempM*60+tempS+tempRest
                        time -=time[0]
               
                        baseline = 15
                        hematocrit = 0.45
                        signal_pars = [aif, time, baseline, hematocrit]
                        mdr.signal_parameters = signal_pars
                        print("DCE parameters were calculated ")

            else:
                mdr.signal_parameters = [hdr[sort_by] for hdr in (header[slice,:,0])]                #extracting relevant parameters from DICOM headers using the string sort_by
                print(mdr.signal_parameters)
                print("sort by")
        #STORING RESULTS
        
        #print("Part -6  before set array: " + str(psutil.virtual_memory()[3]/1000000000))
        mdr.set_array(array[:,:,slice,:,0])    
        mdr.pixel_spacing = header[slice,0,0].PixelSpacing
        mdr.signal_model = signal_model
        mdr.read_elastix(os.path.join(elastix_pars, elastix_file))
        #mdr.pinned_message = 'MDR for slice ' + str(slice+1)
        
        #print("Part -5  before mdr.fit: " + str(psutil.virtual_memory()[3]/1000000000))
        mdr.fit()

        model_fit[:,:,slice,:,0] = mdr.model_fit
        coreg[:,:,slice,:,0] = mdr.coreg
        pars[:,:,slice,:] = mdr.pars

   # array = [x,y,z,TE]
   # pars = [x,y,z,2]
   # model_fit = [x,y,z,TE]
   # coreg = [x,y,z,TE]
    if study is None:
        study = series.parent()
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

def main(folder,filename_log):

    current_study = folder.series()[0].parent()
    study = folder.series()[0].new_pibling(StudyDescription=current_study.StudyDescription + '_MDRresults')

    for series in folder.series():
        SeqName = series["SeriesDescription"]

        if SeqName is not None:
            print(SeqName)

            if SeqName == "T2star_map_kidneys_cor-oblique_mbh_magnitude":
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* motion correction has started")
                    #file.write("\n"+str(datetime.datetime.now())[0:19] + ": RAM Used (GB): " + str(psutil.virtual_memory()[3]/1000000000))
                    file.close()

                    #MDRegT2star(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    #file.write("\n"+str(datetime.datetime.now())[0:19] + ": RAM Used (GB): " + str(psutil.virtual_memory()[3]/1000000000))
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif SeqName == "T1map_kidneys_cor-oblique_mbh_magnitude":
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 motion correction has started")
                    #file.write("\n"+str(datetime.datetime.now())[0:19] + ": RAM Used (GB): " + str(psutil.virtual_memory()[3]/1000000000))
                    file.close()

                    #MDRegT1(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    #file.write("\n"+str(datetime.datetime.now())[0:19] + ": RAM Used (GB): " + str(psutil.virtual_memory()[3]/1000000000))
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif SeqName == "T2map_kidneys_cor-oblique_mbh_magnitude":
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 motion correction has started")
                    #file.write("\n"+str(datetime.datetime.now())[0:19] + ": RAM Used (GB): " + str(psutil.virtual_memory()[3]/1000000000))
                    file.close()

                    #MDRegT2(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    #file.write("\n"+str(datetime.datetime.now())[0:19] + ": RAM Used (GB): " + str(psutil.virtual_memory()[3]/1000000000))
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 motion correction was NOT completed; error: "+str(e)) 
                    file.close()   

            elif SeqName == "DTI_kidneys_cor-oblique_fb":
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI motion correction has started")
                    file.close()

                    #MDRegDTI(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI motion correction was NOT completed; error: "+str(e)) 
                    file.close()
            
            elif SeqName == "MT_OFF_kidneys_cor-oblique_bh":

                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT motion correction has started")
                    file.close()

                    MT_OFF = series
                    for series in folder.series():
                            if series['SeriesDescription'] == "MT_ON_kidneys_cor-oblique_bh":
                                MT_ON = series
                                break
                    #MDRegMT([MT_OFF, MT_ON], study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif SeqName == "DCE_kidneys_cor-oblique_fb":
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DCE motion correction has started")
                    file.close()

                    MDRegDCE(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DCE motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DCE motion correction was NOT completed; error: "+str(e)) 
                    file.close()

    folder.save()


