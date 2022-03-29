import os, sys, time
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from iBEAt_models.iBEAt_Siemens_Rename_Data_Leeds_Button import main as RenameLeeds
from MDR_iBEAt_T2Star_Button import main as T2star_MDR 
from MDR_iBEAt_T2_Button import main as T2_MDR
from MDR_iBEAt_T1_Button import main as T1_MDR
from MDR_iBEAt_DWI_Button import main as DWI_MDR
from MDR_iBEAt_DTI_Button import main as DTI_MDR
from MDR_iBEAt_MT_Button import main as MT_MDR
from XNAT__App_iBEAt import download as importData
import datetime


def main(weasel):

      
      filename_log = datetime.datetime.now().strftime('%Y%m%d_%H%M_') + weasel.DICOMFolder.split('/')[-1] + "_MDRauto_LogFile.txt"
      file = open(filename_log, 'a')
      file.write(str(datetime.datetime.now())[0:19] + ":MDR Auto Button started!")
      file.close()

      start_time = time.time()
      file = open(filename_log, 'a')
      file.write("\n"+str(datetime.datetime.now())[0:19] + ": Importing has started!")
      file.close()
      
      try:
            importData(weasel)
            file = open(filename_log, 'a')
            file.write("\n"+str(datetime.datetime.now())[0:19] + ": Importing was completed --- %s seconds ---" % (int(time.time() - start_time)))
            file.close()
      except Exception as e:
            file = open(filename_log, 'a')
            file.write("\n"+str(datetime.datetime.now())[0:19] + ": Importing was NOT completed; error: "+str(e))
            file.close()


      start_time = time.time()
      file = open(filename_log, 'a')
      file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming has started!")
      file.close()
      try:
            weasel.message(msg="Renaming Data")
            RenameLeeds(weasel)
            weasel.treeView.callCheckAllTreeViewItems()

            file = open(filename_log, 'a')
            file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming was completed --- %s seconds ---" % (int(time.time() - start_time)))
            file.close()
      except Exception as e:
            file = open(filename_log, 'a')
            file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming was NOT completed; error: "+str(e))
            file.close()
      
      list_series = weasel.series()

      start_time_loop = time.time()
      for i,series in enumerate (list_series):
        #print(str(i) + ' : ' + series[0]['SeriesDescription'])
        #print(series[0]['SeriesDescription'])
        if series[0]['SeriesDescription'] == "T1map_kidneys_cor-oblique_mbh_magnitude":
              
              start_time = time.time()
              file = open(filename_log, 'a')
              file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 Motion correction has started")
              file.close()
              try:
                  weasel.message(msg="Performing motion correction in T1 scan")
                  T1_MDR(weasel, series=series)
              
                  file = open(filename_log, 'a')
                  file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                  file.close()
              except Exception as e:
                  file = open(filename_log, 'a')
                  file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 Motion correction was NOT completed; error: "+str(e)) 
                  file.close()
  

        elif series[0]['SeriesDescription'] == "T2star_map_kidneys_cor-oblique_mbh_magnitude":
            start_time = time.time()
            file = open(filename_log, 'a')
            file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Motion correction has started")
            file.close()
            try:
                  weasel.message(msg="Performing motion correction in T2* scan")
                  T2star_MDR(weasel, series=series)

                  file = open(filename_log, 'a')
                  file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                  file.close()
            except Exception as e:
                  file = open(filename_log, 'a')
                  file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Motion correction was NOT completed; error: "+str(e)) 
                  file.close()

        elif series[0]['SeriesDescription'] == "T2map_kidneys_cor-oblique_mbh_magnitude":
              start_time = time.time()
              file = open(filename_log, 'a')
              file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 Motion correction has started")
              file.close()
              
              try:
                  weasel.message(msg="Performing motion correction in T2 scan")
                  T2_MDR(weasel, series=series)

                  file = open(filename_log, 'a')
                  file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                  file.close()
              except Exception as e:
                  file = open(filename_log, 'a')
                  file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 Motion correction was NOT completed; error: "+str(e)) 
                  file.close()

        elif series[0]['SeriesDescription'] == "IVIM_kidneys_cor-oblique_fb":
              start_time = time.time()
              file = open(filename_log, 'a')
              file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM Motion correction has started")
              file.close()
                  
              try:
                  weasel.message(msg="Performing motion correction in IVIM scan")
                  DWI_MDR(weasel, series=series)

                  file = open(filename_log, 'a')
                  file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                  file.close()
              except Exception as e:
                  file = open(filename_log, 'a')
                  file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM Motion correction was NOT completed; error: "+str(e)) 
                  file.close()


        elif series[0]['SeriesDescription'] == "DTI_kidneys_cor-oblique_fb":
              start_time = time.time()
              file = open(filename_log, 'a')
              file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI Motion correction has started")
              file.close()
              weasel.message(msg="Performing motion correction in DTI scan")
              DTI_MDR(weasel, series=series)

              file = open(filename_log, 'a')
              file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
              file.close() 

        elif series[0]['SeriesDescription'] == "MT_OFF_kidneys_cor-oblique_bh":
              MT_OFF = series
              for i_2,series in enumerate (list_series):
                    #print(str(i_2) + ' : ' + series[0]['SeriesDescription'])
                    if series[0]['SeriesDescription'] == "MT_ON_kidneys_cor-oblique_bh":
                          MT_ON = series
                          break
                    
              start_time = time.time()
              file = open(filename_log, 'a')
              file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT Motion correction has started")
              file.close()

              try:
                  weasel.message(msg="Performing motion correction in MT scan")
                  MT_MDR(weasel, series = weasel.series_list([MT_OFF, MT_ON]))


                  file = open(filename_log, 'a')
                  file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                  file.close()
              except Exception as e: 
                  file = open(filename_log, 'a')
                  file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT Motion correction was NOT completed; error: "+str(e)) 
                  file.close()                   
           
      file = open(filename_log, 'a')
      file.write("\n"+str(datetime.datetime.now())[0:19] + ": All scans motion correction was completed --- %s seconds ---" % (int(time.time() - start_time_loop))) 
      file.close()