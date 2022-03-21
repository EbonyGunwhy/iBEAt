
    
#**************************************************************************
# Inverts the images in a number of selected series
# and saves them in a new series, 
# series by series and showing a progress bar
#***************************************************************************

def main(weasel):

    list_of_series = weasel.series()      # get the list of series checked by the user
    for i, series in enumerate(list_of_series):              # Loop over Series in the list and display a progress Bar
        weasel.progress_bar(max=len(list_of_series), index=i+1, msg="Inverting series {}")
        new_series = series.new(suffix="_Invert")    # Derive a new series
        new_series.write(-series.array())         # Write the results in the new series
        new_series.display()     # Display the new series 
    weasel.refresh() # Refresh weasel
    