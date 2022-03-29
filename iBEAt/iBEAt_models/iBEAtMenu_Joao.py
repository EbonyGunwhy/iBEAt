import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.abspath(os.path.join('..', 'GitHub')))
# These 2 lines are required if you're importing an external
# python package that doesn't have "pip install" and that's located
# in the same folder as the current menu script.




def main(weasel):
   
    weasel.menu_file()
    weasel.menu_view()
    weasel.menu_edit()

    iBEAt = weasel.menu(label = "iBEAt")

    iBEAt.item(
    label = 'Import from XNAT',
    pipeline = 'iBEAt_Siemens_Rename_Data_Leeds_Button')

    iBEAt.separator()

    iBEAt.item(
        label = 'Rename Leeds Data (Siemens)',
        pipeline = 'iBEAt_Siemens_Rename_Data_Leeds_Button')

    iBEAt.separator()

    iBEAt.item(
        label = 'MDR T1',
        pipeline = 'MDR_iBEAt_T1_Button')

    iBEAt.item(
        label = 'MDR T2',
        pipeline = 'MDR_iBEAt_T2_Button')

    iBEAt.item(
        label = 'MDR T2*',
        pipeline = 'MDR_iBEAt_T2Star_Button')

    iBEAt.separator()

    iBEAt.item(
        label = 'Joint T1 & T2 Mapping (Siemens)',
        pipeline = 'iBEAt_SiemensT1&T2MapButton')

    iBEAt.item(
        label = 'T2* Mapping (Siemens)',
        pipeline = 'iBEAt_SiemensT2sMapButton')

    iBEAt.item(
        label = 'IVIM: ADC Mapping (Siemens)',
        pipeline = 'iBEAt_SiemensIVIMButton')

    iBEAt.item(
        label = 'DTI: FA Mapping (Siemens)',
        pipeline = 'iBEAt_SiemensDTIButton')


        

        
