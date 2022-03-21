
    
#**************************************************************************
# Thresholds a number of selected images into a new series
#***************************************************************************
import numpy as np

def main(weasel):
    list_of_images = weasel.images()    # get the list of images checked by the user
    if len(list_of_images) == 0: return   # if the user cancels then exit
    
    cancel = 0
    while cancel == 0:
        cancel, input_list = weasel.user_input(
            {"type":"integer", "label":"Lower Threshold", "value":30, "minimum":0, "maximum":100},
            {"type":"integer", "label":"Upper Threshold", "value":70, "minimum":0, "maximum":100}, 
            title = "Insert lower and upper thresholds")
        if cancel: return
        lower_thresh = input_list[0]['value']
        upper_thresh = input_list[1]['value']
        if lower_thresh >= upper_thresh:
            weasel.error("Not possible to threshold the selected images. The upper threshold must be greater than the lower threshold.", "Threshold Input Error")
        else:
            cancel = 1

    threshold = list_of_images.copy()
    for i, image in enumerate(threshold): # Loop over images and display a progress Bar
        weasel.progress_bar(max=len(list_of_images), index=i+1, msg="Thresholding image {}")
        image.write(Thresholded(image.array(), lower_thresh, upper_thresh))
    threshold.merge().display()            # Display all images in the list in a single display
    weasel.refresh()


def Thresholded(pixelArray, lower_threshold, upper_threshold):
    # It doesn't work correctly with negative values, so something isn't correct
    maximum_value = np.amax(pixelArray)
    minimum_value = np.amin(pixelArray)
    upper_value = minimum_value + (upper_threshold / 100) * (maximum_value - minimum_value)
    lower_value = minimum_value + (lower_threshold / 100) * (maximum_value - minimum_value)

    thresholdedArray = pixelArray
    thresholdedArray[thresholdedArray < lower_value] = 0
    thresholdedArray[thresholdedArray > upper_value] = 0
    thresholdedArray[thresholdedArray != 0] = 1
    return thresholdedArray
