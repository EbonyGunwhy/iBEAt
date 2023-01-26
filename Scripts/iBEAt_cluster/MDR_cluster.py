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
import mdreg.models.T2star
import mdreg.models.T2
import mdreg.models.T1
import mdreg.models.DWI_monoexponential
import mdreg.models.DTI
import mdreg.models.DCE_2CFM
import actions.autoaif
import dbdicom
import os
import gc
import matplotlib.pyplot as plt
from skimage.transform import rescale
import nibabel as nib # unnecessary - remove
import scipy

elastix_pars = os.path.join(os.path.join(os.path.dirname(__file__)).split("actions")[0], 'elastix')

def downsample_res_avg(im,newShape):
    print(len(im.shape))
    if len(im.shape)==4:
        original_width = im.shape[1]
        original_height = im.shape[0]
        width = newShape
        height = newShape
        resized_image = np.zeros(shape=(height, width, im.shape[2],im.shape[3]), dtype=np.uint16)
        #upsampled_image = np.zeros(shape=(original_height, original_width, im.shape[2],im.shape[3]), dtype=np.uint16)
        scale = int(im.shape[0]/newShape)

        for slice in range (0,im.shape[2]):
            im_slice = np.squeeze(im[:,:,slice])
            for dynamics in range (0,im.shape[3]):
                im_slice_dyn = np.squeeze(im_slice[:,:,dynamics])
                for i in range(0, original_height, scale):
                    for j in range(0, original_width, scale):
                        resized_image[int(i/scale), int(j/scale),slice,dynamics] = np.mean(im_slice_dyn[i:i + scale, j:j+scale], axis=(0,1))
    elif len(im.shape)==3:
        original_width = im.shape[1]
        original_height = im.shape[0]
        width = newShape
        height = newShape
        resized_image = np.zeros(shape=(height, width, im.shape[2]), dtype=np.uint16)
        #upsampled_image = np.zeros(shape=(original_height, original_width, im.shape[2],im.shape[3]), dtype=np.uint16)
        scale = int(im.shape[0]/newShape)

        for slice in range (0,im.shape[2]):
            im_slice = np.squeeze(im[:,:,slice])
            for i in range(0, original_height, scale):
                for j in range(0, original_width, scale):
                    resized_image[int(i/scale), int(j/scale),slice] = np.mean(im_slice[i:i + scale, j:j+scale], axis=(0,1))


                              
            # temp_up_image = rescale(np.squeeze(resized_image[:,:,slice,dynamics]), scale,anti_aliasing=False)
            #print(np.max(np.squeeze(resized_image[:,:,slice,dynamics])))
            #print(np.min(np.squeeze(resized_image[:,:,slice,dynamics])))
            #print(np.max(np.squeeze(temp_up_image)))
            #print(np.min(np.squeeze(temp_up_image)))
            # temp_up_image = temp_up_image * (np.max(np.squeeze(resized_image[:,:,slice,dynamics]))/np.max(np.squeeze(temp_up_image))) #* (np.max(resized_image) - np.min(resized_image)) + np.min(resized_image)            
            #print(np.max(np.squeeze(temp_up_image)))
            #print(np.min(np.squeeze(temp_up_image)))
            # upsampled_image[:, :,slice,dynamics] = temp_up_image
    
    #### VIZUALIZATION ####
    # Creating figure object
    # plt.figure()
    # plt.subplot(141)
    # plt.imshow(np.squeeze(im[:,:,0,0]),vmin=0,vmax=250)
    # plt.colorbar()
    # plt.subplot(142)
    # plt.imshow(np.squeeze(resized_image[:,:,0,0]),vmin=0,vmax=250)
    # plt.colorbar()
    # plt.subplot(143)
    # plt.imshow(np.squeeze(upsampled_image[:,:,0,0]),vmin=0,vmax=250)
    # plt.colorbar()
    # plt.subplot(144)
    # plt.imshow(np.divide(np.squeeze(im[:,:,0,0])-np.squeeze(upsampled_image[:,:,0,0]),np.squeeze(im[:,:,0,0]))*100,vmin=-10,vmax=10)
    # plt.colorbar()

    return resized_image

def zoom(input, zoom, **kwargs):
    """
    wrapper for scipy.ndimage.zoom.

    Parameters
    ----------
    input: dbdicom series

    Returns
    -------
    zoomed : dbdicom series
    """
    suffix = ' [Resize x ' + str(zoom) + ' ]'
    desc = input.instance().SeriesDescription
    zoomed = input.copy(SeriesDescription = desc + suffix)
    images = zoomed.instances()
    for i, image in enumerate(images):
        input.status.progress(i+1, len(images), 'Resizing ' + desc)
        image.read()
        array = image.array()
        array = scipy.ndimage.zoom(array, zoom, **kwargs)
        image.set_array(array)
        pixel_spacing = image.PixelSpacing
        image.PixelSpacing = [p/zoom for p in pixel_spacing]
        image.clear()
    input.status.hide()
    return zoomed

def MDRegT2star(series=None,study=None):

    series = zoom(series, 0.5)
    array, header = series.array(['SliceLocation', 'EchoTime'], pixels_first=True)

    signal_pars = 0
    signal_model = mdreg.models.T2star
    elastix_file = 'BSplines_T2star.txt'
    number_slices = array.shape[2]

    _mdr(series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='EchoTime',study=study)

def MDRegT1(series=None, study=None):

    series = zoom(series, 0.5)
    array, header = series.array(['SliceLocation', 'InversionTime'], pixels_first=True)
    
    signal_pars = 0
    signal_model = mdreg.models.T1
    elastix_file = 'BSplines_T1.txt'
    number_slices = array.shape[2]

    _mdr(series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='InversionTime', study=study)


def MDRegT2(series=None, study=None):
    """Perform MDR on all slices using a T2 mono-exp model"""
    
    series = zoom(series, 0.5)
    array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

    signal_pars = [0,30,40,50,60,70,80,90,100,110,120]
    signal_model = mdreg.models.T2
    elastix_file = 'BSplines_T2.txt'
    number_slices = array.shape[2]
    
    _mdr(series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='None', study=study)


def MDRegIVIM(series=None,study=None):
    """Perform MDR on all slices using a DWI mono-exp model"""

    series = zoom(series, 0.5)
    array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

    signal_pars = [0,10.000086, 19.99908294, 30.00085926, 50.00168544, 80.007135, 100.0008375, 199.9998135, 300.0027313, 600.0]
    signal_model = mdreg.models.DWI_monoexponential
    elastix_file = 'BSplines_IVIM.txt'

    number_slices = array.shape[2]
    _mdr(series, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='None',study=study)

def MDRegDTI(series=None,study=None):
    """Perform MDR on all slices using a DTI model"""

    series = zoom(series, 0.5)
    array, header = series.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

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

    array_off = np.reshape(array_off,np.shape(array_off)+(1,))
    array_on = np.reshape(array_on,np.shape(array_on)+(1,))
    array = np.concatenate((array_off, array_on), axis=3)
    header = np.concatenate((header_off, header_on), axis=1)
    
    array = np.reshape(array,np.shape(array)+(1,))

    signal_pars = []
    signal_model = mdreg.models.constant
    elastix_file = 'BSplines_MT.txt'

    number_slices = array.shape[2]
    _mdr(mt_on, number_slices, array, header, signal_model, elastix_file, signal_pars, sort_by='None',study=study)

def MDRegDCE(series=None, study=None):
    """Perform MDR on all slices using a DCE linear model"""

    series = zoom(series, 0.5)
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
            print("parameters = pars")
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


                        for i in range(header.shape[0]):
                            if (header[i,0,0]["ImageOrientationPatient"]== [1, 0, 0, 0, 1, 0]):
                                aortaslice = int(i + 1)
                                break
                            else:
                                aortaslice = 9

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
                print("sort by")
        #STORING RESULTS
        
        #print("Part -6  before set array: " + str(psutil.virtual_memory()[3]/1000000000))
        mdr.set_array(np.squeeze(array[:,:,slice,:,0]))     
        mdr.pixel_spacing = header[slice,0,0].PixelSpacing
        mdr.signal_model = signal_model
        mdr.read_elastix(os.path.join(elastix_pars, elastix_file))
        #mdr.pinned_message = 'MDR for slice ' + str(slice+1)
        
        #print("Part -5  before mdr.fit: " + str(psutil.virtual_memory()[3]/1000000000))
        mdr.fit()
        if len(np.shape(mdr.model_fit))==3:
            mdr.model_fit = np.reshape(mdr.model_fit,np.shape(mdr.model_fit)+(1,1,))

        if len(np.shape(mdr.coreg))==3:
            mdr.coreg = np.reshape(mdr.coreg,np.shape(mdr.coreg)+(1,1,))

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

def main(folder,filename_log):

    #filename_log = pathScan + datetime.datetime.now().strftime('%Y%m%d_%H%M_') + "MDRauto_LogFile.txt" #TODO FIND ANOTHER WAY TO GET A PATH

    current_study = folder.series()[0].parent()
    study = folder.series()[0].new_pibling(StudyDescription=current_study.StudyDescription + '_MDRresults')

    for series in folder.series():

        if series["SequenceName"] is not None:
            print(series['SeriesDescription'])

            if series['SeriesDescription'] == "T2star_map_kidneys_cor-oblique_mbh_magnitude":
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* motion correction has started")
                    #file.write("\n"+str(datetime.datetime.now())[0:19] + ": RAM Used (GB): " + str(psutil.virtual_memory()[3]/1000000000))
                    file.close()

                    MDRegT2star(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    #file.write("\n"+str(datetime.datetime.now())[0:19] + ": RAM Used (GB): " + str(psutil.virtual_memory()[3]/1000000000))
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "T1map_kidneys_cor-oblique_mbh_magnitude":
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 motion correction has started")
                    #file.write("\n"+str(datetime.datetime.now())[0:19] + ": RAM Used (GB): " + str(psutil.virtual_memory()[3]/1000000000))
                    file.close()

                    MDRegT1(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    #file.write("\n"+str(datetime.datetime.now())[0:19] + ": RAM Used (GB): " + str(psutil.virtual_memory()[3]/1000000000))
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "T2map_kidneys_cor-oblique_mbh_magnitude":
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 motion correction has started")
                    #file.write("\n"+str(datetime.datetime.now())[0:19] + ": RAM Used (GB): " + str(psutil.virtual_memory()[3]/1000000000))
                    file.close()

                    MDRegT2(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    #file.write("\n"+str(datetime.datetime.now())[0:19] + ": RAM Used (GB): " + str(psutil.virtual_memory()[3]/1000000000))
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 motion correction was NOT completed; error: "+str(e)) 
                    file.close()   

            elif series['SeriesDescription'] == "DTI_kidneys_cor-oblique_fb":
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI motion correction has started")
                    file.close()

                    MDRegDTI(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI motion correction was NOT completed; error: "+str(e)) 
                    file.close()
            
            elif series['SeriesDescription'] == "MT_OFF_kidneys_cor-oblique_bh":

                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT motion correction has started")
                    file.close()

                    MT_OFF = series
                    for i_2,series in enumerate (list_of_series):
                            if series['SeriesDescription'] == "MT_ON_kidneys_cor-oblique_bh":
                                MT_ON = series
                                break
                    MDRegMT([MT_OFF, MT_ON], study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "DCE_kidneys_cor-oblique_fb":
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


