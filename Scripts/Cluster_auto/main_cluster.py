# To develop the application
# --------------------------
# py -3 -m venv .venv           # create virtual environment
# .venv/Scripts/activate        # activate virtual environment

import time
import datetime
from dbdicom import Folder

import XNAT_cluster as xnat
import RENAME_cluster as rename
import MDR_cluster as mdr
import MODELLING_cluster as modelling
import T1T2_alone_cluster_module
import runpy

#################### INPUT ######################
username = "md1jdsp"
password = "K_9X_Vuh3h"
#path = "//data//md1jdsp"
path = "C://Users//md1jdsp//Desktop//BlackHole"
dataset = [6,0,14] 
#################################################

################################################# EXAMPLE DATASET SELECTION #############################################################
#DATASET CODE FOR LEEDS
#  (FIRST NUMBER)                 (SECOND NUMBER)                                 (THIRD NUMBER)
#  2: BEAt-DKD-WP4-Bordeaux    (selected) BEAt-DKD-WP4-Leeds                 (selected) BEAt-DKD-WP4-Leeds -> (selected) Leeds_Patients
#  3: BEAt-DKD-WP4-Exeter       ->0: Leeds_Patients                            0: Leeds_Patient_4128001
#  4: BEAt-DKD-WP4-Turku          1: Leeds_volunteer_repeatability_study       1: Leeds_Patient_4128002
#  5: BEAt-DKD-WP4-Bari           2: Leeds_Phantom_scans                       2: Leeds_Patient_4128004
#->6: BEAt-DKD-WP4-Leeds          3: Leeds_RAVE_Reconstructions                       ..........
#  7: BEAt-DKD-WP4-Sheffield      4: Leeds_setup_scans                      ->14: Leeds_Patient_4128015
#########################################################################################################################################

ExperimentName = xnat.main(username, password, path, dataset)
#ExperimentName = "Leeds_Patient_4128020"
global pathScan
pathScan = path + "//" + ExperimentName


filename_log = pathScan + datetime.datetime.now().strftime('%Y%m%d_%H%M_') + "MDRauto_LogFile.txt" #TODO FIND ANOTHER WAY TO GET A PATH
file = open(filename_log, 'a')
file.write(str(datetime.datetime.now())[0:19] + ": MDR of " + pathScan.split('//')[-1] +  " has started!")
file.close()

start_time = time.time()
file = open(filename_log, 'a')
file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming has started!")
file.close()
try:
    
    rename.main(pathScan)
    Folder(pathScan).scan()
    
    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming was completed --- %s seconds ---" % (int(time.time() - start_time)))
    file.close()
except Exception as e:
    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming was NOT completed; error: "+str(e))
    file.close()

start_time = time.time()
file = open(filename_log, 'a')
file.write("\n"+str(datetime.datetime.now())[0:19] + ": MDR has started!")
file.close()
try:

    mdr.main(pathScan)
    Folder(pathScan).scan()
    
    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MDR was completed --- %s seconds ---" % (int(time.time() - start_time)))
    file.close()
except Exception as e:
    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MDR was NOT completed; error: "+str(e))
    file.close()

start_time = time.time()
file = open(filename_log, 'a')
file.write("\n"+str(datetime.datetime.now())[0:19] + ": Modelling has started!")
file.close()

try:

    modelling.main(pathScan)
    Folder(pathScan).scan()

    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Modelling was completed --- %s seconds ---" % (int(time.time() - start_time)))
    file.close()
except Exception as e:
    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Modelling was NOT completed; error: "+str(e))
    file.close()

try:
    
    runpy.run_module("T1T2_alone_cluster_module", {}, "__main__")

    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 & T2 Modelling was completed --- %s seconds ---" % (int(time.time() - start_time)))
    file.close()
except Exception as e:
    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 & T2 Modelling was NOT completed; error: "+str(e))
    file.close()
    




