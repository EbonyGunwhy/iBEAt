

#**************************************************************************
# Template part of a tutorial 
# Applies a local filter to checked images and saves them in a new series, 
# image by image and showing a progress bar. 
# Filter settings are derived through user input.
#***************************************************************************

import scipy.ndimage as ndimage
from scipy.signal import wiener

def main(weasel):
    # Get images checked by the user
    list_of_images = weasel.images()
    if len(list_of_images) == 0: return 

    # Get user input: type of filter and size
    filters = ["Gaussian", "Uniform", "Median", "Maximum", "Wiener"]
    cancel, filters_input = weasel.user_input(
            {"type":"dropdownlist", "label":"Which filter?", "list":filters, "default": 2},
            {"type":"integer", "label":"Filter size in pixels", "default":20, "minimum":1, "maximum":1000},
            title = "Filter settings")
    if cancel: return

    filter_name = filters_input[0]
    size = filters_input[1]

    # Loop through the images and overwrite with filtered image

    for i, image in enumerate(list_of_images):
        weasel.progress_bar(max=len(list_of_images), index=i+1, msg="Filtering image {}")
        if filter_name['value'] == 0:
            image.write(ndimage.gaussian_filter(image.array(), sigma=size['value']))
        elif filter_name['value'] == 1:
            image.write(ndimage.uniform_filter(image.array(), size=size['value']))
        elif filter_name['value'] == 2:
            image.write(ndimage.median_filter(image.array(), size=size['value']))
        elif filter_name['value'] == 3:
            image.write(ndimage.maximum_filter(image.array(), size=size['value']))
        elif filter_name['value'] == 4:
            image.write(wiener(image.array(), (size['value'], size['value'])))

    list_of_images.display()
    weasel.refresh()