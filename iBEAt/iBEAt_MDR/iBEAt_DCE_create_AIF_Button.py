import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(os.path.abspath(os.path.join('..', 'GitHub')))
# These 2 lines are required if you're importing an external
# python package that doesn't have "pip install" and that's located
# in the same folder as the current menu script.
import numpy as np
#import matplotlib.pyplot as plt
#***************************************************************************

def isSeriesOnly(self):
    return True

def main(weasel, series=None):
    try:
        if series is None:
            series = weasel.series()[0]

        # Get Pixel Array and format it accordingly
        series_magnitude = series.Magnitude.sort("SliceLocation","AcquisitionTime")
        pixel_array = series_magnitude.PixelArray

        # display the new sorted series
        #sorted_series_magnitude = series_magnitude.new(series_name="DCE_Series_Sorted")
        #sorted_series_magnitude.write(pixel_array)
        print("shape weasel input sorted_series_magnitude")
        print(np.shape(pixel_array)) #  
        # Display sorted series
        #sorted_series_magnitude.display()
        
        pixel_array = np.transpose(pixel_array) # CHECK MEMORY ALLOCATION
        print("shape weasel pixel_array after transpose")
        print(np.shape(pixel_array)) # 
        #TODO: read number of dynamics from dicom series
        reformat_shape = (np.shape(pixel_array)[0], np.shape(pixel_array)[1],int(np.shape(pixel_array)[2]/265),265)
        print("reformat_shape")
        print(reformat_shape)# 
        magnitude_array = pixel_array.reshape(reformat_shape)
    
        MaxIm = np.zeros((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
        P_interim = np.zeros((np.shape(pixel_array)[0],np.shape(pixel_array)[1], 265))
        
        for index in range(np.shape(magnitude_array)[2]):
            if index ==8: # for transverse slice only
                ## calculate baseline P0 
                P0 = np.squeeze(magnitude_array[:, :, index, :10]) # 1st ten baseline dynamics of the aorta slice
                mean_baselines = np.mean(P0, axis =2, out=None)#[:,:,:10])#, out=None) # mean image of the 10 baselines
                P =  np.squeeze(magnitude_array[:, :, index, :]) # all dynamics per aorta slice

                for j in range(np.shape(magnitude_array)[3]): # dynamics only
                    P_at_j = P[:,:,j]
                    P_interim[:,:,j] = P_at_j - mean_baselines 
               
                MaxIm = np.amax(P_interim, axis=2)              
        
        MaxIm = np.transpose(MaxIm)  
         
        # # display maps
        MaxIm_final = series.new(series_name="DCE_Aorta_Maximum_Image")
        MaxIm_final.write(MaxIm)
        # Refresh Weasel
     #   weasel.refresh() 
        MaxIm_final.display()
     #   MaxIm_final.export_as_nifti(directory=output_folder)

        # Refresh Weasel
        # weasel.refresh()

    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.main: ' + str(e))

