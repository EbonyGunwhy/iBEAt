
import datetime
import time
from dbdicom import Folder
import numpy as np
import models.T2s_pixelwise_fit
import tqdm
from dipy.core.gradients import gradient_table
import dipy.reconst.dti as dti
from dipy.reconst.dti import fractional_anisotropy, color_fa
from tqdm import tqdm
import T1T2_MODELLING_cluster as T1T2

def T2s_Modelling(series=None, mask=None,export_ROI=False,slice=None,Fat_export=False):

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
        M0_map_series = series_T2s.new_sibling(SeriesDescription=M0_map_series)
        M0_map_series.set_array(M0map,np.squeeze(header[:,0]),pixels_first=True)

        fw_map_series = series_T2s.SeriesDescription + "_T2s_" + "fw_Map"
        fw_map_series = series_T2s.new_sibling(SeriesDescription=fw_map_series)
        fw_map_series.set_array(fwmap,np.squeeze(header[:,0]),pixels_first=True)

        T2s_map_series = series_T2s.SeriesDescription + "_T2s_" + "T2s_Map"
        T2s_map_series = series_T2s.new_sibling(SeriesDescription=T2s_map_series)
        T2s_map_series.set_array(T2smap,np.squeeze(header[:,0]),pixels_first=True)

        rsquare_map_series = series_T2s.SeriesDescription + "_T2s_" + "rsquare_Map"
        rsquare_map_series = series_T2s.new_sibling(SeriesDescription=rsquare_map_series)
        rsquare_map_series.set_array(rsquaremap,np.squeeze(header[:,0]),pixels_first=True)


def IVIM_Modelling(series=None, mask=None,export_ROI=False):

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
        S0_map_series = series_IVIM.new_sibling(SeriesDescription=S0_map_series)
        S0_map_series.set_array(np.squeeze(S0map),np.squeeze(header[:,0]),pixels_first=True)
        
        D_map_series = series_IVIM.SeriesDescription + "_IVIM_" + "D_Map"
        D_map_series = series_IVIM.new_sibling(SeriesDescription=D_map_series)
        D_map_series.set_array(np.squeeze(Dmap),np.squeeze(header[:,0]),pixels_first=True)

        rsquare_map_series = series_IVIM.SeriesDescription + "_IVIM_" + "rsquare_Map"
        rsquare_map_series = series_IVIM.new_sibling(SeriesDescription=rsquare_map_series)
        rsquare_map_series.set_array(np.squeeze(rsquaremap),np.squeeze(header[:,0]),pixels_first=True)

def DTI_Modelling(series=None, mask=None,export_ROI=False):

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
######FROM DIPY          

        FA_map_series = series_DTI.SeriesDescription + "_DTI_" + "FA_Map"
        FA_map_series = series_DTI.new_sibling(SeriesDescription=FA_map_series)
        FA_map_series.set_array(np.squeeze(FAmap),np.squeeze(header[:,0]),pixels_first=True)

def main(pathScan,filename_log):

    list_of_series = Folder(pathScan).open().series()

    current_study = list_of_series[0].parent
    study = list_of_series[0].new_pibling(StudyDescription=current_study.StudyDescription + '_ModellingResults')

    for i,series in enumerate(list_of_series):

        print(series['SeriesDescription'])

        if series['SeriesDescription'] == "T2star_map_kidneys_cor-oblique_mbh_magnitude_moco1":
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

        elif series['SeriesDescription'] == "T1map_kidneys_cor-oblique_mbh_magnitude":
            try:
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 and T2 mapping has started")
                file.close()

                T1 = series
                for i_2,series in enumerate (list_of_series):
                    if series['SeriesDescription'] == "T2map_kidneys_cor-oblique_mbh_magnitude":
                        T2 = series
                        break
                T1T2.main([T1,T2], study=study)

                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 and T2 mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                file.close()   

            except Exception as e: 
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 and T2 mapping was NOT completed; error: "+str(e)) 
                file.close()

        elif series['SeriesDescription'] == "IVIM_kidneys_cor-oblique_fb_moco1":
            try:
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM-ADC mapping has started")
                file.close()
                
                IVIM_Modelling(series, study=study)

                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM-ADC mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                file.close()   

            except Exception as e: 
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM-ADC mapping was NOT completed; error: "+str(e)) 
                file.close()

        elif series['SeriesDescription'] == "DTI_kidneys_cor-oblique_fb_moco1":
            try:
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI-FA mapping has started")
                file.close()
                
                DTI_Modelling(series, study=study)

                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI-FA mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                file.close()   

            except Exception as e: 
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI-FA mapping was NOT completed; error: "+str(e)) 
                file.close()

        elif series['SeriesDescription'] == "MT_OFF_kidneys_cor-oblique_bh_moco":
            pass

    Folder(pathScan).save()
