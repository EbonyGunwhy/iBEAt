################################################
# Prototype: start after T1 map kidney outline #
################################################

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import Birch
from sklearn.mixture import GaussianMixture
from numpy import unique
from numpy import where

#########################################################
# Prepare data for segmentation: multiply data by masks #
#########################################################

slice = 2
mask = np.squeeze(mask_LeftKidneyFinal[:,:,slice])
mapT1 = np.squeeze(array_map_seg[:,:,slice,0,0])

mapT2_allslices, header_mapT2 = app.get_selected(3)[2].array(['SliceLocation','AcquisitionTime'], pixels_first=True)
mapT2 = np.squeeze(mapT2_allslices[:,:,slice,0,0])

size = np.shape(mapT1)


mapT1_w_Mask = mapT1*mask
mapT2_w_Mask = mapT2*mask

mapT1_w_Mask_vec = mapT1_w_Mask.reshape(mapT1_w_Mask.shape[0]*mapT1_w_Mask.shape[1],1)
mapT2_w_Mask_vec = mapT2_w_Mask.reshape(mapT2_w_Mask.shape[0]*mapT2_w_Mask.shape[1],1)

mapT1_w_Mask_vec_sel = mapT1_w_Mask_vec[mapT1_w_Mask_vec!=0]
mapT2_w_Mask_vec_sel = mapT2_w_Mask_vec[mapT2_w_Mask_vec!=0]
###############################################################################################################


#########################################################
# Prepare data for segmentation: replace outliers by median values #
#########################################################

mapT1_w_Mask_vec_sel[mapT1_w_Mask_vec_sel>np.median(mapT1_w_Mask_vec_sel)*1.3] =np.median(mapT1_w_Mask_vec_sel)
mapT1_w_Mask_vec_sel[mapT1_w_Mask_vec_sel<np.median(mapT1_w_Mask_vec_sel)*0.7] =np.median(mapT1_w_Mask_vec_sel)

mapT2_w_Mask_vec_sel[mapT2_w_Mask_vec_sel>np.median(mapT2_w_Mask_vec_sel)*1.3] =np.median(mapT2_w_Mask_vec_sel)
mapT2_w_Mask_vec_sel[mapT2_w_Mask_vec_sel<np.median(mapT2_w_Mask_vec_sel)*0.7] =np.median(mapT2_w_Mask_vec_sel)

X    = np.zeros((mapT1_w_Mask_vec_sel.shape[0],2))

X[:,0] = mapT1_w_Mask_vec_sel
X[:,1] = mapT2_w_Mask_vec_sel

model = GaussianMixture(n_components=2)
# fit the model
model.fit(X)
# assign a cluster to each example
yhat = model.predict(X)
# retrieve unique clusters
clusters = unique(yhat)

segmentedImage = np.zeros((size[0]*size[1],1))-np.ones((size[0]*size[1],1))
k=0
for i in range (len(segmentedImage)):
    if mapT1_w_Mask_vec[i]!=0:
        segmentedImage[i] = yhat[k]
        k=k+1
        
plt.subplot(321)
plt.subplot(321).axis('off')
plt.title('Masked T1 Map')
plt.imshow(np.transpose(mapT1_w_Mask),vmin=1000,vmax=2000)
plt.subplot(322)
plt.subplot(322).axis('off')
plt.title('Masked T2 Map')
plt.imshow(np.transpose(mapT2_w_Mask),vmin=40,vmax=80)
plt.subplot(323)
plt.title('Scatter Plot: Unclassified Points')
plt.scatter(X[:,0],X[:,1])
plt.subplot(324)
plt.title('Scatter Plot: Classified Points')
# create scatter plot for samples from each cluster
for cluster in clusters:
	# get row indexes for samples with this cluster
	row_ix = where(yhat == cluster)
	# create scatter of these samples
	plt.scatter(X[row_ix, 0], X[row_ix, 1])
plt.subplot(325)
plt.title('Segmented Mask')
plt.imshow(np.transpose(segmentedImage.reshape(size[0],size[1])))
plt.subplot(325).axis('off')

