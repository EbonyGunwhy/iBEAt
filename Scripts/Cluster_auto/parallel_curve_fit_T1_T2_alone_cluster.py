import os
import numpy as np
import models.iBEAt_Model_Library.single_pixel_forward_models.iBEAT_T1_FM
import models.iBEAt_Model_Library.single_pixel_forward_models.iBEAT_T2_FM

from tqdm import tqdm
import multiprocessing

from dbdicom import Folder

def main(arguments):

    try:
        x,y,t1_value,t2_value,TI_temp,TE,FA_rad,TR,N_T1,N_T2,FA_Cat,Trec,FA_eff,Tspoil = arguments

        fit_T1, fitted_parameters_T1 = models.iBEAt_Model_Library.single_pixel_forward_models.iBEAT_T1_FM.main (t1_value, TI_temp, [FA_rad, TR, N_T1,FA_Cat])
                                                                                                            
        S0_T1,T1,FA_eff = fitted_parameters_T1

        fit_T2, fitted_parameters_T2 = models.iBEAt_Model_Library.single_pixel_forward_models.iBEAT_T2_FM.main (t2_value, TE,[T1,Tspoil,FA_rad,TR, N_T2,Trec,FA_eff])

        S0_T2, T2, FA_eff_2 =  fitted_parameters_T2
        
        residuals_T1 = t1_value-np.squeeze(fit_T1) 
        residuals_T2 = t2_value-np.squeeze(fit_T2) 

        #r squared calculation 

        ss_res_T1 = np.sum(np.nan_to_num(residuals_T1**2))
        ss_res_T2 = np.sum(np.nan_to_num(residuals_T2**2))
        ss_tot_T1 = np.sum(np.nan_to_num((t1_value-np.nanmean(t1_value))**2))
        ss_tot_T2 = np.sum(np.nan_to_num((t2_value-np.nanmean(t2_value))**2))

        if ss_tot_T1 or ss_tot_T2 == 0:
            r_squared_T1 = 0
            r_squared_T2 = 0
        else:
            r_squared_T1 = np.nan_to_num(1 - (ss_res_T1 / ss_tot_T1))
            r_squared_T2 = np.nan_to_num(1 - (ss_res_T2 / ss_tot_T2))

        #replace possible nan (from division by 0: ss_res_T1 / ss_tot_T1) to 0
        if (np.isnan(r_squared_T1)): r_squared_T1 = 0
        if (np.isnan(r_squared_T2)): r_squared_T2 = 0
        
    except:
        T1 = T2 = S0_T1 = S0_T2 = FA_eff = r_squared_T1 = r_squared_T2 = 0
        
    return x,y,T1, T2, S0_T1, S0_T2, FA_eff, r_squared_T1, r_squared_T2