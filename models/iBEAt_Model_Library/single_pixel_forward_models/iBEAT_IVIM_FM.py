"""
@author: Joao Periquito
iBEAt study IVIM model-fit
Siemens 3T PRISMA - Leeds (DW-EPI sequence)
2021
"""

import numpy as np
from scipy.optimize import curve_fit

def Mono_Exp_IVIM(x,S0, D):
    """ MonoExponential Fit for IVIM data.

    S0, D, Ds and f (perfsion fraction): tissue parameters
    x : List of b-values used between 0 and 600 s/mm2)
    """
    S_IVIM = S0*(np.exp(-x*D))

    return S_IVIM

def Bi_Exp_IVIM(x,S0, D,Ds,f):
    """ BiExponential Fit for IVIM data.

    S0, D, Ds and f (perfsion fraction): tissue parameters
    x : List of b-values used between 0 and 600 s/mm2)
    """
    S_IVIM = S0*(f*np.exp(-x*Ds) + (1-f)*np.exp(-x*D))

    return S_IVIM


def Bi_Exp_IVIM_fitting(images_to_be_fitted, Bval_list):
    """ curve_fit function for IVIM-mapping.

    Args
    ----
    images_to_be_fitted (numpy.ndarray): pixel value for time-series (i.e. at each TE time) with shape [x,:]
    Bval_list (list): list of b-values


    Returns
    -------
    fit (list): signal model fit per pixel
    S0 (numpy.float64): fitted parameter 'S0' per pixel 
    D (numpy.float64): fitted parameter 'tissue diffusion' (mm2/s) per pixel.
    Ds (numpy.float64): fitted parameter 'pseudo diffusion' (mm2/s) per pixel.
    f (numpy.float64): fitted parameter 'pseudo diffusion fraction per pixel [0-100%]
    """

    lb_mono = [0,      0]
    ub_mono = [1,      1]
    initial_guess_mono = [1,0.002] 

    lb_bi = [0,      0]
    ub_bi = [1,      1]
    initial_guess_bi = [1,0.02] 

    try:
        
        fittedParameters_mono, pcov = curve_fit(Mono_Exp_IVIM, Bval_list[len(images_to_be_fitted)-3:len(images_to_be_fitted)], images_to_be_fitted[len(images_to_be_fitted)-3:len(images_to_be_fitted)], initial_guess_mono,bounds=(lb_mono,ub_mono),method='trf',maxfev=5000)

        fittedParameters, pcov = curve_fit(lambda x, S0,Ds: Bi_Exp_IVIM(x,S0, fittedParameters_mono[1],Ds,1-fittedParameters_mono[0]), Bval_list, images_to_be_fitted,initial_guess_bi,bounds=(lb_bi,ub_bi),method='trf',maxfev=5000)    
    
        fit = []

        fit.append(Bi_Exp_IVIM(Bval_list,fittedParameters[0],fittedParameters_mono[1],fittedParameters[1],1-fittedParameters_mono[0]))

        S0 = fittedParameters[0]
        D = fittedParameters_mono[1]
        Ds = fittedParameters[1]
        f = 1-fittedParameters_mono[0]



    except:
        fit = np.zeros(len(images_to_be_fitted))
        S0  = 0
        D  = 0
        Ds = 0
        f = 0

    return fit, S0,D, Ds,f

def Mono_Exp_IVIM_fitting(images_to_be_fitted, Bval_list):
    """ curve_fit function for mono-exp IVIM-mapping (ADC only)

    Args
    ----
    images_to_be_fitted (numpy.ndarray): pixel value for time-series (i.e. at each TE time) with shape [x,:]
    Bval_list (list): list of b-values


    Returns
    -------
    fit (list): signal model fit per pixel
    S0 (numpy.float64): fitted parameter 'S0' per pixel 
    D (numpy.float64): fitted parameter 'tissue diffusion' (mm2/s) per pixel.
    Ds (numpy.float64): fitted parameter 'pseudo diffusion' (mm2/s) per pixel.
    f (numpy.float64): fitted parameter 'pseudo diffusion fraction per pixel [0-100%]
    """

    lb_mono = [0,      0]
    ub_mono = [1,      1]
    initial_guess_mono = [1,0.002] 

    try:
        
        fittedParameters_mono, pcov = curve_fit(Mono_Exp_IVIM, Bval_list, images_to_be_fitted, initial_guess_mono,bounds=(lb_mono,ub_mono),method='trf',maxfev=5000)
    
        fit = []

        fit.append(Mono_Exp_IVIM(Bval_list,fittedParameters_mono[0],fittedParameters_mono[1]))

        S0 = fittedParameters_mono[0]
        D = fittedParameters_mono[1]


    except:
        fit = np.zeros(len(images_to_be_fitted))
        S0  = 0
        D  = 0

    return fit, S0, D

def main(images_to_be_fitted, Bval_list):
    """ main function that performs the IVIM model-fit at single pixel level. 

    Args
    ----
    images_to_be_fitted (numpy.ndarray): pixel value for time-series (i.e. at each b-value) with shape [x,:]
    Bval_list (list): list of b-values

    Returns
    -------
    fit (list): signal model fit per pixel
    fitted_parameters (list): list with signal model fitted parameters 'S0','D' (tissue diffusion), 'Ds' (psudo-diffusion) and 'f' (fraction of pseudo-diffusion).  
    """
    #Two-step Bi-exp
    #results = Bi_Exp_IVIM_fitting(images_to_be_fitted, Bval_list)
 
    #fit = results[0]
    #S0 = results[1]
    #D = results[2]
    #Ds = results[3]
    #f = results[4]
    
    #fitted_parameters = [S0, D, Ds,f]

    #Mono-Exp
    #Two-step Bi-exp
    results = Mono_Exp_IVIM_fitting(images_to_be_fitted, Bval_list)
 
    fit = results[0]
    S0 = results[1]
    D = results[2]

    
    fitted_parameters = [S0, D]

    return fit, fitted_parameters