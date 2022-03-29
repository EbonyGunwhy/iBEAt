from weasel.core import Action
import weasel.actions as actions

#from iBEAt.xnat import Upload, Download
#from iBEAt.rename import Leeds
#import iBEAt.mdr as mdr

def menu(parent): 

    menu = parent.menu('File')
    menu.action(Open, shortcut='Ctrl+O')
    menu.action(actions.folder.Read)
    menu.action(actions.folder.Save, shortcut='Ctrl+S')
    menu.action(actions.folder.Restore, shortcut='Ctrl+R')
    menu.action(actions.folder.Close, shortcut='Ctrl+C')

    actions.edit.menu(parent.menu('Edit'))
    actions.view.menu(parent.menu('View'))

    menu = parent.menu('iBEAt pilot')
    #menu.action(Download, text='Download data from XNAT') # function download
    #menu.action(Leeds, text='Rename DICOMs (Siemens) iBEAt')
    menu.separator()
    #menu.action(mdr.MDRegT2star, text='T2* MDR (Siemens)')
    #menu.action(mdr.MDRegT2, text='T2 MDR (Siemens)')
    #menu.action(mdr.MDRegT1, text='T1 MDR (Siemens)')
    #menu.action(mdr.MDRegDWI, text='IVIM MDR (Siemens)')
    #menu.action(mdr.MDRegDTI, text='DTI MDR (Siemens)')
    #menu.action(mdr.MDRegDCE, text='DCE MDR (Siemens)')
    menu.action(MDR_iBEAt_MT_Button, text='MT MDR (Siemens)')
    menu.separator()
    menu.action(MDR_allSeries_iBEAt_Button, text='MDR ALL SERIES (Siemens) iBEAt')
    menu.action(MDR_allSeries_iBEAt_Button_NO_importing, text = 'MDR ALL SERIES (Siemens) iBEAt (No Import from XNAT)')
    menu.separator()
    menu.action(iBEAt_SiemensT1T2MapButton, text='Joint T1 & T2 Mapping (Siemens)')
    menu.action(iBEAt_SiemensT2sMapButton, text='T2* Mapping (Siemens)')
    menu.action(iBEAt_SiemensIVIMButton, text='IVIM: ADC Mapping (Siemens)')
    menu.action(iBEAt_SiemensDTIButton, text='DTI: FA Mapping (Siemens)')
    menu.separator()
    #menu.action(Upload, text = 'Upload results to XNAT') # function upload

    actions.about.menu(parent.menu('About'))


class Open(Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return True

    def run(self, app):
        """
        Open a DICOM folder and update display.
        """
        # These attributes are used frequently in iBEAt.
        # They are loaded up front to avoid rereading 
        # the folder every time they are needed.
        attributes = [
            'SliceLocation', 'AcquisitionTime', 
            'FlipAngle', 'EchoTime', 'InversionTime',   
            'DiffusionBValue',                          
        ]
        app.status.message("Opening DICOM folder..")
        path = app.dialog.directory("Select a DICOM folder")
        if path == '':
            app.status.message('') 
            return
        app.status.cursorToHourglass()
        app.close()
        app.folder.set_attributes(attributes, scan=False)
        app.open(path)
        app.status.cursorToNormal()



class MDR_iBEAt_MT_Button(Action):
    pass

class MDR_allSeries_iBEAt_Button(Action):
    pass

class MDR_allSeries_iBEAt_Button_NO_importing(Action):
    pass

class iBEAt_SiemensT1T2MapButton(Action):
    pass

class iBEAt_SiemensT2sMapButton(Action):
    pass

class iBEAt_SiemensIVIMButton(Action):
    pass

class iBEAt_SiemensDTIButton(Action):
    pass



