
    
import logging
logger = logging.getLogger(__name__)

from welovewewidgets.ViewMetaData import displayMetaDataSubWindow

def main(weasel):
    """Creates a subwindow that displays a DICOM image's metadata. """
    try:
        logger.info("View__DICOMheader called")
        series_list = weasel.series()
        if series_list == []: 
            for img in weasel.images(msg = 'No images checked'):
                displayMetaDataSubWindow(weasel, "Metadata for image {}".format(img.label()), img.read())
        else:
            for series in series_list:
                img = series.children[0]
                displayMetaDataSubWindow(weasel, "Metadata for image {}".format(img.label()), img.read())
    except (IndexError, AttributeError):
        weasel.information(msg="Select either a series or an image", title="View DICOM header")
    except Exception as e:
        print('Error in View__DICOMheader: ' + str(e))
        logger.error('Error in View__DICOMheader: ' + str(e))