# To develop the application
# --------------------------
# py -3 -m venv .venv           # create virtual environment
# .venv/Scripts/activate        # activate virtual environment

import time
import datetime
from dbdicom import Folder

from utilities import XNAT_cluster as xnat
from utilities import RENAME_cluster as rename
from utilities import MDR_cluster as mdr
from utilities import MODELLING_cluster as modelling

username = "md1jdsp"
#password =
path = "C://Users//md1jdsp//Documents//iBEAt_Data"

#ExperimentName = xnat.main(username, password, path)
ExperimentName = "Leeds_Patient_4128011"
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
    
    #rename.main(pathScan)
    #Folder(pathScan).scan()
    
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

    mdr.main(pathScan,filename_log)
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

    modelling.main(pathScan,filename_log)
    Folder(pathScan).scan()
    
    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Modelling was completed --- %s seconds ---" % (int(time.time() - start_time)))
    file.close()
except Exception as e:
    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Modelling was NOT completed; error: "+str(e))
    file.close()



