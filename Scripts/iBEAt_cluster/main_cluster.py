""" 
@author: Joao Periquito 
iBEAt CLUSTER MAIN Scrpit
2022
Download XNAT dataset -> Name Standardization -> Execute MDR    -> Custom Moddeling (DCE, T2*, DCE)  -> T1 & T2 modelling with parallelization (done in the main)
    XNAT_cluster.py   ->  RENAME_Cluster.py   -> MDR_Cluster.py -> MODELLING_cluster.py
(T1 & T2 modelling are done in the main due to parallelization requirements)

TO RUN THE SCRIPT YOU USE: python main_cluster.py --num n (WHERE n is an integer with the value of the XNAT dataset)
"""

# To develop the application
# --------------------------
# py -3 -m venv .venv           # create virtual environment
# .venv/Scripts/activate        # activate virtual environment

import os
import numpy as np

from tqdm import tqdm
import multiprocessing

import time
import datetime
import dbdicom as db
import argparse

#import XNAT_cluster as xnat
import RENAME_cluster as rename
import MDR_cluster as mdr
import MODELLING_cluster as modelling
import T1T2_fw_modelling_cluster as T1T2_modelling
#import UPLOAD_cluster as upload
import gdrive_upload as upload

def main(path:str,
         ExperimentName:str,
         KeyPath:str
         ) -> None:
    """Import iBEAt_data, rename and perform MDR/modelling.
    
    Args:
        path: Path to input data folder (e.g., "iBEAt_cluster/data")
        ExperimentName: Name of experiment e.g., "iBE-3128-024"
        KeyPath: Path to API keys
    """
    #################### INPUT ######################
    #username = "**********"
    #password = "**********"
    #path = "//mnt//fastdata//" + username #CLUSTER PATH TO SAVE DATA, ADD YOUR LOCAL PATH IF YOU WANT TO RUN IT LOCALLY
    #path = "C://Users//md1jdsp//Desktop//PHILIPS_BARI"
    #################################################

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--num',
    #                     dest='num',
    #                     help='Define the XNAT dataset',
    #                     type=int)

    # args = parser.parse_args()

    #dataset = [2,1,args.num]

    ################################################# EXAMPLE DATASET SELECTION #############################################################
    #DATASET CODE FOR LEEDS
    #  (FIRST NUMBER)                 (SECOND NUMBER)                                 (THIRD NUMBER - INNPUT from --num when you run the main script: python main_cluster.py --num n)
    #  2: BEAt-DKD-WP4-Bordeaux    (selected) BEAt-DKD-WP4-Leeds                 (selected) BEAt-DKD-WP4-Leeds -> (selected) Leeds_Patients
    #  3: BEAt-DKD-WP4-Exeter       ->0: Leeds_Patients                            0: Leeds_Patient_4128001
    #  4: BEAt-DKD-WP4-Turku          1: Leeds_volunteer_repeatability_study       1: Leeds_Patient_4128002
    #  5: BEAt-DKD-WP4-Bari           2: Leeds_Phantom_scans                       2: Leeds_Patient_4128004
    #->6: BEAt-DKD-WP4-Leeds          3: Leeds_RAVE_Reconstructions                       ..........
    #  7: BEAt-DKD-WP4-Sheffield      4: Leeds_setup_scans                      ->14: Leeds_Patient_4128015
    #########################################################################################################################################

    #ExperimentName = xnat.main(username, password, path, dataset)
    #ExperimentName = "iBE-1128-019"
    #dirname = os.path.dirname(__file__)
    #pathScan = dirname + '/' + path + "/" + ExperimentName
    pathScan = path + "/" + ExperimentName
    dbdicomPath = path + '/dbdicom/' + ExperimentName
    
    folder = db.database(path=pathScan)

    try: 
        UsedCores = int(len(os.sched_getaffinity(0)))
    except: 
        UsedCores = int(os.cpu_count())

    filename_log = dbdicomPath + datetime.datetime.now().strftime('%Y%m%d_%H%M_') + "MDRauto_LogFile.txt" #TODO FIND ANOTHER WAY TO GET A PATH
    file = open(filename_log, 'a')
    file.write(str(datetime.datetime.now())[0:19] + ": Analysis of " + pathScan.split('//')[-1] +  " has started!")
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": CPU cores: " + str(UsedCores))
    file.close()

    start_time = time.time()
    file = open(filename_log, 'a')
    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming has started!")
    file.close()
    try:
        
        rename.main(folder)
        
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

        mdr.main(folder,filename_log)
        
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

        modelling.main(folder,filename_log)

        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": Modelling was completed --- %s seconds ---" % (int(time.time() - start_time)))
        file.close()
    except Exception as e:
        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": Modelling was NOT completed; error: "+str(e))
        file.close()


    upload.Gdrive_upload(dbdicomPath, filename_log, KeyPath)

    #upload_folder.main(pathScan)
    #gdrive_backup_creator = GoogleDriveUp.GoogleDriveBackupCreator()
    #gdrive_backup_creator.backup(pathScan)
    #upload_folder.main(pathScan)

    # start_time = time.time()
    # file = open(filename_log, 'a')
    # file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 & T2 forward modelling has started!")
    # file.close()

    # try:

    #     T1T2_modelling.main(pathScan,filename_log)
    #     Folder(pathScan).scan()

    #     file = open(filename_log, 'a')
    #     file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 & T2 forward modelling was completed --- %s seconds ---" % (int(time.time() - start_time)))
    #     file.close()
    # except Exception as e:
    #     file = open(filename_log, 'a')
    #     file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 & T2 forward modelling was NOT completed; error: "+str(e))
    #     file.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Import iBEAt_data from \
                                     filepath of choice, rename and perform \
                                     MDR and modelling',
                                     usage='python main_cluster.py --path path_to_data_folder')
    parser.add_argument("--path",
                        required=True,
                        help="Path to input data folder \
                        e.g., 'data'")
    parser.add_argument("--ExperimentName",
                        required=True,
                        help="Name of experiment \
                        e.g., 'iBE-3128-024'")
    parser.add_argument("--KeyPath",
                        required=True,
                        help="Path to API keys")
    # parser.add_argument('--num',
    #                     dest='num',
    #                     help='Define the XNAT dataset',
    #                     type=int)

    args = parser.parse_args()
    main(args.path, args.ExperimentName, args.KeyPath)
