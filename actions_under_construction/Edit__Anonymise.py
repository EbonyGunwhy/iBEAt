
#**************************************************************************
# Template part of a tutorial 
# Anonymises the checked images
# showing progress with a status bar 
#***************************************************************************

import pydicom
from pydicom.dataset import Dataset

def main(weasel):
    list_of_images = weasel.images()                 # get the list of images checked by the user
    for i, image in enumerate(list_of_images):      # Loop over Series in the list and display a progress Bar
        weasel.progress_bar(max=len(list_of_images), index=i+1, msg="Anonymising images {}")

        ds = image.read()               # Load the dataset into memory
        ds.PatientName = "Anonymous"    # replace PatientName
        ds.PatientID = pydicom.uid.generate_uid()
        ds.PatientBirthDate = "19000101"
        ds.OtherPatientNames = ["Anonymous 1", "Anonymous 2"]
        ds.OtherPatientIDsSequence = [Dataset(),Dataset()]
        ds.ReferencePatientPhotoSequence = [Dataset(),Dataset()]
        image.save(ds)                  # write the dataset to disk

    weasel.refresh()                # Refresh weasel


    

    