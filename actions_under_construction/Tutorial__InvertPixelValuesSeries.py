
    
#**************************************************************************
# Inverts a number of selected images in place, 
# series by series and showing a progress bar
#***************************************************************************

def main(weasel):
    list_of_series = weasel.series()    # get the list of all series checked by the user
    for i, series in enumerate(list_of_series): # Loop over series and display a progress Bar
        weasel.progress_bar(max=len(list_of_series), index=i+1, msg="Inverting series {}", title="Invert pixel values ")
        series.write(-series.array())     # Invert the pixel array and overwrite existing pixel array
    list_of_series.display()        # Display all Series in the list
    weasel.refresh()