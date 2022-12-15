""" 
@author: Joao Periquito 
iBEAt MODELLING Scrpit
2022
Find iBEAt motion corrected pulse sequence name (MDR output: *_mdr_moco) and execute custom modelling for: DCE, DTI, T2*
(T1 & T2 modelling are done in the main due to parallelization requirements)
"""

import datetime
import time
from dbdicom import Folder
import numpy as np
import models.T2s_pixelwise_fit
import models.IVIM_pixelwise_fit
import tqdm
from dipy.core.gradients import gradient_table
import dipy.reconst.dti as dti
from dipy.reconst.dti import fractional_anisotropy, color_fa
import runpy
from scipy.integrate import trapz


def T2s_Modelling(series=None, mask=None,export_ROI=False,slice=None,Fat_export=False,study = None):

    series_T2s = series

    array, header = series.array(['SliceLocation', 'EchoTime'], pixels_first=True)

    TE_list = [hdr["EchoTime"] for hdr in (header[0,:,0])] 

    #Check if the data corresponds to the Siemens protocol (12 TEs)        
    if len(TE_list) == 12 and np.max(TE_list) < 50:

        #app.dialog.information("T2* Mapping has started")

        magnitude_array_T2s = array

        if slice is not None:
            magnitude_array_T2s_slice = magnitude_array_T2s[:,:,int(slice-1),:]
            magnitude_array_T2s = magnitude_array_T2s_slice

        if mask is not None:
            mask = np.transpose(mask)
            for i_slice in range (np.shape(magnitude_array_T2s)[2]):
                for i_w in range (np.shape(magnitude_array_T2s)[3]):
                    magnitude_array_T2s[:,:,i_slice,i_w]=magnitude_array_T2s[:,:,i_slice,i_w]*mask

        #T2* mapping input: T2*-weighted images (x,y,z,TE), echo times, wezel as optional argument to create progress bars in to wezel interface
        M0map, fwmap, T2smap, rsquaremap = models.T2s_pixelwise_fit.main(magnitude_array_T2s, TE_list)

        #wezel vizualitation of T2* mapping parameters: M0 map, Water Fraction map, T2* map,T2* r square (goodness of fit)
        M0_map_series = series_T2s.SeriesDescription + "_T2s_" + "M0_Map"
        M0_map_series = study.new_series(SeriesDescription=M0_map_series)
        M0_map_series.set_array(M0map,np.squeeze(header[:,0]),pixels_first=True)

        fw_map_series = series_T2s.SeriesDescription + "_T2s_" + "fw_Map"
        fw_map_series = study.new_series(SeriesDescription=fw_map_series)
        fw_map_series.set_array(fwmap,np.squeeze(header[:,0]),pixels_first=True)

        T2s_map_series = series_T2s.SeriesDescription + "_T2s_" + "T2s_Map"
        T2s_map_series = study.new_series(SeriesDescription=T2s_map_series)
        T2s_map_series.set_array(T2smap,np.squeeze(header[:,0]),pixels_first=True)

        rsquare_map_series = series_T2s.SeriesDescription + "_T2s_" + "rsquare_Map"
        rsquare_map_series = study.new_series(SeriesDescription=rsquare_map_series)
        rsquare_map_series.set_array(rsquaremap,np.squeeze(header[:,0]),pixels_first=True)

def T1T2_Modelling(series=None, mask=None,export_ROI=False, study=None):
        
        series_T1 = series[0]
        series_T2 = series[1]

        array_T1, header_T1 = series_T1.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
        array_T2, header_T2 = series_T2.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)

        header_T1 = np.squeeze(header_T1)
        header_T2 = np.squeeze(header_T2)

        TR = 4.6                            #in ms
        FA = header_T1[0,0]['FlipAngle']    #in degrees
        FA_rad = FA/360*(2*np.pi)           #convert to rads
        N_T1 = 66                           #number of k-space lines
        FA_Cat  = [(-FA/5)/360*(2*np.pi), (2*FA/5)/360*(2*np.pi), (-3*FA/5)/360*(2*np.pi), (4*FA/5)/360*(2*np.pi), (-5*FA/5)/360*(2*np.pi)] #cat module
        
        TE = [0,30,40,50,60,70,80,90,100,110,120]
        Tspoil = 1
        N_T2 = 72
        Trec = 463*2

        number_slices = np.shape(array_T1)[2]

        T1_S0_map = np.empty(np.shape(array_T1)[0:3])
        T1_map = np.empty(np.shape(array_T1)[0:3])
        FA_Eff_map = np.empty(np.shape(array_T1)[0:3])
        Ref_Eff_map = np.empty(np.shape(array_T1)[0:3])
        T2_S0_map = np.empty(np.shape(array_T1)[0:3])
        T2_map = np.empty(np.shape(array_T1)[0:3])
        T1_rsquare_map = np.empty(np.shape(array_T1)[0:3])
        T2_rsquare_map = np.empty(np.shape(array_T1)[0:3])

        for slice in tqdm(range(number_slices),desc="Slice Completed..."):
            
            TI_temp =  [float(hdr['InversionTime']) for hdr in header_T1[slice,:]]

            array_T1_temp = np.squeeze(array_T1[:,:,slice,:])
            array_T2_temp = np.squeeze(array_T2[:,:,slice,:])
            for xi in tqdm (range((np.size(array_T1_temp,0))),desc="Rows Completed..."):
                for yi in range((np.size(array_T1_temp,1))):
                    
                    Kidney_pixel_T1 = np.squeeze(np.array(array_T1_temp[xi,yi,:]))
                    Kidney_pixel_T2 = np.squeeze(np.array(array_T2_temp[xi,yi,:]))

                    try:

                        fit_T1, fitted_parameters_T1 = models.iBEAt_Model_Library.single_pixel_forward_models.iBEAT_T1_FM.main (Kidney_pixel_T1, TI_temp, [FA_rad, TR, N_T1,FA_Cat])
                                                                                                                

                        S0_T1,T1,FA_eff = fitted_parameters_T1

                        fit_T2, fitted_parameters_T2 = models.iBEAt_Model_Library.single_pixel_forward_models.iBEAT_T2_FM.main (Kidney_pixel_T2, TE,[T1,Tspoil,FA_rad,TR, N_T2,Trec,FA_eff])

                        S0_T2, T2, FA_eff_2 =  fitted_parameters_T2

                        T1_S0_map[xi,yi,slice] = S0_T1
                        T1_map[xi,yi,slice]     = T1
                        FA_Eff_map[xi,yi,slice] = FA_eff
                        T2_S0_map[xi,yi,slice] = S0_T2
                        T2_map[xi,yi,slice] = T2

                        residuals_T1 = Kidney_pixel_T1-np.squeeze(fit_T1) 
                        residuals_T2 = Kidney_pixel_T2-np.squeeze(fit_T2) 

                        #r squared calculation 
                        ss_res_T1 = np.sum(residuals_T1**2)
                        ss_res_T2 = np.sum(residuals_T2**2)

                        ss_tot_T1 = np.sum((Kidney_pixel_T1-np.mean(Kidney_pixel_T1))**2)
                        ss_tot_T2 = np.sum((Kidney_pixel_T2-np.mean(Kidney_pixel_T2))**2)

                        r_squared_T1 = 1 - (ss_res_T1 / ss_tot_T1)
                        r_squared_T2 = 1 - (ss_res_T2 / ss_tot_T2)

                        #replace possible nan (from division by 0: ss_res_T1 / ss_tot_T1) to 0
                        if (np.isnan(r_squared_T1)): r_squared_T1 = 0
                        if (np.isnan(r_squared_T2)): r_squared_T2 = 0
                        
                        T1_rsquare_map[xi,yi,slice] = r_squared_T1
                        T2_rsquare_map[xi,yi,slice] = r_squared_T2

                    except:

                        T1_S0_map[xi,yi,slice] = 0
                        T1_map[xi,yi,slice]     = 0
                        FA_Eff_map[xi,yi,slice] = 0
                        T2_S0_map[xi,yi,slice] = 0
                        T2_map[xi,yi,slice] = 0

                        T1_rsquare_map[xi,yi,slice] = 0
                        T2_rsquare_map[xi,yi,slice] = 0


        T1_S0_map_series = series_T1.SeriesDescription + "_T1_" + "S0_Map"
        T1_S0_map_series = study.new_series(SeriesDescription=T1_S0_map_series)
        T1_S0_map_series.set_array(np.squeeze(T1_S0_map),np.squeeze(header_T1[:,0]),pixels_first=True)
            
        T1_map_series = series_T1.SeriesDescription + "_T1_" + "T1_Map"
        T1_map_series = study.new_series(SeriesDescription=T1_map_series)
        T1_map_series.set_array(np.squeeze(T1_map),np.squeeze(header_T1[:,0]),pixels_first=True)

        FA_Eff_map_series = series_T1.SeriesDescription + "_T1_" + "FA_Eff_Map"
        FA_Eff_map_series = study.new_series(SeriesDescription=FA_Eff_map_series)
        FA_Eff_map_series.set_array(np.squeeze(FA_Eff_map),np.squeeze(header_T1[:,0]),pixels_first=True)

        T2_S0_map_series = series_T2.SeriesDescription + "_T2_" + "S0_Map"
        T2_S0_map_series = study.new_series(SeriesDescription=T2_S0_map_series)
        T2_S0_map_series.set_array(np.squeeze(T2_S0_map),np.squeeze(header_T2[:,0]),pixels_first=True)

        T2_map_series = series_T2.SeriesDescription + "_T2_" + "T2_Map"
        T2_map_series = study.new_series(SeriesDescription=T2_map_series)
        T2_map_series.set_array(np.squeeze(T2_map),np.squeeze(header_T2[:,0]),pixels_first=True)

        T1_rsquare_map_series = series_T1.SeriesDescription + "_T1_" + "rsquare_Map"
        T1_rsquare_map_series = study.new_series(SeriesDescription=T1_rsquare_map_series)
        T1_rsquare_map_series.set_array(np.squeeze(T1_rsquare_map),np.squeeze(header_T1[:,0]),pixels_first=True)

        T2_rsquare_map_series = series_T2.SeriesDescription + "_T2_" + "rsquare_Map"
        T2_rsquare_map_series = study.new_series(SeriesDescription=T2_rsquare_map_series)
        T2_rsquare_map_series.set_array(np.squeeze(T2_rsquare_map),np.squeeze(header_T2[:,0]),pixels_first=True)


# def T1T2_Modelling_with_Par(series=None, mask=None,export_ROI=False, study = None):

        #runpy.run_path("C://Users//md1jdsp//Documents//GitHub//iBEAt//Scripts//T1T2_ForwardModelling_wPara_standaloneScript//T1T2_alone_cluster.py", {}, "__main__")

def IVIM_Modelling(series=None, mask=None,export_ROI=False, study = None):

        series_IVIM = series

        array, header = series_IVIM.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
        b_vals = [0,10.000086, 19.99908294, 30.00085926, 50.00168544, 80.007135, 100.0008375, 199.9998135, 300.0027313, 600.0]

        pixel_array_IVIM = array

        if mask is not None:
                mask=np.transpose(mask)
                for i_slice in range (np.shape(pixel_array_IVIM)[2]):
                    for i_w in range (np.shape(pixel_array_IVIM)[3]):
                        pixel_array_IVIM[:,:,i_slice,i_w]=pixel_array_IVIM[:,:,i_slice,i_w]*mask

        S0map, Dmap,rsquaremap = models.IVIM_pixelwise_fit.main(pixel_array_IVIM,b_vals)

        S0_map_series = series_IVIM.SeriesDescription + "_IVIM_" + "S0_Map"
        S0_map_series = study.new_series(SeriesDescription=S0_map_series)
        S0_map_series.set_array(np.squeeze(S0map),np.squeeze(header[:,0]),pixels_first=True)
        
        D_map_series = series_IVIM.SeriesDescription + "_IVIM_" + "D_Map"
        D_map_series = study.new_series(SeriesDescription=D_map_series)
        D_map_series.set_array(np.squeeze(Dmap),np.squeeze(header[:,0]),pixels_first=True)

        rsquare_map_series = series_IVIM.SeriesDescription + "_IVIM_" + "rsquare_Map"
        rsquare_map_series = study.new_series(SeriesDescription=rsquare_map_series)
        rsquare_map_series.set_array(np.squeeze(rsquaremap),np.squeeze(header[:,0]),pixels_first=True)

def DTI_Modelling(series=None, mask=None,export_ROI=False, study = None):

    series_DTI = series

    array, header = series_DTI.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
    pixel_array_DTI = array
    header = np.squeeze(header)
    
    b_vals_check = [float(hdr[(0x19, 0x100c)]) for hdr in header[0,:]]
    b_vecs_check = [hdr[(0x19, 0x100e)] for hdr in header[0,:]]

    #Check if the data corresponds to the Siemens protocol (more than 1 unique b-value)        
    if len(b_vals_check) >= 1 and np.shape(b_vecs_check)[0] >=6:

######FROM DIPY
        gtab = gradient_table(np.squeeze(b_vals_check), np.squeeze(b_vecs_check))
        tenmodel = dti.TensorModel(gtab)
        tenfit = tenmodel.fit(np.squeeze(pixel_array_DTI))

        FAmap = fractional_anisotropy(tenfit.evals)
        MDmap = dti.mean_diffusivity(tenfit.evals)
######FROM DIPY          

        FA_map_series = series_DTI.SeriesDescription + "_DTI_" + "FA_Map"
        FA_map_series = study.new_series(SeriesDescription=FA_map_series)
        FA_map_series.set_array(np.squeeze(FAmap),np.squeeze(header[:,0]),pixels_first=True)

        MD_map_series = series_DTI.SeriesDescription + "_DTI_" + "MD_Map"
        MD_map_series = study.new_series(SeriesDescription=MD_map_series)
        MD_map_series.set_array(np.squeeze(MDmap),np.squeeze(header[:,0]),pixels_first=True)

def MTR_Modelling(series=None, mask=None, export_ROI=False, study=None):
        
        array_mt_moco, header_mt_moco = series.array(['SliceLocation', 'AcquisitionTime'],pixels_first=True)
        header_on = header_mt_moco[:,0,0]

        array_mt_off = np.squeeze(array_mt_moco[:,:,:,0])
        array_mt_on = np.squeeze(array_mt_moco[:,:,:,1])
        array_mtr = np.zeros((np.shape(array_mt_off)[0:3]))
        
        for s in range (np.shape(array_mt_off)[2]):
            temp_off_moco = np.squeeze(array_mt_off[:,:,s])
            temp_on_moco = np.squeeze(array_mt_on[:,:,s])

            array_mtr[:,:,s] = np.divide((temp_off_moco - temp_on_moco),temp_off_moco, out=np.zeros_like(temp_off_moco - temp_on_moco), where=temp_off_moco!=0) * 100
        
        study = series.parent
        mtr = series.SeriesDescription + '_MTR'
        mtr = study.new_series(SeriesDescription = mtr)
        mtr.set_array(array_mtr, np.squeeze(header_on), pixels_first=True)


def DCE_MAX_Modelling(series=None, mask=None,export_ROI=False, study=None):

    series_DCE = series

    array, header = series_DCE.array(['SliceLocation', 'AcquisitionTime'], pixels_first=True)
    
    header = np.squeeze(header)

    if np.shape(array)[-1] == 2:
        array = array[...,0]

    if np.shape(header)[-1] == 2:
        header = header[...,0:1]

    pixel_array_DCE = array
    number_slices = np.shape(pixel_array_DCE)[2]

    DCE_Max_map = np.empty(np.shape(pixel_array_DCE)[0:3])
    DCE_Area_map = np.empty(np.shape(pixel_array_DCE)[0:3])
    timeDCE = np.zeros(header.shape[1])

    for slice in range(number_slices):   
        for i in range(header.shape[1]):
            tempTime = header[slice,i]['AcquisitionTime']
            tempH = int(tempTime[0:2])
            tempM = int(tempTime[2:4])
            tempS = int(tempTime[4:6])
            tempRest = float("0." + tempTime[7:])
            timeDCE[i] = tempH*3600+tempM*60+tempS+tempRest
        timeDCE -=timeDCE[0]

        array_DCE_temp = np.squeeze(pixel_array_DCE[:,:,slice,:])

        for xi in range((np.size(array_DCE_temp,0))):
            for yi in range((np.size(array_DCE_temp,1))):

                
                Kidney_pixel_DCE = np.squeeze(np.array(array_DCE_temp[xi,yi,:]))
                DCE_Max_map[xi,yi,slice] = np.max(Kidney_pixel_DCE-np.mean(Kidney_pixel_DCE[0:11]))
                DCE_Area_map[xi,yi,slice] = trapz(Kidney_pixel_DCE,timeDCE)

    DCEMax_map_series = series_DCE.SeriesDescription + "_DCE_" + "Max_Map"
    DCEMax_map_series = study.new_series(SeriesDescription=DCEMax_map_series)
    DCEMax_map_series.set_array(np.squeeze(DCE_Max_map),np.squeeze(header[:,0]),pixels_first=True)

    DCEArea_map_series = series_DCE.SeriesDescription + "_DCE_" + "AUC_Map"
    DCEArea_map_series = study.new_series(SeriesDescription=DCEArea_map_series)
    DCEArea_map_series.set_array(np.squeeze(DCE_Area_map),np.squeeze(header[:,0]),pixels_first=True)

def main(pathScan,filename_log):

    list_of_series = Folder(pathScan).open().series()

    current_study = list_of_series[0].parent
    study = list_of_series[0].new_pibling(StudyDescription=current_study.StudyDescription + '_ModellingResults')

    for i,series in enumerate(list_of_series):

        if series["SequenceName"] is not None:

            #print(series['SeriesDescription'])

            if series['SeriesDescription'] == "T2star_map_kidneys_cor-oblique_mbh_magnitude_mdr_moco":
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* mapping has started")
                    file.close()

                    T2s_Modelling(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()   
                except Exception as e: 

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* mapping was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "DTI_kidneys_cor-oblique_fb_mdr_moco":
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI-FA & ADC mapping has started")
                    file.close()
                    
                    DTI_Modelling(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI-FA & ADC mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI-FA mapping was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "DCE_kidneys_cor-oblique_fb_mdr_moco":
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DCE-MAX mapping has started")
                    file.close()
                    
                    DCE_MAX_Modelling(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DCE-MAX mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DCE-MAX mapping was NOT completed; error: "+str(e)) 
                    file.close()

            elif series.SeriesDescription == 'MT_ON_kidneys_cor-oblique_bh_mdr_moco':
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MTR mapping has started")
                    file.close()
                    
                    MTR_Modelling(series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MTR mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MTR mapping was NOT completed; error: "+str(e)) 
                    file.close()

    Folder(pathScan).save()
