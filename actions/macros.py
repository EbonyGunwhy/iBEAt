import time
import datetime
import os, sys
import csv

import weasel

import actions.xnat as xnat
import actions.rename as rename
import actions.mdr as mdr

class MDRegMacro(weasel.Action):

    def run(self, app):
      
        filename_log = weasel.__file__.split('__')[0] + datetime.datetime.now().strftime('%Y%m%d_%H%M_') + "MDRauto_LogFile.txt" #TODO FIND ANOTHER WAY TO GET A PATH
        file = open(filename_log, 'a')
        file.write(str(datetime.datetime.now())[0:19] + ":MDR Auto Button started!")
        file.close()

        start_time = time.time()
        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": Importing has started!")
        file.close()
        
        try:
            xnat.Download.run(self, app)
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
            #app.status.message(msg="Renaming Data")
            rename.Leeds.run(self, app)
            file = open(filename_log, 'a')
            file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming was completed --- %s seconds ---" % (int(time.time() - start_time)))
            file.close()
        except Exception as e:
            file = open(filename_log, 'a')
            file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming was NOT completed; error: "+str(e))
            file.close()
        
        list_series = app.folder.series()
        current_study = list_series[0].parent()
        study = list_series[0].new_pibling(StudyDescription=current_study.StudyDescription + '_MDRresults')

        start_time_loop = time.time()
        for i,series in enumerate(list_series):
            print(series['SeriesDescription'])
            #print(str(i) + ' : ' + series[0]['SeriesDescription'])
            #print(series[0]['SeriesDescription'])
            if series['SeriesDescription'] == "T1map_kidneys_cor-oblique_mbh_magnitude":
                
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 Motion correction has started")
                file.close()
                try:
                    #app.status.message(msg="Performing motion correction in T1 scan")
                    print("Performing motion correction in T1 scan")
                    mdr.MDRegT1.run(self,app, series, parent=study)
                
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()
                except Exception as e:
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 Motion correction was NOT completed; error: "+str(e)) 
                    file.close()
    
            elif series['SeriesDescription'] == "T2star_map_kidneys_cor-oblique_mbh_magnitude":
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Motion correction has started")
                file.close()
                try:
                    #app.status.message(msg="Performing motion correction in T2* scan")
                    print("Performing motion correction in T2* scan")
                    mdr.MDRegT2star.run(self,app, series,parent=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()
                except Exception as e:
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "T2map_kidneys_cor-oblique_mbh_magnitude":
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 Motion correction has started")
                file.close()
                
                try:
                    #app.status.message(msg="Performing motion correction in T2 scan")
                    print("Performing motion correction in T2 scan")
                    mdr.MDRegT2.run(self,app, series, parent=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()
                except Exception as e:
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 Motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "IVIM_kidneys_cor-oblique_fb":
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM Motion correction has started")
                file.close()
                    
                try:
                    #app.status.message(msg="Performing motion correction in IVIM scan")
                    print("Performing motion correction in IVIM scan")
                    mdr.MDRegDWI.run(self,app, series, parent=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()
                except Exception as e:
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM Motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "DTI_kidneys_cor-oblique_fb":
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI Motion correction has started")
                file.close()

                try:
                    print("Performing motion correction in DTI scan")
                    mdr.MDRegDTI.run(self,app, series, parent=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close() 

                except Exception as e:
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI Motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "MT_OFF_kidneys_cor-oblique_bh":
                MT_OFF = series
                for i_2,series in enumerate (list_series):
                        #print(str(i_2) + ' : ' + series[0]['SeriesDescription'])
                        if series['SeriesDescription'] == "MT_ON_kidneys_cor-oblique_bh":
                            MT_ON = series
                            break
                        
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT Motion correction has started")
                file.close()

                try:
                    #app.status.message(msg="Performing motion correction in MT scan")
                    print("Performing motion correction in MT scan")
                    mdr.MDRegMT.run(self,app, [MT_OFF, MT_ON], parent=study)

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


class MDRegMacroNoImport(weasel.Action):

    def run(self, app):
      
        filename_log = datetime.datetime.now().strftime('%Y%m%d_%H%M_') + app.folder.path.split('/')[-1] + "_MDRauto_LogFile.txt"
        file = open(filename_log, 'a')
        file.write(str(datetime.datetime.now())[0:19] + ":MDR Auto Button started!")
        file.close()

        start_time = time.time()
        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": Importing has started!")
        file.close()
        
        try:
            # xnat.Download.run(app)
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
            app.status.message(msg="Renaming Data")
            rename.Leeds.run(app)
            file = open(filename_log, 'a')
            file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming was completed --- %s seconds ---" % (int(time.time() - start_time)))
            file.close()
        except Exception as e:
            file = open(filename_log, 'a')
            file.write("\n"+str(datetime.datetime.now())[0:19] + ": Renaming was NOT completed; error: "+str(e))
            file.close()
        
        list_series = app.folder.series()

        start_time_loop = time.time()
        for i,series in enumerate(list_series):
            #print(str(i) + ' : ' + series[0]['SeriesDescription'])
            #print(series[0]['SeriesDescription'])
            if series['SeriesDescription'] == "T1map_kidneys_cor-oblique_mbh_magnitude":
                
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 Motion correction has started")
                file.close()
                try:
                    #app.status.message(msg="Performing motion correction in T1 scan")
                    print("Performing motion correction in T1 scan")
                    mdr.MDRegT1.run(app, series)
                
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()
                except Exception as e:
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T1 Motion correction was NOT completed; error: "+str(e)) 
                    file.close()
    
            elif series['SeriesDescription'] == "T2star_map_kidneys_cor-oblique_mbh_magnitude":
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Motion correction has started")
                file.close()
                try:
                    #app.status.message(msg="Performing motion correction in T2* scan")
                    print("Performing motion correction in T2* scan")
                    mdr.MDRegT2star.run(app, series)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()
                except Exception as e:
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "T2map_kidneys_cor-oblique_mbh_magnitude":
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 Motion correction has started")
                file.close()
                
                try:
                    app.status.message(msg="Performing motion correction in T2 scan")
                    mdr.MDRegT2.run(app, series)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()
                except Exception as e:
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2 Motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "IVIM_kidneys_cor-oblique_fb":
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM Motion correction has started")
                file.close()
                    
                try:
                    app.status.message(msg="Performing motion correction in IVIM scan")
                    mdr.MDRegDWI.run(app, series)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()
                except Exception as e:
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM Motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "DTI_kidneys_cor-oblique_fb":
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI Motion correction has started")
                file.close()
                app.status.message(msg="Performing motion correction in DTI scan")
                mdr.MDRegDTI.run(app, series)

                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                file.close() 

            elif series['SeriesDescription'] == "MT_OFF_kidneys_cor-oblique_bh":
                MT_OFF = series
                for i_2,series in enumerate (list_series):
                        #print(str(i_2) + ' : ' + series[0]['SeriesDescription'])
                        if series['SeriesDescription'] == "MT_ON_kidneys_cor-oblique_bh":
                            MT_ON = series
                            break
                        
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT Motion correction has started")
                file.close()

                try:
                    app.status.message(msg="Performing motion correction in MT scan")
                    mdr.MDRegMT.run(app, [MT_OFF, MT_ON])

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

class ModellingMacro(weasel.Action):

    def run(self, app):
        filename_log = weasel.__file__.split('__')[0] + datetime.datetime.now().strftime('%Y%m%d_%H%M_') + "_ModelAuto_LogFile.txt"
        file = open(filename_log, 'a')
        file.write(str(datetime.datetime.now())[0:19] + ": " + app.folder.files[0].split('\\dbdicom')[0])
        file.write("\n" + str(datetime.datetime.now())[0:19] + ": Model Auto Button started!")
        
        file.close()

        filename_csv = datetime.datetime.now().strftime('%Y%m%d_%H%M_') + app.folder.files[0].split('\\dbdicom')[0].split('/')[-1]+'.csv'
        csv_file = open(filename_csv, mode='w',newline='')
        fieldnames = ['Date', 'Site', 'Subect','Parameter Name','Kidney (L or R)','ROI (Cortex or Medulla)','Metric','Units','Value']
        csvwriter = csv.writer(csv_file) 
        csvwriter.writerow(fieldnames)
        csv_file.close()

        list_series = app.folder.series()

        studyDescription = app.folder.series()[0]['StudyDescription']
        site = studyDescription.split('-')[-1]
        subject = app.folder.files[0].split('\\dbdicom')[0].split('/')[-1]
        studydate = app.folder.series()[0]['SeriesDate']

        start_time_loop = time.time()
        print('Starting the job')
        for i,series in enumerate (list_series):
            print(str(i) + ' : ' + series[0]['SeriesDescription'])
            if 'T1T2_COR_R' in series[0]['SeriesDescription']:
                mask_T1T2_COR_R = series.PixelArray
            elif 'T1T2_MED_R' in series[0]['SeriesDescription']:
                mask_T1T2_MED_R = series.PixelArray
            elif 'T1T2_COR_L' in series[0]['SeriesDescription']:
                mask_T1T2_COR_L = series.PixelArray
            elif 'T1T2_MED_L' in series[0]['SeriesDescription']:
                mask_T1T2_MED_L = series.PixelArray
            elif 'T1T2_KID_R' in series[0]['SeriesDescription']:
                mask_T1T2_KID_R = series.PixelArray
            elif 'T1T2_KID_L' in series[0]['SeriesDescription']:
                mask_T1T2_KID_L = series.PixelArray
            elif 'T2s_COR_R' in series[0]['SeriesDescription']:
                mask_T2s_COR_R = series.PixelArray
            elif 'T2s_MED_R' in series[0]['SeriesDescription']:
                mask_T2s_MED_R = series.PixelArray
            elif 'T2s_COR_L' in series[0]['SeriesDescription']:
                mask_T2s_COR_L = series.PixelArray
            elif 'T2s_MED_L' in series[0]['SeriesDescription']:
                mask_T2s_MED_L = series.PixelArray
            elif 'T2s_KID_R' in series[0]['SeriesDescription']:
                mask_T2s_KID_R = series.PixelArray
            elif 'T2s_KID_L' in series[0]['SeriesDescription']:
                mask_T2s_KID_L = series.PixelArray
            elif 'IVIM_COR_R' in series[0]['SeriesDescription']:
                mask_IVIM_COR_R = series.PixelArray
            elif 'IVIM_MED_R' in series[0]['SeriesDescription']:
                mask_IVIM_MED_R = series.PixelArray
            elif 'IVIM_COR_L' in series[0]['SeriesDescription']:
                mask_IVIM_COR_L = series.PixelArray
            elif 'IVIM_MED_L' in series[0]['SeriesDescription']:
                mask_IVIM_MED_L = series.PixelArray
            elif 'IVIM_KID_R' in series[0]['SeriesDescription']:
                mask_IVIM_KID_R = series.PixelArray
            elif 'IVIM_KID_L' in series[0]['SeriesDescription']:
                mask_IVIM_KID_L = series.PixelArray
            elif 'DTI_COR_R' in series[0]['SeriesDescription']:
                mask_DTI_COR_R = series.PixelArray
            elif 'DTI_MED_R' in series[0]['SeriesDescription']:
                mask_DTI_MED_R = series.PixelArray
            elif 'DTI_COR_L' in series[0]['SeriesDescription']:
                mask_DTI_COR_L = series.PixelArray
            elif 'DTI_MED_L' in series[0]['SeriesDescription']:
                mask_DTI_MED_L = series.PixelArray
            elif 'DTI_KID_R' in series[0]['SeriesDescription']:
                mask_DTI_KID_R = series.PixelArray
            elif 'DTI_KID_L' in series[0]['SeriesDescription']:
                mask_DTI_KID_L = series.PixelArray
            elif 'MT_COR_R' in series[0]['SeriesDescription']:
                mask_MT_COR_R = series.PixelArray
            elif 'MT_MED_R' in series[0]['SeriesDescription']:
                mask_MT_MED_R = series.PixelArray
            elif 'MT_COR_L' in series[0]['SeriesDescription']:
                mask_MT_COR_L = series.PixelArray
            elif 'MT_MED_L' in series[0]['SeriesDescription']:
                mask_MT_MED_L = series.PixelArray
            elif 'MT_KID_R' in series[0]['SeriesDescription']:
                mask_MT_KID_R = series.PixelArray
            elif 'MT_KID_L' in series[0]['SeriesDescription']:
                mask_MT_KID_L = series.PixelArray
                ### FROM HERE ###
            #elif 'T2s_PAN' in series[0]['SeriesDescription']:
            # mask_T2s_PAN = series.PixelArray
                #PAN_slice = int(series[0]['SeriesDescription'].split('slice')[1])
            #elif 'T2s_LIV' in series[0]['SeriesDescription']:
                #mask_T2s_LIV = series.PixelArray
                #LIV_slice = int(series[0]['SeriesDescription'].split('slice')[1])
            elif 'ASL_KID_R' in series[0]['SeriesDescription']:
                mask_ASL_KID_R = series.PixelArray
                ASL_R_slice = int(series[0]['SeriesDescription'].split('slice')[1])
            elif 'ASL_KID_L' in series[0]['SeriesDescription']:
                mask_ASL_KID_L = series.PixelArray
                ASL_L_slice = int(series[0]['SeriesDescription'].split('slice')[1])
            elif 'T1w_COR_VOL_R' in series[0]['SeriesDescription']:
                mask_T1w_COR_VOL_R = series.PixelArray            
            elif 'T1w_COR_VOL_L' in series[0]['SeriesDescription']:
                mask_T1w_COR_VOL_L = series.PixelArray
            elif 'T1w_ABD_SIN_R' in series[0]['SeriesDescription']:
                mask_T1w_SIN_FAT_VOL_R = series.PixelArray
            elif 'T1w_ABD_SIN_L' in series[0]['SeriesDescription']:
                mask_T1w_SIN_FAT_VOL_L = series.PixelArray
            elif 'T1w_ABD_PAR_R' in series[0]['SeriesDescription']:
                mask_T1w_PAR_VOL_R = series.PixelArray
            elif 'T1w_ABD_PAR_L' in series[0]['SeriesDescription']:
                mask_T1w_PAR_VOL_L = series.PixelArray
            elif 'T1w_COR_TIC_R_1' in series[0]['SeriesDescription']:
                mask_T1w_COR_TIC_R_1 = series.PixelArray
            elif 'T1w_COR_TIC_R_2' in series[0]['SeriesDescription']:
                mask_T1w_COR_TIC_R_2 = series.PixelArray
            elif 'T1w_COR_TIC_R_3' in series[0]['SeriesDescription']:
                mask_T1w_COR_TIC_R_3 = series.PixelArray
            elif 'T1w_COR_TIC_R_4' in series[0]['SeriesDescription']:
                mask_T1w_COR_TIC_R_4 = series.PixelArray
            elif 'T1w_COR_TIC_R_5' in series[0]['SeriesDescription']:
                mask_T1w_COR_TIC_R_5 = series.PixelArray
            elif 'T1w_COR_TIC_L_1' in series[0]['SeriesDescription']:
                mask_T1w_COR_TIC_L_1 = series.PixelArray
            elif 'T1w_COR_TIC_L_2' in series[0]['SeriesDescription']:
                mask_T1w_COR_TIC_L_2 = series.PixelArray
            elif 'T1w_COR_TIC_L_3' in series[0]['SeriesDescription']:
                mask_T1w_COR_TIC_L_3 = series.PixelArray
            elif 'T1w_COR_TIC_L_4' in series[0]['SeriesDescription']:
                mask_T1w_COR_TIC_L_4 = series.PixelArray
            elif 'T1w_COR_TIC_L_5' in series[0]['SeriesDescription']:
                mask_T1w_COR_TIC_L_5 = series.PixelArray
            elif 'PC_ART_R' in series[0]['SeriesDescription']:
                mask_PC_ART_R = series.PixelArray
            elif 'PC_ART_L' in series[0]['SeriesDescription']:
                mask_PC_ART_L = series.PixelArray
            elif 'T1w_POST_PEL_R' in series[0]['SeriesDescription']:
                mask_T1w_PEL_R = series.PixelArray
            elif 'T1w_POST_PEL_L' in series[0]['SeriesDescription']:
                mask_T1w_PEL_L = series.PixelArray
            elif 'DCE_ART' in series[0]['SeriesDescription']:
                mask_DCE_ART = series.PixelArray
            elif 'DCE_KID_R' in series[0]['SeriesDescription']:
                mask_DCE_KID_R = series.PixelArray
            elif 'DCE_KID_L' in series[0]['SeriesDescription']:
                mask_DCE_KID_L = series.PixelArray
            elif 'DCE_COR_R' in series[0]['SeriesDescription']:
                mask_DCE_COR_R = series.PixelArray
            elif 'DCE_COR_L' in series[0]['SeriesDescription']:
                mask_DCE_COR_L = series.PixelArray
            elif 'DCE_MED_R' in series[0]['SeriesDescription']:
                mask_DCE_MED_R = series.PixelArray
            elif 'DCE_MED_L' in series[0]['SeriesDescription']:
                mask_DCE_MED_L = series.PixelArray

        for j,series in enumerate (list_series):
            print(str(j) + ' : ' + series[0]['SeriesDescription'])

            if series[0]['SeriesDescription'] == "Fp_final": #CHANGE TO THE RIGHT MDR OUTPUT PUT IN THE RIGHT ORDER
                try:
                    start_time = time.time()
                    DCE_FP = series.PixelArray
                    for j_1,series in enumerate (list_series):
                        if series[0]['SeriesDescription'] == "Ps_final":
                            DCE_PS = series.PixelArray
                            for j_1,series in enumerate (list_series):
                                if series[0]['SeriesDescription'] == "Tp_final":
                                    DCE_TP = series.PixelArray
                                    for j_1,series in enumerate (list_series):
                                        if series[0]['SeriesDescription'] == "Te_final":
                                            DCE_TE = series.PixelArray
                                            break
                    
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DCE Quantification has started")
                    file.close()
                    # Hct = 0.45
                    # DCE_series = series
                    #DCE_series_images = DCE_series.Magnitude.sort("SliceLocation","AcquisitionTime")
                    #pixelArray_DCE = DCE_series_images.PixelArray
                    #pixelArray_DCE = np.transpose(pixelArray_DCE)
                    #reformat_shape_DCE = np.shape(pixelArray_DCE)[0], np.shape(pixelArray_DCE)[1],9,int(np.shape(pixelArray_DCE)[2]/9)
                    #pixelArray_DCE = pixelArray_DCE.reshape(reformat_shape_DCE)
                    #pixelArray_DCE_ART = np.squeeze(pixelArray_DCE[:,:,8,:])
                    #pixelArray_DCE = np.squeeze(pixelArray_DCE[:,:,3,:])

                    #DCE_timecourse = np.zeros(np.shape(pixelArray_DCE_ART)[2])
                    #mask_DCE_ART = np.transpose(mask_DCE_ART)

                    #FOR KANISHKA (loop to average the arteria)
                    #for k in range(np.shape(pixelArray_DCE_ART)[2]):
                    #    tempPixelMask = np.squeeze(pixelArray_DCE_ART[:,:,k])*np.squeeze(mask_DCE_ART)
                    #    DCE_timecourse[k] = np.median(tempPixelMask[tempPixelMask!=0])

                    #DCE_time = np.arange(0, 1.61*len(DCE_timecourse), 1.61)
                    #signal_model_parameters = [DCE_timecourse, DCE_time, 15, Hct]
                    #pixelArray_DCE = pixelArray_DCE.reshape(np.shape(pixelArray_DCE)[0]*np.shape(pixelArray_DCE)[1],np.shape(pixelArray_DCE)[2])
        
                    #full_module_name = "MDR_Library.models.two_compartment_filtration_model_DCE"
                    #model = importlib.import_module(full_module_name)   

                    #fit, fitted_parameters = model.main(pixelArray_DCE, signal_model_parameters)
                    #Fp = np.squeeze(fitted_parameters[0,:,:])
                    #Tp = np.squeeze(fitted_parameters[1,:,:])
                    #Ps = np.squeeze(fitted_parameters[2,:,:])
                    #Te = np.squueze(fitted_parameters[3,:,:])

                    Hct = 0.45
                    f = 0.99 #reabsorption fraction fo the kidney
                    DCE_PERF = DCE_FP/(1-Hct)
                    DCE_FILT = np.divide(DCE_PS, DCE_FP, out=np.zeros_like(DCE_PS), where=DCE_FP!=0)
                    DCE_BVF  = DCE_FP*DCE_TP/(1-Hct)
                    DCE_TVF = DCE_PS*DCE_TE*(1-f)
                    
                    DCE_PS_KID_R = np.transpose(DCE_PS)*np.transpose(mask_DCE_KID_R)
                    DCE_PS_KID_L = np.transpose(DCE_PS)*np.transpose(mask_DCE_KID_L)
                    DCE_GFR_KID_R =  np.mean(DCE_PS_KID_R[DCE_PS_KID_R!=0])*PAR_VOL_R_ml*60
                    DCE_GFR_KID_L =  np.mean(DCE_PS_KID_L[DCE_PS_KID_L!=0])*PAR_VOL_L_ml*60

                    DCE_PERF_KID_R = np.transpose(DCE_PERF)*np.transpose(mask_DCE_KID_R)
                    DCE_PERF_KID_L = np.transpose(DCE_PERF)*np.transpose(mask_DCE_KID_L)
                    DCE_RBF_KID_R  = np.mean(DCE_PERF_KID_R[DCE_PERF_KID_R!=0])*PAR_VOL_R_ml*60
                    DCE_RBF_KID_L  = np.mean(DCE_PERF_KID_L[DCE_PERF_KID_L!=0])*PAR_VOL_L_ml*60

                    DCE_PERF_COR_R = np.transpose(DCE_PERF)*np.transpose(mask_DCE_COR_R)*6000
                    DCE_PERF_COR_L = np.transpose(DCE_PERF)*np.transpose(mask_DCE_COR_L)*6000
                    DCE_FILT_KID_R = np.transpose(DCE_FILT)*np.transpose(mask_DCE_KID_R)*6000
                    DCE_FILT_KID_L = np.transpose(DCE_FILT)*np.transpose(mask_DCE_KID_L)*6000
                    DCE_BVF_MED_R = np.transpose(DCE_BVF)*np.transpose(mask_DCE_MED_R)
                    DCE_BVF_MED_L = np.transpose(DCE_BVF)*np.transpose(mask_DCE_MED_L)
                    DCE_BVF_COR_R = np.transpose(DCE_BVF)*np.transpose(mask_DCE_COR_R)
                    DCE_BVF_COR_L = np.transpose(DCE_BVF)*np.transpose(mask_DCE_COR_L)
                    DCE_TVF_COR_R = np.transpose(DCE_TVF)*np.transpose(mask_DCE_COR_R)
                    DCE_TVF_COR_L = np.transpose(DCE_TVF)*np.transpose(mask_DCE_COR_L)
                    DCE_TVF_MED_R = np.transpose(DCE_TVF)*np.transpose(mask_DCE_MED_R)
                    DCE_TVF_MED_L = np.transpose(DCE_TVF)*np.transpose(mask_DCE_MED_L)

                    row_DCE_GFR_RBF = [
                                [studydate,site,subject,'GFR','R','KID','Mean','mL/min',str(DCE_GFR_KID_R)],
                                [studydate,site,subject,'GFR','L','KID','Mean','mL/min',str(DCE_GFR_KID_L)],
                                [studydate,site,subject,'RBF','R','KID','Mean','mL/min',str(DCE_RBF_KID_R)],
                                [studydate,site,subject,'RBF','L','KID','Mean','mL/min',str(DCE_RBF_KID_L)],
                                        ]

                    row_DCE_PERF_COR_R = [
                                [studydate,site,subject,'MRR Perfusion','R','COR','Median','mL/min/100mL',str(np.median(DCE_PERF_COR_R[DCE_PERF_COR_R!=0]))],
                                [studydate,site,subject,'MRR Perfusion','R','COR','Mean','mL/min/100mL',str(np.mean(DCE_PERF_COR_R[DCE_PERF_COR_R!=0]))],
                                [studydate,site,subject,'MRR Perfusion','R','COR','Stdev','mL/min/100mL',str(np.std(DCE_PERF_COR_R[DCE_PERF_COR_R!=0]))],
                                [studydate,site,subject,'MRR Perfusion','R','COR','Mode','mL/min/100mL',str(stats.mode(DCE_PERF_COR_R[DCE_PERF_COR_R!=0])[0][0])],
                                [studydate,site,subject,'MRR Perfusion','R','COR','95%','mL/min/100mL',str(np.percentile(DCE_PERF_COR_R[DCE_PERF_COR_R!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MRR Perfusion','R','COR','75%','mL/min/100mL',str(np.percentile(DCE_PERF_COR_R[DCE_PERF_COR_R!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MRR Perfusion','R','COR','25%','mL/min/100mL',str(np.percentile(DCE_PERF_COR_R[DCE_PERF_COR_R!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MRR Perfusion','R','COR','5%','mL/min/100mL',str(np.percentile(DCE_PERF_COR_R[DCE_PERF_COR_R!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MRR Perfusion','R','COR','IQR','mL/min/100mL',str(np.percentile(DCE_PERF_COR_R[DCE_PERF_COR_R!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_PERF_COR_R[DCE_PERF_COR_R!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MRR Perfusion','R','COR','IQR/Median','%',str((np.percentile(DCE_PERF_COR_R[DCE_PERF_COR_R!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_PERF_COR_R[DCE_PERF_COR_R!=0], 25, interpolation = 'midpoint'))/np.median(DCE_PERF_COR_R[DCE_PERF_COR_R!=0]))],
                                        ]

                    row_DCE_PERF_COR_L = [
                                [studydate,site,subject,'MRR Perfusion','L','COR','Median','mL/min/100mL',str(np.median(DCE_PERF_COR_L[DCE_PERF_COR_L!=0]))],
                                [studydate,site,subject,'MRR Perfusion','L','COR','Mean','mL/min/100mL',str(np.mean(DCE_PERF_COR_L[DCE_PERF_COR_L!=0]))],
                                [studydate,site,subject,'MRR Perfusion','L','COR','Stdev','mL/min/100mL',str(np.std(DCE_PERF_COR_L[DCE_PERF_COR_L!=0]))],
                                [studydate,site,subject,'MRR Perfusion','L','COR','Mode','mL/min/100mL',str(stats.mode(DCE_PERF_COR_L[DCE_PERF_COR_L!=0])[0][0])],
                                [studydate,site,subject,'MRR Perfusion','L','COR','95%','mL/min/100mL',str(np.percentile(DCE_PERF_COR_L[DCE_PERF_COR_L!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MRR Perfusion','L','COR','75%','mL/min/100mL',str(np.percentile(DCE_PERF_COR_L[DCE_PERF_COR_L!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MRR Perfusion','L','COR','25%','mL/min/100mL',str(np.percentile(DCE_PERF_COR_L[DCE_PERF_COR_L!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MRR Perfusion','L','COR','5%','mL/min/100mL',str(np.percentile(DCE_PERF_COR_L[DCE_PERF_COR_L!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MRR Perfusion','L','COR','IQR','mL/min/100mL',str(np.percentile(DCE_PERF_COR_L[DCE_PERF_COR_L!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_PERF_COR_L[DCE_PERF_COR_L!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MRR Perfusion','L','COR','IQR/Median','%',str((np.percentile(DCE_PERF_COR_L[DCE_PERF_COR_L!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_PERF_COR_L[DCE_PERF_COR_L!=0], 25, interpolation = 'midpoint'))/np.median(DCE_PERF_COR_L[DCE_PERF_COR_L!=0]))],
                                        ]

                    row_DCE_FILT_KID_R = [
                                [studydate,site,subject,'Filtration','R','KID','Median','mL/min/100mL',str(np.median(DCE_FILT_KID_R[DCE_FILT_KID_R!=0]))],
                                [studydate,site,subject,'Filtration','R','KID','Mean','mL/min/100mL',str(np.mean(DCE_FILT_KID_R[DCE_FILT_KID_R!=0]))],
                                [studydate,site,subject,'Filtration','R','KID','Stdev','mL/min/100mL',str(np.std(DCE_FILT_KID_R[DCE_FILT_KID_R!=0]))],
                                [studydate,site,subject,'Filtration','R','KID','Mode','mL/min/100mL',str(stats.mode(DCE_FILT_KID_R[DCE_FILT_KID_R!=0])[0][0])],
                                [studydate,site,subject,'Filtration','R','KID','95%','mL/min/100mL',str(np.percentile(DCE_FILT_KID_R[DCE_FILT_KID_R!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Filtration','R','KID','75%','mL/min/100mL',str(np.percentile(DCE_FILT_KID_R[DCE_FILT_KID_R!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Filtration','R','KID','25%','mL/min/100mL',str(np.percentile(DCE_FILT_KID_R[DCE_FILT_KID_R!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Filtration','R','KID','5%','mL/min/100mL',str(np.percentile(DCE_FILT_KID_R[DCE_FILT_KID_R!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Filtration','R','KID','IQR','mL/min/100mL',str(np.percentile(DCE_FILT_KID_R[DCE_FILT_KID_R!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_FILT_KID_R[DCE_FILT_KID_R!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Filtration','R','KID','IQR/Median','%',str((np.percentile(DCE_FILT_KID_R[DCE_FILT_KID_R!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_FILT_KID_R[DCE_FILT_KID_R!=0], 25, interpolation = 'midpoint'))/np.median(DCE_FILT_KID_R[DCE_FILT_KID_R!=0]))],
                                        ]

                    row_DCE_FILT_KID_L = [
                                [studydate,site,subject,'Filtration','L','KID','Median','mL/min/100mL',str(np.median(DCE_FILT_KID_L[DCE_FILT_KID_L!=0]))],
                                [studydate,site,subject,'Filtration','L','KID','Mean','mL/min/100mL',str(np.mean(DCE_FILT_KID_L[DCE_FILT_KID_L!=0]))],
                                [studydate,site,subject,'Filtration','L','KID','Stdev','mL/min/100mL',str(np.std(DCE_FILT_KID_L[DCE_FILT_KID_L!=0]))],
                                [studydate,site,subject,'Filtration','L','KID','Mode','mL/min/100mL',str(stats.mode(DCE_FILT_KID_L[DCE_FILT_KID_L!=0])[0][0])],
                                [studydate,site,subject,'Filtration','L','KID','95%','mL/min/100mL',str(np.percentile(DCE_FILT_KID_L[DCE_FILT_KID_L!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Filtration','L','KID','75%','mL/min/100mL',str(np.percentile(DCE_FILT_KID_L[DCE_FILT_KID_L!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Filtration','L','KID','25%','mL/min/100mL',str(np.percentile(DCE_FILT_KID_L[DCE_FILT_KID_L!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Filtration','L','KID','5%','mL/min/100mL',str(np.percentile(DCE_FILT_KID_L[DCE_FILT_KID_L!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Filtration','L','KID','IQR','mL/min/100mL',str(np.percentile(DCE_FILT_KID_L[DCE_FILT_KID_L!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_FILT_KID_L[DCE_FILT_KID_L!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Filtration','L','KID','IQR/Median','%',str((np.percentile(DCE_FILT_KID_L[DCE_FILT_KID_L!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_FILT_KID_L[DCE_FILT_KID_L!=0], 25, interpolation = 'midpoint'))/np.median(DCE_FILT_KID_L[DCE_FILT_KID_L!=0]))],
                                        ]

                    row_DCE_BVF_MED_R = [
                                [studydate,site,subject,'Blood Volume Fraction','R','MED','Median','%',str(np.median(DCE_BVF_MED_R[DCE_BVF_MED_R!=0]))],
                                [studydate,site,subject,'Blood Volume Fraction','R','MED','Mean','%',str(np.mean(DCE_BVF_MED_R[DCE_BVF_MED_R!=0]))],
                                [studydate,site,subject,'Blood Volume Fraction','R','MED','Stdev','%',str(np.std(DCE_BVF_MED_R[DCE_BVF_MED_R!=0]))],
                                [studydate,site,subject,'Blood Volume Fraction','R','MED','Mode','%',str(stats.mode(DCE_BVF_MED_R[DCE_BVF_MED_R!=0])[0][0])],
                                [studydate,site,subject,'Blood Volume Fraction','R','MED','95%','%',str(np.percentile(DCE_BVF_MED_R[DCE_BVF_MED_R!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','R','MED','75%','%',str(np.percentile(DCE_BVF_MED_R[DCE_BVF_MED_R!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','R','MED','25%','%',str(np.percentile(DCE_BVF_MED_R[DCE_BVF_MED_R!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','R','MED','5%','%',str(np.percentile(DCE_BVF_MED_R[DCE_BVF_MED_R!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','R','MED','IQR','%',str(np.percentile(DCE_BVF_MED_R[DCE_BVF_MED_R!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_BVF_MED_R[DCE_BVF_MED_R!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','R','MED','IQR/Median','%',str((np.percentile(DCE_BVF_MED_R[DCE_BVF_MED_R!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_BVF_MED_R[DCE_BVF_MED_R!=0], 25, interpolation = 'midpoint'))/np.median(DCE_BVF_MED_R[DCE_BVF_MED_R!=0]))],
                                        ]
                                        
                    row_DCE_BVF_MED_L = [
                                [studydate,site,subject,'Blood Volume Fraction','L','MED','Median','%',str(np.median(DCE_BVF_MED_L[DCE_BVF_MED_L!=0]))],
                                [studydate,site,subject,'Blood Volume Fraction','L','MED','Mean','%',str(np.mean(DCE_BVF_MED_L[DCE_BVF_MED_L!=0]))],
                                [studydate,site,subject,'Blood Volume Fraction','L','MED','Stdev','%',str(np.std(DCE_BVF_MED_L[DCE_BVF_MED_L!=0]))],
                                [studydate,site,subject,'Blood Volume Fraction','L','MED','Mode','%',str(stats.mode(DCE_BVF_MED_L[DCE_BVF_MED_L!=0])[0][0])],
                                [studydate,site,subject,'Blood Volume Fraction','L','MED','95%','%',str(np.percentile(DCE_BVF_MED_L[DCE_BVF_MED_L!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','L','MED','75%','%',str(np.percentile(DCE_BVF_MED_L[DCE_BVF_MED_L!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','L','MED','25%','%',str(np.percentile(DCE_BVF_MED_L[DCE_BVF_MED_L!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','L','MED','5%','%',str(np.percentile(DCE_BVF_MED_L[DCE_BVF_MED_L!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','L','MED','IQR','%',str(np.percentile(DCE_BVF_MED_L[DCE_BVF_MED_L!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_BVF_MED_L[DCE_BVF_MED_L!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','L','MED','IQR/Median','%',str((np.percentile(DCE_BVF_MED_L[DCE_BVF_MED_L!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_BVF_MED_L[DCE_BVF_MED_L!=0], 25, interpolation = 'midpoint'))/np.median(DCE_BVF_MED_L[DCE_BVF_MED_L!=0]))],
                                        ]

                    row_DCE_BVF_COR_R = [
                                [studydate,site,subject,'Blood Volume Fraction','R','COR','median','%',str(np.median(DCE_BVF_COR_R[DCE_BVF_COR_R!=0]))],
                                [studydate,site,subject,'Blood Volume Fraction','R','COR','Mean','%',str(np.mean(DCE_BVF_COR_R[DCE_BVF_COR_R!=0]))],
                                [studydate,site,subject,'Blood Volume Fraction','R','COR','Stdev','%',str(np.std(DCE_BVF_COR_R[DCE_BVF_COR_R!=0]))],
                                [studydate,site,subject,'Blood Volume Fraction','R','COR','Mode','%',str(stats.mode(DCE_BVF_COR_R[DCE_BVF_COR_R!=0])[0][0])],
                                [studydate,site,subject,'Blood Volume Fraction','R','COR','95%','%',str(np.percentile(DCE_BVF_COR_R[DCE_BVF_COR_R!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','R','COR','75%','%',str(np.percentile(DCE_BVF_COR_R[DCE_BVF_COR_R!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','R','COR','25%','%',str(np.percentile(DCE_BVF_COR_R[DCE_BVF_COR_R!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','R','COR','5%','%',str(np.percentile(DCE_BVF_COR_R[DCE_BVF_COR_R!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','R','COR','IQR','%',str(np.percentile(DCE_BVF_COR_R[DCE_BVF_COR_R!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_BVF_COR_R[DCE_BVF_COR_R!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','R','COR','IQR/Median','%',str((np.percentile(DCE_BVF_COR_R[DCE_BVF_COR_R!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_BVF_COR_R[DCE_BVF_COR_R!=0], 25, interpolation = 'midpoint'))/np.median(DCE_BVF_COR_R[DCE_BVF_COR_R!=0]))],
                                        ]

                    row_DCE_BVF_COR_L = [
                                [studydate,site,subject,'Blood Volume Fraction','L','COR','median','%',str(np.median(DCE_BVF_COR_L[DCE_BVF_COR_L!=0]))],
                                [studydate,site,subject,'Blood Volume Fraction','L','COR','Mean','%',str(np.mean(DCE_BVF_COR_L[DCE_BVF_COR_L!=0]))],
                                [studydate,site,subject,'Blood Volume Fraction','L','COR','Stdev','%',str(np.std(DCE_BVF_COR_L[DCE_BVF_COR_L!=0]))],
                                [studydate,site,subject,'Blood Volume Fraction','L','COR','Mode','%',str(stats.mode(DCE_BVF_COR_L[DCE_BVF_COR_L!=0])[0][0])],
                                [studydate,site,subject,'Blood Volume Fraction','L','COR','95%','%',str(np.percentile(DCE_BVF_COR_L[DCE_BVF_COR_L!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','L','COR','75%','%',str(np.percentile(DCE_BVF_COR_L[DCE_BVF_COR_L!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','L','COR','25%','%',str(np.percentile(DCE_BVF_COR_L[DCE_BVF_COR_L!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','L','COR','5%','%',str(np.percentile(DCE_BVF_COR_L[DCE_BVF_COR_L!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','L','COR','IQR','%',str(np.percentile(DCE_BVF_COR_L[DCE_BVF_COR_L!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_BVF_COR_L[DCE_BVF_COR_L!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Blood Volume Fraction','L','COR','IQR/Median','%',str((np.percentile(DCE_BVF_COR_L[DCE_BVF_COR_L!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_BVF_COR_L[DCE_BVF_COR_L!=0], 25, interpolation = 'midpoint'))/np.median(DCE_BVF_COR_L[DCE_BVF_COR_L!=0]))],
                                        ]

                    row_DCE_TVF_MED_R = [
                                [studydate,site,subject,'Tubular Volume Fraction','R','MED','Median','%',str(np.median(DCE_TVF_MED_R[DCE_TVF_MED_R!=0]))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','MED','Mean','%',str(np.mean(DCE_TVF_MED_R[DCE_TVF_MED_R!=0]))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','MED','Stdev','%',str(np.std(DCE_TVF_MED_R[DCE_TVF_MED_R!=0]))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','MED','Mode','%',str(stats.mode(DCE_TVF_MED_R[DCE_TVF_MED_R!=0])[0][0])],
                                [studydate,site,subject,'Tubular Volume Fraction','R','MED','95%','%',str(np.percentile(DCE_TVF_MED_R[DCE_TVF_MED_R!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','MED','75%','%',str(np.percentile(DCE_TVF_MED_R[DCE_TVF_MED_R!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','MED','25%','%',str(np.percentile(DCE_TVF_MED_R[DCE_TVF_MED_R!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','MED','5%','%',str(np.percentile(DCE_TVF_MED_R[DCE_TVF_MED_R!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','MED','IQR','%',str(np.percentile(DCE_TVF_MED_R[DCE_TVF_MED_R!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_TVF_MED_R[DCE_TVF_MED_R!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','MED','IQR/Median','%',str((np.percentile(DCE_TVF_MED_R[DCE_TVF_MED_R!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_TVF_MED_R[DCE_TVF_MED_R!=0], 25, interpolation = 'midpoint'))/np.median(DCE_TVF_MED_R[DCE_TVF_MED_R!=0]))],
                                        ]

                    row_DCE_TVF_MED_L = [
                                [studydate,site,subject,'Tubular Volume Fraction','L','MED','Median','%',str(np.median(DCE_TVF_MED_L[DCE_TVF_MED_L!=0]))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','MED','Mean','%',str(np.mean(DCE_TVF_MED_L[DCE_TVF_MED_L!=0]))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','MED','Stdev','%',str(np.std(DCE_TVF_MED_L[DCE_TVF_MED_L!=0]))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','MED','Mode','%',str(stats.mode(DCE_TVF_MED_L[DCE_TVF_MED_L!=0])[0][0])],
                                [studydate,site,subject,'Tubular Volume Fraction','L','MED','95%','%',str(np.percentile(DCE_TVF_MED_L[DCE_TVF_MED_L!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','MED','75%','%',str(np.percentile(DCE_TVF_MED_L[DCE_TVF_MED_L!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','MED','25%','%',str(np.percentile(DCE_TVF_MED_L[DCE_TVF_MED_L!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','MED','5%','%',str(np.percentile(DCE_TVF_MED_L[DCE_TVF_MED_L!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','MED','IQR','%',str(np.percentile(DCE_TVF_MED_L[DCE_TVF_MED_L!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_TVF_MED_L[DCE_TVF_MED_L!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','MED','IQR/Median','%',str((np.percentile(DCE_TVF_MED_L[DCE_TVF_MED_L!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_TVF_MED_L[DCE_TVF_MED_L!=0], 25, interpolation = 'midpoint'))/np.median(DCE_TVF_MED_L[DCE_TVF_MED_L!=0]))],
                                        ]

                    row_DCE_TVF_COR_R = [
                                [studydate,site,subject,'Tubular Volume Fraction','R','COR','Median','%',str(np.median(DCE_TVF_COR_R[DCE_TVF_COR_R!=0]))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','COR','Mean','%',str(np.mean(DCE_TVF_COR_R[DCE_TVF_COR_R!=0]))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','COR','Stdev','%',str(np.std(DCE_TVF_COR_R[DCE_TVF_COR_R!=0]))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','COR','Mode','%',str(stats.mode(DCE_TVF_COR_R[DCE_TVF_COR_R!=0])[0][0])],
                                [studydate,site,subject,'Tubular Volume Fraction','R','COR','95%','%',str(np.percentile(DCE_TVF_COR_R[DCE_TVF_COR_R!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','COR','75%','%',str(np.percentile(DCE_TVF_COR_R[DCE_TVF_COR_R!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','COR','25%','%',str(np.percentile(DCE_TVF_COR_R[DCE_TVF_COR_R!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','COR','5%','%',str(np.percentile(DCE_TVF_COR_R[DCE_TVF_COR_R!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','COR','IQR','%',str(np.percentile(DCE_TVF_COR_R[DCE_TVF_COR_R!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_TVF_COR_R[DCE_TVF_COR_R!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','R','COR','IQR/Median','%',str((np.percentile(DCE_TVF_COR_R[DCE_TVF_COR_R!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_TVF_COR_R[DCE_TVF_COR_R!=0], 25, interpolation = 'midpoint'))/np.median(DCE_TVF_COR_R[DCE_TVF_COR_R!=0]))],
                                        ]

                    row_DCE_TVF_COR_L = [
                                [studydate,site,subject,'Tubular Volume Fraction','L','COR','Median','%',str(np.median(DCE_TVF_COR_L[DCE_TVF_COR_L!=0]))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','COR','Mean','%',str(np.mean(DCE_TVF_COR_L[DCE_TVF_COR_L!=0]))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','COR','Stdev','%',str(np.std(DCE_TVF_COR_L[DCE_TVF_COR_L!=0]))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','COR','Mode','%',str(stats.mode(DCE_TVF_COR_L[DCE_TVF_COR_L!=0])[0][0])],
                                [studydate,site,subject,'Tubular Volume Fraction','L','COR','95%','%',str(np.percentile(DCE_TVF_COR_L[DCE_TVF_COR_L!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','COR','75%','%',str(np.percentile(DCE_TVF_COR_L[DCE_TVF_COR_L!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','COR','25%','%',str(np.percentile(DCE_TVF_COR_L[DCE_TVF_COR_L!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','COR','5%','%',str(np.percentile(DCE_TVF_COR_L[DCE_TVF_COR_L!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','COR','IQR','%',str(np.percentile(DCE_TVF_COR_L[DCE_TVF_COR_L!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_TVF_COR_L[DCE_TVF_COR_L!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Tubular Volume Fraction','L','COR','IQR/Median','%',str((np.percentile(DCE_TVF_COR_L[DCE_TVF_COR_L!=0], 75, interpolation = 'midpoint')-np.percentile(DCE_TVF_COR_L[DCE_TVF_COR_L!=0], 25, interpolation = 'midpoint'))/np.median(DCE_TVF_COR_L[DCE_TVF_COR_L!=0]))],
                                        ]

                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_DCE_PERF_COR_R)
                    csvwriter.writerows(row_DCE_PERF_COR_L)
                    csvwriter.writerows(row_DCE_FILT_KID_R)
                    csvwriter.writerows(row_DCE_FILT_KID_L)
                    csvwriter.writerows(row_DCE_BVF_MED_R)
                    csvwriter.writerows(row_DCE_BVF_MED_L)
                    csvwriter.writerows(row_DCE_BVF_COR_R)
                    csvwriter.writerows(row_DCE_BVF_COR_L)
                    csvwriter.writerows(row_DCE_TVF_COR_R)
                    csvwriter.writerows(row_DCE_TVF_COR_L)
                    csvwriter.writerows(row_DCE_TVF_MED_R)
                    csvwriter.writerows(row_DCE_TVF_MED_L)
                    csvwriter.writerows(row_DCE_GFR_RBF)
                    csv_file.close()

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DCE was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DCE Quantification was NOT completed; error: "  + str(e))
                    file.close()

            if series[0]['SeriesDescription'] == "T1w_abdomen_dixon_cor_bh_fat_post_contrast":
                try:
                    T1w_Post_VolumeQuantification = series
                    
                    start_time = time.time()
                    
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Pelvis Volume Quantification has started")
                    file.close()

                    PEL_VOL_R = 0
                    for k in range(np.shape(mask_T1w_PEL_R)[0]):
                        tempVolSlice = np.squeeze(mask_T1w_PEL_R[k,:,:])
                        tempCount = len(tempVolSlice[tempVolSlice!=0])
                        PEL_VOL_R = PEL_VOL_R + tempCount

                    PEL_VOL_L = 0
                    for k in range(np.shape(mask_T1w_PEL_L)[0]):
                        tempVolSlice = np.squeeze(mask_T1w_PEL_L[k,:,:])
                        tempCount = len(tempVolSlice[tempVolSlice!=0])
                        PEL_VOL_L = PEL_VOL_L + tempCount

                    PEL_VOL_R_ml = PEL_VOL_R*T1w_Post_VolumeQuantification[0]['PixelSpacing'][0]*T1w_Post_VolumeQuantification[0]['PixelSpacing'][1]*T1w_Post_VolumeQuantification[0]['SliceThickness']/1000
                    PEL_VOL_L_ml = PEL_VOL_L*T1w_Post_VolumeQuantification[0]['PixelSpacing'][0]*T1w_Post_VolumeQuantification[0]['PixelSpacing'][1]*T1w_Post_VolumeQuantification[0]['SliceThickness']/1000
                    
                                
                    #ADD CORTICAL TICKNESS L and R
                    row_T1w_PR =[
                                [studydate,site,subject,'Pelvis Volume','R','None','Total','ml',str(PEL_VOL_R_ml)],
                                ]
                    
                    row_T1w_PL =[
                                [studydate,site,subject,'Pelvis Volume','L','None','Total','ml',str(PEL_VOL_L_ml)],
                                ]

                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_T1w_PR)
                    csvwriter.writerows(row_T1w_PL)
                    csv_file.close()

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Pelvis Volume Quantification was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Pelvis Volume Quantification was NOT completed; error: "  + str(e))
                    file.close()

            if series[0]['SeriesDescription'] == "PC_RenalArtery_Right_EcgTrig_fb_120_phase":
                try:
                    PC_R_series = series
                    PC_R = series.PixelArray
                    PC_R_timecourse = np.zeros(np.shape(PC_R)[0])
                    PC_Area_R = np.zeros(np.shape(PC_R)[0])

                    #plt.imshow(PC_R[0,:,:])
                    #plt.imshow(mask_PC_ART_R[0,:,:])

                    start_time = time.time()
                    
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": PC Right Artery has started")
                    file.close()

                    for k in range(np.shape(PC_R)[0]):
                        tempPixelMask = np.squeeze(PC_R[k,:,:])*np.squeeze(mask_PC_ART_R[k,:,:])
                        tempMaskArea =(np.squeeze(mask_PC_ART_R[k,:,:]))
                        PC_Area_R[k] = len(tempMaskArea[tempMaskArea!=0])
                        PC_R_timecourse[k] = np.abs(np.median(tempPixelMask[tempPixelMask!=0]))
                        #ACTION NEEDED: multiply PC by a constant
                    
                    PC_Area_R_cm2 =PC_Area_R*PC_R_series[0]['PixelSpacing'][0]*PC_R_series[0]['PixelSpacing'][1]/100

                    PC_SIS_R = np.max(PC_R_timecourse)/4096*120/2
                    PC_DIA_R = np.min(PC_R_timecourse)/4096*120/2
                    PC_MVEL_R =np.mean(PC_R_timecourse)/4096*120/2
                    PC_MFLW_R =np.mean(PC_R_timecourse/4096*120/2*PC_Area_R_cm2*60)

                    row_T1w_PR =[
                                [studydate,site,subject,'Arterial Blood Velocity','R','None','Mean','cm/s',str(PC_MVEL_R)],
                                [studydate,site,subject,'Arterial Systolic Blood Velocity','R','None','Maximum','cm/s',str(PC_SIS_R)],
                                [studydate,site,subject,'Arterial Enc Diastolic Blood Velocity','R','None','Minimum','cm/s',str(PC_DIA_R)],
                                [studydate,site,subject,'Aterial Blood Flow','R','None','Mean','ml/min',str(PC_MFLW_R)],
                                ]


                    #plt.plot(PC_R_timecourse)

                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_T1w_PR)
                    csv_file.close()

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": PC Right Artery was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": PC Right Artery was NOT completed; error: "  + str(e))
                    file.close()


            if series[0]['SeriesDescription'] == "PC_RenalArtery_Left_EcgTrig_fb_120_phase":
                try:
                    PC_L_series = series
                    PC_L = series.PixelArray
                    PC_L_timecourse = np.zeros(np.shape(PC_L)[0])
                    PC_Area_L = np.zeros(np.shape(PC_L)[0])

                    start_time = time.time()
                    
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": PC Left Artery has started")
                    file.close()

                    for k in range(np.shape(PC_L)[0]):
                        tempPixelMask = np.squeeze(PC_L[k,:,:])*np.squeeze(mask_PC_ART_L[k,:,:])
                        tempMaskArea =(np.squeeze(mask_PC_ART_L[k,:,:]))
                        PC_Area_L[k] = len(tempMaskArea[tempMaskArea!=0])
                        PC_L_timecourse[k] = np.abs(np.median(tempPixelMask[tempPixelMask!=0]))
                        #ACTION NEEDED: multiply PC by a constant
                    
                    PC_Area_L_cm2 =PC_Area_L*PC_L_series[0]['PixelSpacing'][0]*PC_L_series[0]['PixelSpacing'][1]/100

                    PC_SIS_L = np.max(PC_L_timecourse)/4096*120/2
                    PC_DIA_L = np.min(PC_L_timecourse)/4096*120/2
                    PC_MVEL_L =np.mean(PC_L_timecourse)/4096*120/2
                    PC_MFLW_L =np.mean(PC_L_timecourse/4096*120/2*PC_Area_L_cm2*60)

                    row_T1w_PL =[
                                [studydate,site,subject,'Arterial Blood Velocity','L','None','Mean','cm/s',str(PC_MVEL_L)],
                                [studydate,site,subject,'Arterial Systolic Blood Velocity','L','None','Maximum','cm/s',str(PC_SIS_L)],
                                [studydate,site,subject,'Arterial End Diastolic Blood Velocity','L','None','Minimum','cm/s',str(PC_DIA_L)],
                                [studydate,site,subject,'Aterial Blood Flow','L','None','Mean','ml/min',str(PC_MFLW_L)],
                                ]

                    #plt.plot(PC_L_timecourse)

                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_T1w_PL)
                    csv_file.close()

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": PC Left Artery was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": PC Left Artery was NOT completed; error: "  + str(e))
                    file.close()


            if series[0]['SeriesDescription'] == "T1w_kidneys_cor-oblique_mbh_magnitude":
                try:
                    T1w_VolumeQuantification = series
                    
                    start_time = time.time()
                    
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Volume Quantification has started")
                    file.close()

                    COR_VOL_R = 0
                    for k in range(np.shape(mask_T1w_COR_VOL_R)[0]):
                        tempVolSlice = np.squeeze(mask_T1w_COR_VOL_R[k,:,:])
                        tempCount = len(tempVolSlice[tempVolSlice!=0])
                        COR_VOL_R = COR_VOL_R + tempCount

                    COR_VOL_L = 0
                    for k in range(np.shape(mask_T1w_COR_VOL_L)[0]):
                        tempVolSlice = np.squeeze(mask_T1w_COR_VOL_L[k,:,:])
                        tempCount = len(tempVolSlice[tempVolSlice!=0])
                        COR_VOL_L = COR_VOL_L + tempCount

                    COR_VOL_R_ml = COR_VOL_R*T1w_VolumeQuantification[0]['PixelSpacing'][0]*T1w_VolumeQuantification[0]['PixelSpacing'][1]*T1w_VolumeQuantification[0]['SpacingBetweenSlices']/1000
                    COR_VOL_L_ml = COR_VOL_L*T1w_VolumeQuantification[0]['PixelSpacing'][0]*T1w_VolumeQuantification[0]['PixelSpacing'][1]*T1w_VolumeQuantification[0]['SpacingBetweenSlices']/1000
                    
                    COR_Tic_R = [
                                len(mask_T1w_COR_TIC_R_1[mask_T1w_COR_TIC_R_1!=0])*T1w_VolumeQuantification[0]['PixelSpacing'][0],
                                len(mask_T1w_COR_TIC_R_2[mask_T1w_COR_TIC_R_2!=0])*T1w_VolumeQuantification[0]['PixelSpacing'][0],
                                len(mask_T1w_COR_TIC_R_3[mask_T1w_COR_TIC_R_3!=0])*T1w_VolumeQuantification[0]['PixelSpacing'][0],
                                len(mask_T1w_COR_TIC_R_4[mask_T1w_COR_TIC_R_4!=0])*T1w_VolumeQuantification[0]['PixelSpacing'][0],
                                len(mask_T1w_COR_TIC_R_5[mask_T1w_COR_TIC_R_5!=0])*T1w_VolumeQuantification[0]['PixelSpacing'][0]
                                ]
                    
                    COR_Tic_L = [
                                len(mask_T1w_COR_TIC_L_1[mask_T1w_COR_TIC_L_1!=0])*T1w_VolumeQuantification[0]['PixelSpacing'][0],
                                len(mask_T1w_COR_TIC_L_2[mask_T1w_COR_TIC_L_2!=0])*T1w_VolumeQuantification[0]['PixelSpacing'][0],
                                len(mask_T1w_COR_TIC_L_3[mask_T1w_COR_TIC_L_3!=0])*T1w_VolumeQuantification[0]['PixelSpacing'][0],
                                len(mask_T1w_COR_TIC_L_4[mask_T1w_COR_TIC_L_4!=0])*T1w_VolumeQuantification[0]['PixelSpacing'][0],
                                len(mask_T1w_COR_TIC_L_5[mask_T1w_COR_TIC_L_5!=0])*T1w_VolumeQuantification[0]['PixelSpacing'][0]
                                ]
                                
                    #ADD CORTICAL TICKNESS L and R
                    row_T1w_CR =[
                                [studydate,site,subject,'Cortical Volume','R','COR','Total','ml',str(COR_VOL_R_ml)],
                                [studydate,site,subject,'Cortical Tickness','R','COR','Total','mm',str(np.mean(COR_Tic_R))]
                                ]
                    
                    row_T1w_CL =[
                                [studydate,site,subject,'Cortical Volume','L','COR','Total','ml',str(COR_VOL_L_ml)],
                                [studydate,site,subject,'Cortical Tickness','L','COR','Total','mm',str(np.mean(COR_Tic_L))]
                                ]

                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_T1w_CR)
                    csvwriter.writerows(row_T1w_CL)
                    csv_file.close()

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Volume Quantification was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Volume Quantification was NOT completed; error: "  + str(e))
                    file.close()

            if series[0]['SeriesDescription'] == "T1w_abdomen_dixon_cor_bh_fat":
                try:
                    T1w_Abdomen = series
                    
                    start_time = time.time()
                    
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Abdomen Quantification has started")
                    file.close()

                    ABD_SIN_FAT_R = 0
                    for k in range(np.shape(mask_T1w_SIN_FAT_VOL_R)[0]):
                        tempVolSlice = np.squeeze(mask_T1w_SIN_FAT_VOL_R[k,:,:])
                        tempCount = len(tempVolSlice[tempVolSlice!=0])
                        ABD_SIN_FAT_R = ABD_SIN_FAT_R + tempCount

                    ABD_SIN_FAT_L = 0
                    for k in range(np.shape(mask_T1w_SIN_FAT_VOL_L)[0]):
                        tempVolSlice = np.squeeze(mask_T1w_SIN_FAT_VOL_L[k,:,:])
                        tempCount = len(tempVolSlice[tempVolSlice!=0])
                        ABD_SIN_FAT_L = ABD_SIN_FAT_L + tempCount

                    PAR_VOL_R = 0
                    for k in range(np.shape(mask_T1w_PAR_VOL_R)[0]):
                        tempVolSlice = np.squeeze(mask_T1w_PAR_VOL_R[k,:,:])
                        tempCount = len(tempVolSlice[tempVolSlice!=0])
                        PAR_VOL_R = PAR_VOL_R + tempCount

                    PAR_VOL_L = 0
                    for k in range(np.shape(mask_T1w_PAR_VOL_L)[0]):
                        tempVolSlice = np.squeeze(mask_T1w_PAR_VOL_L[k,:,:])
                        tempCount = len(tempVolSlice[tempVolSlice!=0])
                        PAR_VOL_L = PAR_VOL_L + tempCount

                    ABD_SIN_FAT_R_ml = ABD_SIN_FAT_R*T1w_Abdomen[0]['PixelSpacing'][0]*T1w_Abdomen[0]['PixelSpacing'][1]*T1w_Abdomen[0]['SliceThickness']/1000
                    ABD_SIN_FAT_L_ml = ABD_SIN_FAT_L*T1w_Abdomen[0]['PixelSpacing'][0]*T1w_Abdomen[0]['PixelSpacing'][1]*T1w_Abdomen[0]['SliceThickness']/1000
                    PAR_VOL_R_ml = PAR_VOL_R*T1w_Abdomen[0]['PixelSpacing'][0]*T1w_Abdomen[0]['PixelSpacing'][1]*T1w_Abdomen[0]['SliceThickness']/1000
                    PAR_VOL_L_ml = PAR_VOL_L*T1w_Abdomen[0]['PixelSpacing'][0]*T1w_Abdomen[0]['PixelSpacing'][1]*T1w_Abdomen[0]['SliceThickness']/1000



                    row_T1w_ABD =[
                                [studydate,site,subject,'Sinus Volume','R','SIN','Total','ml',str(ABD_SIN_FAT_R_ml)],
                                [studydate,site,subject,'Sinus Volume','L','SIN','Total','ml',str(ABD_SIN_FAT_L_ml)],
                                [studydate,site,subject,'Parenchima Volume','R','PAR','Total','ml',str(PAR_VOL_R_ml)],
                                [studydate,site,subject,'Parenchima Volume','L','PAR','Total','ml',str(PAR_VOL_L_ml)],
                                ]


                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_T1w_ABD)
                    csv_file.close()

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Abdomen Quantification was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Abdomen Quantification was NOT completed; error: "  + str(e))
                    file.close()

            if series[0]['SeriesDescription'] == "T1_Map_Series_Registered":
                try:
                    T1_registered = series
                    for j_2,series in enumerate (list_series):
                        print(str(j_2) + ' : ' + series[0]['SeriesDescription'])
                        if series[0]['SeriesDescription'] == "T2_Series_Registered":
                            T2_registered = series
                            break

                    start_time = time.time()

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Joint T1 & T2 Mapping has started")
                    file.close()
                    
                    T1_KR,T2_KR = JointT1T2map(weasel, series = weasel.series_list([T1_registered, T2_registered]), mask=mask_T1T2_KID_R, export_ROI=True)
                    T1_KR = np.squeeze(T1_KR)
                    T2_KR = np.squeeze(T2_KR)

                    row_T1_KR = [
                                [studydate,site,subject,'T1','R','KID','Median','ms',str(np.median(T1_KR[T1_KR!=0]))],
                                [studydate,site,subject,'T1','R','KID','Mean','ms',str(np.mean(T1_KR[T1_KR!=0]))],
                                [studydate,site,subject,'T1','R','KID','Stdev','ms',str(np.std(T1_KR[T1_KR!=0]))],
                                [studydate,site,subject,'T1','R','KID','Mode','ms',str(stats.mode(T1_KR[T1_KR!=0])[0][0])],
                                [studydate,site,subject,'T1','R','KID','95%','ms',str(np.percentile(T1_KR[T1_KR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','KID','75%','ms',str(np.percentile(T1_KR[T1_KR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','KID','25%','ms',str(np.percentile(T1_KR[T1_KR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','KID','5%','ms',str(np.percentile(T1_KR[T1_KR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','KID','IQR','ms',str(np.percentile(T1_KR[T1_KR!=0], 75, interpolation = 'midpoint')-np.percentile(T1_KR[T1_KR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','KID','IQR/Median','%',str((np.percentile(T1_KR[T1_KR!=0], 75, interpolation = 'midpoint')-np.percentile(T1_KR[T1_KR!=0], 25, interpolation = 'midpoint'))/np.median(T1_KR[T1_KR!=0]))],
                                ]
                                        
                    row_T2_KR = [
                                [studydate,site,subject,'T2','R','KID','Median','ms',str(np.median(T2_KR[T2_KR!=0]))],
                                [studydate,site,subject,'T2','R','KID','Mean','ms',str(np.mean(T2_KR[T2_KR!=0]))],
                                [studydate,site,subject,'T2','R','KID','Stdev','ms',str(np.std(T2_KR[T2_KR!=0]))],
                                [studydate,site,subject,'T2','R','KID','Mode','ms',str(stats.mode(T2_KR[T2_KR!=0])[0][0])],
                                [studydate,site,subject,'T2','R','KID','95%','ms',str(np.percentile(T2_KR[T2_KR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','KID','75%','ms',str(np.percentile(T2_KR[T2_KR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','KID','25%','ms',str(np.percentile(T2_KR[T2_KR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','KID','5%','ms',str(np.percentile(T2_KR[T2_KR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','KID','IQR','ms',str(np.percentile(T2_KR[T2_KR!=0], 75, interpolation = 'midpoint')-np.percentile(T2_KR[T2_KR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','KID','IQR/Median','%',str((np.percentile(T2_KR[T2_KR!=0], 75, interpolation = 'midpoint')-np.percentile(T2_KR[T2_KR!=0], 25, interpolation = 'midpoint'))/np.median(T1_KR[T1_KR!=0]))],
                                ]                
                    
                    T1_CR = T1_KR*np.transpose(mask_T1T2_COR_R)
                    T2_CR = T2_KR*np.transpose(mask_T1T2_COR_R)
    
                    row_T1_CR = [
                                [studydate,site,subject,'T1','R','COR','Median','ms',str(np.median(T1_CR[T1_CR!=0]))],
                                [studydate,site,subject,'T1','R','COR','Mean','ms',str(np.mean(T1_CR[T1_CR!=0]))],
                                [studydate,site,subject,'T1','R','COR','Stdev','ms',str(np.std(T1_CR[T1_CR!=0]))],
                                [studydate,site,subject,'T1','R','COR','Mode','ms',str(stats.mode(T1_CR[T1_CR!=0])[0][0])],
                                [studydate,site,subject,'T1','R','COR','95%','ms',str(np.percentile(T1_CR[T1_CR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','COR','75%','ms',str(np.percentile(T1_CR[T1_CR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','COR','25%','ms',str(np.percentile(T1_CR[T1_CR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','COR','5%','ms',str(np.percentile(T1_CR[T1_CR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','COR','IQR','ms',str(np.percentile(T1_CR[T1_CR!=0], 75, interpolation = 'midpoint')-np.percentile(T1_CR[T1_CR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','COR','IQR/Median','%',str((np.percentile(T1_CR[T1_CR!=0], 75, interpolation = 'midpoint')-np.percentile(T1_CR[T1_CR!=0], 25, interpolation = 'midpoint'))/np.median(T1_CR[T1_CR!=0]))],
                                ]
                                        
                    row_T2_CR = [
                                [studydate,site,subject,'T2','R','COR','Median','ms',str(np.median(T2_CR[T2_CR!=0]))],
                                [studydate,site,subject,'T2','R','COR','Mean','ms',str(np.mean(T2_CR[T2_CR!=0]))],
                                [studydate,site,subject,'T2','R','COR','Stdev','ms',str(np.std(T2_CR[T2_CR!=0]))],
                                [studydate,site,subject,'T2','R','COR','Mode','ms',str(stats.mode(T2_CR[T2_CR!=0])[0][0])],
                                [studydate,site,subject,'T2','R','COR','95%','ms',str(np.percentile(T2_CR[T2_CR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','COR','75%','ms',str(np.percentile(T2_CR[T2_CR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','COR','25%','ms',str(np.percentile(T2_CR[T2_CR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','COR','5%','ms',str(np.percentile(T2_CR[T2_CR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','COR','IQR','ms',str(np.percentile(T2_CR[T2_CR!=0], 75, interpolation = 'midpoint')-np.percentile(T2_CR[T2_CR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','COR','IQR/Median','%',str((np.percentile(T2_CR[T2_CR!=0], 75, interpolation = 'midpoint')-np.percentile(T2_CR[T2_CR!=0], 25, interpolation = 'midpoint'))/np.median(T1_CR[T1_CR!=0]))],
                                ]

                    T1_MR = T1_KR*np.transpose(mask_T1T2_MED_R)
                    T2_MR = T2_KR*np.transpose(mask_T1T2_MED_R)

                    row_T1_MR = [
                                [studydate,site,subject,'T1','R','MED','Median','ms',str(np.median(T1_MR[T1_MR!=0]))],
                                [studydate,site,subject,'T1','R','MED','Mean','ms',str(np.mean(T1_MR[T1_MR!=0]))],
                                [studydate,site,subject,'T1','R','MED','Stdev','ms',str(np.std(T1_MR[T1_MR!=0]))],
                                [studydate,site,subject,'T1','R','MED','Mode','ms',str(stats.mode(T1_MR[T1_MR!=0])[0][0])],
                                [studydate,site,subject,'T1','R','MED','95%','ms',str(np.percentile(T1_MR[T1_MR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','MED','75%','ms',str(np.percentile(T1_MR[T1_MR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','MED','25%','ms',str(np.percentile(T1_MR[T1_MR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','MED','5%','ms',str(np.percentile(T1_MR[T1_MR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','MED','IQR','ms',str(np.percentile(T1_MR[T1_MR!=0], 75, interpolation = 'midpoint')-np.percentile(T1_MR[T1_MR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','R','MED','IQR/Median','%',str((np.percentile(T1_MR[T1_MR!=0], 75, interpolation = 'midpoint')-np.percentile(T1_MR[T1_MR!=0], 25, interpolation = 'midpoint'))/np.median(T1_CR[T1_CR!=0]))],
                                ] 
                    
            
                    row_T2_MR = [			    
                                [studydate,site,subject,'T2','R','MED','Median','ms',str(np.median(T2_MR[T2_MR!=0]))],
                                [studydate,site,subject,'T2','R','MED','Mean','ms',str(np.mean(T2_MR[T2_MR!=0]))],
                                [studydate,site,subject,'T2','R','MED','Stdev','ms',str(np.std(T2_MR[T2_MR!=0]))],
                                [studydate,site,subject,'T2','R','MED','Mode','ms',str(stats.mode(T2_MR[T2_MR!=0])[0][0])],
                                [studydate,site,subject,'T2','R','MED','95%','ms',str(np.percentile(T2_MR[T2_MR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','MED','75%','ms',str(np.percentile(T2_MR[T2_MR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','MED','25%','ms',str(np.percentile(T2_MR[T2_MR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','MED','5%','ms',str(np.percentile(T2_MR[T2_MR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','MED','IQR','ms',str(np.percentile(T2_MR[T2_MR!=0], 75, interpolation = 'midpoint')-np.percentile(T2_MR[T2_MR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','R','MED','IQR/Median','%',str((np.percentile(T2_MR[T2_MR!=0], 75, interpolation = 'midpoint')-np.percentile(T2_MR[T2_MR!=0], 25, interpolation = 'midpoint'))/np.median(T2_MR[T2_MR!=0]))],
                                ]
                    T1_KL,T2_KL = JointT1T2map(weasel, series = weasel.series_list([T1_registered, T2_registered]), mask=mask_T1T2_KID_L, export_ROI=True)
                    T1_KL = np.squeeze(T1_KL)
                    T2_KL = np.squeeze(T2_KL)

                    row_T1_KL = [
                                [studydate,site,subject,'T1','L','KID','Median','ms',str(np.median(T1_KL[T1_KL!=0]))],
                                [studydate,site,subject,'T1','L','KID','Mean','ms',str(np.mean(T1_KL[T1_KL!=0]))],
                                [studydate,site,subject,'T1','L','KID','Stdev','ms',str(np.std(T1_KL[T1_KL!=0]))],
                                [studydate,site,subject,'T1','L','KID','Mode','ms',str(stats.mode(T1_KL[T1_KL!=0])[0][0])],
                                [studydate,site,subject,'T1','L','KID','95%','ms',str(np.percentile(T1_KL[T1_KL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','KID','75%','ms',str(np.percentile(T1_KL[T1_KL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','KID','25%','ms',str(np.percentile(T1_KL[T1_KL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','KID','5%','ms',str(np.percentile(T1_KL[T1_KL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','KID','IQR','ms',str(np.percentile(T1_KL[T1_KL!=0], 75, interpolation = 'midpoint')-np.percentile(T1_KL[T1_KL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','KID','IQR/Median','%',str((np.percentile(T1_KL[T1_KL!=0], 75, interpolation = 'midpoint')-np.percentile(T1_KL[T1_KL!=0], 25, interpolation = 'midpoint'))/np.median(T1_KL[T1_KL!=0]))],
                                ]
                                        
                    row_T2_KL = [
                                [studydate,site,subject,'T2','L','KID','Median','ms',str(np.median(T2_KL[T2_KL!=0]))],
                                [studydate,site,subject,'T2','L','KID','Mean','ms',str(np.mean(T2_KL[T2_KL!=0]))],
                                [studydate,site,subject,'T2','L','KID','Stdev','ms',str(np.std(T2_KL[T2_KL!=0]))],
                                [studydate,site,subject,'T2','L','KID','Mode','ms',str(stats.mode(T2_KL[T2_KL!=0])[0][0])],
                                [studydate,site,subject,'T2','L','KID','95%','ms',str(np.percentile(T2_KL[T2_KL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','KID','75%','ms',str(np.percentile(T2_KL[T2_KL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','KID','25%','ms',str(np.percentile(T2_KL[T2_KL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','KID','5%','ms',str(np.percentile(T2_KL[T2_KL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','KID','IQR','ms',str(np.percentile(T2_KL[T2_KL!=0], 75, interpolation = 'midpoint')-np.percentile(T2_KL[T2_KL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','KID','IQR/Median','%',str((np.percentile(T2_KL[T2_KL!=0], 75, interpolation = 'midpoint')-np.percentile(T2_KL[T2_KL!=0], 25, interpolation = 'midpoint'))/np.median(T1_KL[T1_KL!=0]))],
                                ] 

                    T1_CL = T1_KL*np.transpose(mask_T1T2_COR_L)
                    T2_CL = T2_KL*np.transpose(mask_T1T2_COR_L)

                    row_T1_CL = [
                                [studydate,site,subject,'T1','L','COR','Median','ms',str(np.median(T1_CL[T1_CL!=0]))],
                                [studydate,site,subject,'T1','L','COR','Mean','ms',str(np.mean(T1_CL[T1_CL!=0]))],
                                [studydate,site,subject,'T1','L','COR','Stdev','ms',str(np.std(T1_CL[T1_CL!=0]))],
                                [studydate,site,subject,'T1','L','COR','Mode','ms',str(stats.mode(T1_CL[T1_CL!=0])[0][0])],
                                [studydate,site,subject,'T1','L','COR','95%','ms',str(np.percentile(T1_CL[T1_CL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','COR','75%','ms',str(np.percentile(T1_CL[T1_CL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','COR','25%','ms',str(np.percentile(T1_CL[T1_CL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','COR','5%','ms',str(np.percentile(T1_CL[T1_CL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','COR','IQR','ms',str(np.percentile(T1_CL[T1_CL!=0], 75, interpolation = 'midpoint')-np.percentile(T1_CL[T1_CL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','COR','IQR/Median','%',str((np.percentile(T1_CL[T1_CL!=0], 75, interpolation = 'midpoint')-np.percentile(T1_CL[T1_CL!=0], 25, interpolation = 'midpoint'))/np.median(T1_CL[T1_CL!=0]))],
                                ]

                    row_T2_CL = [
                                [studydate,site,subject,'T2','L','COR','Median','ms',str(np.median(T2_CL[T2_CL!=0]))],
                                [studydate,site,subject,'T2','L','COR','Mean','ms',str(np.mean(T2_CL[T2_CL!=0]))],
                                [studydate,site,subject,'T2','L','COR','Stdev','ms',str(np.std(T2_CL[T2_CL!=0]))],
                                [studydate,site,subject,'T2','L','COR','Mode','ms',str(stats.mode(T2_CL[T2_CL!=0])[0][0])],
                                [studydate,site,subject,'T2','L','COR','95%','ms',str(np.percentile(T2_CL[T2_CL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','COR','75%','ms',str(np.percentile(T2_CL[T2_CL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','COR','25%','ms',str(np.percentile(T2_CL[T2_CL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','COR','5%','ms',str(np.percentile(T2_CL[T2_CL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','COR','IQR','ms',str(np.percentile(T2_CL[T2_CL!=0], 75, interpolation = 'midpoint')-np.percentile(T2_CL[T2_CL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','COR','IQR/Median','%',str((np.percentile(T2_CL[T2_CL!=0], 75, interpolation = 'midpoint')-np.percentile(T2_CL[T2_CL!=0], 25, interpolation = 'midpoint'))/np.median(T1_CL[T1_CL!=0]))],
                                ]

                    T1_ML = T1_KL*np.transpose(mask_T1T2_MED_L)
                    T2_ML = T2_KL*np.transpose(mask_T1T2_MED_L)

                    row_T1_ML = [
                                [studydate,site,subject,'T1','L','MED','Median','ms',str(np.median(T1_ML[T1_ML!=0]))],
                                [studydate,site,subject,'T1','L','MED','Mean','ms',str(np.mean(T1_ML[T1_ML!=0]))],
                                [studydate,site,subject,'T1','L','MED','Stdev','ms',str(np.std(T1_ML[T1_ML!=0]))],
                                [studydate,site,subject,'T1','L','MED','Mode','ms',str(stats.mode(T1_ML[T1_ML!=0])[0][0])],
                                [studydate,site,subject,'T1','L','MED','95%','ms',str(np.percentile(T1_ML[T1_ML!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','MED','75%','ms',str(np.percentile(T1_ML[T1_ML!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','MED','25%','ms',str(np.percentile(T1_ML[T1_ML!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','MED','5%','ms',str(np.percentile(T1_ML[T1_ML!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','MED','IQR','ms',str(np.percentile(T1_ML[T1_ML!=0], 75, interpolation = 'midpoint')-np.percentile(T1_ML[T1_ML!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T1','L','MED','IQR/Median','%',str((np.percentile(T1_ML[T1_ML!=0], 75, interpolation = 'midpoint')-np.percentile(T1_ML[T1_ML!=0], 25, interpolation = 'midpoint'))/np.median(T1_ML[T1_ML!=0]))],
                                ]

                    row_T2_ML = [
                                [studydate,site,subject,'T2','L','MED','Median','ms',str(np.median(T2_ML[T2_ML!=0]))],
                                [studydate,site,subject,'T2','L','MED','Mean','ms',str(np.mean(T2_ML[T2_ML!=0]))],
                                [studydate,site,subject,'T2','L','MED','Stdev','ms',str(np.std(T2_ML[T2_ML!=0]))],
                                [studydate,site,subject,'T2','L','MED','Mode','ms',str(stats.mode(T2_ML[T2_ML!=0])[0][0])],
                                [studydate,site,subject,'T2','L','MED','95%','ms',str(np.percentile(T2_ML[T2_ML!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','MED','75%','ms',str(np.percentile(T2_ML[T2_ML!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','MED','25%','ms',str(np.percentile(T2_ML[T2_ML!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','MED','5%','ms',str(np.percentile(T2_ML[T2_ML!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','MED','IQR','ms',str(np.percentile(T2_ML[T2_ML!=0], 75, interpolation = 'midpoint')-np.percentile(T2_ML[T2_ML!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2','L','MED','IQR/Median','%',str((np.percentile(T2_ML[T2_ML!=0], 75, interpolation = 'midpoint')-np.percentile(T2_ML[T2_ML!=0], 25, interpolation = 'midpoint'))/np.median(T2_ML[T2_ML!=0]))],
                                ]
        
                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_T1_KR)
                    csvwriter.writerows(row_T2_KR)
                    csvwriter.writerows(row_T1_CR)
                    csvwriter.writerows(row_T2_CR)
                    csvwriter.writerows(row_T1_MR)
                    csvwriter.writerows(row_T2_MR)
                    csvwriter.writerows(row_T1_KL)
                    csvwriter.writerows(row_T2_KL)
                    csvwriter.writerows(row_T1_CL) 
                    csvwriter.writerows(row_T2_CL)
                    csvwriter.writerows(row_T1_ML) 
                    csvwriter.writerows(row_T2_ML)            
                    csv_file.close()
                
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Joint T1 & T2 Mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Joint T1 & T2 Mapping was NOT completed; error: "  + str(e))
                    file.close()

            elif series[0]['SeriesDescription'] == "T2star_MDR_Registered":
                try:
                    T2s_registered = series

                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Mapping has started")
                    file.close()

                    T2s_KR = T2smap(weasel, series=T2s_registered, mask=mask_T2s_KID_R, export_ROI=True)
                    T2s_KR = np.squeeze(T2s_KR)

                    row_T2s_KR =[
                                [studydate,site,subject,'T2*','R','KID','Median','ms',str(np.median(T2s_KR[T2s_KR!=0]))],
                                [studydate,site,subject,'T2*','R','KID','Mean','ms',str(np.mean(T2s_KR[T2s_KR!=0]))],
                                [studydate,site,subject,'T2*','R','KID','Stdev','ms',str(np.std(T2s_KR[T2s_KR!=0]))],
                                [studydate,site,subject,'T2*','R','KID','Mode','ms',str(stats.mode(T2s_KR[T2s_KR!=0])[0][0])],
                                [studydate,site,subject,'T2*','R','KID','95%','ms',str(np.percentile(T2s_KR[T2s_KR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','KID','75%','ms',str(np.percentile(T2s_KR[T2s_KR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','KID','25%','ms',str(np.percentile(T2s_KR[T2s_KR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','KID','5%','ms',str(np.percentile(T2s_KR[T2s_KR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','KID','IQR','ms',str(np.percentile(T2s_KR[T2s_KR!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_KR[T2s_KR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','KID','IQR/Median','%',str((np.percentile(T2s_KR[T2s_KR!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_KR[T2s_KR!=0], 25, interpolation = 'midpoint'))/np.median(T2s_KR[T2s_KR!=0]))],
                                ]  

                    T2s_CR = T2s_KR*np.transpose(mask_T2s_COR_R)

                    row_T2s_CR =[
                                [studydate,site,subject,'T2*','R','COR','Median','ms',str(np.median(T2s_CR[T2s_CR!=0]))],
                                [studydate,site,subject,'T2*','R','COR','Mean','ms',str(np.mean(T2s_CR[T2s_CR!=0]))],
                                [studydate,site,subject,'T2*','R','COR','Stdev','ms',str(np.std(T2s_CR[T2s_CR!=0]))],
                                [studydate,site,subject,'T2*','R','COR','Mode','ms',str(stats.mode(T2s_CR[T2s_CR!=0])[0][0])],
                                [studydate,site,subject,'T2*','R','COR','95%','ms',str(np.percentile(T2s_CR[T2s_CR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','COR','75%','ms',str(np.percentile(T2s_CR[T2s_CR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','COR','25%','ms',str(np.percentile(T2s_CR[T2s_CR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','COR','5%','ms',str(np.percentile(T2s_CR[T2s_CR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','COR','IQR','ms',str(np.percentile(T2s_CR[T2s_CR!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_CR[T2s_CR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','COR','IQR/Median','%',str((np.percentile(T2s_CR[T2s_CR!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_CR[T2s_CR!=0], 25, interpolation = 'midpoint'))/np.median(T2s_CR[T2s_CR!=0]))],
                                ]
                    
                    T2s_MR = T2s_KR*np.transpose(mask_T2s_MED_R)        
                    row_T2s_MR =[
                                [studydate,site,subject,'T2*','R','MED','Median','ms',str(np.median(T2s_MR[T2s_MR!=0]))],
                                [studydate,site,subject,'T2*','R','MED','Mean','ms',str(np.mean(T2s_MR[T2s_MR!=0]))],
                                [studydate,site,subject,'T2*','R','MED','Stdev','ms',str(np.std(T2s_MR[T2s_MR!=0]))],
                                [studydate,site,subject,'T2*','R','MED','Mode','ms',str(stats.mode(T2s_MR[T2s_MR!=0])[0][0])],
                                [studydate,site,subject,'T2*','R','MED','95%','ms',str(np.percentile(T2s_MR[T2s_MR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','MED','75%','ms',str(np.percentile(T2s_MR[T2s_MR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','MED','25%','ms',str(np.percentile(T2s_MR[T2s_MR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','MED','5%','ms',str(np.percentile(T2s_MR[T2s_MR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','MED','IQR','ms',str(np.percentile(T2s_MR[T2s_MR!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_MR[T2s_MR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','R','MED','IQR/Median','%',str((np.percentile(T2s_MR[T2s_MR!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_MR[T2s_MR!=0], 25, interpolation = 'midpoint'))/np.median(T2s_MR[T2s_MR!=0]))],
                                ]
                    
                    T2s_KL = T2smap(weasel, series=T2s_registered, mask=mask_T2s_KID_L, export_ROI=True)
                    T2s_KL = np.squeeze(T2s_KL)
                    row_T2s_KL =[
                                [studydate,site,subject,'T2*','L','KID','Median','ms',str(np.median(T2s_KL[T2s_KL!=0]))],
                                [studydate,site,subject,'T2*','L','KID','Mean','ms',str(np.mean(T2s_KL[T2s_KL!=0]))],
                                [studydate,site,subject,'T2*','L','KID','Stdev','ms',str(np.std(T2s_KL[T2s_KL!=0]))],
                                [studydate,site,subject,'T2*','L','KID','Mode','ms',str(stats.mode(T2s_KL[T2s_KL!=0])[0][0])],
                                [studydate,site,subject,'T2*','L','KID','95%','ms',str(np.percentile(T2s_KL[T2s_KL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','KID','75%','ms',str(np.percentile(T2s_KL[T2s_KL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','KID','25%','ms',str(np.percentile(T2s_KL[T2s_KL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','KID','5%','ms',str(np.percentile(T2s_KL[T2s_KL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','KID','IQR','ms',str(np.percentile(T2s_KL[T2s_KL!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_KL[T2s_KL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','KID','IQR/Median','%',str((np.percentile(T2s_KL[T2s_KL!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_KL[T2s_KL!=0], 25, interpolation = 'midpoint'))/np.median(T2s_KL[T2s_KL!=0]))],
                                ] 

                    T2s_CL = T2s_KL*np.transpose(mask_T2s_COR_L)
                    row_T2s_CL =[
                                [studydate,site,subject,'T2*','L','COR','Median','ms',str(np.median(T2s_CL[T2s_CL!=0]))],
                                [studydate,site,subject,'T2*','L','COR','Mean','ms',str(np.mean(T2s_CL[T2s_CL!=0]))],
                                [studydate,site,subject,'T2*','L','COR','Stdev','ms',str(np.std(T2s_CL[T2s_CL!=0]))],
                                [studydate,site,subject,'T2*','L','COR','Mode','ms',str(stats.mode(T2s_CL[T2s_CL!=0])[0][0])],
                                [studydate,site,subject,'T2*','L','COR','95%','ms',str(np.percentile(T2s_CL[T2s_CL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','COR','75%','ms',str(np.percentile(T2s_CL[T2s_CL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','COR','25%','ms',str(np.percentile(T2s_CL[T2s_CL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','COR','5%','ms',str(np.percentile(T2s_CL[T2s_CL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','COR','IQR','ms',str(np.percentile(T2s_CL[T2s_CL!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_CL[T2s_CL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','COR','IQR/Median','%',str((np.percentile(T2s_CL[T2s_CL!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_CL[T2s_CL!=0], 25, interpolation = 'midpoint'))/np.median(T2s_CL[T2s_CL!=0]))],
                                ]

                    T2s_ML = T2s_KL*np.transpose(mask_T2s_MED_L)                
                    row_T2s_ML =[
                                [studydate,site,subject,'T2*','L','MED','Median','ms',str(np.median(T2s_ML[T2s_ML!=0]))],
                                [studydate,site,subject,'T2*','L','MED','Mean','ms',str(np.mean(T2s_ML[T2s_ML!=0]))],
                                [studydate,site,subject,'T2*','L','MED','Stdev','ms',str(np.std(T2s_ML[T2s_ML!=0]))],
                                [studydate,site,subject,'T2*','L','MED','Mode','ms',str(stats.mode(T2s_ML[T2s_ML!=0])[0][0])],
                                [studydate,site,subject,'T2*','L','MED','95%','ms',str(np.percentile(T2s_ML[T2s_ML!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','MED','75%','ms',str(np.percentile(T2s_ML[T2s_ML!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','MED','25%','ms',str(np.percentile(T2s_ML[T2s_ML!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','MED','5%','ms',str(np.percentile(T2s_ML[T2s_ML!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','MED','IQR','ms',str(np.percentile(T2s_ML[T2s_ML!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_ML[T2s_ML!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','L','MED','IQR/Median','%',str((np.percentile(T2s_ML[T2s_ML!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_ML[T2s_ML!=0], 25, interpolation = 'midpoint'))/np.median(T2s_ML[T2s_ML!=0]))],
                                ]

                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_T2s_KR)
                    csvwriter.writerows(row_T2s_CR)
                    csvwriter.writerows(row_T2s_MR)
                    csvwriter.writerows(row_T2s_KL)
                    csvwriter.writerows(row_T2s_CL)
                    csvwriter.writerows(row_T2s_ML)           
                    csv_file.close()

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Mapping was NOT completed; error: " + str(e)) 
                    file.close()


                
            elif series[0]['SeriesDescription'] == "IVIM_Registered":
                try:
                    IVIM_registered = series

                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM Mapping has started")
                    file.close()


                    ADC_KR = ADCmap(weasel, series=IVIM_registered, mask=mask_IVIM_KID_R,export_ROI=True)
                    ADC_KR = np.squeeze(ADC_KR)


                    row_ADC_KR =[
                                [studydate,site,subject,'ADC','R','KID','Median','mm2/s',str(np.median(ADC_KR[ADC_KR!=0]))],
                                [studydate,site,subject,'ADC','R','KID','Mean','mm2/s',str(np.mean(ADC_KR[ADC_KR!=0]))],
                                [studydate,site,subject,'ADC','R','KID','Stdev','mm2/s',str(np.std(ADC_KR[ADC_KR!=0]))],
                                [studydate,site,subject,'ADC','R','KID','Mode','mm2/s',str(stats.mode(ADC_KR[ADC_KR!=0])[0][0])],
                                [studydate,site,subject,'ADC','R','KID','95%','mm2/s',str(np.percentile(ADC_KR[ADC_KR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','KID','75%','mm2/s',str(np.percentile(ADC_KR[ADC_KR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','KID','25%','mm2/s',str(np.percentile(ADC_KR[ADC_KR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','KID','5%','mm2/s',str(np.percentile(ADC_KR[ADC_KR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','KID','IQR','mm2/s',str(np.percentile(ADC_KR[ADC_KR!=0], 75, interpolation = 'midpoint')-np.percentile(ADC_KR[ADC_KR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','KID','IQR/Median','%',str((np.percentile(ADC_KR[ADC_KR!=0], 75, interpolation = 'midpoint')-np.percentile(ADC_KR[ADC_KR!=0], 25, interpolation = 'midpoint'))/np.median(ADC_KR[ADC_KR!=0]))],
                                ]

                    ADC_CR = ADC_KR*np.transpose(mask_IVIM_COR_R)
                    row_ADC_CR =[
                                [studydate,site,subject,'ADC','R','COR','Median','mm2/s',str(np.median(ADC_CR[ADC_CR!=0]))],
                                [studydate,site,subject,'ADC','R','COR','Mean','mm2/s',str(np.mean(ADC_CR[ADC_CR!=0]))],
                                [studydate,site,subject,'ADC','R','COR','Stdev','mm2/s',str(np.std(ADC_CR[ADC_CR!=0]))],
                                [studydate,site,subject,'ADC','R','COR','Mode','mm2/s',str(stats.mode(ADC_CR[ADC_CR!=0])[0][0])],
                                [studydate,site,subject,'ADC','R','COR','95%','mm2/s',str(np.percentile(ADC_CR[ADC_CR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','COR','75%','mm2/s',str(np.percentile(ADC_CR[ADC_CR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','COR','25%','mm2/s',str(np.percentile(ADC_CR[ADC_CR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','COR','5%','mm2/s',str(np.percentile(ADC_CR[ADC_CR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','COR','IQR','mm2/s',str(np.percentile(ADC_CR[ADC_CR!=0], 75, interpolation = 'midpoint')-np.percentile(ADC_CR[ADC_CR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','COR','IQR/Median','%',str((np.percentile(ADC_CR[ADC_CR!=0], 75, interpolation = 'midpoint')-np.percentile(ADC_CR[ADC_CR!=0], 25, interpolation = 'midpoint'))/np.median(ADC_CR[ADC_CR!=0]))],
                                ]

                    ADC_MR = ADC_KR*np.transpose(mask_IVIM_MED_R)
                    row_ADC_MR =[
                                [studydate,site,subject,'ADC','R','MED','Median','mm2/s',str(np.median(ADC_MR[ADC_MR!=0]))],
                                [studydate,site,subject,'ADC','R','MED','Mean','mm2/s',str(np.mean(ADC_MR[ADC_MR!=0]))],
                                [studydate,site,subject,'ADC','R','MED','Stdev','mm2/s',str(np.std(ADC_MR[ADC_MR!=0]))],
                                [studydate,site,subject,'ADC','R','MED','Mode','mm2/s',str(stats.mode(ADC_MR[ADC_MR!=0])[0][0])],
                                [studydate,site,subject,'ADC','R','MED','95%','mm2/s',str(np.percentile(ADC_MR[ADC_MR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','MED','75%','mm2/s',str(np.percentile(ADC_MR[ADC_MR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','MED','25%','mm2/s',str(np.percentile(ADC_MR[ADC_MR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','MED','5%','mm2/s',str(np.percentile(ADC_MR[ADC_MR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','MED','IQR','mm2/s',str(np.percentile(ADC_MR[ADC_MR!=0], 75, interpolation = 'midpoint')-np.percentile(ADC_MR[ADC_MR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','R','MED','IQR/Median','%',str((np.percentile(ADC_MR[ADC_MR!=0], 75, interpolation = 'midpoint')-np.percentile(ADC_MR[ADC_MR!=0], 25, interpolation = 'midpoint'))/np.median(ADC_MR[ADC_MR!=0]))],
                                ]

                    ADC_KL = ADCmap(weasel, series=IVIM_registered, mask=mask_IVIM_KID_L,export_ROI=True)
                    ADC_KL = np.squeeze(ADC_KL)

                    row_ADC_KL =[
                                [studydate,site,subject,'ADC','L','KID','Median','mm2/s',str(np.median(ADC_KL[ADC_KL!=0]))],
                                [studydate,site,subject,'ADC','L','KID','Mean','mm2/s',str(np.mean(ADC_KL[ADC_KL!=0]))],
                                [studydate,site,subject,'ADC','L','KID','Stdev','mm2/s',str(np.std(ADC_KL[ADC_KL!=0]))],
                                [studydate,site,subject,'ADC','L','KID','Mode','mm2/s',str(stats.mode(ADC_KL[ADC_KL!=0])[0][0])],
                                [studydate,site,subject,'ADC','L','KID','95%','mm2/s',str(np.percentile(ADC_KL[ADC_KL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','KID','75%','mm2/s',str(np.percentile(ADC_KL[ADC_KL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','KID','25%','mm2/s',str(np.percentile(ADC_KL[ADC_KL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','KID','5%','mm2/s',str(np.percentile(ADC_KL[ADC_KL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','KID','IQR','mm2/s',str(np.percentile(ADC_KL[ADC_KL!=0], 75, interpolation = 'midpoint')-np.percentile(ADC_KL[ADC_KL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','KID','IQR/Median','%',str((np.percentile(ADC_KL[ADC_KL!=0], 75, interpolation = 'midpoint')-np.percentile(ADC_KL[ADC_KL!=0], 25, interpolation = 'midpoint'))/np.median(ADC_KL[ADC_KL!=0]))],
                                ]

                    ADC_CL = ADC_KL*np.transpose(mask_IVIM_COR_L)
                    row_ADC_CL =[
                                [studydate,site,subject,'ADC','L','COR','Median','mm2/s',str(np.median(ADC_CL[ADC_CL!=0]))],
                                [studydate,site,subject,'ADC','L','COR','Mean','mm2/s',str(np.mean(ADC_CL[ADC_CL!=0]))],
                                [studydate,site,subject,'ADC','L','COR','Stdev','mm2/s',str(np.std(ADC_CL[ADC_CL!=0]))],
                                [studydate,site,subject,'ADC','L','COR','Mode','mm2/s',str(stats.mode(ADC_CL[ADC_CL!=0])[0][0])],
                                [studydate,site,subject,'ADC','L','COR','95%','mm2/s',str(np.percentile(ADC_CL[ADC_CL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','COR','75%','mm2/s',str(np.percentile(ADC_CL[ADC_CL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','COR','25%','mm2/s',str(np.percentile(ADC_CL[ADC_CL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','COR','5%','mm2/s',str(np.percentile(ADC_CL[ADC_CL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','COR','IQR','mm2/s',str(np.percentile(ADC_CL[ADC_CL!=0], 75, interpolation = 'midpoint')-np.percentile(ADC_CL[ADC_CL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','COR','IQR/Median','%',str((np.percentile(ADC_CL[ADC_CL!=0], 75, interpolation = 'midpoint')-np.percentile(ADC_CL[ADC_CL!=0], 25, interpolation = 'midpoint'))/np.median(ADC_CL[ADC_CL!=0]))],
                                ]

                    ADC_ML = ADC_KL*np.transpose(mask_IVIM_MED_L)
                    row_ADC_ML =[
                                [studydate,site,subject,'ADC','L','MED','Median','mm2/s',str(np.median(ADC_ML[ADC_ML!=0]))],
                                [studydate,site,subject,'ADC','L','MED','Mean','mm2/s',str(np.mean(ADC_ML[ADC_ML!=0]))],
                                [studydate,site,subject,'ADC','L','MED','Stdev','mm2/s',str(np.std(ADC_ML[ADC_ML!=0]))],
                                [studydate,site,subject,'ADC','L','MED','Mode','mm2/s',str(stats.mode(ADC_ML[ADC_ML!=0])[0][0])],
                                [studydate,site,subject,'ADC','L','MED','95%','mm2/s',str(np.percentile(ADC_ML[ADC_ML!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','MED','75%','mm2/s',str(np.percentile(ADC_ML[ADC_ML!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','MED','25%','mm2/s',str(np.percentile(ADC_ML[ADC_ML!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','MED','5%','mm2/s',str(np.percentile(ADC_ML[ADC_ML!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','MED','IQR','mm2/s',str(np.percentile(ADC_ML[ADC_ML!=0], 75, interpolation = 'midpoint')-np.percentile(ADC_ML[ADC_ML!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'ADC','L','MED','IQR/Median','%',str((np.percentile(ADC_ML[ADC_ML!=0], 75, interpolation = 'midpoint')-np.percentile(ADC_ML[ADC_ML!=0], 25, interpolation = 'midpoint'))/np.median(ADC_ML[ADC_ML!=0]))],
                                ]
                    
                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_ADC_KR)
                    csvwriter.writerows(row_ADC_CR)
                    csvwriter.writerows(row_ADC_MR)
                    csvwriter.writerows(row_ADC_KL)  
                    csvwriter.writerows(row_ADC_CL)  
                    csvwriter.writerows(row_ADC_ML)             
                    csv_file.close()            

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM-ADC Mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()
                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": IVIM-ADC Mapping was NOT completed; error: " + str(e)) 
                    file.close()

            elif series[0]['SeriesDescription'] == "DTI_Registered":
                try:
                    DTI_registered = series

                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI Mapping has started")
                    file.close()

                    DTI_FAmap = FAmap(weasel, series=DTI_registered, mask=None,export_ROI=True)
                    FA_KR = DTI_FAmap*np.transpose(mask_DTI_KID_R)
                    FA_CR = DTI_FAmap*np.transpose(mask_DTI_COR_R)
                    FA_MR = DTI_FAmap*np.transpose(mask_DTI_MED_R)
                    FA_KL = DTI_FAmap*np.transpose(mask_DTI_KID_L)
                    FA_CL = DTI_FAmap*np.transpose(mask_DTI_COR_L)
                    FA_ML = DTI_FAmap*np.transpose(mask_DTI_MED_L)

                    row_FA_KR =[
                                [studydate,site,subject,'FA','R','KID','Median','%',str(np.median(FA_KR[FA_KR!=0]))],
                                [studydate,site,subject,'FA','R','KID','Mean','%',str(np.mean(FA_KR[FA_KR!=0]))],
                                [studydate,site,subject,'FA','R','KID','Stdev','%',str(np.std(FA_KR[FA_KR!=0]))],
                                [studydate,site,subject,'FA','R','KID','Mode','%',str(stats.mode(FA_KR[FA_KR!=0])[0][0])],
                                [studydate,site,subject,'FA','R','KID','95%','%',str(np.percentile(FA_KR[FA_KR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','KID','75%','%',str(np.percentile(FA_KR[FA_KR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','KID','25%','%',str(np.percentile(FA_KR[FA_KR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','KID','5%','%',str(np.percentile(FA_KR[FA_KR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','KID','IQR','%',str(np.percentile(FA_KR[FA_KR!=0], 75, interpolation = 'midpoint')-np.percentile(FA_KR[FA_KR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','KID','IQR/Median','%',str((np.percentile(FA_KR[FA_KR!=0], 75, interpolation = 'midpoint')-np.percentile(FA_KR[FA_KR!=0], 25, interpolation = 'midpoint'))/np.median(FA_KR[FA_KR!=0]))],
                                ]

                    row_FA_CR =[
                                [studydate,site,subject,'FA','R','COR','Median','%',str(np.median(FA_CR[FA_CR!=0]))],
                                [studydate,site,subject,'FA','R','COR','Mean','%',str(np.mean(FA_CR[FA_CR!=0]))],
                                [studydate,site,subject,'FA','R','COR','Stdev','%',str(np.std(FA_CR[FA_CR!=0]))],
                                [studydate,site,subject,'FA','R','COR','Mode','%',str(stats.mode(FA_CR[FA_CR!=0])[0][0])],
                                [studydate,site,subject,'FA','R','COR','95%','%',str(np.percentile(FA_CR[FA_CR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','COR','75%','%',str(np.percentile(FA_CR[FA_CR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','COR','25%','%',str(np.percentile(FA_CR[FA_CR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','COR','5%','%',str(np.percentile(FA_CR[FA_CR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','COR','IQR','%',str(np.percentile(FA_CR[FA_CR!=0], 75, interpolation = 'midpoint')-np.percentile(FA_CR[FA_CR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','COR','IQR/Median','%',str((np.percentile(FA_CR[FA_CR!=0], 75, interpolation = 'midpoint')-np.percentile(FA_CR[FA_CR!=0], 25, interpolation = 'midpoint'))/np.median(FA_CR[FA_CR!=0]))],
                                ]
                    
                    row_FA_MR =[
                                [studydate,site,subject,'FA','R','MED','Median','%',str(np.median(FA_MR[FA_MR!=0]))],
                                [studydate,site,subject,'FA','R','MED','Mean','%',str(np.mean(FA_MR[FA_MR!=0]))],
                                [studydate,site,subject,'FA','R','MED','Stdev','%',str(np.std(FA_MR[FA_MR!=0]))],
                                [studydate,site,subject,'FA','R','MED','Mode','%',str(stats.mode(FA_MR[FA_MR!=0])[0][0])],
                                [studydate,site,subject,'FA','R','MED','95%','%',str(np.percentile(FA_MR[FA_MR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','MED','75%','%',str(np.percentile(FA_MR[FA_MR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','MED','25%','%',str(np.percentile(FA_MR[FA_MR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','MED','5%','%',str(np.percentile(FA_MR[FA_MR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','MED','IQR','%',str(np.percentile(FA_MR[FA_MR!=0], 75, interpolation = 'midpoint')-np.percentile(FA_MR[FA_MR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','R','MED','IQR/Median','%',str((np.percentile(FA_MR[FA_MR!=0], 75, interpolation = 'midpoint')-np.percentile(FA_MR[FA_MR!=0], 25, interpolation = 'midpoint'))/np.median(FA_MR[FA_MR!=0]))],
                                ]

                    row_FA_KL =[
                                [studydate,site,subject,'FA','L','KID','Median','%',str(np.median(FA_KL[FA_KL!=0]))],
                                [studydate,site,subject,'FA','L','KID','Mean','%',str(np.mean(FA_KL[FA_KL!=0]))],
                                [studydate,site,subject,'FA','L','KID','Stdev','%',str(np.std(FA_KL[FA_KL!=0]))],
                                [studydate,site,subject,'FA','L','KID','Mode','%',str(stats.mode(FA_KL[FA_KL!=0])[0][0])],
                                [studydate,site,subject,'FA','L','KID','95%','%',str(np.percentile(FA_KL[FA_KL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','KID','75%','%',str(np.percentile(FA_KL[FA_KL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','KID','25%','%',str(np.percentile(FA_KL[FA_KL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','KID','5%','%',str(np.percentile(FA_KL[FA_KL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','KID','IQR','%',str(np.percentile(FA_KL[FA_KL!=0], 75, interpolation = 'midpoint')-np.percentile(FA_KL[FA_KL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','KID','IQR/Median','%',str((np.percentile(FA_KL[FA_KL!=0], 75, interpolation = 'midpoint')-np.percentile(FA_KL[FA_KL!=0], 25, interpolation = 'midpoint'))/np.median(FA_KL[FA_KL!=0]))],
                                ]

                    row_FA_CL =[
                                [studydate,site,subject,'FA','L','COR','Median','%',str(np.median(FA_CL[FA_CL!=0]))],
                                [studydate,site,subject,'FA','L','COR','Mean','%',str(np.mean(FA_CL[FA_CL!=0]))],
                                [studydate,site,subject,'FA','L','COR','Stdev','%',str(np.std(FA_CL[FA_CL!=0]))],
                                [studydate,site,subject,'FA','L','COR','Mode','%',str(stats.mode(FA_CL[FA_CL!=0])[0][0])],
                                [studydate,site,subject,'FA','L','COR','95%','%',str(np.percentile(FA_CL[FA_CL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','COR','75%','%',str(np.percentile(FA_CL[FA_CL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','COR','25%','%',str(np.percentile(FA_CL[FA_CL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','COR','5%','%',str(np.percentile(FA_CL[FA_CL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','COR','IQR','%',str(np.percentile(FA_CL[FA_CL!=0], 75, interpolation = 'midpoint')-np.percentile(FA_CL[FA_CL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','COR','IQR/Median','%',str((np.percentile(FA_CL[FA_CL!=0], 75, interpolation = 'midpoint')-np.percentile(FA_CL[FA_CL!=0], 25, interpolation = 'midpoint'))/np.median(FA_CL[FA_CL!=0]))],
                                ]

                    row_FA_ML =[
                                [studydate,site,subject,'FA','L','MED','Median','%',str(np.median(FA_ML[FA_ML!=0]))],
                                [studydate,site,subject,'FA','L','MED','Mean','%',str(np.mean(FA_ML[FA_ML!=0]))],
                                [studydate,site,subject,'FA','L','MED','Stdev','%',str(np.std(FA_ML[FA_ML!=0]))],
                                [studydate,site,subject,'FA','L','MED','Mode','%',str(stats.mode(FA_ML[FA_ML!=0])[0][0])],
                                [studydate,site,subject,'FA','L','MED','95%','%',str(np.percentile(FA_ML[FA_ML!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','MED','75%','%',str(np.percentile(FA_ML[FA_ML!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','MED','25%','%',str(np.percentile(FA_ML[FA_ML!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','MED','5%','%',str(np.percentile(FA_ML[FA_ML!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','MED','IQR','%',str(np.percentile(FA_ML[FA_ML!=0], 75, interpolation = 'midpoint')-np.percentile(FA_ML[FA_ML!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'FA','L','MED','IQR/Median','%',str((np.percentile(FA_ML[FA_ML!=0], 75, interpolation = 'midpoint')-np.percentile(FA_ML[FA_ML!=0], 25, interpolation = 'midpoint'))/np.median(FA_ML[FA_ML!=0]))],
                                ]

                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_FA_KR)
                    csvwriter.writerows(row_FA_CR)
                    csvwriter.writerows(row_FA_MR)
                    csvwriter.writerows(row_FA_KL)
                    csvwriter.writerows(row_FA_CL)  
                    csvwriter.writerows(row_FA_ML)             
                    csv_file.close()                

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI-FA Mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI-FA Mapping was NOT completed; error: "+str(e)) 
                    file.close()

            elif series[0]['SeriesDescription'] == "MTR_Map_Registered":
                try:

                    MT_registered = series.PixelArray

                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT Mapping has started")
                    file.close()

                    MT_KR = MT_registered*mask_MT_KID_R
                    MT_CR = MT_registered*mask_MT_COR_R
                    MT_MR = MT_registered*mask_MT_MED_R
                    MT_KL = MT_registered*mask_MT_KID_L
                    MT_CL = MT_registered*mask_MT_COR_L
                    MT_ML = MT_registered*mask_MT_MED_L

                    row_MT_KR =[
                                [studydate,site,subject,'MT','R','KID','Median','%',str(np.median(MT_KR[MT_KR!=0]))],
                                [studydate,site,subject,'MT','R','KID','Mean','%',str(np.mean(MT_KR[MT_KR!=0]))],
                                [studydate,site,subject,'MT','R','KID','Stdev','%',str(np.std(MT_KR[MT_KR!=0]))],
                                [studydate,site,subject,'MT','R','KID','Mode','%',str(stats.mode(MT_KR[MT_KR!=0])[0][0])],
                                [studydate,site,subject,'MT','R','KID','95%','%',str(np.percentile(MT_KR[MT_KR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','KID','75%','%',str(np.percentile(MT_KR[MT_KR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','KID','25%','%',str(np.percentile(MT_KR[MT_KR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','KID','5%','%',str(np.percentile(MT_KR[MT_KR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','KID','IQR','%',str(np.percentile(MT_KR[MT_KR!=0], 75, interpolation = 'midpoint')-np.percentile(MT_KR[MT_KR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','KID','IQR/Median','%',str((np.percentile(MT_KR[MT_KR!=0], 75, interpolation = 'midpoint')-np.percentile(MT_KR[MT_KR!=0], 25, interpolation = 'midpoint'))/np.median(MT_KR[MT_KR!=0]))],
                                ]

                    row_MT_CR =[
                                [studydate,site,subject,'MT','R','COR','Median','%',str(np.median(MT_CR[MT_CR!=0]))],
                                [studydate,site,subject,'MT','R','COR','Mean','%',str(np.mean(MT_CR[MT_CR!=0]))],
                                [studydate,site,subject,'MT','R','COR','Stdev','%',str(np.std(MT_CR[MT_CR!=0]))],
                                [studydate,site,subject,'MT','R','COR','Mode','%',str(stats.mode(MT_CR[MT_CR!=0])[0][0])],
                                [studydate,site,subject,'MT','R','COR','95%','%',str(np.percentile(MT_CR[MT_CR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','COR','75%','%',str(np.percentile(MT_CR[MT_CR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','COR','25%','%',str(np.percentile(MT_CR[MT_CR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','COR','5%','%',str(np.percentile(MT_CR[MT_CR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','COR','IQR','%',str(np.percentile(MT_CR[MT_CR!=0], 75, interpolation = 'midpoint')-np.percentile(MT_CR[MT_CR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','COR','IQR/Median','%',str((np.percentile(MT_CR[MT_CR!=0], 75, interpolation = 'midpoint')-np.percentile(MT_CR[MT_CR!=0], 25, interpolation = 'midpoint'))/np.median(MT_CR[MT_CR!=0]))],
                                ]

                    row_MT_MR =[
                                [studydate,site,subject,'MT','R','MED','Median','%',str(np.median(MT_MR[MT_MR!=0]))],
                                [studydate,site,subject,'MT','R','MED','Mean','%',str(np.mean(MT_MR[MT_MR!=0]))],
                                [studydate,site,subject,'MT','R','MED','Stdev','%',str(np.std(MT_MR[MT_MR!=0]))],
                                [studydate,site,subject,'MT','R','MED','Mode','%',str(stats.mode(MT_MR[MT_MR!=0])[0][0])],
                                [studydate,site,subject,'MT','R','MED','95%','%',str(np.percentile(MT_MR[MT_MR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','MED','75%','%',str(np.percentile(MT_MR[MT_MR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','MED','25%','%',str(np.percentile(MT_MR[MT_MR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','MED','5%','%',str(np.percentile(MT_MR[MT_MR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','MED','IQR','%',str(np.percentile(MT_MR[MT_MR!=0], 75, interpolation = 'midpoint')-np.percentile(MT_MR[MT_MR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','R','MED','IQR/Median','%',str((np.percentile(MT_MR[MT_MR!=0], 75, interpolation = 'midpoint')-np.percentile(MT_MR[MT_MR!=0], 25, interpolation = 'midpoint'))/np.median(MT_MR[MT_MR!=0]))],
                                ]

                    row_MT_KL =[
                                [studydate,site,subject,'MT','L','KID','Median','%',str(np.median(MT_KL[MT_KL!=0]))],
                                [studydate,site,subject,'MT','L','KID','Mean','%',str(np.mean(MT_KL[MT_KL!=0]))],
                                [studydate,site,subject,'MT','L','KID','Stdev','%',str(np.std(MT_KL[MT_KL!=0]))],
                                [studydate,site,subject,'MT','L','KID','Mode','%',str(stats.mode(MT_KL[MT_KL!=0])[0][0])],
                                [studydate,site,subject,'MT','L','KID','95%','%',str(np.percentile(MT_KL[MT_KL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','KID','75%','%',str(np.percentile(MT_KL[MT_KL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','KID','25%','%',str(np.percentile(MT_KL[MT_KL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','KID','5%','%',str(np.percentile(MT_KL[MT_KL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','KID','IQR','%',str(np.percentile(MT_KL[MT_KL!=0], 75, interpolation = 'midpoint')-np.percentile(MT_KL[MT_KL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','KID','IQR/Median','%',str((np.percentile(MT_KL[MT_KL!=0], 75, interpolation = 'midpoint')-np.percentile(MT_KL[MT_KL!=0], 25, interpolation = 'midpoint'))/np.median(MT_KL[MT_KL!=0]))],
                                ]

                    row_MT_CL =[
                                [studydate,site,subject,'MT','L','COR','Median','%',str(np.median(MT_CL[MT_CL!=0]))],
                                [studydate,site,subject,'MT','L','COR','Mean','%',str(np.mean(MT_CL[MT_CL!=0]))],
                                [studydate,site,subject,'MT','L','COR','Stdev','%',str(np.std(MT_CL[MT_CL!=0]))],
                                [studydate,site,subject,'MT','L','COR','Mode','%',str(stats.mode(MT_CL[MT_CL!=0])[0][0])],
                                [studydate,site,subject,'MT','L','COR','95%','%',str(np.percentile(MT_CL[MT_CL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','COR','75%','%',str(np.percentile(MT_CL[MT_CL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','COR','25%','%',str(np.percentile(MT_CL[MT_CL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','COR','5%','%',str(np.percentile(MT_CL[MT_CL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','COR','IQR','%',str(np.percentile(MT_CL[MT_CL!=0], 75, interpolation = 'midpoint')-np.percentile(MT_CL[MT_CL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','COR','IQR/Median','%',str((np.percentile(MT_CL[MT_CL!=0], 75, interpolation = 'midpoint')-np.percentile(MT_CL[MT_CL!=0], 25, interpolation = 'midpoint'))/np.median(MT_CL[MT_CL!=0]))],
                                ]

                    row_MT_ML =[
                                [studydate,site,subject,'MT','L','MED','Median','%',str(np.median(MT_ML[MT_ML!=0]))],
                                [studydate,site,subject,'MT','L','MED','Mean','%',str(np.mean(MT_ML[MT_ML!=0]))],
                                [studydate,site,subject,'MT','L','MED','Stdev','%',str(np.std(MT_ML[MT_ML!=0]))],
                                [studydate,site,subject,'MT','L','MED','Mode','%',str(stats.mode(MT_ML[MT_ML!=0])[0][0])],
                                [studydate,site,subject,'MT','L','MED','95%','%',str(np.percentile(MT_ML[MT_ML!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','MED','75%','%',str(np.percentile(MT_ML[MT_ML!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','MED','25%','%',str(np.percentile(MT_ML[MT_ML!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','MED','5%','%',str(np.percentile(MT_ML[MT_ML!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','MED','IQR','%',str(np.percentile(MT_ML[MT_ML!=0], 75, interpolation = 'midpoint')-np.percentile(MT_ML[MT_ML!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'MT','L','MED','IQR/Median','%',str((np.percentile(MT_ML[MT_ML!=0], 75, interpolation = 'midpoint')-np.percentile(MT_ML[MT_ML!=0], 25, interpolation = 'midpoint'))/np.median(MT_ML[MT_ML!=0]))],
                                ]

                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_MT_KR)
                    csvwriter.writerows(row_MT_CR)
                    csvwriter.writerows(row_MT_MR)
                    csvwriter.writerows(row_MT_KL)
                    csvwriter.writerows(row_MT_CL)  
                    csvwriter.writerows(row_MT_ML)             
                    csv_file.close()                

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT Mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT Mapping was NOT completed; error: "+str(e)) 
                    file.close()

            elif series[0]['SeriesDescription'] == "T2star_map_pancreas_tra_mbh_magnitude":
                try:
                    start_time = time.time()
                    T2s_LIV_PAN = series

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Liver & Pancreas T2s Mapping has started")
                    file.close()

                    T2s_LIV, Fat_LIV = T2smap(weasel, series=T2s_LIV_PAN, mask=mask_T2s_LIV, export_ROI=True,slice=LIV_slice,Fat_export=True)
                    T2s_LIV = np.squeeze(T2s_LIV)
                    Fat_LIV = np.squeeze(Fat_LIV)

                    row_T2s_LIV=[
                                [studydate,site,subject,'T2*','None','LIV','Median','ms',str(np.median(T2s_LIV[T2s_LIV!=0]))],
                                [studydate,site,subject,'T2*','None','LIV','Mean','ms',str(np.mean(T2s_LIV[T2s_LIV!=0]))],
                                [studydate,site,subject,'T2*','None','LIV','Stdev','ms',str(np.std(T2s_LIV[T2s_LIV!=0]))],
                                [studydate,site,subject,'T2*','None','LIV','Mode','ms',str(stats.mode(T2s_LIV[T2s_LIV!=0])[0][0])],
                                [studydate,site,subject,'T2*','None','LIV','95%','ms',str(np.percentile(T2s_LIV[T2s_LIV!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','None','LIV','75%','ms',str(np.percentile(T2s_LIV[T2s_LIV!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','None','LIV','25%','ms',str(np.percentile(T2s_LIV[T2s_LIV!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','None','LIV','5%','ms',str(np.percentile(T2s_LIV[T2s_LIV!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','None','LIV','IQR','ms',str(np.percentile(T2s_LIV[T2s_LIV!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_LIV[T2s_LIV!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'T2*','None','LIV','IQR/Median','%',str((np.percentile(T2s_LIV[T2s_LIV!=0], 75, interpolation = 'midpoint')-np.percentile(T2s_LIV[T2s_LIV!=0], 25, interpolation = 'midpoint'))/np.median(T2s_LIV[T2s_LIV!=0]))],
                                ]

                    row_Fat_LIV=[
                                [studydate,site,subject,'Fat','None','LIV','Median','%',str(np.median(Fat_LIV[Fat_LIV!=0]))],
                                [studydate,site,subject,'Fat','None','LIV','Mean','%',str(np.mean(Fat_LIV[Fat_LIV!=0]))],
                                [studydate,site,subject,'Fat','None','LIV','Stdev','%',str(np.std(Fat_LIV[Fat_LIV!=0]))],
                                [studydate,site,subject,'Fat','None','LIV','Mode','%',str(stats.mode(Fat_LIV[Fat_LIV!=0])[0][0])],
                                [studydate,site,subject,'Fat','None','LIV','95%','%',str(np.percentile(Fat_LIV[Fat_LIV!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Fat','None','LIV','75%','%',str(np.percentile(Fat_LIV[Fat_LIV!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Fat','None','LIV','25%','%',str(np.percentile(Fat_LIV[Fat_LIV!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Fat','None','LIV','5%','%',str(np.percentile(Fat_LIV[Fat_LIV!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Fat','None','LIV','IQR','%',str(np.percentile(Fat_LIV[Fat_LIV!=0], 75, interpolation = 'midpoint')-np.percentile(Fat_LIV[Fat_LIV!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Fat','None','LIV','IQR/Median','%',str((np.percentile(Fat_LIV[Fat_LIV!=0], 75, interpolation = 'midpoint')-np.percentile(Fat_LIV[Fat_LIV!=0], 25, interpolation = 'midpoint'))/np.median(Fat_LIV[Fat_LIV!=0]))],
                                ]
                    
                    T2s_PAN,Fat_PAN = T2smap(weasel, series=T2s_LIV_PAN, mask=mask_T2s_PAN, export_ROI=True,slice=PAN_slice,Fat_export=True)
                    Fat_PAN = np.squeeze(Fat_PAN)

                    row_Fat_PAN=[
                                [studydate,site,subject,'Fat','None','PAN','Median','%',str(np.median(Fat_PAN[Fat_PAN!=0]))],
                                [studydate,site,subject,'Fat','None','PAN','Mean','%',str(np.mean(Fat_PAN[Fat_PAN!=0]))],
                                [studydate,site,subject,'Fat','None','PAN','Stdev','%',str(np.std(Fat_PAN[Fat_PAN!=0]))],
                                [studydate,site,subject,'Fat','None','PAN','Mode','%',str(stats.mode(Fat_PAN[Fat_PAN!=0])[0][0])],
                                [studydate,site,subject,'Fat','None','PAN','95%','%',str(np.percentile(Fat_PAN[Fat_PAN!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Fat','None','PAN','75%','%',str(np.percentile(Fat_PAN[Fat_PAN!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Fat','None','PAN','25%','%',str(np.percentile(Fat_PAN[Fat_PAN!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Fat','None','PAN','5%','%',str(np.percentile(Fat_PAN[Fat_PAN!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Fat','None','PAN','IQR','%',str(np.percentile(Fat_PAN[Fat_PAN!=0], 75, interpolation = 'midpoint')-np.percentile(Fat_PAN[Fat_PAN!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Fat','None','PAN','IQR/Median','%',str((np.percentile(Fat_PAN[Fat_PAN!=0], 75, interpolation = 'midpoint')-np.percentile(Fat_PAN[Fat_PAN!=0], 25, interpolation = 'midpoint'))/np.median(Fat_PAN[Fat_PAN!=0]))],
                                ]

                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_T2s_LIV)
                    csvwriter.writerows(row_Fat_LIV)
                    csvwriter.writerows(row_Fat_PAN)          
                    csv_file.close()
                
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Liver & Pancreas T2s Mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Liver & Pancreas T2s Mapping was NOT completed; error: "  + str(e))
                    file.close()

            elif series[0]['SeriesDescription'] == "ASL_kidneys_pCASL_cor-oblique_fb_RBF_moco":
                try:
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": ASL Mapping has started")
                    file.close()

                    ASL_RBF = series.PixelArray

                    ASL_KR = np.squeeze(ASL_RBF[int(ASL_R_slice-1),:,:])*mask_ASL_KID_R
                    ASL_KL = np.squeeze(ASL_RBF[int(ASL_L_slice-1),:,:])*mask_ASL_KID_L

                    row_ASL_KR=[
                                [studydate,site,subject,'Perfusion','R','COR','Median','mL/min/100mL',str(np.median(ASL_KR[ASL_KR!=0]))],
                                [studydate,site,subject,'Perfusion','R','COR','Mean','mL/min/100mL',str(np.mean(ASL_KR[ASL_KR!=0]))],
                                [studydate,site,subject,'Perfusion','R','COR','Stdev','mL/min/100mL',str(np.std(ASL_KR[ASL_KR!=0]))],
                                [studydate,site,subject,'Perfusion','R','COR','Mode','mL/min/100mL',str(stats.mode(ASL_KR[ASL_KR!=0])[0][0])],
                                [studydate,site,subject,'Perfusion','R','COR','95%','mL/min/100mL',str(np.percentile(ASL_KR[ASL_KR!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Perfusion','R','COR','75%','mL/min/100mL',str(np.percentile(ASL_KR[ASL_KR!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Perfusion','R','COR','25%','mL/min/100mL',str(np.percentile(ASL_KR[ASL_KR!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Perfusion','R','COR','5%','mL/min/100mL',str(np.percentile(ASL_KR[ASL_KR!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Perfusion','R','COR','IQR','mL/min/100mL',str(np.percentile(ASL_KR[ASL_KR!=0], 75, interpolation = 'midpoint')-np.percentile(ASL_KR[ASL_KR!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Perfusion','R','COR','IQR/Median','%',str((np.percentile(ASL_KR[ASL_KR!=0], 75, interpolation = 'midpoint')-np.percentile(ASL_KR[ASL_KR!=0], 25, interpolation = 'midpoint'))/np.median(ASL_KR[ASL_KR!=0]))],
                                ]

                    row_ASL_KL=[
                                [studydate,site,subject,'Perfusion','L','COR','Median','mL/min/100mL',str(np.median(ASL_KL[ASL_KL!=0]))],
                                [studydate,site,subject,'Perfusion','L','COR','Mean','mL/min/100mL',str(np.mean(ASL_KL[ASL_KL!=0]))],
                                [studydate,site,subject,'Perfusion','L','COR','Stdev','mL/min/100mL',str(np.std(ASL_KL[ASL_KL!=0]))],
                                [studydate,site,subject,'Perfusion','L','COR','Mode','mL/min/100mL',str(stats.mode(ASL_KL[ASL_KL!=0])[0][0])],
                                [studydate,site,subject,'Perfusion','L','COR','95%','mL/min/100mL',str(np.percentile(ASL_KL[ASL_KL!=0],95, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Perfusion','L','COR','75%','mL/min/100mL',str(np.percentile(ASL_KL[ASL_KL!=0],75, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Perfusion','L','COR','25%','mL/min/100mL',str(np.percentile(ASL_KL[ASL_KL!=0],25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Perfusion','L','COR','5%','mL/min/100mL',str(np.percentile(ASL_KL[ASL_KL!=0],5, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Perfusion','L','COR','IQR','mL/min/100mL',str(np.percentile(ASL_KL[ASL_KL!=0], 75, interpolation = 'midpoint')-np.percentile(ASL_KL[ASL_KL!=0], 25, interpolation = 'midpoint'))],
                                [studydate,site,subject,'Perfusion','L','COR','IQR/Median','%',str((np.percentile(ASL_KL[ASL_KL!=0], 75, interpolation = 'midpoint')-np.percentile(ASL_KL[ASL_KL!=0], 25, interpolation = 'midpoint'))/np.median(ASL_KL[ASL_KL!=0]))],
                                ]

                    csv_file = open(filename_csv, mode='a',newline='')
                    csvwriter = csv.writer(csv_file)
                    csvwriter.writerows(row_ASL_KR)
                    csvwriter.writerows(row_ASL_KL)        
                    csv_file.close()

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": ASL Mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": ASL Mapping was NOT completed; error: "  + str(e))
                    file.close()

            elif series[0]['SeriesDescription'] == "T1w_abdomen_dixon_cor_bh_post_contrast_______" :
                try:
                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Pelvis Volume Quantification has started")
                    file.close()

                    T1w_Pelvis_Volume_Quantification = series.PixelArray

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Pelvis Volume Quantification was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()

                except Exception as e:

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": Pelvis Volume Quantification was NOT completed; error: "  + str(e))
                    file.close()


        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": All modelling was completed --- %s seconds ---" % (int(time.time() - start_time_loop))) 
        file.close()