"""
@author: Joao Periquito
iBEAt study T2* model-fit 
Siemens 3T PRISMA - Leeds (T2* sequence)
2021
"""
import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.abspath(os.path.join('..', 'GitHub')))

import numpy as np
from numpy.core.numeric import NaN
from tqdm import tqdm
import time

from iBEAt_Model_Library.single_pixel_forward_models import iBEAT_T2s_FM

#from iBEAt_Model_Library.single_pixel_forward_models import iBEAT_T2s_FM

def main(T2s_images_to_be_fitted, sequenceParam,GUI_object=None):
    """ main function that performs the T2* model-fit with shared parameters at single pixel level. 

    Args
    ----
    T2s_images_to_be_fitted (numpy.ndarray): pixel value for time-series (i.e. at each T2 prep time) with shape [x,:]
    
    sequenceParam (list): [TE_list]


    Returns
    -------
    fitted_parameters: Map with signal model fitted parameters: 'S0', 'T1','T2','Flip Efficency','180 Efficency'.  
    """
    TE_list = np.array(sequenceParam)

    T2smap = np.zeros((np.size(T2s_images_to_be_fitted,0), np.size(T2s_images_to_be_fitted,1), np.size(T2s_images_to_be_fitted,2)))
    M0map  = np.zeros((np.size(T2s_images_to_be_fitted,0), np.size(T2s_images_to_be_fitted,1), np.size(T2s_images_to_be_fitted,2)))
    fwmap  = np.zeros((np.size(T2s_images_to_be_fitted,0), np.size(T2s_images_to_be_fitted,1), np.size(T2s_images_to_be_fitted,2)))
    rsquaremap  = np.zeros((np.size(T2s_images_to_be_fitted,0), np.size(T2s_images_to_be_fitted,1), np.size(T2s_images_to_be_fitted,2)))

    #T2s_images_to_be_fitted = T2s_images_to_be_fitted[:,:,2:4,:]
    #T2s_images_to_be_fitted = T2s_images_to_be_fitted[:,:,2:3,:]

    for i in tqdm (range(np.shape(T2s_images_to_be_fitted)[2]),desc="Slice Completed..."):

        #if GUI_object:
            #GUI_object.progress_bar(max=np.shape(T2s_images_to_be_fitted)[2], index=i+1)

        tempImpageSlice_T2s = np.squeeze(T2s_images_to_be_fitted[:,:,i,:])

        for xi in tqdm(range((np.size(tempImpageSlice_T2s,0))),desc="Rows Completed..."):

            if GUI_object:
                GUI_object.progress_bar(max=np.size(tempImpageSlice_T2s,0), index=xi+1)
                GUI_object.update_progress_bar(index=xi+1)
            
            for yi in range((np.size(tempImpageSlice_T2s,1))):
                
                Kidney_pixel_T2s = np.squeeze(np.array(tempImpageSlice_T2s[xi,yi,:]))

                if Kidney_pixel_T2s[0] == 0:
                    continue

                [Fit,Fitted_Parameters] = iBEAT_T2s_FM.main(Kidney_pixel_T2s, TE_list)

                residuals = Kidney_pixel_T2s - Fit
                ss_res = np.sum(residuals**2)
                ss_tot = np.sum((Kidney_pixel_T2s-np.mean(Kidney_pixel_T2s))**2)
                r_squared = 1 - (ss_res / ss_tot)

                M0map[xi, yi,i] = Fitted_Parameters[0]
                fwmap[xi, yi,i] = Fitted_Parameters[1]
                T2smap[xi,yi,i] = Fitted_Parameters[2]
                rsquaremap[xi,yi,i] = r_squared


    fittedMaps = M0map, fwmap, T2smap, rsquaremap
    #print('iupi')
    return fittedMaps