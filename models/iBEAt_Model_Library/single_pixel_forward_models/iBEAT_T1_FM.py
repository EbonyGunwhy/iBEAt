"""
@author: Joao Periquito
iBEAt study T1-mapping forward model-fit
Siemens 3T PRISMA - Leeds (T1-mapping sequence)
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

def FLASHreadout_CatModule(M_init, M_eq, T1, FA, TR, N):
    """ Catalization Module

    M_init: initial magnetization state
    M_eq, T1: tissue parameters
    FA : list of flip angle in radians
    TR : time between FA pulses in ms
    N : number of readout pulses
    """
    M_current = M_init
    
    for i in range(np.int(N)):
        M_current = pulse(M_current, FA[i])
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


def signalSequenceT1_FLASH(M_eq, T1, TI, FA,FA_Eff, TR, N, FA_Cat):
    """ All shots of a T2 prep sequence.

    M_eq, T1: tissue parameters
    TI : list of inversion times (between 100 and 7700ms)
    FA : Flip angle in radians (12 degrees)
    TR : time between FA pulses in ms (about 4.6ms)
    N : number of readout pulses (66)

    k-space center: 13 (66/2 - 20 due to 5/8 partial Fourier) 
    """
    FA = FA*FA_Eff
    FA_Cat = np.array(FA_Cat)*FA_Eff
    M_result = np.zeros(28) 
    ####### 1st SET: 16 TI's ########



#SLICE 1
    #M_current = M_eq*(-1)                                          # 180 in z-
    #M_current = freeRecoveryMagnetization(M_current, 9120, M_eq, T1)
    #M_current = M_current*(-1)
    #M_current = freeRecoveryMagnetization(M_current, 5060, M_eq, T1)
    #M_current = M_current*(-1)
    #M_current = freeRecoveryMagnetization(M_current, 10200, M_eq, T1)

#SLICE 2
    #M_current = M_current*(-1)
    #M_current = freeRecoveryMagnetization(M_current, 9120, M_eq, T1)
    #M_current = M_current*(-1)
    #M_current = freeRecoveryMagnetization(M_current, 5060, M_eq, T1)
    #M_current = M_current*(-1)
    #M_current = freeRecoveryMagnetization(M_current, 10200, M_eq, T1)
    #M_current = M_current*(-1)

    # Inversion                                              
    M_current = M_eq*(-1)                                          # 180 in z-
    M_current = freeRecoveryMagnetization(M_current, 6.5, M_eq, T1)     # half of inversion pulse delay
    
    # TIfill  
    M_current = freeRecoveryMagnetization(M_current, 6.5, M_eq, T1)     # TIfill delay
    
    # Catalization Module (25ms)
    M_current = FLASHreadout_CatModule(M_current, M_eq, T1, FA_Cat, TR, 5)
    #M_current = freeRecoveryMagnetization(M_current, 2, M_eq, T1)   # 2ms to make 25ms
    M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2-20)   
    #Acquisition (66 lines: 13 + 53) 
    M_result[0] =M_current                                          # save result (13 lines)
    M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2+20)       # rest of the readout (53 lines)

    for t in range(1, np.size(TI)-12):

        M_current = freeRecoveryMagnetization(M_current, 80, M_eq, T1)  # fixed 80ms delay Siemens
        M_current = freeRecoveryMagnetization(M_current, 80, M_eq, T1)  # fixed 80ms delay Siemens
        M_current = freeRecoveryMagnetization(M_current, 13, M_eq, T1)  # inversion pulse duration
        M_current = freeRecoveryMagnetization(M_current, 6.5, M_eq, T1) # TI fill delay
        M_current = FLASHreadout_CatModule(M_current, M_eq, T1, FA_Cat, TR, 5) 
       # M_current = freeRecoveryMagnetization(M_current, 2, M_eq, T1)   # 2ms to make 25ms
        M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2-20)   # k-space center
        M_result[t] =M_current                                      # save result
        M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2+20)   # rest of the readout
    
    ####### Recovery ########
    #Beat 1  2
    M_current = freeRecoveryMagnetization(M_current, 507*2, M_eq, T1)   # recovery time (2 beats: ms)
    #M_current = freeRecoveryMagnetization(M_current, 80+80+13, M_eq, T1)  
    #M_current = FLASHreadout_CatModule(M_current, M_eq, T1, FA_Cat, TR, 5)
    #M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N)
    #M_current = freeRecoveryMagnetization(M_current, 507-80-80-13-23, M_eq, T1)

    #M_current = freeRecoveryMagnetization(M_current, 80+80+13, M_eq, T1)  
    #M_current = FLASHreadout_CatModule(M_current, M_eq, T1, FA_Cat, TR, 5)
    #M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N)
    #M_current = freeRecoveryMagnetization(M_current, 507-80-80-13-23, M_eq, T1)


    
    ####### 2nd SET: 8 TI's ########
    M_current = freeRecoveryMagnetization(M_current, 80, M_eq, T1)
    M_current = freeRecoveryMagnetization(M_current, 6.5, M_eq, T1)
    M_current = M_current*(-1)
    M_current = freeRecoveryMagnetization(M_current, 6.5, M_eq, T1)
    M_current = freeRecoveryMagnetization(M_current, 80, M_eq, T1)
    M_current = freeRecoveryMagnetization(M_current, 6.5, M_eq, T1)
    M_current = FLASHreadout_CatModule(M_current, M_eq, T1, FA_Cat, TR, 5)           
    #M_current = freeRecoveryMagnetization(M_current, 2, M_eq, T1)       
    M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2-20)       
    M_result[16] = M_current                                          
    M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2+20)

    for t in range(1, np.size(TI)-20):

        M_current = freeRecoveryMagnetization(M_current, 80, M_eq, T1)
        M_current = freeRecoveryMagnetization(M_current, 13, M_eq, T1)
        M_current = freeRecoveryMagnetization(M_current, 80, M_eq, T1)
        M_current = freeRecoveryMagnetization(M_current, 6.5, M_eq, T1)
        M_current = FLASHreadout_CatModule(M_current, M_eq, T1, FA_Cat, TR, 5)             # 5 flash readouts
        #M_current = freeRecoveryMagnetization(M_current, 2, M_eq, T1)   # 2m spoiler gradient in z
        M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2-20)   # k-space center
        M_result[16+t] = M_current                                      # save result
        M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2+20)
     
    ####### Recovery 2 ########
    #Beat 1 & 2
    M_current = freeRecoveryMagnetization(M_current, 507*2, M_eq, T1)   # recovery time (2 beats: ms)
    #M_current = freeRecoveryMagnetization(M_current, 80+80+13, M_eq, T1)  
    #M_current = FLASHreadout_CatModule(M_current, M_eq, T1, FA_Cat, TR, 5)
    #M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N)
    #M_current = freeRecoveryMagnetization(M_current, 507-80-80-13-23, M_eq, T1)

    #M_current = freeRecoveryMagnetization(M_current, 80+80+13, M_eq, T1)  
    #M_current = FLASHreadout_CatModule(M_current, M_eq, T1, FA_Cat, TR, 5)
    #M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N)
    #M_current = freeRecoveryMagnetization(M_current, 507-80-80-13-23, M_eq, T1)
    
    ####### 3rd SET: 4 TI's ########
    M_current = freeRecoveryMagnetization(M_current, 6.5, M_eq, T1)
    M_current = M_current*(-1)
    M_current = freeRecoveryMagnetization(M_current, 6.5, M_eq, T1)
    M_current = freeRecoveryMagnetization(M_current, 80, M_eq, T1)
    M_current = freeRecoveryMagnetization(M_current, 80, M_eq, T1)
    M_current = freeRecoveryMagnetization(M_current, 6.5, M_eq, T1)
    M_current = FLASHreadout_CatModule(M_current, M_eq, T1, FA_Cat, TR, 5)             # 5 flash readouts
    #M_current = freeRecoveryMagnetization(M_current, 2, M_eq, T1)       # 2m spoiler gradient in z
    M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2-20)       # k-space center
    M_result[24] = M_current                                          # save result
    M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2+20)

    for t in range(1, np.size(TI)-24):

        M_current = freeRecoveryMagnetization(M_current, 13, M_eq, T1)
        M_current = freeRecoveryMagnetization(M_current, 80, M_eq, T1)
        M_current = freeRecoveryMagnetization(M_current, 80, M_eq, T1)
        M_current = freeRecoveryMagnetization(M_current, 6.5, M_eq, T1)
        M_current = FLASHreadout_CatModule(M_current, M_eq, T1, FA_Cat, TR, 5)             # 5 flash readouts
        #M_current = freeRecoveryMagnetization(M_current, 2, M_eq, T1)       # 2m spoiler gradient in z
        M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2-20)       # k-space center
        M_result[24+t] = M_current                                          # save result
        M_current = FLASHreadout(M_current, M_eq, T1, FA, TR, N/2+20)

    M_result = np.abs(M_result)

    return M_result

def T1_fitting(images_to_be_fitted, TI, sequenceParam):
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
    FA     = sequenceParam[0]
    TR     = sequenceParam[1] 
    N      = sequenceParam[2]
    FA_Cat = sequenceParam[3]
    

    lb = [0,     0,    0]
    ub = [np.inf,5000,1]
    initial_guess = [np.max(images_to_be_fitted),1200,1] 

    popt, pcov = curve_fit(lambda TI, M_eq, T1,FA_Eff: signalSequenceT1_FLASH(M_eq, T1, TI, FA,FA_Eff, TR, N,FA_Cat), xdata = TI, ydata = images_to_be_fitted, p0=initial_guess, bounds=(lb,ub), method='trf',maxfev=100)

    fit=signalSequenceT1_FLASH(popt[0],popt[1],TI,sequenceParam[0],popt[2],sequenceParam[1],sequenceParam[2],sequenceParam[3])

    S0 = popt[0]
    T1 = popt[1]
    FA_Eff = popt[2]

    return fit, S0, T1,FA_Eff

#T2_fitting(signalSequenceT2prep(np.array([0,30,40,50,60,70,80,90,100,110,120]),1, 100, 1000, 1, 0.3, 3, 30, 1000), np.array([0,30,40,50,60,70,80,90,100,110,120]), [1000,1,0.3,3,30,1000])


def main(images_to_be_fitted, TI, sequenceParam):
    """ main function that performs the T1 model-fit at single pixel level. 

    Args
    ----
    images_to_be_fitted (numpy.ndarray): pixel value for time-series (i.e. at each T2-prep time) with shape [x,:]
    TI (list): list of inversion times
    sequenceParam (list): [T1, FA, TR, N]


    Returns
    -------
    fit (list): signal model fit per pixel
    fitted_parameters (list): list with signal model fitted parameters 'S0' and 'T1'.  
    """

    results = T1_fitting(images_to_be_fitted, TI, sequenceParam)
 
    fit = results[0]
    S0 = results[1]
    T1 = results[2]
    FA_eff = results[3]

    
    fitted_parameters = [S0, T1,FA_eff]

    return fit, fitted_parameters