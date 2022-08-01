import weasel

import actions.modelling as modelling
import actions.macros as macros
import actions.tools as tools
import actions.xnat as xnat
import actions.rename as rename
import actions.mdr as mdr
import actions.kidneyOutline as kidney_segmentation

def pilot(parent): 

    menu = parent.menu('File')
    menu.action(tools.Open, shortcut='Ctrl+O')
    menu.action(tools.OpenSubFolders, text='Read subfolders')
    menu.action(weasel.actions.folder.Read)
    menu.action(weasel.actions.folder.Save, shortcut='Ctrl+S')
    menu.action(weasel.actions.folder.Restore, shortcut='Ctrl+R')
    menu.action(weasel.actions.folder.Close, shortcut='Ctrl+C')

    menu = parent.menu('View')
    menu.action(weasel.actions.view.Series)
    menu.action(tools.RegionDraw, text='Draw ROI')
    menu.action(tools.FourDimArrayDisplay, text='4D Array')
    menu.separator()
    menu.action(weasel.actions.view.CloseWindows, text='Close windows')
    menu.action(weasel.actions.view.TileWindows, text='Tile windows')

    menu = parent.menu('Edit')
    weasel.actions.edit.menu(menu)

    menu = parent.menu('iBEAt-Auto')
    menu.action(macros.MDRegMacro, text='MDR-Auto')
    menu.action(macros.MDRegMacroNoImport, text='MDR-Auto (No XNAT importing)')
    menu.action(macros.MapToExcel, text='Generate Excel File')
    menu.separator()
    menu.action(tools.TimeMIP, text='DCE create AIF (Siemens)')
    menu.action(modelling.DCE_Button_modelling_only, text='DCE modelling - pilot (Siemens)')
    menu.separator()
<<<<<<< HEAD
    #menu.action(macros.ModellingMacro, text='All modelling - pilot (Siemens)')
=======
    menu.action(kidney_segmentation.kidoutline, text='Outline Kidneys')
>>>>>>> f9c4d1e4182e356c48a5f6ff4a382b6d49fe927b

    menu = parent.menu('iBEAt-MDR')
    menu.action(xnat.Download, text='XNAT Download') 
    menu.action(rename.Leeds, text='Rename DICOMs (Leeds)')
    menu.separator()
    menu.action(mdr.MDRegConst, text='Constant')
    menu.action(mdr.MDRegT2star, text='T2* MDR (Siemens)')
    menu.action(mdr.MDRegT2, text='T2 MDR (Siemens)')
    menu.action(mdr.MDRegT1, text='T1 MDR (Siemens)')
    menu.action(mdr.MDRegDWI, text='IVIM MDR (Siemens)')
    menu.action(mdr.MDRegDTI, text='DTI MDR (Siemens)')
    menu.action(mdr.MDRegDCE, text='DCE MDR (Siemens)')
    menu.action(mdr.MDRegMT, text='MT MDR (Siemens)')
    menu.separator()
    menu.action(xnat.Upload, text = 'XNAT Upload') 
    
    menu = parent.menu('iBEAt-Modelling')
    menu.action(modelling.SiemensT1T2MapButton, text='Joint T1 & T2 Mapping (Siemens)')
    menu.action(modelling.SiemensT2sMapButton, text='T2* Mapping (Siemens)')
    menu.action(modelling.SiemensIVIMButton, text='IVIM: ADC Mapping (Siemens)')
    menu.action(modelling.SiemensDTIButton, text='DTI: FA Mapping (Siemens)')
    