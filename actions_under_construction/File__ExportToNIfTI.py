
def main(weasel):
    try:
        dicomList = weasel.series()
        if len(dicomList) == 0: dicomList = weasel.images()
        if len(dicomList) == 0: return
        local_path = weasel.dialog.directory(weasel)
        if local_path is None: return
        for i, series in enumerate(dicomList):
            weasel.progress(max=len(dicomList), index=i+1, msg="Saving series " + series.label() + " to NIfTI")
            series.export_as_nifti(directory=local_path)
        weasel.hide()
        weasel.dialog.information(msg="Selected series/images successfully saved as NIfTI", title="Export to NIfTI")
    except Exception as e:
        # Record error message in the log and prints in the terminal
        weasel.logError('Error in function File__ExportToNIfTI.main: ' + str(e))
        # If we want to show the message in the GUI
        weasel.dialog.error(weasel, msg=str(e), title="Error Exporting to NIfTI")