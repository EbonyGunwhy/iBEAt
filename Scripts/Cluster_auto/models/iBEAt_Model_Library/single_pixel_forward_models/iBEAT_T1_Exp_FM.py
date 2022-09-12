"""
@author: Joao Periquito
iBEAt study T1-mapping forward model-fit
Siemens 3T PRISMA - Leeds (T1-mapping sequence)
2021
"""

import numpy as np
from scipy.optimize import curve_fit

def T1_FLASH_MOLLI_Eq(TI,M_eq, M_eq_App,T1_App,Inv_Eff):
    """ T1 Calculation using MOLLI.

    TI : list of inversion times (between 100 and 7700ms)
    M_eq, M_eq_App, T1_App: tissue parameters
    Inv_Eff: Efficency of the 180 inversion pulse

    """
    S_t = M_eq_App -(Inv_Eff*M_eq+M_eq_App)*np.exp(-TI/T1_App)

    return np.abs(S_t)

def T1_corrected(M_eq, M_eq_App,T1_App,Inv_Eff):

    A = M_eq_App
    B = M_eq_App + M_eq
    T1 = (B/A - 1)*T1_App/Inv_Eff

    return T1

def T1_fitting(images_to_be_fitted, TI):
    """ curve_fit function for T1-mapping.

    Args
    ----
    images_to_be_fitted (numpy.ndarray): pixel value for time-series (i.e. at each TI time) with shape [x,:]
    TI (list): list of inversion times
    sequenceParam (list): [FA, TR, N]

    Returns
    -------
    fit (list): signal model fit per pixel
    S0 (numpy.float64): fitted parameter 'S0' per pixel 
    T1 (numpy.float64): fitted parameter 'T1' (ms) per pixel.
    """   


    lb =            [0     , 0     , 0     , 0]
    ub =            [np.inf, np.inf, np.inf, 1]
    initial_guess = [1500  , 700   , 1000  , 1] 


    popt, pcov = curve_fit(T1_FLASH_MOLLI_Eq, TI, images_to_be_fitted, initial_guess, bounds=(lb,ub), method='trf',maxfev=5000)

    residuals = images_to_be_fitted - T1_FLASH_MOLLI_Eq(TI,*popt)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((images_to_be_fitted-np.mean(images_to_be_fitted))**2)
    r_squared = 1 - (ss_res / ss_tot)

    S0      = popt[0]
    S0_App  = popt[1]
    T1_app  = popt[2]
    Inv_Eff = popt[3]

    T1 = T1_corrected(S0, S0_App,T1_app,Inv_Eff)

    return S0, S0_App,T1_app,Inv_Eff,T1,r_squared



def main(images_to_be_fitted, TI):
    """ main function that performs the T2 model-fit at single pixel level. 

    Args
    ----
    images_to_be_fitted (numpy.ndarray): pixel value for time-series (i.e. at each echo time) with shape [x,:]
    TE_list (list): list of echo times

    Returns
    -------
    fit (list): signal model fit per pixel
    fitted_parameters (list): list with signal model fitted parameters 'S0','fw' (fraction of water) and 'T2sw'.  
    """

    
    results = T1_fitting(images_to_be_fitted, TI)

    S0      = results[0]
    S0_App  = results[1]
    T1_app  = results[2]
    Inv_Eff = results[3]
    T1      = results[4]
    r_square= results[5]

    
    

    return S0, S0_App, T1_app, Inv_Eff, T1, r_square