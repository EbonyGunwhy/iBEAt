import os
import numpy as np
import weasel
import models.T2s_pixelwise_fit

class allSeries(weasel.Action):
    pass

class DCE_Button_modelling_only(weasel.Action):
    pass

class SiemensT1T2MapButton(weasel.Action):
    pass

class SiemensIVIMButton(weasel.Action):
    pass

class SiemensDTIButton(weasel.Action):
    def run(self, app, series=None, mask=None,export_ROI=False):

        if series is None:
            series_DTI = app.get_selected(3)[0]
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
            #weasel.message(msg="Calculating FA Map")
            
            # Get Pixel Array and format it accordingly
            array, header = series_DTI.array(['SliceLocation', 'InversionTime'], pixels_first=True)
            pixel_array_DTI = array

            bvecs = np.array(series_DTI[(0x0019,0x100E)])

            bvals = series_DTI[(0x0019,0x100C)]
            bvals = [int(x) for x in bvals]
            bvals = np.array(bvals)

            b_values = [float(hdr[(0x19, 0x100c)]) for hdr in header[:,:,0]]
            b_vectors = [hdr[(0x19, 0x100e)] for hdr in header[:,:,0]]
            orientation = [hdr.ImageOrientationPatient for hdr in header[:,:,0]] 



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

            FA_map_series = series_DTI.SeriesDescription + "_DTI_Map_" + "FA_Map"
            FA_map_series = series_DTI.new_sibling(SeriesDescription=FA_map_series)
            FA_map_series.set_array(np.squeeze(FAmap),np.squeeze(header[:,0],pixels_first=True))
        
            # Display series
            #FA_map_series.display()

            # Refresh Weasel
            app.refresh()
            #output_folder = weasel.select_folder()
            #FA_map_series.export_as_nifti(directory=output_folder)
            if (export_ROI == True):
                return FAmap

        else:
            app.warning("The selected series doesn't have sufficient requirements to calculate the DTI Parameters.", "DTI Sequence not selected")


class SiemensT2sMapButton(weasel.Action):
    
    def run(self, app, series=None, mask=None,export_ROI=False,slice=None,Fat_export=False):

        if series is None:
            series_T2s = series = app.get_selected(3)[0]
        else:
            series_T2s = series

        array, header = series.array(['SliceLocation', 'EchoTime'], pixels_first=True)

        TE_list = [hdr["EchoTime"] for hdr in (header[0,:,0])] 

        #Check if the data corresponds to the Siemens protocol (12 TEs)        
        if len(TE_list) == 12 and np.max(TE_list) < 50:

            app.dialog.information("T2* Mapping has started")

            magnitude_array_T2s = array

            if slice is not None:
                magnitude_array_T2s_slice = magnitude_array_T2s[:,:,int(slice-1),:]
                magnitude_array_T2s = magnitude_array_T2s_slice

            if mask is not None:
                mask = np.transpose(mask)
                for i_slice in range (np.shape(magnitude_array_T2s)[2]):
                    for i_w in range (np.shape(magnitude_array_T2s)[3]):
                        magnitude_array_T2s[:,:,i_slice,i_w]=magnitude_array_T2s[:,:,i_slice,i_w]*mask

            #T2* mapping input: T2*-weighted images (x,y,z,TE), echo times, weasel as optional argument to create progress bars in to weasel interface
            M0map, fwmap, T2smap, rsquaremap = models.T2s_pixelwise_fit.main(magnitude_array_T2s[128:384,128:384,...], TE_list, GUI_object=weasel)

            #Weasel vizualitation of T2* mapping parameters: M0 map, Water Fraction map, T2* map,T2* r square (goodness of fit)
            M0_map_series = series_T2s.SeriesDescription + "_T2s_Map_" + "M0_Map"
            M0_map_series = series_T2s.new_sibling(SeriesDescription=M0_map_series)
            M0_map_series.set_array(M0map,np.squeeze(header[:,0]),pixels_first=True)

            fw_map_series = series_T2s.SeriesDescription + "_T2s_Map_" + "fw_Map"
            fw_map_series = series_T2s.new_sibling(SeriesDescription=fw_map_series)
            fw_map_series.set_array(fwmap,np.squeeze(header[:,0]),pixels_first=True)

            T2s_map_series = series_T2s.SeriesDescription + "_T2s_Map_" + "T2s_Map"
            T2s_map_series = series_T2s.new_sibling(SeriesDescription=T2s_map_series)
            T2s_map_series.set_array(T2smap,np.squeeze(header[:,0]),pixels_first=True)

            rsquare_map_series = series_T2s.SeriesDescription + "_T2s_Map_" + "rsquare_Map"
            rsquare_map_series = series_T2s.new_sibling(SeriesDescription=rsquare_map_series)
            rsquare_map_series.set_array(rsquaremap,np.squeeze(header[:,0]),pixels_first=True)

            app.refresh()

            if (export_ROI == True and Fat_export==False):
                return T2smap
            elif(export_ROI == True and Fat_export==True):
                return T2smap, np.squeeze(mask)-np.squeeze(fwmap)

        else:
            app.warning("The selected series doesn't have sufficient requirements to calculate the T2* Map.", "T2* Sequence not selected")
