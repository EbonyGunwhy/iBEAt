"""
@author: Joao Periquito
iBEAt study T2-mapping forward model-fit
Siemens 3T PRISMA - Leeds (T2-prep sequence)
2021
"""

import numpy as np
from scipy.optimize import curve_fit


def freeRecoveryMagnetization(M_init, t, M_eq, T1):
    """ Free Longitudinal Recovery

    M_init: initial magnetization state
    M_eq, T1: tissue parameters
    t: recovery time
    """
    E = np.exp(-t/T1)
    Mt = M_init * E  + M_eq * (1-E)
    return Mt

def pulse(M_init, FA):
    """ Alpha Pulse

    M_init: initial magnetization state
    FA: used flip-angle in radians
    """
    return np.cos(FA) * M_init


def FLASHreadout(M_init, M_eq, T1, FA, TR, N):
    """ FLASH readout

    M_init: initial magnetization state
    M_eq, T1: tissue parameters
    FA : Flip angle in radians
    TR : time between FA pulses in ms
    N : number of readout pulses
    """
    M_current = M_init
    
    for i in range(np.int(N)):
        M_current = pulse(M_current, FA)
        M_current = freeRecoveryMagnetization(M_current, TR, M_eq, T1)
    return M_current

def freeDecayMagnetization(M_init, t, T2):
    """ T2 prep

    M_init: initial magnetization state
    t: T2 prep duration
    T2: tissue parameters
    """
    E = np.exp(-t/T2)
    return E * M_init


def signalSequenceT2prepOneShot(M_init, M_eq, T1, T2, Tprep, Tspoil, FA, TR, N):
    """ One shot of a T2-prep sequence

    M_eq, T1, T2 : tissue parameters
    Tprep : preparation time in ms (between 0 and 120ms)
    Tspoil: time for spoiling after prep pulse (1ms)
    FA : Flip angle in radians (12 degrees)
    TR : time between FA pulses in ms (about 4.6ms)
    N : number of readout pulses (72)
    Trec : recovery time after readout (2 * 463ms)
    k-space center: 48 (72/2 + 12 due to partial Fourier) 
    """

    Mcurrent = freeDecayMagnetization(M_init, Tprep, T2) # prep pulse
    Mcurrent = freeRecoveryMagnetization(Mcurrent, Tspoil, M_eq, T1) # during spoiling
    Mcurrent = FLASHreadout(Mcurrent, M_eq, T1, FA, TR, N/2-12) # readout
    

    return Mcurrent 


def signalSequenceT2prep(Tprep, M_eq, T2, T1 , Tspoil, FA,FA_Eff, TR, N, Trec):
    """ All shots of a T2 prep sequence.

    M_eq, T1, T2 : tissue parameters
    Tprep : preparation time in ms (between 0 and 120ms)
    Tspoil: time for spoiling after prep pulse (1ms)
    FA : Flip angle in radians (12 degrees)
    TR : time between FA pulses in ms (about 4.6ms)
    N : number of readout pulses (72)
    Trec : recovery time after readout (2 * 463ms)
    k-space center: 48 (72/2 + 12 due to partial Fourier) 
    """
    FA = FA * FA_Eff
    M_result = np.zeros(11) 
    M_current = M_eq
    M_current = signalSequenceT2prepOneShot(M_current, M_eq, T1, T2, Tprep[0], Tspoil, FA, TR, N) # signal at first Tprep
    M_result[0]=M_current

    for t in range(1, np.size(Tprep)):
        
        M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2+12) # readout
        M_current = freeRecoveryMagnetization(M_current, 120-Tprep[t-1], M_eq, T1) # recovery after readout
        M_current = freeRecoveryMagnetization(M_current, Trec, M_eq, T1) # recovery after readout
        M_current = signalSequenceT2prepOneShot(M_current, M_eq, T1, T2, Tprep[t], Tspoil, FA, TR, N) # signal at first Tprep
        M_result[t] =M_current
    return M_result

def T2_fitting(images_to_be_fitted, T2_prep_times, sequenceParam):
    """ curve_fit function for T2-mapping.

    Args
    ----
    images_to_be_fitted (numpy.ndarray): pixel value for time-series (i.e. at each T2-prep time) with shape [x,:]
    T2_prep_times (list): list of T2-preparation times
    sequenceParam (list): [T1, Tspoil, FA, TR, N, Trec]

    Returns
    -------
    fit (list): signal model fit per pixel
    S0 (numpy.float64): fitted parameter 'S0' per pixel 
    T2 (numpy.float64): fitted parameter 'T2' (ms) per pixel.
    """
    T1 = sequenceParam[0]
    Tspoil = sequenceParam[1]
    FA = sequenceParam[2]     
    TR = sequenceParam[3] 
    N = sequenceParam[4]
    Trec = sequenceParam[5]


    lb = [0,0,0]
    ub = [10000,200,1]
    initial_guess = [np.max(images_to_be_fitted),80,1] 

    popt, pcov = curve_fit(lambda Tprep, M_eq, T2, FA_Eff: signalSequenceT2prep(Tprep, M_eq, T2, T1, Tspoil, FA,FA_Eff, TR, N, Trec), xdata = T2_prep_times, ydata = images_to_be_fitted, p0=initial_guess, bounds=(lb,ub), method='trf',maxfev=100)
    
    T2_prep_times

    fit=signalSequenceT2prep(T2_prep_times, popt[0],popt[1],sequenceParam[0],sequenceParam[1],sequenceParam[2],popt[2],sequenceParam[3],sequenceParam[4],sequenceParam[5])

    S0 = popt[0]
    T2 = popt[1]
    FA_Eff = popt[2]

    return fit, S0, T2,FA_Eff

#T2_fitting(signalSequenceT2prep(np.array([0,30,40,50,60,70,80,90,100,110,120]),1, 100, 1000, 1, 0.3, 3, 30, 1000), np.array([0,30,40,50,60,70,80,90,100,110,120]), [1000,1,0.3,3,30,1000])


def main(images_to_be_fitted, T2_prep_times, sequenceParam):
    """ main function that performs the T2 model-fit at single pixel level. 

    Args
    ----
    images_to_be_fitted (numpy.ndarray): pixel value for time-series (i.e. at each T2-prep time) with shape [x,:]
    T2_prep_times (list): list of T2-preparation times
    sequenceParam (list): [T1, Tspoil, FA, TR, N, Trec]


    Returns
    -------
    fit (list): signal model fit per pixel
    fitted_parameters (list): list with signal model fitted parameters 'S0' and 'T2'.  
    """

    results = T2_fitting(images_to_be_fitted, T2_prep_times,sequenceParam)
 
    fit = results[0]
    S0 = results[1]
    T2 = results[2]
    FA_Eff = results[3]
    
    fitted_parameters = [S0, T2,FA_Eff]

    return fit, fitted_parameters
