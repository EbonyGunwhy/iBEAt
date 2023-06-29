import pandas as pd
from dbdicom.wrappers import vreg, scipy
from dbdicom.pipelines import input_series

export_study = "ASL"

def perfusion(database):

    # Get input parameters
    series_desc = [   
        'T1w_abdomen_dixon_cor_bh_water_post_contrast',
        'ASL_kidneys_pCASL_cor-oblique_fb_RBF_moco',
        'LK',
        'RK',
    ]
    series, study = input_series(database, series_desc, export_study)
    if series is None:
        return None, None
    dixon = series[0]
    rbf = series[1]
    lk = series[2]
    rk = series[3]

    # Perform a separate registration for each target region
    rbf_moved = []
    rbf_stats = []
    for kidney in [(lk,'LK'), (rk,'RK')]:

        # Perform coregistration based on m0
        params = vreg.find_rigid_transformation(rbf, dixon, tolerance=0.1, region=kidney[0], margin=0)

        # Apply transformation to rbf image
        moved = vreg.apply_rigid_transformation(rbf, params, target=dixon, description='RBF - ' + kidney[1])

        # Get ROI statistics
        df = scipy.mask_statistics(kidney[0], moved)

        # Organise results
        moved.move_to(study)
        rbf_moved.append(moved)
        rbf_stats.append(df)

    # Keep a copy of the kidneys in the export folder for overlay.
    lk.copy_to(study)
    rk.copy_to(study)

    return rbf_moved, pd.concat(rbf_stats)