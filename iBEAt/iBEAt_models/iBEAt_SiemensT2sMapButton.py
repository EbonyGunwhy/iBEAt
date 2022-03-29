import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# These 2 lines are required if you're importing an external
# python package that doesn't have "pip install" and that's located
# in the same folder as the current menu script.
import numpy as np
import T2s_pixelwise_fit
import matplotlib.pylab as plt
#***************************************************************************

def isSeriesOnly(self):
    return True

def main(weasel, series=None, mask=None,export_ROI=False,slice=None,Fat_export=False):
    try:
        if series is None:
            weasel.message(msg="T2* Mapping has started")
            series_T2s = weasel.series()[0]
        else:
            series_T2s = series

        #series_T2s = series()[0]
        TE_list = np.array(weasel.unique_elements(series_T2s["EchoTime"]))
        #print(TE_list)
        #Check if the data corresponds to the Siemens protocol (12 TEs)        
        if len(TE_list) == 12 and np.max(TE_list) < 50:
            
            weasel.message(msg="Calculating T2* Map from T2* sequence ")

            # Get Pixel Array and format it accordingly
            series_magnitude_T2s = series_T2s.Magnitude.sort("SliceLocation","EchoTime")
            
            #T2s Magnitude images reshaped (y,x,z*TE) -> (x,y,z*TE)
            pixel_array_T2s = series_magnitude_T2s.PixelArray
            pixel_array_T2s =np.transpose(pixel_array_T2s)

            reformat_shape_T2s = (np.shape(pixel_array_T2s)[0], np.shape(pixel_array_T2s)[1],int(np.shape(pixel_array_T2s)[2]/len(TE_list)),len(TE_list))

            magnitude_array_T2s = pixel_array_T2s.reshape(reformat_shape_T2s) # (x, y, z*TE) => (x, y, z, TE)

            #magnitude_array_T2s = magnitude_array_T2s[172:292,311:397,2:4,:]
            if slice is not None:
                magnitude_array_T2s_slice = magnitude_array_T2s[:,:,int(slice-1),:]
                magnitude_array_T2s = magnitude_array_T2s_slice.reshape(np.shape(pixel_array_T2s)[0], np.shape(pixel_array_T2s)[1],1,len(TE_list))


            #print(np.shape(magnitude_array_T2s))
            #print(np.shape(mask))
            if mask is not None:
                mask = np.transpose(mask)
                for i_slice in range (np.shape(magnitude_array_T2s)[2]):
                    for i_w in range (np.shape(magnitude_array_T2s)[3]):
                        magnitude_array_T2s[:,:,i_slice,i_w]=magnitude_array_T2s[:,:,i_slice,i_w]*mask

            #T2* mapping input: T2*-weighted images (x,y,z,TE), echo times, weasel as optional argument to create progress bars in to weasel interface
            M0map, fwmap, T2smap, rsquaremap = T2s_pixelwise_fit.main(magnitude_array_T2s, TE_list, GUI_object=weasel)

            #Weasel vizualitation of T2* mapping parameters: M0 map, Water Fraction map, T2* map,T2* r square (goodness of fit)
            M0_map_series = series_magnitude_T2s.new(series_name="M0_Map")
            M0_map_series.write(np.transpose(M0map), value_range=[-10000, 10000])

            fw_map_series = series_magnitude_T2s.new(series_name="fw_Map")
            fw_map_series.write(np.transpose(fwmap), value_range=[-10000, 10000])
            
            T2s_map_series = series_magnitude_T2s.new(series_name="T2s_Map")
            T2s_map_series.write(np.transpose(T2smap), value_range=[-10000, 10000])

            rsquaremap_series = series_magnitude_T2s.new(series_name="rsquaremap")
            rsquaremap_series.write(np.transpose(rsquaremap), value_range=[-10000, 10000])
            
            # Display series
            #M0_map_series.display()
            #fw_map_series.display()
            #T2s_map_series.display()
            #rsquaremap_series.display()

            # Refresh Weasel
            weasel.refresh()
            #output_folder = weasel.select_folder()
            #M0_map_series.export_as_nifti(directory=output_folder)
            #fw_map_series.export_as_nifti(directory=output_folder)
            #T2s_map_series.export_as_nifti(directory=output_folder)
            if (export_ROI == True and Fat_export==False):
                return T2smap
            elif(export_ROI == True and Fat_export==True):
                return T2smap, np.squeeze(mask)-np.squeeze(fwmap)

        else:
            weasel.warning("The selected series doesn't have sufficient requirements to calculate the T2* Map.", "T2* Sequence not selected")
    except Exception as e:
        weasel.log_error('Error in function T2s_Siemens_MapButton.main: ' + str(e))