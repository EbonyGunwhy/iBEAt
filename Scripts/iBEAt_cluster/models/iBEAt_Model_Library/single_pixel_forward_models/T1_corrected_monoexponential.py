"""
iBEAt study model library 
corrected model for T1-MOLLI inversion recovery
@owner: Kanishka Sharma
2021
"""
    
import numpy as np

def T1_corrected_monoexponential(model_parameters, sequence_parameters):
    """ main corrected function for forward signal model fit.

    Parameters
    ---------- 
    model_parameters: list 
        example for MOLLI-T1: [a, b, T1]
        
    sequence_parameters: list
        example for MOLLI-T1: [TI]
        
    Return values
    ------------
       list containing simulated values per pixel
    """

    a =  model_parameters[0]
    b =  model_parameters[1]
    T1 = model_parameters[2]

    TI =  sequence_parameters[0]

    return a - b * np.exp(-TI/T1) #S = a-b*exp(-TI/T1)



