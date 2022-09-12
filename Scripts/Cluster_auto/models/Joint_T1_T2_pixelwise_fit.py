"""
@author: Joao Periquito
iBEAt study T1 & T2 joint model-fit 
Siemens 3T PRISMA - Leeds (T1 & T2 sequence)
2021
"""
import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.abspath(os.path.join('..', 'GitHub')))
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from tqdm import tqdm

from iBEAt_Model_Library.single_pixel_forward_models import iBEAT_T1_FM, iBEAT_T2_FM 

global x1
global x2

#T1 Fit Model
def mod1(TI,Eff,M_eq, T1,FA_Eff,T2): # not all parameters are used here
    """ mod1 is T1 Fit Model used for joint T1 & T2 fit
    
    TI: list of inversion times
    Eff: 180 Ref Pulse efficency
    M_eq: equilibrim magnetization state
    T1: T1 value
    FA_Eff: Flip Angle Efficency
    T2: T2 value (not used in mod1)
    
    """

    TR      = 4.6# TR in ms (hardcoded from Siemens protocol)
    FA_Cat  = [(-12/5)/360*(2*np.pi), (2*12/5)/360*(2*np.pi), (-3*12/5)/360*(2*np.pi), (4*12/5)/360*(2*np.pi), (-5*12/5)/360*(2*np.pi)] #Catalization module confirmed by Siemens (Peter Schmitt): Magn Reson Med 2003 Jan;49(1):151-7. doi: 10.1002/mrm.10337
    N_T1    = 66# Number of k-space lines (hardcoded from Siemens protocol)
    FA      = 12/360*(2*np.pi)# Flip angle in degrees (hardcoded from Siemens protocol) converted to radians

    #T1 Forward Model    
    M_result = iBEAT_T1_FM.signalSequenceT1_FLASH(M_eq, T1, TI, FA,FA_Eff, TR, N_T1, Eff, FA_Cat)
        
    return M_result

#T2 Fit Model
def mod2(Tprep,Eff, M_eq, T1,FA_Eff,T2): # not all parameters are used here
    """ mod1 is T1 Fit Model used for joint T1 & T2 fit
    
    Tprep: list of T2 preparation times
    Eff: 180 Ref Pulse efficency (not used in mod2)
    M_eq: equilibrim magnetization state
    T1: T1 value
    FA_Eff: Flip Angle Efficency
    T2: T2 value
    
    """

    Tspoil = 1# Spoil time in ms
    N_T2   = 72# Number of k-space lines (hardcoded from Siemens protocol)
    Trec   = 463*2# Recovery time in ms (hardcoded from Siemens protocol)
    TR     = 4.6# TR in ms (hardcoded from Siemens protocol)
    FA     = 12/360*(2*np.pi) # Flip angle in degrees (hardcoded from Siemens protocol) converted to radians

    #T2 Forward Model 
    M_result = iBEAT_T2_FM.signalSequenceT2prep(Tprep, M_eq, T2, T1 , Tspoil, FA,FA_Eff, TR, N_T2, Trec)
        
    return M_result

#Join T1 & T2 Fit model to perform a joint fit
def comboFunc(comboX,Eff, M_eq, T1,FA_Eff,T2):
    """ combine mod1 and mod2 for joint T1 & T2 fit
    
    comboX: a list that combines inversion times and echo times
    Eff: 180 Ref Pulse efficency
    M_eq: equilibrim magnetization state
    T1: T1 value
    FA_Eff: Flip Angle Efficency
    T2: T2 value
    
    """

    extract1 = comboX[:28]
    extract2 = comboX[28:] 

    result1 = mod1(extract1,Eff, M_eq, T1,FA_Eff,T2)
    result2 = mod2(extract2,Eff, M_eq, T1,FA_Eff,T2)

    return np.append(result1, result2)



def main(T1_images_to_be_fitted, T2_images_to_be_fitted, sequenceParam,GUI_object=None):
    """ main function that performs the joint T1 & T2 model-fit with shared parameters at single pixel level. 

    Args
    ----
    T1_images_to_be_fitted (numpy.ndarray) (x,y,z,TI): pixel value for time-series (i.e. at each TI time) with shape [x,:]
    T2_images_to_be_fitted (numpy.ndarray) (x,y,z,TE): pixel value for time-series (i.e. at each T2 prep time) with shape [x,:]
    
    sequenceParam (list): [TI,Tprep]


    Returns
    -------
    fitted_parameters: Map with signal model fitted parameters: 'S0', 'T1','T2','Flip Efficency','180 Efficency'.  
    """
    x1 = np.array(sequenceParam[0])
    x2 = np.array(sequenceParam[1])

    #Combine TI and TE for the joint T1 & T2 Fit
    comboX = np.append(x1, x2)

    # boundaries
    lb = [0  ,0     ,0   ,  0,  0  ]
    ub = [1  ,10000 ,5000,  1,  500]

    #prepare loop variables 
    T1map           = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))
    T2map           = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))
    M0map           = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))
    FA_Effmap       = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))
    Ref_Effmap      = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))
    T1_rsquare_map  = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))
    T2_rsquare_map  = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))

    #T1_images_to_be_fitted = T1_images_to_be_fitted[:,128:224,235:301,3:5]
    #T2_images_to_be_fitted = T2_images_to_be_fitted[:,128:224,235:301,3:5]
    
    #T1_images_to_be_fitted = T1_images_to_be_fitted[172:175,235:301,3:4,:]
    #T2_images_to_be_fitted = T2_images_to_be_fitted[172:175,235:301,3:4,:]

    #print(np.shape(T1_images_to_be_fitted))
    #print(np.shape(T2_images_to_be_fitted))

    #loop through slice, x, y and extract T1 and T2 pixel signal intensity along TI and TE
    for i in tqdm(range(np.shape(T1_images_to_be_fitted)[2]),desc="Slice Completed..."): #tqdm: terminal progress bar

#        if GUI_object:
#            GUI_object.progress_bar(max=np.shape(T1_images_to_be_fitted)[2], index=i+1) #wreasel progress bar (optional argument)

        tempImpageSlice_T1 = np.squeeze(T1_images_to_be_fitted[:,:,i,:]) #extract i slice from T1 images
        tempImpageSlice_T2 = np.squeeze(T2_images_to_be_fitted[:,:,i,:]) #extract i slice from T2 images
        #print(np.shape(tempImpageSlice_T1))
        #print(np.shape(tempImpageSlice_T2))

        for xi in tqdm (range((np.size(tempImpageSlice_T1,0))),desc="Rows Completed..."): #tqdm: terminal progress bar
            if GUI_object:
                GUI_object.progress_bar(max=np.shape(T1_images_to_be_fitted)[0], index=xi+1) #wreasel progress bar (optional argument)
                #GUI_object.update_progress_bar(index=xi+1)

            for yi in range((np.size(tempImpageSlice_T1,1))):
                
                #print(xi)
                #print(yi)
                Kidney_pixel_T1 = np.squeeze(np.array(tempImpageSlice_T1[xi,yi,:])) #T1 pixel signal intensity along TIs
                Kidney_pixel_T2 = np.squeeze(np.array(tempImpageSlice_T2[xi,yi,:])) #T2 pixel signal intensity along TEs

                if (Kidney_pixel_T1[0] and Kidney_pixel_T2[0]) ==0:
                    continue

                comboY = np.append(Kidney_pixel_T1, Kidney_pixel_T2) #combine T1 and T2 pixel signal intensity for joint T1 & T2 fit
                initialParameters = np.array([1,np.max(Kidney_pixel_T2), 1400, 1,80])# initial parameters [180 Efficency, Signal at equilibrium, T1 value,Flip Angle Efficency,T2 value]
        

                try:
                    #Joint T1  T2 Fit
                    fittedParameters, pcov = curve_fit(comboFunc, comboX, comboY, initialParameters,bounds=(lb,ub),method='trf',maxfev=5000)

                    #Fitted Parameters: [180 Efficency, Signal at equilibrium, T1 value,Flip Angle Efficency,T2 value]
                    Eff, M_eq, T1, FA_Eff,T2 = fittedParameters

                    #residuals calculation 
                    residuals_T1 = Kidney_pixel_T1-mod1(x1,Eff, M_eq, T1, FA_Eff,T2)
                    residuals_T2 = Kidney_pixel_T2-mod2(x2,Eff, M_eq, T1, FA_Eff,T2)

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

                    #plt.plot(np.arange(1,29), Kidney_pixel_T1,'.' ,label ="data")
                    #plt.plot(np.arange(1,29), mod1(x1,Eff, M_eq, T1, FA_Eff,T2),label ="Fitted curve: T1 =  " + str(np.round(T1,0))) # plot the equation using the fitted parameters
                    #plt.show()

                    #plt.plot(x2,Kidney_pixel_T2,'.',label ="data")
                    #plt.plot(x2, mod2(x2,Eff, M_eq, T1, FA_Eff,T2),label ="Fitted curve: T2 =  " + str(np.round(T2,0))) # plot the equation using the fitted parameters
                    #plt.show()

                    #store the fitted parameters
                    T1map[xi,yi,i]          = T1
                    T2map[xi,yi,i]          = T2
                    M0map[xi,yi,i]          = M_eq
                    FA_Effmap[xi,yi,i]      = FA_Eff
                    Ref_Effmap[xi,yi,i]     = Eff
                    T1_rsquare_map[xi,yi,i] = r_squared_T1
                    T2_rsquare_map[xi,yi,i] = r_squared_T2

                    #print('T1 R2 = ' + str(np.round(r_squared_T1,2)))
                    #print('T2 R2 = ' + str(np.round(r_squared_T2,2)))
                    #print('T1 = ' + str(np.round(T1,1)))
                    #print('T2 = ' + str(np.round(T2,1)))

                except:

                    T1map[xi,yi,i] = 0
                    T2map[xi,yi,i]  = 0
                    M0map[xi,yi,i]  = 0
                    FA_Effmap[xi,yi,i] = 0
                    Ref_Effmap[xi,yi,i] = 0
                    T1_rsquare_map[xi,yi,i] = 0
                    T2_rsquare_map[xi,yi,i] = 0

    fittedMaps = T1map, T2map, M0map, FA_Effmap, Ref_Effmap,T1_rsquare_map,T2_rsquare_map
    #print('iupi')
    return fittedMaps