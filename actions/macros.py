import time
import datetime
import os, sys
import csv

import weasel

import actions.xnat as xnat
import actions.rename as rename
import actions.mdr as mdr
import actions.modelling as modelling

class MDRegMacro(weasel.Action):

    def run(self, app):
        
        xnat.Download.run(self, app)

        filename_log = app.folder.path.split(app.folder.path.split('\\')[-1])[0] + app.folder.path.split('\\')[-1] + ('\\') + datetime.datetime.now().strftime('%Y%m%d_%H%M_') + "MDRauto_LogFile.txt" #TODO FIND ANOTHER WAY TO GET A PATH
        file = open(filename_log, 'a')
        file.write(str(datetime.datetime.now())[0:19] + ": MDR of " + app.folder.path.split('//')[-1] +  " has started!")
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
        current_study = list_series[0].parent
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
                    #mdr.MDRegT1.run(self,app, series, study=study)
                
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
                    #mdr.MDRegT2star.run(self,app, series,study=study)

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
                    #mdr.MDRegT2.run(self,app, series, study=study)

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
                    #mdr.MDRegDWI.run(self,app, series, study=study)

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
                    #mdr.MDRegDTI.run(self,app, series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close() 

                except Exception as e:
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DTI Motion correction was NOT completed; error: "+str(e)) 
                    file.close()

            elif series['SeriesDescription'] == "DCE_kidneys_cor-oblique_fb":
                start_time = time.time()
                file = open(filename_log, 'a')
                file.write("\n"+str(datetime.datetime.now())[0:19] + ": DCE Motion correction has started")
                file.close()

                try:
                    print("Performing motion correction in DCE scan")
                    #mdr.MDRegDTI.run(self,app, series, study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DCE Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close() 

                except Exception as e:
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": DCE Motion correction was NOT completed; error: "+str(e)) 
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
                    #mdr.MDRegMT.run(self,app, [MT_OFF, MT_ON], study=study)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT Motion correction was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()
                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": MT Motion correction was NOT completed; error: "+str(e)) 
                    file.close()                   
            
        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": Motion correction was completed for all scans  --- %s seconds ---" % (int(time.time() - start_time_loop))) 
        file.close()

        file = open(filename_log, 'a')
        file.write("\n"+str(datetime.datetime.now())[0:19] + ": Modelling started") 
        file.close()

        start_time_loop = time.time()
        for j,series in enumerate(list_series):
            print(series['SeriesDescription'])

            if series['SeriesDescription'] == "T2star_map_kidneys_cor-oblique_mbh_magnitude":
                try:

                    start_time = time.time()
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Mapping has started")
                    file.close()

                    modelling.SiemensT2sMapButton.run(self,app,series)

                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Mapping was completed --- %s seconds ---" % (int(time.time() - start_time))) 
                    file.close()   

                except Exception as e: 
                    file = open(filename_log, 'a')
                    file.write("\n"+str(datetime.datetime.now())[0:19] + ": T2* Mapping was NOT completed; error: "+str(e)) 
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