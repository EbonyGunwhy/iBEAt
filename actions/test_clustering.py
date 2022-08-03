import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import Birch
from sklearn.mixture import GaussianMixture
from numpy import unique
from numpy import where

size = 20
noiseSTD = 0.15

T1_Square = np.ones((size,size))
T2_Square = np.ones((size,size))
X         = np.ones((size*size,2))

T1_Square[0:int(size/2),:]    = 2000
T1_Square[int(size/2):size,:] = 1200

T2_Square[0:int(size/2),:]    = 40
T2_Square[int(size/2):size,:] = 60


plt.imshow(T1_Square, vmin=1200, vmax=2000, cmap='jet', aspect='auto')
plt.colorbar()
plt.title('T1 Map')
plt.show()


plt.imshow(T2_Square, vmin=40, vmax=60, cmap='jet', aspect='auto')
plt.colorbar()
plt.title('T2 Map')
plt.show()

noiseT1 = np.random.normal(1,noiseSTD,size*size)
noiseT1 = noiseT1.reshape(size,size)

noiseT2 = np.random.normal(1,noiseSTD,size*size)
noiseT2 = noiseT2.reshape(size,size)

T1_Sq_w_noise = T1_Square*noiseT1
T2_Sq_w_noise = T2_Square*noiseT2

plt.imshow(T1_Sq_w_noise.reshape((size,size)), vmin=800, vmax=2500, cmap='jet', aspect='auto')
plt.colorbar()
plt.title('T1 Map with noise')
plt.show()

plt.imshow(T2_Sq_w_noise.reshape((size,size)), vmin=40, vmax=130, cmap='jet', aspect='auto')
plt.colorbar()
plt.title('T2 Map with noise')
plt.show()

T1_Sq_w_noise = T1_Sq_w_noise.reshape(size*size)
T2_Sq_w_noise = T2_Sq_w_noise.reshape(size*size)

plt.scatter(T1_Sq_w_noise,T2_Sq_w_noise)
plt.title('Scatter Plot: Unclassified Points')
plt.show()

X[:,0] = T1_Sq_w_noise
X[:,1] = T2_Sq_w_noise

#X[:,0] = mapT1_test
#X[:,1] = mapT2_test

#model = Birch(threshold=0.01, n_clusters=2)
model = GaussianMixture(n_components=2)
# fit the model
model.fit(X)
# assign a cluster to each example
yhat = model.predict(X)
# retrieve unique clusters
clusters = unique(yhat)
# create scatter plot for samples from each cluster
for cluster in clusters:
	# get row indexes for samples with this cluster
	row_ix = where(yhat == cluster)
	# create scatter of these samples
	plt.scatter(X[row_ix, 0], X[row_ix, 1])
# show the plot
plt.title('Scatter Plot: Classified Points')
plt.show()

plt.imshow(yhat.reshape((size,size)))
plt.title('Segmented Image')
plt.show()