import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# These 2 lines are required if you're importing an external
# python package that doesn't have "pip install" and that's located
# in the same folder as the current menu script.
import Joint_T1_T2_pixelwise_fit
import numpy as np
import matplotlib.pyplot as plt

#***************************************************************************

def isSeriesOnly(self):
    return True
    #it is required the user selects both T1 series and T2 series (T1 should be the first series)
def main(weasel, series=None, mask=None,export_ROI=False):
    try:
        if series is None:
            weasel.message(msg="Please Select MT_OFF and MT_ON series from list!")
            list_of_series = weasel.series()
        else:
            list_of_series = series

        series_T1 = list_of_series[0]
        series_T2 = list_of_series[1]

        #ACTION FOR LATER#  TIs and TEs are hardcoded (for now) accordingly to the Siemens pulse sequence details
        TI_list = np.array([100, 608, 1113, 1620, 2128, 2633, 3140, 3648, 4153, 4660, 5168, 5673, 6180, 6688, 7193, 7700, 180, 685, 1193, 1700, 2205, 2713, 3220, 3725, 260, 768, 1275, 1780]) 
        echo_list = np.array([0,30,40,50,60,70,80,90,100,110,120])

        #Check if the data corresponds to the Siemens protocol (11 TEs and 28 TIs)
        if len(echo_list) == 11 and len(TI_list) == 28:
            
            weasel.message(msg="Calculating T1 & T2 Map from sequence ")


            # Get Pixel Array and format it accordingly
            series_magnitude_T1 = series_T1.Magnitude.sort("SliceLocation","AcquisitionTime")
            series_magnitude_T2 = series_T2.Magnitude.sort("SliceLocation","EchoTime")
            
            #T2 Magnitude images reshaped (y,x,z*TE) -> (x,y,z*TE)
            pixel_array_T2 = series_magnitude_T2.PixelArray
            pixel_array_T2 =np.transpose(pixel_array_T2)
            #print(np.shape(pixel_array_T2))

            reformat_shape_T2 = (np.shape(pixel_array_T2)[0], np.shape(pixel_array_T2)[1],int(np.shape(pixel_array_T2)[2]/len(echo_list)),len(echo_list))
            #print(reformat_shape_T2)

            magnitude_array_T2 = pixel_array_T2.reshape(reformat_shape_T2) # (x, y, z*TE) => (x, y, z, TE)

            #T1 Magnitude images reshaped (y,x,z*TE) -> (x,y,z*TE)
            pixel_array_T1 = series_magnitude_T1.PixelArray
            pixel_array_T1 =np.transpose(pixel_array_T1)
            #print(np.shape(pixel_array_T1))
            
            new_pixel_array_T1  = np.zeros((np.size(pixel_array_T1,0), np.size(pixel_array_T1,1), np.size(pixel_array_T1,2)))
            inds = TI_list.argsort()
            inds_sort = inds.argsort()


            for i in range(np.shape(pixel_array_T1)[2]):
                new_pixel_array_T1 [:,:,i] = pixel_array_T1[:,:,inds_sort[i]]

            #plt.plot(np.squeeze(pixel_array_T1[182,124,:]))
            #plt.show
            #plt.plot(np.squeeze(new_pixel_array_T1[182,124,:]))
            #plt.show



            reformat_shape_T1 = (np.shape(pixel_array_T1)[0], np.shape(pixel_array_T1)[1],int(np.shape(pixel_array_T1)[2]/len(TI_list)),len(TI_list))            # The np.squeeze below is for the High-Res case where it's single slice - if there is one
            #print(reformat_shape_T1)
            
            magnitude_array_T1 = new_pixel_array_T1.reshape(reformat_shape_T1) # (x, y, z*TI) => (x, y, z, TI)
            
            #ACTION FOR LATER# Extract sequence details from DICOM headers (Flip Angle, TR, k-space lines)
            #sequence parameters for T1 (Inversion Times: TI_list) and T2 mapping (echo times: echo_list)
            sequenceParam = [TI_list,echo_list]

            #magnitude_array_T1 = magnitude_array_T1[126:223,230:300,2:3,:]
            #magnitude_array_T2 = magnitude_array_T2[126:223,230:300,2:3,:]


            
            if mask is not None:
                mask = np.transpose(mask)
                for i_slice in range (np.shape(magnitude_array_T1)[2]):
                    for i_w in range (np.shape(magnitude_array_T1)[3]):
                        magnitude_array_T1[:,:,i_slice,i_w]=magnitude_array_T1[:,:,i_slice,i_w]*mask
                for i_slice_T2 in range (np.shape(magnitude_array_T2)[2]):
                    for i_w_T2 in range (np.shape(magnitude_array_T2)[3]):
                        magnitude_array_T2[:,:,i_slice_T2,i_w_T2]=magnitude_array_T2[:,:,i_slice_T2,i_w_T2]*mask

            #joint T1 & T2 mapping, input: T1-weighted images (x,y,z,TI), T1-weighted images (x,y,z,TE), Sequence parameters: 1.Inversion Times and 2.echo times, weasel as optional argument to create progress bars in to weasel interface
            T1_Map, T2_Map, M0_Map, FA_Eff_Map, Ref_Eff_Map, T1_rsquare_map, T2_rsquare_map = Joint_T1_T2_pixelwise_fit.main(magnitude_array_T1, magnitude_array_T2, sequenceParam, GUI_object=weasel)

            #Weasel vizualitation of T1 & T2 mapping parameters: T1 map, T2 map, M0 map, FA Efficency map, T1 & T2 r square (goodness of fit)
            t1_map_series = series_magnitude_T1.new(series_name="T1_Map")
            t1_map_series.write(np.transpose(T1_Map), value_range=[-10000, 10000])
            
            t2_map_series = series_magnitude_T2.new(series_name="T2_Map")
            t2_map_series.write(np.transpose(T2_Map), value_range=[-10000, 10000])
            
            m0_map_series = series_magnitude_T1.new(series_name="M0_Map")
            m0_map_series.write(np.transpose(M0_Map), value_range=[-10000, 10000])

            FA_Eff_map_series = series_magnitude_T1.new(series_name="FA_Eff_Map")
            FA_Eff_map_series.write(np.transpose(FA_Eff_Map), value_range=[-10000, 10000])

            t1_rsquare_map_series = series_magnitude_T1.new(series_name="T1_rsquare_map")
            t1_rsquare_map_series.write(np.transpose(T1_rsquare_map), value_range=[-10000, 10000])

            t2_rsquare_map_series = series_magnitude_T2.new(series_name="T2_rsquare_map")
            t2_rsquare_map_series.write(np.transpose(T2_rsquare_map), value_range=[-10000, 10000])
            


            # Display series
            #t1_map_series.display()
            #t2_map_series.display()
            #m0_map_series.display()
            #FA_Eff_map_series.display()
            #t1_rsquare_map_series.display()
            #t2_rsquare_map_series.display()


            # Refresh Weasel
            weasel.refresh()
            #output_folder = weasel.select_folder()
            #t1_map_series.export_as_nifti(directory=output_folder)
            #t2_map_series.export_as_nifti(directory=output_folder)
            #m0_map_series.export_as_nifti(directory=output_folder)
            #FA_Eff_map_series.export_as_nifti(directory=output_folder)
            #t1_rsquare_map_series.export_as_nifti(directory=output_folder)
            #t2_rsquare_map_series.export_as_nifti(directory=output_folder)
            if (export_ROI == True):
                return T1_Map, T2_Map

        else:
            weasel.warning("The selected series doesn't have sufficient requirements to calculate the joint T1 & T2 Map.", "T1 or T2 Sequence not selected")
    except Exception as e:
        weasel.log_error('Error in function T1 & T2 Siemens MapButton.main: ' + str(e))