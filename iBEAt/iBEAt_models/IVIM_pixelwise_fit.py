import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.abspath(os.path.join('..', 'GitHub')))
import numpy as np
from numpy.core.numeric import NaN
from tqdm import tqdm
import time
import matplotlib.pyplot as plt
from iBEAt_Model_Library.single_pixel_forward_models import iBEAT_IVIM_FM


def main(IVIM_images_to_be_fitted, sequenceParam,GUI_object=None):
    """ main function that performs the T2* model-fit with shared parameters at single pixel level. 

    Args
    ----
    IVIM_images_to_be_fitted (numpy.ndarray): pixel value for time-series (i.e. at each T2 prep time) with shape [x,:]
    
    sequenceParam (list): [TE_list]


    Returns
    -------
    fitted_parameters: Map with signal model fitted parameters: 'S0', 'T1','T2','Flip Efficency','180 Efficency'.  
    """
    
    bvals_list = np.array(sequenceParam[0])
    #print(bvals_list)

    bvals_unique = bvals_list[0:10]
    inds = bvals_list.argsort()
    bvals_list = bvals_list[inds]
    #print(bvals_list)

    S0map = np.zeros((np.size(IVIM_images_to_be_fitted,0), np.size(IVIM_images_to_be_fitted,1), np.size(IVIM_images_to_be_fitted,2)))
    Dmap = np.zeros((np.size(IVIM_images_to_be_fitted,0), np.size(IVIM_images_to_be_fitted,1), np.size(IVIM_images_to_be_fitted,2)))
    Dsmap  = np.zeros((np.size(IVIM_images_to_be_fitted,0), np.size(IVIM_images_to_be_fitted,1), np.size(IVIM_images_to_be_fitted,2)))
    fmap  = np.zeros((np.size(IVIM_images_to_be_fitted,0), np.size(IVIM_images_to_be_fitted,1), np.size(IVIM_images_to_be_fitted,2)))
    rsquaremap  = np.zeros((np.size(IVIM_images_to_be_fitted,0), np.size(IVIM_images_to_be_fitted,1), np.size(IVIM_images_to_be_fitted,2)))
    IVIM_images_avg = np.zeros((np.size(IVIM_images_to_be_fitted,0), np.size(IVIM_images_to_be_fitted,1), len(bvals_unique)))

    #IVIM_images_to_be_fitted = IVIM_images_to_be_fitted[:,:,2:4,:]
    #IVIM_images_to_be_fitted = IVIM_images_to_be_fitted[172:292,311:397,:,:]
    

    for i in tqdm (range(np.shape(IVIM_images_to_be_fitted)[2]),desc="Slice Completed..."):

        tempImageSlice_IVIM = np.squeeze(IVIM_images_to_be_fitted[:,:,i,:])
        tempImageSlice_IVIM_sorted = np.squeeze(tempImageSlice_IVIM[:,:,[inds]])

        bval_counter=0
        for k in range(len(bvals_unique)):
            b_temp = bvals_unique[k]
            b_vals_temp = bvals_list[bvals_list == b_temp]
            
            #print(bval_counter)
            #print(bval_counter+len(b_vals_temp))
            #print(bvals_list[bval_counter:bval_counter+len(b_vals_temp)])

            IVIM_images_avg[:,:,k] = np.average(tempImageSlice_IVIM_sorted[:,:,bval_counter:bval_counter+len(b_vals_temp)],axis =2)
            
            bval_counter = bval_counter + len(b_vals_temp)
        
        for xi in tqdm(range((np.size(IVIM_images_avg,0))),desc="Rows Completed..."):

            if GUI_object:
                GUI_object.progress_bar(max=np.shape(IVIM_images_to_be_fitted)[0], index=xi+1)
                GUI_object.update_progress_bar(index=xi+1)
            
            for yi in range((np.size(IVIM_images_avg,1))):
                
                Kidney_pixel_IVIM = np.squeeze(np.array(IVIM_images_avg[xi,yi,:]))


                if (Kidney_pixel_IVIM[0]==0):
                    continue
                 
                #print(Kidney_pixel_IVIM)
                Kidney_pixel_IVIM = Kidney_pixel_IVIM/Kidney_pixel_IVIM[0]

                [Fit,Fitted_Parameters] = iBEAT_IVIM_FM.main(Kidney_pixel_IVIM, bvals_unique)

                residuals =  Kidney_pixel_IVIM - Fit
                ss_res = np.sum(residuals**2)
                ss_tot = np.sum((Kidney_pixel_IVIM-np.mean(Kidney_pixel_IVIM))**2)
                r_squared = 1 - (ss_res / ss_tot)
                if (np.isnan(r_squared)): r_squared = 0


                #print(r_squared)
                #print(Fitted_Parameters[0])
                #print(Fitted_Parameters[1])
                #print(Fitted_Parameters[2])
                #print(Fitted_Parameters[3])

                #plt.plot(bvals_unique,Kidney_pixel_IVIM,'.',label ="data")
                #plt.plot(bvals_unique,np.squeeze(Fit),'--', label="fitted")
                #plt.show()

                S0map[xi, yi,i] = Fitted_Parameters[0]
                Dmap[xi, yi,i] = Fitted_Parameters[1]*1000
                #Dsmap[xi,yi,i] = Fitted_Parameters[2]*1000
                #fmap[xi,yi,i] = Fitted_Parameters[3]
                rsquaremap[xi,yi,i] = r_squared
                #else:
                #S0map[xi, yi,i] = 0
                #Dmap[xi, yi,i] = 0
                #Dsmap[xi,yi,i] = 0
                #fmap[xi,yi,i] = 0
                #rsquaremap[xi,yi,i] = 0

    #fittedMaps = np.squeeze(S0map), np.squeeze(Dmap), np.squeeze(Dsmap),np.squeeze(fmap), np.squeeze(rsquaremap)
    fittedMaps = np.squeeze(S0map), np.squeeze(Dmap),np.squeeze(rsquaremap)
    #print('iupi')
    return fittedMaps