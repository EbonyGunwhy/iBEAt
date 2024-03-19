
import numpy as np 
from scipy import integrate

def pars():
    return ['FP', 'TP', 'PS', 'TE']

def ddint(c, t):
    ci = integrate.cumtrapz(c, t)
    ci = np.insert(ci, 0, 0)
    cii = integrate.cumtrapz(ci, t)
    cii = np.insert(cii, 0, 0)
    return cii, ci

def params_2cfm(X):

    alpha = X[0]
    beta = X[1]
    gamma = X[2]
    Fp = X[3]
    
    if alpha == 0: 
        if beta == 0:
            return [Fp, 0, 0, 0]
        else:
            return [Fp, 1/beta, 0, 0]

    nom = 2*alpha
    det = beta**2 - 4*alpha
    if det < 0 :
        Tp = beta/nom
        Te = Tp
    else:
        root = np.sqrt(det)
        Tp = (beta - root)/nom
        Te = (beta + root)/nom

    if Te == 0:
        PS = 0
    else:   
        if Fp == 0:
            PS == 0
        else:
            T = gamma/(alpha*Fp) 
            PS = Fp*(T-Tp)/Te   

    # Convert to conventional units and apply bounds
    Fp*=6000
    if Fp<0: Fp=0
    if Fp>2000: Fp=2000
    if Tp<0: Tp=0
    if Tp>600: Tp=600
    PS*=6000
    if PS<0: PS=0
    if PS>2000: PS=2000
    if Te<0: Te=0
    if Te>600: Te=600
    return [Fp, Tp, PS, Te] 


def fit(imgs:np.ndarray, aif:np.ndarray=None, time:np.ndarray=None, baseline:int=1, Hct=0.45):

    # Reshape to 2D (x,t)
    shape = np.shape(imgs)
    imgs = imgs.reshape((-1,shape[-1]))

    S0 = np.mean(imgs[:,:baseline], axis=1)
    Sa0 = np.mean(aif[:baseline])
    ca = (aif-Sa0)/(1-Hct)
    
    A = np.empty((imgs.shape[1],4))
    A[:,2], A[:,3] = ddint(ca, time)

    fit = np.empty(imgs.shape)
    par = np.empty((imgs.shape[0], 4))
    for x in range(imgs.shape[0]):
        c = imgs[x,:] - S0[x]
        ctii, cti = ddint(c, time)
        A[:,0] = -ctii
        A[:,1] = -cti
        p = np.linalg.lstsq(A, c, rcond=None)[0] 
        fit[x,:] = S0[x] + p[0]*A[:,0] + p[1]*A[:,1] + p[2]*A[:,2] + p[3]*A[:,3]
        par[x,:] = params_2cfm(p)

    # Apply bounds
    smax = np.amax(imgs)
    fit[fit<0]=0
    fit[fit>2*smax]=2*smax

    # Return in original shape
    fit = fit.reshape(shape)
    par = par.reshape(shape[:-1] + (4,))

    return fit, par