import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# These 2 lines are required if you're importing an external
# python package that doesn't have "pip install" and that's located
# in the same folder as the current menu script.

import numpy as np
import matplotlib.pyplot as plt
from dipy.core.gradients import gradient_table
import dipy.reconst.dti as dti
from dipy.reconst.dti import fractional_anisotropy, color_fa


#***************************************************************************

def isSeriesOnly(self):
    return True

def main(weasel, series=None, mask=None,export_ROI=False):
    try:
        if series is None:
            weasel.message(msg="Calculating FA from DTI")
            series_DTI = weasel.series()[0]
        else:
            series_DTI = series
            
        bvecs = np.array(series_DTI[(0x0019,0x100E)])

        bvals = series_DTI[(0x0019,0x100C)]
        bvals = [int(x) for x in bvals]
        bvals = np.array(bvals)
        

        image_orientation_patient = series_DTI[(0x0020,0x0037)]


        #bvecs_list = series["DiffusionGradientOrientation"]
        #Check if the data corresponds to the Siemens protocol (more than 1 unique b-value)        
        if len(bvals) >= 1 and np.shape(bvecs)[0] >=6:
            weasel.message(msg="Calculating FA Map")
            
            # Get Pixel Array and format it accordingly
            series_DTI.sort("SliceLocation")

            bvecs = np.array(series_DTI[(0x0019,0x100E)])

            bvals = series_DTI[(0x0019,0x100C)]
            bvals = [int(x) for x in bvals]
            bvals = np.array(bvals)



            #IVIM images reshaped (y,x,z*b-values) -> (x,y,z*b-values)
            pixel_array_DTI = series_DTI.PixelArray
            pixel_array_DTI = np.transpose(pixel_array_DTI)

            slice_locations = weasel.unique_elements(series_DTI["SliceLocation"])
            #print(np.shape(bvecs)[0])
            reformat_shape_DTI = (np.shape(pixel_array_DTI)[0], np.shape(pixel_array_DTI)[1],len(slice_locations),int(np.shape(bvecs)[0]/len(slice_locations))) # (x, y, z*b-values) => (x, y, z, b-values)
            #print(reformat_shape_DTI)

            pixel_array_DTI = np.squeeze(pixel_array_DTI.reshape(reformat_shape_DTI)) # (x,y, z and b) => (x, y, z, b)
            bvals = bvals[0:int(np.shape(bvecs)[0]/len(slice_locations))]
            bvecs = bvecs[0:int(np.shape(bvecs)[0]/len(slice_locations))]
            #print(np.shape(pixel_array_DTI))
            #print(np.shape(bvals))
            #print(np.shape(bvecs))
         

######FROM DIPY
            gtab = gradient_table(bvals, bvecs)
            tenmodel = dti.TensorModel(gtab)
            tenfit = tenmodel.fit(pixel_array_DTI)

            FAmap = fractional_anisotropy(tenfit.evals)
######FROM DIPY          

            FAmap[np.isnan(FAmap)] = 0

            FA_map_series = series_DTI.new(series_name="FA_Map")
            FA_map_series.write(np.transpose(FAmap), value_range=[-10000, 10000])
          
            # Display series
            #FA_map_series.display()

            # Refresh Weasel
            weasel.refresh()
            #output_folder = weasel.select_folder()
            #FA_map_series.export_as_nifti(directory=output_folder)
            if (export_ROI == True):
                return FAmap

        else:
            weasel.warning("The selected series doesn't have sufficient requirements to calculate the DTI Parameters.", "DTI Sequence not selected")
    except Exception as e:
        weasel.log_error('Error in function DTI_Siemens_MapButton.main: ' + str(e))