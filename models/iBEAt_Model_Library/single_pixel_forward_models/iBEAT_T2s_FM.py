"""
@author: Joao Periquito
iBEAt study T2-mapping forward model-fit
Siemens 3T PRISMA - Leeds (T2-prep sequence)
2021
"""

import numpy as np
from scipy.optimize import curve_fit

def Mono_Exp_T2s_with_Water_Fat(x,M_eq, fw, T2sw):
    """ MonoExponential Fit of a T2* sequence takin in account in/out Fat.

    M_eq, T2sw, T2sf and fw (fraction of water): tissue parameters, T2sf = 9.3ms (Le Ster, C. et al. doi:10.1002/jmri.25205)
    x : List of echo times used between 3.7 and 44.3ms)
    """
    S_T2s = np.zeros(np.size(x))
    for m in range(np.size(x)):
        if m % 2 == 0:
            n=-1
            #print(n)
        else:
            n=1
            #print(n)

        S_T2s[m] = M_eq*(fw*np.exp(-x[m]/T2sw) + n*(1-fw)*np.exp(-x[m]/9.3))
    return S_T2s


def T2s_fitting(images_to_be_fitted, TE_list, ModelParam):
    """ curve_fit function for T2*-mapping.

    Args
    ----
    images_to_be_fitted (numpy.ndarray): pixel value for time-series (i.e. at each TE time) with shape [x,:]
    TE_list (list): list of echo times
    ModelParam: T2sf: T2* of Fat at 3.0T = 9.3 (Le Ster, C. et al. doi:10.1002/jmri.25205)

    Returns
    -------
    fit (list): signal model fit per pixel
    S0 (numpy.float64): fitted parameter 'S0' per pixel 
    T2s (numpy.float64): fitted parameter 'T2*' (ms) per pixel.
    fw (numpy.float64): fitted parameter 'water fraction per pixel [0-100%]
    """
    T2sf = ModelParam

    lb = [0,     0,     0]
    ub = [np.inf,     1,   100]
    initial_guess = [np.max(images_to_be_fitted),1,60] 


    try:


        fittedParameters, pcov = curve_fit(Mono_Exp_T2s_with_Water_Fat, TE_list, images_to_be_fitted, initial_guess,bounds=(lb,ub),method='trf',maxfev=5000)    
    
        fit = []

        fit.append(Mono_Exp_T2s_with_Water_Fat(TE_list,fittedParameters[0],fittedParameters[1],fittedParameters[2]))

        S0 = fittedParameters[0]
        fw = fittedParameters[1]
        T2s = fittedParameters[2]

    except:
        fit = 0
        S0  = 0
        fw  = 0
        T2s = 0

    return fit, S0,fw, T2s

def main(images_to_be_fitted, TE_list):
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

    ModelParam = 9.3     #T2* of Fat at 3.0T = 9.3 (Le Ster, C. et al. doi:10.1002/jmri.25205)
    results = T2s_fitting(images_to_be_fitted, TE_list,ModelParam)
 
    fit = results[0]
    S0 = results[1]
    fw = results[2]
    T2s = results[3]
    
    fitted_parameters = [S0, fw, T2s]

    return fit, fitted_parameters