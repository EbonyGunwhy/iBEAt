import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dbdicom.extensions import vreg
import dcmri

from pipelines import measure
import models


def PC(folder):

    results_path = folder.path() + '_output'
    if not os.path.exists(results_path):
        os.mkdir(results_path)

    dyn_desc = [
        'PC_RenalArtery_Left_EcgTrig_fb_120_velocity',
        'PC_RenalArtery_Right_EcgTrig_fb_120_velocity',
    ]

    dims = 'InstanceNumber'
    model = models.PC
    id = folder.PatientID

    figs = []
    bk_pars = []
    table = pd.DataFrame()
    for k, kidney in enumerate(['LK','RK']):

        # Check if the required series are there and raise an error if not
        dyn_kidney = dyn_desc[k]  
        folder.message('Finding ' + dyn_kidney)
        dyn_kidney = folder.series(SeriesDescription=dyn_kidney)
        if dyn_kidney == []:
            raise ValueError('Cannot perform PC ROI analysis: missing dynamic series aligned to kidney ' + kidney)
        folder.message('Finding ' + 'PC-'+kidney[0]+'RA')
        kidney_mask = folder.series(SeriesDescription='PC-'+kidney[0]+'RA')
        if kidney_mask == []:
            raise ValueError('Cannot perform PC ROI analysis: missing mask for kidney' + kidney)
                
        # Load curve and T1 values for the kidney
        time = dyn_kidney[0].values('TriggerTime').astype(np.float32)
        velocity = dyn_kidney[0].pixel_values(dims) 
        if kidney == 'RK':
            velocity = -velocity
        mask = kidney_mask[0].pixel_values(dims)
        dx = kidney_mask[0].values('PixelSpacing')
        velocity, flow = model.curve(velocity, mask[...,0], pixel_spacing=dx[0][0]) 

        # Export the results (velocity)
        fig, ax = plt.subplots(1,1,figsize=(5,5))
        #time = np.arange(len(velocity))
        ax.plot(time, velocity, 'ro', label='Velocity for kidney ' + kidney, linewidth=3.0)
        ax.plot(time, velocity, 'r-')
        ax.plot(time, np.full(time.shape, np.mean(velocity)), 'b-', label = 'Average velocity')
        ax.plot(time, 0*time, color='gray')
        ax.set(xlabel='Time (msec)', ylabel='Velocity (cm/sec)')
        ax.legend()
        plt.savefig(os.path.join(results_path, 'model fit velocity PC ('+ kidney +').png'), dpi=600)
        figs.append(fig)

        # Export the results (flow)
        fig, ax = plt.subplots(1,1,figsize=(5,5))
        ax.plot(time, flow, 'ro', label='Flow for kidney ' + kidney, linewidth=3.0)
        ax.plot(time, flow, 'r-')
        ax.plot(time, np.full(time.shape, np.mean(flow)), 'b-', label = 'Average flow')
        ax.plot(time, 0*time, color='gray')
        ax.set(xlabel='Time (msec)', ylabel='Flow (mL/min)')
        ax.legend()
        plt.savefig(os.path.join(results_path, 'model fit flow PC ('+ kidney +').png'), dpi=600)
        figs.append(fig)

        # Calculate the fit
        pars = model.params(time, velocity, flow)
        pn, u = model.pars(), model.units()
        rows = []
        for i, p in enumerate(pn):
            rows.append([id, kidney, 'Kidney', 'ROI', pars[i], u[i], kidney + '-' + p + '-ROI', 'ROI fit'])
        
        # Save results
        table['time'] = time
        table['velocity '+ kidney] = velocity
        table['flow '+ kidney] = flow     
        measure.add_rows(folder, rows)
        bk_pars.append(pars)

    rows = []
    for i, p in enumerate(pn):
        rows.append([id, 'BK', 'Kidney', 'ROI', (bk_pars[0][i]+bk_pars[1][i])/2, u[i], 'BK' + '-' + p + '-ROI', 'ROI fit'])
    table['velocity BK'] = (table['velocity LK'].values + table['velocity RK'].values)/2
    table['flow BK'] = table['flow LK'].values + table['flow RK'].values
    measure.add_rows(folder, rows)

    table.to_csv(os.path.join(results_path, 'data_PC.csv'))
    return figs


def T1(folder):

    results_path = folder.path() + '_output'
    if not os.path.exists(results_path):
        os.mkdir(results_path)

    dyn_desc = 'T1map_kidneys_cor-oblique_mbh_magnitude_mdr_moco'
    
    # Model parameters (Siemens)
    TR = 4.6 # Echo Spacing is msec but not in header -> Set as TR in harmonize
    FA_cat = [-1, 2, -3, 4, -5] # Catalization module confirmed by Siemens (Peter Schmitt): Magn Reson Med 2003 Jan;49(1):151-7. doi: 10.1002/mrm.10337
    N_T1 = 66 # Number of k-space lines (hardcoded from Siemens protocol)
    FA_nom = 12 # Flip angle in degrees (hardcoded from Siemens protocol)

    model = models.T1.Bloch()
    kwargs = {'TR':TR, 'FA_cat':FA_cat, 'N_T1':N_T1, 'FA':FA_nom}
    dims = ('SliceLocation', 'AcquisitionTime')

    figs = []
    table = pd.DataFrame()
    for struct in ['','C','M']:
        vals_kidneys = []
        for kidney in ['LK'+struct,'RK'+struct]:

            # Check if the required series are there and raise an error if not
            dyn_kidney = dyn_desc + '_' + kidney[:2] + '_align' 
            folder.message('Finding ' + dyn_kidney)
            dyn_kidney = folder.series(SeriesDescription=dyn_kidney)
            if dyn_kidney == []:
                raise ValueError('Cannot perform T1 ROI analysis: missing dynamic series aligned to kidney ' + kidney)
            folder.message('Finding ' + kidney)
            kidney_mask = folder.series(SeriesDescription=kidney)
            if kidney_mask == []:
                raise ValueError('Cannot perform T1 ROI analysis: missing mask for kidney' + kidney)
            map_kidney = dyn_desc + '_T1_map_' + kidney[:2] + '_align' 
            folder.message('Finding ' + map_kidney)
            map_kidney = folder.series(SeriesDescription=map_kidney)
            if map_kidney == []:
                raise ValueError('Cannot perform T1 ROI analysis: missing T1 aligned to kidney ' + kidney)
            
            # Load curve and T1 values for the kidney
            TI = dyn_kidney[0].values('InversionTime', dims=dims)
            TI = TI[0,:].astype(np.float32)
            dyn_kidney, vals_kidney = load_roi_curve(dyn_kidney[0], kidney_mask[0], map_kidney[0], dims=dims)
            vals_kidneys.append(vals_kidney)

            # Calculate the fit
            pars = model.fit_signal((TI, dyn_kidney, 1e-6, True, kwargs))
            fit = model.signal(TI, *pars, **kwargs)

            # Export the results
            fig, ax = plt.subplots(1,1,figsize=(5,5))
            iTI = np.argsort(TI)
            ax.plot(TI[iTI], dyn_kidney[iTI], 'ro', label='Signal for ' + kidney, linewidth=3.0)
            ax.plot(TI[iTI], fit[iTI], 'b-', label='T1 model fit for ' + kidney, linewidth=3.0)
            ax.plot(TI[iTI], 0*TI[iTI], color='gray')
            ax.set(xlabel='Inversion time (msec)', ylabel='Signal (a.u.)')
            ax.legend()

            plt.savefig(os.path.join(results_path, 'model fit T1 ('+ kidney +').png'), dpi=600)
            figs.append(fig)

            # Update master table
            table['TI (msec)'] = TI
            table[kidney] = dyn_kidney
            p = model.pars()
            measure.add_rows(folder, [
                [folder.PatientID, kidney, 'Kidney', 'ROI', pars[1], 'msec', kidney + '-' + p[1] + '-ROI', 'ROI fit'],
                [folder.PatientID, kidney, 'Kidney', 'ROI', pars[2], 'deg', kidney + '-' + p[2] + '-ROI', 'ROI fit'],
            ])

        # Build dynamic for BK
        kidney = 'BK' + struct
        nt = len(vals_kidneys[0])
        dyn_kidney = np.zeros(nt)
        for t in range(nt):
            vals_t = list(vals_kidneys[0][t]) + list(vals_kidneys[1][t])
            dyn_kidney[t] = np.mean(vals_t)

        # Calculate the fit
        pars = model.fit_signal((TI, dyn_kidney, 1e-6, True, kwargs))
        fit = model.signal(TI, *pars, **kwargs)

        # Export the results
        fig, ax = plt.subplots(1,1,figsize=(5,5))
        iTI = np.argsort(TI)
        ax.plot(TI[iTI], dyn_kidney[iTI], 'ro', label='Signal for ' + kidney, linewidth=3.0)
        ax.plot(TI[iTI], fit[iTI], 'b-', label='T1 model fit for ' + kidney, linewidth=3.0)
        ax.plot(TI[iTI], 0*TI[iTI], color='gray')
        ax.set(xlabel='Inversion time (msec)', ylabel='Signal (a.u.)')
        ax.legend()

        plt.savefig(os.path.join(results_path, 'model fit T1 ('+ kidney +').png'), dpi=600)
        #plt.close()
        figs.append(fig)

        # Update master table
        table[kidney] = dyn_kidney
        p = model.pars()
        measure.add_rows(folder, [
            [folder.PatientID, kidney, 'Kidney', 'ROI', pars[1], 'msec', kidney + '-' + p[1] + '-ROI', 'ROI fit'],
            [folder.PatientID, kidney, 'Kidney', 'ROI', pars[2], 'deg', kidney + '-' + p[2] + '-ROI', 'ROI fit'],
        ])

    table.to_csv(os.path.join(results_path, 'data_T1.csv'))
    return figs


def T2(folder):

    results_path = folder.path() + '_output'
    if not os.path.exists(results_path):
        os.mkdir(results_path)

    dyn_desc = 'T2map_kidneys_cor-oblique_mbh_magnitude_mdr_moco'

    # Parameters
    # Defaults from Siemens iBEAt protocol
    Tspoil = 1# Spoil time in ms
    N_T2 = 72# Number of k-space lines (hardcoded from Siemens protocol)
    Trec = 463*2# Recovery time in ms (hardcoded from Siemens protocol)
    TR = 4.6# TR in ms (hardcoded from Siemens protocol)
    FA = 12 # Flip angle in degrees (hardcoded from Siemens protocol) converted to radians

    # model = T2_mono_exp_offset
    # dims = ('SliceLocation', 'InversionTime')
    # kwargs = {}
    model = models.T2.Bloch()
    #model = T2_prep
    dims = ('SliceLocation', 'AcquisitionTime')
    kwargs = {'Tspoil':Tspoil, 'N_T2':N_T2, 'Trec':Trec, 'TR':TR, 'FA':FA}
    
    figs = []
    table = pd.DataFrame()
    for struct in ['','C','M']:
        vals_kidneys = []
        for kidney in ['LK'+struct,'RK'+struct]:

            # Check if the required series are there and raise an error if not
            dyn_kidney = dyn_desc + '_' + kidney[:2] + '_align' 
            folder.message('Finding ' + dyn_kidney)
            dyn_kidney = folder.series(SeriesDescription=dyn_kidney)
            if dyn_kidney == []:
                raise ValueError('Cannot perform T2 ROI analysis: missing dynamic series aligned to kidney ' + kidney)
            folder.message('Finding ' + kidney)
            kidney_mask = folder.series(SeriesDescription=kidney)
            if kidney_mask == []:
                raise ValueError('Cannot perform T2 ROI analysis: missing mask for kidney' + kidney)
            map_kidney = dyn_desc + '_T2_map_' + kidney[:2] + '_align' 
            folder.message('Finding ' + map_kidney)
            map_kidney = folder.series(SeriesDescription=map_kidney)
            if map_kidney == []:
                raise ValueError('Cannot perform T2 ROI analysis: missing T1 aligned to kidney ' + kidney)
            
            # Load curve and T1 values for the kidney
            TI = dyn_kidney[0].values('InversionTime', dims=dims)
            TI = TI[0,:].astype(np.float32)
            dyn_kidney, vals_kidney = load_roi_curve(dyn_kidney[0], kidney_mask[0], map_kidney[0], dims=dims)
            vals_kidneys.append(vals_kidney)
            kwargs['T1'] = measure.read_master_table(folder, kidney+'-T1-ROI')

            # Calculate the fit
            pars = model.fit_signal((TI, dyn_kidney, 1e-6, True, kwargs))
            fit = model.signal(TI, *pars, **kwargs)

            # Export the results
            fig, ax = plt.subplots(1,1,figsize=(5,5))
            ax.plot(TI, dyn_kidney, 'ro', label='Signal for ' + kidney, linewidth=3.0)
            ax.plot(TI, fit, 'b-', label='T2 model fit for ' + kidney, linewidth=3.0)
            ax.plot(TI, 0*TI, color='gray')
            ax.set(xlabel='Preparation delay (msec)', ylabel='Signal (a.u.)')
            ax.legend()

            plt.savefig(os.path.join(results_path, 'model fit T2 ('+ kidney +').png'), dpi=600)
            figs.append(fig)

            # Update master table
            table['TP (msec)'] = TI
            table[kidney] = dyn_kidney
            p = model.pars()
            measure.add_rows(folder, [
                [folder.PatientID, kidney, 'Kidney', 'ROI', pars[1], 'msec', kidney + '-' + p[1] + '-ROI', 'ROI fit'],
                [folder.PatientID, kidney, 'Kidney', 'ROI', pars[2], 'deg', kidney + '-' + p[2] + '-ROI', 'ROI fit'],            
            ])

        # Build dynamic for BK
        kidney = 'BK' + struct
        nt = len(vals_kidneys[0])
        dyn_kidney = np.zeros(nt)
        for t in range(nt):
            vals_t = list(vals_kidneys[0][t]) + list(vals_kidneys[1][t])
            dyn_kidney[t] = np.mean(vals_t)

        # Calculate the fit
        kwargs['T1'] = measure.read_master_table(folder, kidney+'-T1-ROI')
        pars = model.fit_signal((TI, dyn_kidney, 1e-6, True, kwargs))
        fit = model.signal(TI, *pars, **kwargs)

        # Export the results
        fig, ax = plt.subplots(1,1,figsize=(5,5))
        ax.plot(TI, dyn_kidney, 'ro', label='Signal for ' + kidney, linewidth=3.0)
        ax.plot(TI, fit, 'b-', label='T2 model fit for ' + kidney, linewidth=3.0)
        ax.plot(TI, 0*TI, color='gray')
        ax.set(xlabel='Preparation delay (msec)', ylabel='Signal (a.u.)')
        ax.legend()

        plt.savefig(os.path.join(results_path, 'model fit T2 ('+ kidney +').png'), dpi=600)
        figs.append(fig)

        # Update master table
        table['TP (msec)'] = TI
        table[kidney] = dyn_kidney
        p = model.pars()
        measure.add_rows(folder, [
            [folder.PatientID, kidney, 'Kidney', 'ROI', pars[1], 'msec', kidney + '-' + p[1] + '-ROI', 'ROI fit'],
            [folder.PatientID, kidney, 'Kidney', 'ROI', pars[2], 'deg', kidney + '-' + p[2] + '-ROI', 'ROI fit'],
        ])

    table.to_csv(os.path.join(results_path, 'data_T2.csv'))
    return figs


def T2star(folder):

    results_path = folder.path() + '_output'
    if not os.path.exists(results_path):
        os.mkdir(results_path)

    dyn_desc = 'T2star_map_kidneys_cor-oblique_mbh_magnitude_mdr_moco'
    dims = ('SliceLocation', 'EchoTime')
    model = models.T2star.BiExp()
    figs = []
    table = pd.DataFrame()
    for struct in ['','C','M']:
        vals_kidneys = []
        for kidney in ['LK'+struct,'RK'+struct]:

            # Check if the required series are there and raise an error if not
            dyn_kidney = dyn_desc + '_' + kidney[:2] + '_align' 
            folder.message('Finding ' + dyn_kidney)
            dyn_kidney = folder.series(SeriesDescription=dyn_kidney[:64])
            if dyn_kidney == []:
                raise ValueError('Cannot perform T2* ROI analysis: missing dynamic series aligned to kidney ' + kidney)
            folder.message('Finding ' + kidney)
            kidney_mask = folder.series(SeriesDescription=kidney)
            if kidney_mask == []:
                raise ValueError('Cannot perform T2* ROI analysis: missing mask for kidney' + kidney)
            map_kidney = dyn_desc + '_T2star_map_' + kidney[:2] + '_align' 
            folder.message('Finding ' + map_kidney)
            map_kidney = folder.series(SeriesDescription=map_kidney[:64])
            if map_kidney == []:
                raise ValueError('Cannot perform T2* ROI analysis: missing T1 aligned to kidney ' + kidney)
            
            # Load curve and T1 values for the kidney
            TE = dyn_kidney[0].values('EchoTime', dims=dims)
            TE = TE[0,:].astype(np.float32)
            dyn_kidney, vals_kidney = load_roi_curve(dyn_kidney[0], kidney_mask[0], map_kidney[0], dims=dims)
            vals_kidneys.append(vals_kidney)

            # Calculate the fit
            pars = model.fit_signal((TE, dyn_kidney, 1e-6, True, {}))
            fit = model.signal(TE, *pars)

            # Export the results
            fig, ax = plt.subplots(1,1,figsize=(5,5))
            ax.plot(TE, dyn_kidney, 'ro', label='Signal for ' + kidney, linewidth=3.0)
            ax.plot(TE, fit, 'b-', label='T2* model fit for ' + kidney, linewidth=3.0)
            ax.plot(TE, 0*TE, color='gray')
            ax.set(xlabel='Echo time (msec)', ylabel='Signal (a.u.)')
            ax.legend()

            plt.savefig(os.path.join(results_path, 'model fit T2star ('+ kidney +').png'), dpi=600)
            figs.append(fig)

            # Update master table
            table['TE '+kidney] = TE
            table[kidney] = dyn_kidney
            p = model.pars()
            measure.add_rows(folder, [
                [folder.PatientID, kidney, 'Kidney', 'ROI', pars[1], 'msec', kidney + '-' + p[1] + '-ROI', 'ROI fit'],
                [folder.PatientID, kidney, 'Kidney', 'ROI', 100*pars[2], '%', kidney + '-' + p[2] + '-ROI', 'ROI fit'],
            ])

        # Build dynamic for BK
        kidney = 'BK' + struct
        nt = len(vals_kidneys[0])
        dyn_kidney = np.zeros(nt)
        for t in range(nt):
            vals_t = list(vals_kidneys[0][t]) + list(vals_kidneys[1][t])
            dyn_kidney[t] = np.mean(vals_t)

        # Calculate the fit
        pars = model.fit_signal((TE, dyn_kidney, 1e-6, True, {}))
        fit = model.signal(TE, *pars)

        # Export the results
        fig, ax = plt.subplots(1,1,figsize=(5,5))
        ax.plot(TE, dyn_kidney, 'ro', label='Signal for ' + kidney, linewidth=3.0)
        ax.plot(TE, fit, 'b-', label='T2 model fit for ' + kidney, linewidth=3.0)
        ax.plot(TE, 0*TE, color='gray')
        ax.set(xlabel='Echo time (msec)', ylabel='Signal (a.u.)')
        ax.legend()

        plt.savefig(os.path.join(results_path, 'model fit T2star ('+ kidney +').png'), dpi=600)
        figs.append(fig)

        # Update master table
        table['TE '+kidney] = TE
        table[kidney] = dyn_kidney
        p = model.pars()
        measure.add_rows(folder, [
            [folder.PatientID, kidney, 'Kidney', 'ROI', pars[1], 'msec', kidney + '-' + p[1] + '-ROI', 'ROI fit'],
            [folder.PatientID, kidney, 'Kidney', 'ROI', 100*pars[2], '%', kidney + '-' + p[2] + '-ROI', 'ROI fit']
        ])

    table.to_csv(os.path.join(results_path, 'data_T2star.csv'))
    return figs


def dce(folder):

    results_path = folder.path() + '_output'
    if not os.path.exists(results_path):
        os.mkdir(results_path)

    dyn_desc = "DCE_kidneys_cor-oblique_fb_mdr_moco"

    dyn_kidneys = []
    vals_kidneys = []
    table = pd.DataFrame()
    for kidney in ['LK','RK']:

        # Check if the required series are there and raise an error if not
        dyn_kidney = dyn_desc + '_' + kidney + '_align' 
        folder.message('Finding ' + dyn_kidney)
        dyn_kidney = folder.series(SeriesDescription=dyn_kidney)
        if dyn_kidney == []:
            raise ValueError('Cannot perform DCE ROI analysis: missing dynamic series aligned to kidney ' + kidney)

        folder.message('Finding ' + kidney)
        kidney_mask = folder.series(SeriesDescription=kidney)
        if kidney_mask == []:
            raise ValueError('Cannot perform DCE ROI analysis: missing mask for kidney' + kidney)
        
        map_kidney = dyn_desc + '_AUC_map_' + kidney + '_align' 
        folder.message('Finding ' + map_kidney)
        map_kidney = folder.series(SeriesDescription=map_kidney)
        if map_kidney == []:
            raise ValueError('Cannot perform DCE ROI analysis: missing AUC aligned to kidney ' + kidney)
        
        # Load curve and values for the kidney
        curve_kidney, vals_kidney = load_roi_curve(dyn_kidney[0], kidney_mask[0], map_kidney[0])
        dyn_kidneys.append(curve_kidney)
        vals_kidneys.append(vals_kidney)

    # Get sequence parameters
    pid = folder.PatientID
    frame = dyn_kidney[0].instance()
    dx = frame.PixelSpacing
    dz = frame.SpacingBetweenSlices
    vox = dx[0]*dx[1]*dz/1000 # voxel volume in mL
    TD = frame.InversionTime/1000 # sec
    TR = 2.2/1000 # Echo Spacing is sec but not in header -> Set as TR in harmonize
    FA = frame.FlipAngle #deg
    agent = frame.ContrastBolusAgent
    dose = 0.25*dcmri.ca_std_dose(agent) #mL/kg
    weight = frame.PatientWeight
    if weight is None:
        vol = frame.ContrastBolusVolume #mL 
        if vol is None:
            raise ValueError('Cannot compute DCE: missing patient weight or bolus volume.')
        weight = vol/dose
    Hct = 0.45

    # Graphical constants
    markersize=3
    linewidth=2.0
    figs = []

    # Fit AIF and get concentrations (here for debugging)
    time, aif = load_aif(folder)
    vars = {
        'dt': 0.5,
        'weight': weight, 
        'dose': dose,
        'rate': 2, # mL/sec (different for Gadovist?)
        'agent': agent, 
        'TD': TD, 
        'R10': 1/dcmri.T1(field_strength=3, tissue='blood', Hct=Hct),
    }
    folder.message('Fitting AIF.. ')
    pars, _, fit = dcmri.fit_aorta_signal_8b(time, aif, parset='TRISTAN', **vars)

    # Export the results
    fig, ax = plt.subplots(1,1,figsize=(5,5))
    ax.plot(time/60, aif, 'ro', label='Signal for aorta', markersize=markersize)
    ax.plot(time/60, fit, 'b-', label='Fit for aorta', linewidth=linewidth)
    ax.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    ax.legend()
    plt.savefig(os.path.join(results_path, 'model fit DCE (Aorta).png'), dpi=600)
    figs.append(fig)

    # Update master table
    table['time (s)'] = time
    table['AIF'] = aif
    measure.add_rows(folder, [
        [pid, 'Body', 'Body', 'ROI', pars[0], 'sec', 'AO-BAT' + '-ROI', 'ROI fit'],
        [pid, 'Body', 'Body', 'ROI', pars[1]*60/1000, 'L/min', 'AO-CO' + '-ROI', 'ROI fit'],
        [pid, 'Body', 'Body', 'ROI', pars[2], 'sec', 'AO-HLMTT' + '-ROI', 'ROI fit'],
        [pid, 'Body', 'Body', 'ROI', pars[3]*100, '%', 'AO-HLD' + '-ROI', 'ROI fit'],
        [pid, 'Body', 'Body', 'ROI', pars[4]*100, '%', 'AO-VEF' + '-ROI', 'ROI fit'],
        [pid, 'Body', 'Body', 'ROI', pars[5], 'sec', 'AO-PMTT' + '-ROI', 'ROI fit'],
        [pid, 'Body', 'Body', 'ROI', pars[6]/60, 'min', 'AO-EMTT' + '-ROI', 'ROI fit'],
        [pid, 'Body', 'Body', 'ROI', pars[7]/100, '%', 'AO-BEF' + '-ROI', 'ROI fit'],
    ])

    # variables for kidney fitting
    CO = pars[1] # mL/sec
    t, cb = dcmri.aorta_signal_8b(time, *pars, return_conc=True, **vars)
    vars = {'dt':0.5, 'cb':cb, 'agent':agent, 'TR':TR, 'FA':FA, 'TD':TD, 'Hct':Hct}

    # Fit LK
    folder.message('Fitting LK.. ')
    kidney = 'LK'
    t1_kidney = measure.read_master_table(folder, kidney+'-T1-ROI')
    vars['R10'] = 1/(t1_kidney/1000)
    FAcorr = measure.read_master_table(folder, kidney+'-T1FA-ROI')
    vars['FA'] = FA*FAcorr/12 # Use B1 correction from T1 mapping 
    pars, _, fit = dcmri.fit_kidney_signal_6(time, dyn_kidneys[0], parset='iBEAt', **vars) 

    # Export the results
    fig, ax = plt.subplots(1,1,figsize=(5,5))
    ax.plot(time/60, dyn_kidneys[0], 'ro', label='Signal for left kidney', markersize=markersize)
    ax.plot(time/60, fit, 'b-', label='Signal for left kidney', linewidth=linewidth)
    ax.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    ax.legend()
    plt.savefig(os.path.join(results_path, 'model fit DCE (LK).png'), dpi=600)
    figs.append(fig)

    # Update master table
    table[kidney] = dyn_kidneys[0]
    vol = len(vals_kidneys[0][0])*vox # kidney volume mL
    measure.add_rows(folder, [
        [pid, kidney, 'Kidney', 'ROI', 6000*pars[0]/(1-Hct), 'mL/min/100mL', kidney + '-' + 'RBF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', pars[1], 'sec', kidney + '-' + 'PMTT' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 6000*pars[2], 'mL/min/100mL', kidney + '-' + 'TF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', pars[3]/60, 'min', kidney + '-' + 'TMTT' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 100*pars[1]*pars[0], 'mL/100mL', kidney + '-' + 'ECV' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 60*vol*pars[2], 'mL/min', kidney + '-' + 'SKGFR' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 60*vol*pars[0]/(1-Hct), 'mL/min', kidney + '-' + 'SKBF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 100*pars[2]/pars[0], '%', kidney + '-' + 'FF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 100*pars[2]/(pars[0]+pars[2]), '%', kidney + '-' + 'KEF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', pars[4], 'sec', kidney + '-' + 'AMTT' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 100*vol*pars[0]/(1-Hct)/CO, '%', kidney + '-' + 'PCO' + '-ROI', 'ROI fit'],
    ])

    # Fit RK
    folder.message('Fitting RK.. ')
    kidney = 'RK'
    t1_kidney = measure.read_master_table(folder, kidney+'-T1-Median')
    vars['R10'] = 1/(t1_kidney/1000)
    FAcorr = measure.read_master_table(folder, kidney+'-T1FA-ROI')
    vars['FA'] = FA*FAcorr/12 # Use B1 correction from T1 mapping 
    pars, _, fit = dcmri.fit_kidney_signal_6(time, dyn_kidneys[1], parset='iBEAt', **vars) 

    # Plot fit
    fig, ax = plt.subplots(1,1,figsize=(5,5))
    ax.plot(time/60, dyn_kidneys[1], 'ro', label='Signal for right kidney', markersize=markersize)
    ax.plot(time/60, fit, 'b-', label='Signal for right kidney', linewidth=linewidth)
    ax.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    ax.legend()
    plt.savefig(os.path.join(results_path, 'model fit DCE ('+kidney+').png'), dpi=600)
    figs.append(fig)

    # Update master table
    table[kidney] = dyn_kidneys[1]
    vol = len(vals_kidneys[1][0])*vox # kidney volume mL
    measure.add_rows(folder, [
        [pid, kidney, 'Kidney', 'ROI', 6000*pars[0]/(1-Hct), 'mL/min/100mL', kidney + '-' + 'RBF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', pars[1], 'sec', kidney + '-' + 'PMTT' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 6000*pars[2], 'mL/min/100mL', kidney + '-' + 'TF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', pars[3]/60, 'min', kidney + '-' + 'TMTT' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 100*pars[1]*pars[0], 'mL/100mL', kidney + '-' + 'ECV' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 60*vol*pars[2], 'mL/min', kidney + '-' + 'SKGFR' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 60*vol*pars[0]/(1-Hct), 'mL/min', kidney + '-' + 'SKBF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 100*pars[2]/pars[0], '%', kidney + '-' + 'FF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 100*pars[2]/(pars[0]+pars[2]), '%', kidney + '-' + 'KEF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', pars[4], 'sec', kidney + '-' + 'AMTT' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 100*vol*pars[0]/(1-Hct)/CO, '%', kidney + '-' + 'PCO' + '-ROI', 'ROI fit'],
    ])

    # Fit BK
    folder.message('Fitting BK.. ')
    kidney = 'BK'
    nt = len(vals_kidneys[0])
    dyn_kidney = np.zeros(nt)
    for t in range(nt):
        vals_t = list(vals_kidneys[0][t]) + list(vals_kidneys[1][t])
        dyn_kidney[t] = np.mean(vals_t)

    t1_kidney = measure.read_master_table(folder, kidney+'-T1-Median')
    vars['R10'] = 1/(t1_kidney/1000)
    FAcorr = measure.read_master_table(folder, kidney+'-T1FA-ROI')
    vars['FA'] = FA*FAcorr/12 # Use B1 correction from T1 mapping 
    pars, _, fit = dcmri.fit_kidney_signal_6(time, dyn_kidney, parset='iBEAt', **vars) 
    
    # Plot fit
    fig, ax = plt.subplots(1,1,figsize=(5,5))
    ax.plot(time/60, dyn_kidney, 'ro', label='Signal for both kidneys', markersize=markersize)
    ax.plot(time/60, fit, 'b-', label='Signal for both kidneys', linewidth=linewidth)
    ax.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    ax.legend()
    plt.savefig(os.path.join(results_path, 'model fit DCE ('+kidney+').png'), dpi=600)
    figs.append(fig)

    # Update master table
    table[kidney] = dyn_kidney
    vol = len(vals_kidneys[0][0])*vox + len(vals_kidneys[1][0])*vox # kidney volume mL
    measure.add_rows(folder, [
        [pid, kidney, 'Kidney', 'ROI', 6000*pars[0]/(1-Hct), 'mL/min/100mL', kidney + '-' + 'RBF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', pars[1], 'sec', kidney + '-' + 'PMTT' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 6000*pars[2], 'mL/min/100mL', kidney + '-' + 'TF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', pars[3]/60, 'min', kidney + '-' + 'TMTT' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 100*pars[1]*pars[0], 'mL/100mL', kidney + '-' + 'ECV' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 60*vol*pars[2], 'mL/min', kidney + '-' + 'GFR' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 60*vol*pars[0]/(1-Hct), 'mL/min', kidney + '-' + 'BF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 100*pars[2]/pars[0], '%', kidney + '-' + 'FF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 100*pars[2]/(pars[0]+pars[2]), '%', kidney + '-' + 'KEF' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', pars[4], 'sec', kidney + '-' + 'AMTT' + '-ROI', 'ROI fit'],
        [pid, kidney, 'Kidney', 'ROI', 100*vol*pars[0]/(1-Hct)/CO, '%', kidney + '-' + 'PCO' + '-ROI', 'ROI fit'],
    ])

    table.to_csv(os.path.join(results_path, 'data_DCE.csv'))
    return figs


def dce_cm(folder):

    results_path = folder.path() + '_output'
    if not os.path.exists(results_path):
        os.mkdir(results_path)

    dyn_desc = "DCE_kidneys_cor-oblique_fb_mdr_moco"

    dyn_cortex, dyn_medulla = [], []
    vals_cortex, vals_medulla = [], []
    table = pd.DataFrame()
    for kidney in ['LK','RK']:

        # Check if the required series are there and are unique and raise an error if not
        dyn_kidney = dyn_desc + '_' + kidney + '_align' 
        folder.message('Finding ' + dyn_kidney)
        dyn_kidney = folder.series(SeriesDescription=dyn_kidney)
        if dyn_kidney == []:
            raise ValueError('Cannot perform DCE ROI analysis: missing dynamic series aligned to kidney ' + kidney)

        folder.message('Finding ' + kidney)
        cortex_mask = folder.series(SeriesDescription=kidney+'C')
        if cortex_mask == []:
            raise ValueError('Cannot perform DCE ROI analysis: missing mask for kidney' + kidney + 'C')
        medulla_mask = folder.series(SeriesDescription=kidney+'M')
        if medulla_mask == []:
            raise ValueError('Cannot perform DCE ROI analysis: missing mask for kidney' + kidney + 'M')
        
        map_kidney = dyn_desc + '_AUC_map_' + kidney + '_align' 
        folder.message('Finding ' + map_kidney)
        map_kidney = folder.series(SeriesDescription=map_kidney)
        if map_kidney == []:
            raise ValueError('Cannot perform DCE ROI analysis: missing AUC aligned to kidney ' + kidney)
        
        # Load curve and values for the kidney
        curve_medulla, v_medulla = load_roi_curve(dyn_kidney[0], medulla_mask[0], map_kidney[0])
        curve_cortex, v_cortex = load_roi_curve(dyn_kidney[0], cortex_mask[0], map_kidney[0])
        dyn_cortex.append(curve_cortex)
        vals_cortex.append(v_cortex)
        dyn_medulla.append(curve_medulla)
        vals_medulla.append(v_medulla)

    # Get sequence parameters
    pid = folder.PatientID
    frame = dyn_kidney[0].instance()
    dx = frame.PixelSpacing
    dz = frame.SpacingBetweenSlices
    vox = dx[0]*dx[1]*dz/1000 # voxel volume in mL
    TD = frame.InversionTime/1000 # sec
    TR = 2.2/1000 # Echo Spacing not in header -> Set as TR in harmonize
    FA = frame.FlipAngle #deg
    agent = frame.ContrastBolusAgent
    dose = 0.25*dcmri.ca_std_dose(agent) #mL/kg
    weight = frame.PatientWeight
    if weight is None:
        vol = frame.ContrastBolusVolume #mL 
        if vol is None:
            raise ValueError('Cannot compute DCE: missing patient weight or bolus volume.')
        weight = vol/dose
    Hct = 0.45

    # Graphical constants
    markersize=3
    linewidth=2.0
    figs = []

    # Fit AIF and get concentrations (here for debugging)
    time, aif = load_aif(folder)
    vars = {
        'dt': 0.5,
        'weight': weight, 
        'dose': dose,
        'rate': 2, # mL/sec (different for Gadovist?)
        'agent': agent, 
        'TD': TD, 
        'R10': 1/dcmri.T1(field_strength=3, tissue='blood', Hct=Hct),
    }
    folder.message('Fitting AIF.. ')
    pars, _, fit = dcmri.fit_aorta_signal_8b(time, aif, parset='TRISTAN', **vars)

    # variables for cortex-medulla fitting
    CO = pars[1] # mL/sec
    t, cb = dcmri.aorta_signal_8b(time, *pars, return_conc=True, **vars)
    vars = {'dt':0.5, 'cb':cb, 'agent':agent, 'TR':TR, 'TD':TD, 'Hct':Hct}

    # Fit LK
    folder.message('Fitting LK.. ')
    kidney = 'LK'
    t1_cortex = measure.read_master_table(folder, kidney+'C-T1-ROI') 
    vars['R10c'] = 1/(t1_cortex/1000)
    t1_medulla = measure.read_master_table(folder, kidney+'M-T1-ROI')
    vars['R10m'] = 1/(t1_medulla/1000)
    FAcorr = measure.read_master_table(folder, kidney+'C-T1FA-ROI')
    vars['FAc'] = FA*FAcorr/12 # Use B1 correction from T1 mapping
    FAcorr = measure.read_master_table(folder, kidney+'M-T1FA-ROI')
    vars['FAm'] = FA*FAcorr/12 # Use B1 correction from T1 mapping 
    pars, _, fit_cortex, fit_medulla = dcmri.fit_kidney_cm_signal_9(
            time, dyn_cortex[0], dyn_medulla[0], parset='iBEAt', **vars) 

    # Export the results
    fig, (axc, axm) = plt.subplots(1,2,figsize=(10,5))
    axc.plot(time/60, dyn_cortex[0], 'ro', label='Signal for left cortex', markersize=markersize)
    axc.plot(time/60, fit_cortex, 'b-', label='Fit for left cortex', linewidth=linewidth)
    axc.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    axc.legend()
    axm.plot(time/60, dyn_medulla[0], 'ro', label='Signal for left medulla', markersize=markersize)
    axm.plot(time/60, fit_medulla, 'b-', label='Fit for left medulla', linewidth=linewidth)
    axm.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    axm.legend()
    plt.savefig(os.path.join(results_path, 'model fit DCE (LKCM).png'), dpi=600)
    figs.append(fig)

    # Update tables
    table['time (s)'] = time
    table['AIF'] = aif
    table['LKC'] = dyn_cortex[0]
    table['LKM'] = dyn_medulla[0]
    vol = len(vals_cortex[0][0])*vox # kidney volume mL
    measure.add_rows(folder, [
        [pid, kidney+'CM', 'Kidney', 'ROI', 6000*pars[0]/(1-Hct), 'mL/min/100mL', kidney + '-' + 'CBF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 100*pars[1], '%', kidney + '-' + 'CM-KEF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 100*pars[2], '%', kidney + '-' + 'CPVF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[3], 'sec', kidney + '-' + 'GMTT' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[4], 'sec', kidney + '-' + 'VMTT' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[5]/60, 'min', kidney + '-' + 'PTMTT' + '-ROI', 'ROI fit'],    
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[6]/60, 'min', kidney + '-' + 'LHMTT' + '-ROI', 'ROI fit'],    
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[7]/60, 'min', kidney + '-' + 'DTMTT' + '-ROI', 'ROI fit'],    
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[8]/60, 'min', kidney + '-' + 'CDMTT' + '-ROI', 'ROI fit'], 
        [pid, kidney+'CM', 'Kidney', 'ROI', 100*pars[1]/(1-pars[1]), '%', kidney + '-' + 'CM-FF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[1]/(1-pars[1])*6000*pars[0], 'mL/min/100mL', kidney + '-' + 'CM-TF' + '-ROI', 'ROI fit'],   
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[1]/(1-pars[1])*pars[0]*vol*60, 'mL/min', kidney + '-' + 'CM-SKGFR' + '-ROI', 'ROI fit'],   
        [pid, kidney+'CM', 'Kidney', 'ROI', 6000*pars[2]*(1-pars[1])*pars[0]/(1-Hct), 'mL/min/100mL', kidney + '-' + 'MBF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 60*vol*pars[0]/(1-Hct), 'mL/min', kidney + '-' + 'CM-SKBF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 60*vol*pars[2]*(1-pars[1])*pars[0]/(1-Hct), 'mL/min', kidney + '-' + 'SKMBF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 100*vol*pars[0]/(1-Hct)/CO, '%', kidney + '-' + 'CM-PCO' + '-ROI', 'ROI fit'],
    ])

    # Fit RK
    folder.message('Fitting RK.. ')
    kidney = 'RK'
    t1_cortex = measure.read_master_table(folder, kidney+'C-T1-ROI') 
    vars['R10c'] = 1/(t1_cortex/1000)
    t1_medulla = measure.read_master_table(folder, kidney+'M-T1-ROI')
    vars['R10m'] = 1/(t1_medulla/1000)
    FAcorr = measure.read_master_table(folder, kidney+'C-T1FA-ROI')
    vars['FAc'] = FA*FAcorr/12 # Use B1 correction from T1 mapping
    FAcorr = measure.read_master_table(folder, kidney+'M-T1FA-ROI')
    vars['FAm'] = FA*FAcorr/12 # Use B1 correction from T1 mapping 
    pars, _, fit_cortex, fit_medulla = dcmri.fit_kidney_cm_signal_9(
            time, dyn_cortex[1], dyn_medulla[1], parset='iBEAt', **vars) 

    # Export the results
    fig, (axc, axm) = plt.subplots(1,2,figsize=(10,5))
    axc.plot(time/60, dyn_cortex[1], 'ro', label='Signal for right cortex', markersize=markersize)
    axc.plot(time/60, fit_cortex, 'b-', label='Fit for right cortex', linewidth=linewidth)
    axc.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    axc.legend()
    axm.plot(time/60, dyn_medulla[1], 'ro', label='Signal for right medulla', markersize=markersize)
    axm.plot(time/60, fit_medulla, 'b-', label='Fit for right medulla', linewidth=linewidth)
    axm.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    axm.legend()
    plt.savefig(os.path.join(results_path, 'model fit DCE (RKCM).png'), dpi=600)
    figs.append(fig)


    # Update master table
    table['RKC'] = dyn_cortex[1]
    table['RKM'] = dyn_medulla[1]
    vol = len(vals_cortex[1][0])*vox # kidney volume mL
    measure.add_rows(folder, [
        [pid, kidney+'CM', 'Kidney', 'ROI', 6000*pars[0]/(1-Hct), 'mL/min/100mL', kidney + '-' + 'CBF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 100*pars[1], '%', kidney + '-' + 'CM-KEF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 100*pars[2], '%', kidney + '-' + 'CPVF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[3], 'sec', kidney + '-' + 'GMTT' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[4], 'sec', kidney + '-' + 'VMTT' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[5]/60, 'min', kidney + '-' + 'PTMTT' + '-ROI', 'ROI fit'],    
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[6]/60, 'min', kidney + '-' + 'LHMTT' + '-ROI', 'ROI fit'],    
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[7]/60, 'min', kidney + '-' + 'DTMTT' + '-ROI', 'ROI fit'],    
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[8]/60, 'min', kidney + '-' + 'CDMTT' + '-ROI', 'ROI fit'], 
        [pid, kidney+'CM', 'Kidney', 'ROI', 100*pars[1]/(1-pars[1]), '%', kidney + '-' + 'CM-FF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[1]/(1-pars[1])*6000*pars[0], 'mL/min/100mL', kidney + '-' + 'CM-TF' + '-ROI', 'ROI fit'],   
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[1]/(1-pars[1])*pars[0]*vol*60, 'mL/min', kidney + '-' + 'CM-SKGFR' + '-ROI', 'ROI fit'],   
        [pid, kidney+'CM', 'Kidney', 'ROI', 6000*pars[2]*(1-pars[1])*pars[0]/(1-Hct), 'mL/min/100mL', kidney + '-' + 'MBF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 60*vol*pars[0]/(1-Hct), 'mL/min', kidney + '-' + 'CM-SKBF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 60*vol*pars[2]*(1-pars[1])*pars[0]/(1-Hct), 'mL/min', kidney + '-' + 'SKMBF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 100*vol*pars[0]/(1-Hct)/CO, '%', kidney + '-' + 'CM-PCO' + '-ROI', 'ROI fit'],
    ])

    # Fit BK
    folder.message('Fitting BK.. ')
    kidney = 'BK'
    nt = len(vals_cortex[0])
    dyn_cor = np.zeros(nt)
    dyn_med = np.zeros(nt)
    for t in range(nt):
        vals_t = list(vals_cortex[0][t]) + list(vals_cortex[1][t])
        dyn_cor[t] = np.mean(vals_t)
        vals_t = list(vals_medulla[0][t]) + list(vals_medulla[1][t])
        dyn_med[t] = np.mean(vals_t)

    t1_cortex = measure.read_master_table(folder, kidney+'C-T1-ROI') 
    vars['R10c'] = 1/(t1_cortex/1000)
    t1_medulla = measure.read_master_table(folder, kidney+'M-T1-ROI')
    vars['R10m'] = 1/(t1_medulla/1000)
    FAcorr = measure.read_master_table(folder, kidney+'C-T1FA-ROI')
    vars['FAc'] = FA*FAcorr/12 # Use B1 correction from T1 mapping
    FAcorr = measure.read_master_table(folder, kidney+'M-T1FA-ROI')
    vars['FAm'] = FA*FAcorr/12 # Use B1 correction from T1 mapping 
    pars, _, fit_cortex, fit_medulla = dcmri.fit_kidney_cm_signal_9(
            time, dyn_cor, dyn_med, parset='iBEAt', **vars) 
    
    # Export the results
    fig, (axc, axm) = plt.subplots(1,2,figsize=(10,5))
    axc.plot(time/60, dyn_cor, 'ro', label='Signal for cortex', markersize=markersize)
    axc.plot(time/60, fit_cortex, 'b-', label='Fit for cortex', linewidth=linewidth)
    axc.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    axc.legend()
    axm.plot(time/60, dyn_med, 'ro', label='Signal for medulla', markersize=markersize)
    axm.plot(time/60, fit_medulla, 'b-', label='Fit for medulla', linewidth=linewidth)
    axm.set(xlabel='Time (min)', ylabel='Signal (a.u.)')
    axm.legend()
    plt.savefig(os.path.join(results_path, 'model fit DCE (BKCM).png'), dpi=600)
    figs.append(fig)

    # Update master table
    table['BKC'] = dyn_cor
    table['BKM'] = dyn_med
    vol = len(vals_cortex[0][0])*vox + len(vals_cortex[1][0])*vox # kidney volume mL
    measure.add_rows(folder, [
        [pid, kidney+'CM', 'Kidney', 'ROI', 6000*pars[0]/(1-Hct), 'mL/min/100mL', kidney + '-' + 'CBF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 100*pars[1], '%', kidney + '-' + 'CM-KEF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 100*pars[2], '%', kidney + '-' + 'CPVF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[3], 'sec', kidney + '-' + 'GMTT' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[4], 'sec', kidney + '-' + 'VMTT' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[5]/60, 'min', kidney + '-' + 'PTMTT' + '-ROI', 'ROI fit'],    
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[6]/60, 'min', kidney + '-' + 'LHMTT' + '-ROI', 'ROI fit'],    
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[7]/60, 'min', kidney + '-' + 'DTMTT' + '-ROI', 'ROI fit'],    
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[8]/60, 'min', kidney + '-' + 'CDMTT' + '-ROI', 'ROI fit'], 
        [pid, kidney+'CM', 'Kidney', 'ROI', 100*pars[1]/(1-pars[1]), '%', kidney + '-' + 'CM-FF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[1]/(1-pars[1])*6000*pars[0], 'mL/min/100mL', kidney + '-' + 'CM-TF' + '-ROI', 'ROI fit'],   
        [pid, kidney+'CM', 'Kidney', 'ROI', pars[1]/(1-pars[1])*pars[0]*vol*60, 'mL/min', kidney + '-' + 'CM-SKGFR' + '-ROI', 'ROI fit'],   
        [pid, kidney+'CM', 'Kidney', 'ROI', 6000*pars[2]*(1-pars[1])*pars[0]/(1-Hct), 'mL/min/100mL', kidney + '-' + 'MBF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 60*vol*pars[0]/(1-Hct), 'mL/min', kidney + '-' + 'CM-SKBF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 60*vol*pars[2]*(1-pars[1])*pars[0]/(1-Hct), 'mL/min', kidney + '-' + 'SKMBF' + '-ROI', 'ROI fit'],
        [pid, kidney+'CM', 'Kidney', 'ROI', 100*vol*pars[0]/(1-Hct)/CO, '%', kidney + '-' + 'CM-PCO' + '-ROI', 'ROI fit'],
    ])

    table.to_csv(os.path.join(results_path, 'data_DCE_CM.csv'))
    return figs



def load_roi_curve(dynamic, roi, map, dims=('SliceLocation', 'AcquisitionTime')):

    array = dynamic.pixel_values(dims)
    mask = vreg.pixel_values(roi, on=map, dims=dims[0])
    mask = mask > 0.5
    vals = [array[...,t][mask] for t in range(array.shape[-1])]
    curve = np.array([np.mean(v) for v in vals])
    return curve, vals

  
def load_aif(folder):

    dce = folder.series(SeriesDescription="DCE_aorta_axial_fb")
    aif = folder.series(SeriesDescription='DCE-AIF')
    if dce==[]:
        raise RuntimeError('No DCE data found: cannot export AIF')
    if aif==[]:
        raise RuntimeError('No AIF data found: cannot export AIF')
    array, header = dce[0].array(['AcquisitionTime'], pixels_first=True, first_volume=True)
    aif_mask, _ = aif[0].array(pixels_first=True, first_volume=True)
    dce[0].message('Loading AIF curve..')
    time = np.array([header[k]['AcquisitionTime'] for k in range(header.shape[0])])
    time -= time[0]
    loc = aif_mask != 0
    aif = np.array([np.mean(array[:,:,k][loc]) for k in range(array.shape[2])])

    return time, aif




    



    
