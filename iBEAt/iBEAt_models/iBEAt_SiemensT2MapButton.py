import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# These 2 lines are required if you're importing an external
# python package that doesn't have "pip install" and that's located
# in the same folder as the current menu script.
from iBEAt import Joint_T1_T2_Fit
import numpy as np
#***************************************************************************

def isSeriesOnly(self):
    return True

def main(weasel):
    try:
        series = weasel.series()[0]
        echo_list = weasel.unique_elements(series["EchoTime"])
        if len(echo_list) >= 6 and weasel.match_search(".*T2_.*", series.label):
            weasel.message(msg="Calculating T2 Map from sequence " + series.label, title="T2 Map")
            if 0 in echo_list: echo_list.remove(0)
            # Get Pixel Array and format it accordingly
            series_magnitude = series.Magnitude.sort("EchoTime", "SliceLocation")
            pixel_array = series_magnitude.PixelArray
            reformat_shape = (len(echo_list), int(np.shape(pixel_array)[0]/len(echo_list)), np.shape(pixel_array)[1], np.shape(pixel_array)[2])
            # The np.squeeze below is for the High-Res case where it's single slice - if there is one
            magnitude_array = np.squeeze(np.transpose(pixel_array.reshape(reformat_shape))) # (te, z, y, x) => (x, y, z, te) after the np.transpose
            affine_array = series_magnitude.Affine
            mask = magnitude_array[..., -1] >= 0.0 # Generate a mask based on the signal intensity of the last echo (UKAT value is 50)
            # Initialise the T2 Mapping object - 2 or 3 parameters?
            #mapper_2p = T2(magnitude_array, echo_list, affine_array, mask, method='2p_exp')
            mapper_3p = T2(magnitude_array, np.array(echo_list), affine_array, mask, multithread=False, method='3p_exp')
            # Extract the T2 map, T2 error, M0 map, M0 error from the object
            T2_Map = mapper_3p.t2_map
            t2_map_series = series_magnitude.new(series_name="T2_Map")
            t2_map_series.write(np.transpose(T2_Map), value_range=[-10000, 10000])
            t2_map_series["EchoTime"] = 0.0
            T2_Map_Error = mapper_3p.t2_err
            t2_map_error_series = series_magnitude.new(series_name="T2_Error_Map")
            t2_map_error_series.write(np.transpose(T2_Map_Error), value_range=[-10000, 10000])
            t2_map_error_series["EchoTime"] = 0.0
            M0_Map = mapper_3p.m0_map
            m0_map_series = series_magnitude.new(series_name="M0_Map")
            m0_map_series.write(np.transpose(M0_Map), value_range=[-10000, 10000])
            m0_map_series["EchoTime"] = 0.0
            M0_Map_Error = mapper_3p.m0_err
            m0_map_error_series = series_magnitude.new(series_name="M0_Error_Map")
            m0_map_error_series.write(np.transpose(M0_Map_Error), value_range=[-10000, 10000])
            m0_map_error_series["EchoTime"] = 0.0
            # Maybe change Image Type DICOM tag to T2?
            # Display series
            t2_map_series.display()
            t2_map_error_series.display()
            m0_map_series.display()
            m0_map_error_series.display()
            # Refresh Weasel
            weasel.refresh()
            output_folder = weasel.select_folder()
            t2_map_series.export_as_nifti(directory=output_folder)
            t2_map_error_series.export_as_nifti(directory=output_folder)
            m0_map_series.export_as_nifti(directory=output_folder)
            m0_map_error_series.export_as_nifti(directory=output_folder)
        else:
            weasel.warning("The selected series doesn't have sufficient requirements to calculate the T2 Map.", "T2 Sequence not selected")
    except Exception as e:
        weasel.log_error('Error in function T2MapButton.main: ' + str(e))