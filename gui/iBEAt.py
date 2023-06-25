from wezel.gui import Menu
from . import segment
from . import contrasts
from . import process
from . import mdr
from . import mapping


menu = Menu('iBEAt')
menu.add(process.action_rename)
menu.add(segment.action_unetr)
menu.add(segment.renal_sinus_fat)
menu.add(contrasts.asl_perfusion)
menu.add(contrasts.T1_mdr)
menu.add(contrasts.T1_map)
menu.add_separator()
menu.add(segment.whole_kidney_mask)
menu.add_separator()
menu.add(mdr.action_T2star)
menu.add(mdr.action_T1)
menu.add(mdr.action_T2)
menu.add(mdr.action_DTI)
menu.add(mdr.action_MT)
menu.add(mdr.action_DCE)
menu.add_separator()
menu.add(mapping.action_T2star)
menu.add(mapping.action_T1)
menu.add(mapping.action_DTI)
menu.add(mapping.action_MT)
menu.add(mapping.action_DCE)
menu.add_separator()
menu.add(process.action_mdr)
menu.add(process.action_mapping)
menu.add(process.action_segmentation)
menu.add(process.action_upload)



