
    
#**************************************************************************
# Apply Gaussian filter to a number of selected images in new series
#***************************************************************************
import scipy.ndimage as ndimage

def main(weasel):
    list_of_images = weasel.images()    # get the list of images checked by the user
    if len(list_of_images) == 0: return   # if the user cancels then exit
    
    cancel, input_list = weasel.user_input(
        {"type":"integer", "label":"Size in pixels", "value":5, "minimum":1, "maximum":1000}, 
        title = "Select Gaussian Filter size")
    if cancel: return
    size = input_list[0]['value']
    
    filtered = list_of_images.copy()
    for i, image in enumerate(filtered): # Loop over images and display a progress Bar
        weasel.progress_bar(max=len(list_of_images), index=i+1, msg="Filtering image {} with gaussian filter")
        image.write(ndimage.gaussian_filter(image.array(), sigma=size))
    filtered.merge().display()
    weasel.refresh()
    