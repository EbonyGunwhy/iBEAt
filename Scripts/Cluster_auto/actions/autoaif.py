import os
import numpy as np

import actions.reggrow as reg
import cv2
import matplotlib.pyplot as plt

    
def DCEautoAIF(array, header, series,targetslice, cutRatio, filter_kernel, regGrow_threshold ):

    if np.shape(array)[-1] == 2:
        array = array[...,0]

    if np.shape(header)[-1] == 2:
        header = header[...,0:1]


    aortaImgs = array[:,:,targetslice-1,...]
    verticalCenter = int(np.shape(aortaImgs)[0]/2)
    horizontalCenter = int(np.shape(aortaImgs)[1]/2)
    verticalLimInf = int(verticalCenter-verticalCenter*cutRatio)
    verticalLimSup = int(verticalCenter+verticalCenter*cutRatio)
    horizontalLimInf  = int(horizontalCenter-horizontalCenter*cutRatio)
    horizontalLimSup = int(horizontalCenter+horizontalCenter*cutRatio)

    aortaImgs_cut = np.empty(np.shape(aortaImgs))
    aortaImgs_cut[verticalLimInf:verticalLimSup,horizontalLimInf:horizontalLimSup,...] = aortaImgs [verticalLimInf:verticalLimSup,horizontalLimInf:horizontalLimSup,...]
    aortaImgs_cutMaxMin = np.squeeze(np.max(aortaImgs_cut,axis=2)-np.min(aortaImgs_cut,axis=2))

    aortaImgs_cutMaxMinBlurred = cv2.GaussianBlur(aortaImgs_cutMaxMin, filter_kernel,cv2.BORDER_DEFAULT)
    (minVal1, maxVal1, minLoc1, maxLoc1) = cv2.minMaxLoc(aortaImgs_cutMaxMinBlurred)
    aortaImgs_cutMaxMinBlurred [maxLoc1[1],maxLoc1[0]] = 0
    (minVal2, maxVal2, minLoc2, maxLoc2) = cv2.minMaxLoc(aortaImgs_cutMaxMinBlurred)
    aortaImgs_cutMaxMinBlurred [maxLoc2[1],maxLoc2[0]] = 0
    (minVal3, maxVal3, minLoc3, maxLoc3) = cv2.minMaxLoc(aortaImgs_cutMaxMinBlurred)

    seeds = [reg.Point(maxLoc1[1],maxLoc1[0]),reg.Point(maxLoc2[1],maxLoc2[0]),reg.Point(maxLoc3[1],maxLoc3[0])]
    max_iteration = 20
    for i in range(max_iteration):
        aif_mask = reg.regionGrow(aortaImgs_cutMaxMin,seeds,regGrow_threshold)
        if len(aif_mask[aif_mask==1]) < 100:
            regGrow_threshold = regGrow_threshold + i
            continue
        else:
            break

    aif_mask = aif_mask[..., np.newaxis]

    aif_maskTowezel = series.SeriesDescription + '_DCE_ART'
    aif_maskTowezel = series.new_sibling(SeriesDescription=aif_maskTowezel)

    aif_maskTowezel.set_array(aif_mask, (header[targetslice-1,0]), pixels_first=True)

    aif =[]
    for z in range(aortaImgs_cut.shape[2]):
        tmask = np.squeeze(aortaImgs[:,:,z]) * np.squeeze(aif_mask)
        aif.append(np.mean(tmask[tmask!=0]))

    return aif
