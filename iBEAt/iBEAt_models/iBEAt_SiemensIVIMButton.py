import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# These 2 lines are required if you're importing an external
# python package that doesn't have "pip install" and that's located
# in the same folder as the current menu script.

import numpy as np
import matplotlib.pyplot as plt
import IVIM_pixelwise_fit

#***************************************************************************

def isSeriesOnly(self):
    return True

def main(weasel, series=None, mask=None,export_ROI=False):
    try:
        if series is None:
            weasel.message(msg="Please Select MT_OFF and MT_ON series from list!")
            series_IVIM = weasel.series()
        else:
            series_IVIM = series

        bvalues_unique = np.array(weasel.unique_elements(series_IVIM[(0x0019,0x100C)]))
        #bvecs_list = series["DiffusionGradientOrientation"]
        #Check if the data corresponds to the Siemens protocol (more than 1 unique b-value)        
        if len(bvalues_unique) >= 1:
            weasel.message(msg="Calculating Diffusion Map")
            
            # Get Pixel Array and format it accordingly
            series_IVIM.sort("SliceLocation")

            #IVIM images reshaped (y,x,z*b-values) -> (x,y,z*b-values)
            pixel_array_IVIM = series_IVIM.PixelArray
            pixel_array_IVIM = np.transpose(pixel_array_IVIM)

            slice_locations = weasel.unique_elements(series_IVIM["SliceLocation"])

            reformat_shape_IVIM = (np.shape(pixel_array_IVIM)[0], np.shape(pixel_array_IVIM)[1],len(slice_locations),int(len(series_IVIM[(0x0019,0x100C)])/len(slice_locations))) # (x, y, z*b-values) => (x, y, z, b-values)

            pixel_array_IVIM = pixel_array_IVIM.reshape(reformat_shape_IVIM) # (x,y, z and b) => (x, y, z, b)
            
            #ACTION FOR LATER# Extract b-values from gradient files
            #b-values hardcoded
            bvalues_list = np.array([0,10,20,30,50,80,100,200,300,600,0,10,20,30,50,80,100,200,300,600,0,10,20,30,50,80,100,200,300,600])
            sequenceParam = [bvalues_list]

            # Calculate maps and save them to DICOM
            #plt.imshow(pixel_array_IVIM[58:96,108:132,0,0])
            #plt.show()
            #pixel_array_IVIM = pixel_array_IVIM[58:96,108:132,12:17,:]
            
            #IVIM mapping, input: IVIM images (x,y,z,b-values), b-values, weasel as optional argument to create progress bars in to weasel interface
            #S0map, Dmap, Dsmap,fmap, rsquaremap = IVIM_pixelwise_fit.main(pixel_array_IVIM,sequenceParam, GUI_object=weasel)
            
            if mask is not None:
                mask=np.transpose(mask)
                for i_slice in range (np.shape(pixel_array_IVIM)[2]):
                    for i_w in range (np.shape(pixel_array_IVIM)[3]):
                        pixel_array_IVIM[:,:,i_slice,i_w]=pixel_array_IVIM[:,:,i_slice,i_w]*mask
            
            S0map, Dmap,rsquaremap = IVIM_pixelwise_fit.main(pixel_array_IVIM,sequenceParam, GUI_object=weasel)

            #Weasel vizualitation of IVIM mapping parameters: D map, D* map, S0 map, D* fraction map, r square (goodness of fit)
            S0_map_series = series_IVIM.new(series_name="S0_Map")
            S0_map_series.write(np.transpose(S0map), value_range=[-10000, 10000])

            D_map_series = series_IVIM.new(series_name="D_Map")
            D_map_series.write(np.transpose(Dmap), value_range=[-10000, 10000])

            #Ds_map_series = series_IVIM.new(series_name="Ds_Map")
            #Ds_map_series.write(np.transpose(Dsmap), value_range=[-10000, 10000])

            #f_map_series = series_IVIM.new(series_name="f_Map")
            #f_map_series.write(np.transpose(fmap), value_range=[-10000, 10000])

            rsquaremap_series = series_IVIM.new(series_name="rsquaremap")
            rsquaremap_series.write(np.transpose(rsquaremap), value_range=[-10000, 10000])
            
            # Display series
            #S0_map_series.display()
            #D_map_series.display()
            #Ds_map_series.display()
            #f_map_series.display()
            #rsquaremap_series.display()

            # Refresh Weasel
            weasel.refresh()
            #output_folder = weasel.select_folder()
            #S0_map_series.export_as_nifti(directory=output_folder)
            #D_map_series.export_as_nifti(directory=output_folder)
            #Ds_map_series.export_as_nifti(directory=output_folder)
            #f_map_series.export_as_nifti(directory=output_folder)
            #rsquaremap_series.export_as_nifti(directory=output_folder)
            if (export_ROI == True):
                return Dmap

        else:
            weasel.warning("The selected series doesn't have sufficient requirements to calculate the IVIM Parameters.", "IVIM Sequence not selected")
    except Exception as e:
        weasel.log_error('Error in function IVIM_Siemens_MapButton.main: ' + str(e))