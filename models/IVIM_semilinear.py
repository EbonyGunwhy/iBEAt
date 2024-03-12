import numpy as np
import os 
import multiprocessing

from scipy.optimize import curve_fit

import models.DWI_linear as dwi


def init(sig):
    smax = np.amax(sig)
    if smax<=0:
        return (0.0025, 0)
    else:
        return (0.0025, smax)

def bnds(sig):
    smax = np.amax(sig)
    if smax<=0:
        upper = [1, np.inf]
    else:
        upper = [1.0, 2*smax]
    lower = [0,0]
    return lower, upper

def signal(bvals, Df, Sf, Dxx, Dyy, Dzz, Sd):
    Sflow = Sf*np.exp(-bvals*Df)
    return np.concatenate([
        Sflow + Sd*np.exp(-bvals*Dxx),
        Sflow + Sd*np.exp(-bvals*Dyy),
        Sflow + Sd*np.exp(-bvals*Dzz),
    ])

def fit_signal(args):
    bvals, ydata, pars_dwi, xtol, bounds = args
    if bounds==True:
        bounds = bnds(ydata)
    else:
        bounds = (-np.inf, np.inf)
    pars = init(ydata)
    try:
        # Fit the IVIM signal on all data points, but fixing the DWI part
        pars, _ = curve_fit(
            lambda b, Df, Sf: signal(b, Df, Sf, *tuple(pars_dwi)),
            bvals, ydata, p0=pars, xtol=xtol, bounds=bounds)
    except RuntimeError:
        # If the model does not fit, return initial values
        pass
    return tuple(pars) + tuple(pars_dwi) # Df, Sf, Dxx, Dyy, Dzz, Sd

def pars():
    return ['Df', 'Sf', 'Dxx', 'Dyy', 'Dzz', 'Sd']

def derived(par):
    Df = par[...,0]
    S0f = par[...,1] 
    MD = np.mean(par[...,2:5], axis=-1)
    S0d = par[...,5]
    S0 = S0f+S0d
    ff = S0f/S0
    ff[S0==0]=0
    ff[ff>1]=1
    ff[ff<0]=0
    return S0, Df, MD, ff


try: 
    num_workers = int(len(os.sched_getaffinity(0)))
except: 
    num_workers = int(os.cpu_count())


def fit(imgs:np.ndarray, bvals=None, bvecs=None, xtol=1e-3, bounds=False, parallel=True):

    # Reshape to (x,t)
    shape = imgs.shape
    imgs = imgs.reshape((-1,shape[-1]))

    # Fit the DWI parameters linearly to the last 3 b-values
    k, n = 3, len(bvals)
    imgs_dwi = np.concatenate([imgs[:,n-k:n], imgs[:,2*n-k:2*n], imgs[:,3*n-k:3*n]], axis=-1)
    bvals_dwi = np.concatenate([bvals[n-k:], bvals[n-k:], bvals[n-k:]])
    bvecs_dwi = np.concatenate([bvecs[n-k:], bvecs[n-k:], bvecs[n-k:]])
    _, pars_dwi = dwi.fit(imgs_dwi, bvals_dwi, bvecs_dwi)

    # Perform the fit pixelwise
    if parallel:
        args = [(bvals, imgs[x,:], pars_dwi[x,:], xtol, bounds) for x in range(imgs.shape[0])]
        pool = multiprocessing.Pool(processes=num_workers)
        fit_pars = pool.map(fit_signal, args)
        pool.close()
        pool.join()
    else: # for debugging
        fit_pars = [fit_signal((bvals, imgs[x,:], pars_dwi[x,:], xtol, bounds)) for x in range(imgs.shape[0])]

    # Create output arrays
    npars = len(pars())
    fit = np.empty(imgs.shape)
    par = np.empty((imgs.shape[0], npars))
    for x, p in enumerate(fit_pars):
        fit[x,:] = signal(bvals, *p)
        par[x,:] = p

    # Return in original shape
    fit = fit.reshape(shape)
    par = par.reshape(shape[:-1] + (npars,))
       
    return fit, par






