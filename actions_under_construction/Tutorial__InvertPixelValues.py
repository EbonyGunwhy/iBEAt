

#**************************************************************************
# Inverts a number of selected images in place, 
# image by image and showing a progress bar
#***************************************************************************

def main(weasel):
    list_of_images = weasel.images()    # get the list of images checked by the user
    for i, image in enumerate(list_of_images): # Loop over images and display a progress Bar
        weasel.progress_bar(max=len(list_of_images), index=i+1, msg="Inverting image {}")
        image.write(-image.array())      # Invert the pixel array and overwrite existing pixel array
    list_of_images.display()            # Display all images in the list in a single display
    weasel.refresh()