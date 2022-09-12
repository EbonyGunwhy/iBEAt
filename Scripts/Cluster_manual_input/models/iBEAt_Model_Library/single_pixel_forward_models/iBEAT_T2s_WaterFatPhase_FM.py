"""
@author: Joao Periquito
iBEAt study T2s-mapping
Siemens 3T PRISMA - Leeds
2021
"""

import numpy as np
from scipy.optimize import curve_fit

def generate_Sx_and_Sy(magnitude_array, radians_array):
    """Calculate Sx and Sy components from magnitude and phase data

    magnitude_array: magnitude images
    radians_array: phase data scaled between 0 and 2pi
    """

    Sx_array = magnitude_array*np.cos(radians_array)
    Sy_array = magnitude_array*np.sin(radians_array)
    
    comboY = np.append(Sx_array,Sy_array)

    return comboY


def X_Water_wPhase(TE,S0,fw,T2sw,Ww):
    """Calculate X of water signal contribuition

   TE: echo time
   S0: signal at equilibrium
   fw: fraction of water
   T2sw: t2* water
   Ww: precession frequency of water
    """

    S_Wx = S0*fw*np.exp(-TE/T2sw)*np.cos(Ww*TE)

    return S_Wx

def Y_Water_wPhase(TE,S0,fw,T2sw,Ww):
    """Calculate Y of water signal contribuition
   TE: echo time
   S0: signal at equilibrium
   fw: fraction of water
   T2sw: t2* water
   Ww: precession frequency of water
    """

    S_Wy = S0*fw*np.exp(-TE/T2sw)*np.sin(Ww*TE)

    return S_Wy

def X_Fat_wPhase(TE,S0,fw,Ww):
    """Calculate X of fat signal contribuition

   TE: echo time
   S0: signal at equilibrium
   fw: fraction of water
   Ww: precession frequency of water
    """

    S_Fx = np.zeros(np.size(TE))
    for m in range(np.size(TE)):
        if m % 2 == 0:
            n=-1
            #print(n)
        else:
            n=1
            #print(n)

        S_Fx[m] = S0*n*(1-fw)*np.exp(-TE[m]/9.3)*np.cos(Ww*0.0000035*TE[m])

    return S_Fx

def Y_Fat_wPhase(TE,S0,fw,Ww):
    """Calculate Y of fat signal contribuition

   TE: echo time
   S0: signal at equilibrium
   fw: fraction of water
   Ww: precession frequency of water
    """

    S_Fy = np.zeros(np.size(TE))
    for m in range(np.size(TE)):
        if m % 2 == 0:
            n=-1
            #print(n)
        else:
            n=1
            #print(n)

        S_Fy[m] = S0*n*(1-fw)*np.exp(-TE[m]/9.3)*np.sin(Ww*0.0000035*TE[m])

    return S_Fy

def X_WF (TE,S0,fw,T2sw,Ww):
    """Sum the X components of water and fat signal contribuitions

   TE: echo time
   S0: signal at equilibrium
   fw: fraction of water
   Ww: precession frequency of water
    """

    X_Water = X_Water_wPhase(TE,S0,fw,T2sw,Ww)
    X_Fat   = X_Fat_wPhase(TE,S0,fw,Ww)

    return X_Water + X_Fat


def Y_WF (TE,S0,fw,T2sw,Ww):
    """Sum the Y components of water and fat signal contribuitions

   TE: echo time
   S0: signal at equilibrium
   fw: fraction of water
   Ww: precession frequency of water
    """

    Y_Water = Y_Water_wPhase(TE,S0,fw,T2sw,Ww)
    Y_Fat = Y_Fat_wPhase(TE,S0,fw,Ww)

    return Y_Water + Y_Fat

def comboFunc(comboX,S0,fw,T2sw,Ww):
    """Join Y and X fnction to perform a joint fit

   comboX: echo time for X and Y component of the signal
   S0: signal at equilibrium
   fw: fraction of water
   Ww: precession frequency of water
    """

    extract1 = comboX[:12] #12 is the Number of TEs used (hardcoded)
    extract2 = comboX[12:] #12 is the Number of TEs used (hardcoded)

    result_X = X_WF (extract1,S0,fw,T2sw,Ww)
    result_Y = Y_WF (extract2,S0,fw,T2sw,Ww)

    return np.append(result_X, result_Y)

def T2s_fitting(magnitude_array, phase_array, TE_list):
    """ curve_fit function for T2*-mapping.

    Args
    ----
    magnitude_array (numpy.ndarray): magnitude pixel value for time-series (i.e. at each TE time) with shape [x,:]
    phase_array (numpy.ndarray): phase pixel value for time-series (i.e. at each TE time) with shape [x,:]
    TE_list (list): list of echo times

    Returns
    -------
    fit (list): signal model fit per pixel
    S0 (numpy.float64): fitted parameter 'S0' per pixel 
    T2s (numpy.float64): fitted parameter 'T2*' (ms) per pixel.
    fw (numpy.float64): fitted parameter 'water fraction per pixel [0-100%]
    Ww: fitted parameter precession frequency of water
    """
    comboX = np.append(TE_list, TE_list)
    comboY = generate_Sx_and_Sy(magnitude_array, phase_array)

    lb = [  0,  0,    0,     -1] #lower boundary
    ub = [500,  1,    150,    1] #upper boundary
    initial_guess = [200,1,60,0] #starting value

    try:

        fittedParameters, pcov = curve_fit(comboFunc, comboX, comboY, initial_guess,bounds=(lb,ub),method='trf',maxfev=5000)    
    
        S0 = fittedParameters[0]
        fw = fittedParameters[1]
        T2s = fittedParameters[2]
        Ww = fittedParameters[3]

    except:
        S0  = -1234
        fw  = -1234
        T2s = -1234
        Ww = -1234
        #print('Nao')

    results = [S0,fw, T2s, Ww]

    return results 



def main(magnitude_array, phase_array, TE_list):
    """ main function that performs the T2 model-fit at single pixel level. 

    Args
    ----
    magnitude_array (numpy.ndarray): magnitude pixel value for time-series (i.e. at each TE time) with shape [x,:]
    phase_array (numpy.ndarray): phase pixel value for time-series (i.e. at each TE time) with shape [x,:]
    TE_list (list): list of echo times

    Returns
    -------
    fit (list): signal model fit per pixel
    fitted_parameters (list): list with signal model fitted parameters 'S0','fw' (fraction of water) 'T2sw' and Ww.  
    """

    results = T2s_fitting(magnitude_array, phase_array, TE_list)
 
    S0 = results[0]
    fw = results[1]
    T2s = results[2]
    Ww =  results[3]

    return S0,fw,T2s,Ww