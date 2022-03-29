import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
#***************************************************************************

def main(weasel):
        weasel.menu_file()
        weasel.menu_view()
        weasel.menu_edit()

        iBEAt_Auto = weasel.menu(label = "iBEAt Auto")
        
        iBEAt_Auto.item(
        label = 'MDR-Auto',
        pipeline = 'MDR_allSeries_iBEAt_Button')

        iBEAt_Auto.item(
        label = 'MDR-Auto (No XNAT importing)',
        pipeline = 'MDR_allSeries_iBEAt_Button_NO_importing')

        iBEAt_Auto.separator()

        iBEAt_Auto.item(
        label = 'DCE create AIF (Siemens)',
        pipeline = 'iBEAt_DCE_create_AIF_Button')

        iBEAt_Auto.item(
        label = 'DCE Modelling pilot analysis (Siemens)',
        pipeline = 'iBEAt_DCE_Button_modelling_only')

        iBEAt_Auto.separator()

        iBEAt_Auto.item(
        label = 'Modelling-Auto',
        pipeline = 'Modelling_allSeries_iBEAt_Button')

        iBEAt_MDR = weasel.menu(label = "iBEAt-MDR")

        iBEAt_MDR.item(
        label = 'XNAT iBEAt Download',
        functionName = 'download',
        pipeline = 'XNAT__App_iBEAt')

        iBEAt_MDR.item(
        label = 'Rename DICOMs (Siemens) iBEAt',
        pipeline = 'iBEAt_Siemens_Rename_Data_Leeds_Button')

        iBEAt_MDR.item(
        label = 'T2* MDR (Siemens)',
        pipeline = 'MDR_iBEAt_T2Star_Button')

        iBEAt_MDR.item(
        label = 'T2 MDR (Siemens)',
        pipeline = 'MDR_iBEAt_T2_Button')

        iBEAt_MDR.item(
        label = 'T1 MDR (Siemens)',
        pipeline = 'MDR_iBEAt_T1_Button')

        iBEAt_MDR.item(
        label = 'IVIM MDR (Siemens)',
        pipeline = 'MDR_iBEAt_DWI_Button')

        iBEAt_MDR.item(
        label = 'DTI MDR (Siemens)',
        pipeline = 'MDR_iBEAt_DTI_Button')

        #iBEAt_MDR.item(
        #label = 'DCE MDR (Siemens)',
        #pipeline = 'MDR_iBEAt_DCE_Button')

        iBEAt_MDR.item(
        label = 'MT MDR (Siemens)',
        pipeline = 'MDR_iBEAt_MT_Button')

        iBEAt_MDR.item(
        label = 'XNAT iBEAt Upload',
        functionName = 'upload',
        pipeline = 'XNAT__App_iBEAt')

        iBEAt_Modelling = weasel.menu(label = "iBEAt-Modelling")

        iBEAt_Modelling.item(
        label = 'T1 & T2 Joint Mapping (Siemens)',
        pipeline = 'iBEAt_SiemensT1T2MapButton')

        iBEAt_Modelling.item(
        label = 'T2* Mapping (Siemens)',
        pipeline = 'iBEAt_SiemensT2sMapButton')

        iBEAt_Modelling.item(
        label = 'IVIM: ADC Mapping (Siemens)',
        pipeline = 'iBEAt_SiemensIVIMButton')

        iBEAt_Modelling.item(
        label = 'DTI: FA Mapping (Siemens)',
        pipeline = 'iBEAt_SiemensDTIButton')

        





        
