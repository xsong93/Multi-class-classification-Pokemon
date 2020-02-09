# -*- coding: utf-8 -*-
"""lab34.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gh2iHRqHVdycoOzTL02Vgsv3xCVgxp2D
"""

# Load the Google Drive helper and mount
from google.colab import drive
# This will prompt for authorization.
drive.mount('/content/drive')

# TODO
import tensorflow as tf
device_name = tf.test.gpu_device_name()
if device_name != '/device:GPU:0':
  raise SystemError('GPU device not found')
print('Found GPU at: {}'.format(device_name))

import numpy as np
import matplotlib.pyplot as plt
from keras.preprocessing import image
nrow = 50
ncol = 50
data_dir = '/content/drive/My Drive/Colab Notebooks/project/test'

data_size = 800
folder = np.array(['Bulbasaur','Charmander','Pikachu','Squirtle'], dtype=str)

# data_size = 500*12
# folder = np.array(['Arcanine','Bulbasaur','Charizard','Charmander','Eevee','Jigglypuff','Lucario','Mew','Mudkip','Pikachu','Squirtle','Umbereon'], dtype=str)

import os
k = 0;
data_shape = (data_size,nrow,ncol)
x = np.zeros(data_shape)
y = np.zeros(data_size)
for i, j in enumerate(folder):
  class_path = os.path.join(data_dir, folder[i])
  for image_name in os.listdir(class_path):
    if(image_name != '.ipynb_checkpoints'):
      image_path = os.path.join(class_path, image_name)
      x[k,:,:] = image.load_img(image_path, target_size=(nrow, ncol), grayscale=True)
      y[k] = i
      k = k + 1

X = x.reshape((data_size,nrow*ncol))

def plt_pic(x):
    h = nrow
    w = ncol
    plt.imshow(x.reshape((h, w)), cmap=plt.cm.gray)
    plt.xticks([])
    plt.yticks([])
    
I = np.random.permutation(data_size)
plt.figure(figsize=(10,20))
nplt = 4;
for i in range(nplt):    
    ind = I[i]
    plt.subplot(1,nplt,i+1)
    plt_pic(X[ind])
    plt.title(folder[int(y[ind])])

nplt = 2               # number of pics to plot
ds = [0,50,100,200,400]   # number of SVD approximations
use_pca = True         # True=Use sklearn reconstruction, else use SVD

if use_pca:
    # Construct the PCA object for the max number of coefficient
    dmax = np.max(ds)
    pca = PCA(n_components=dmax, svd_solver='randomized', whiten=True)
    
    # Fit and transform the data
    pca.fit(X)
    Z = pca.transform(X)
    

# Fit the PCA components on the entire dataset
pca.fit(X)

# Select random pics
inds = np.random.permutation(data_size)
inds = inds[:nplt]
nd = len(ds)

# Set figure size
plt.figure(figsize=(1.8 * (nd+1), 2.4 * nplt))
plt.subplots_adjust(bottom=0, left=.01, right=.99, top=.90, hspace=.35)

# Loop over figures
iplt = 0
for ind in inds:
    for d in ds:
        plt.subplot(nplt,nd+1,iplt+1)
        if use_pca:
            # Zero out coefficients after d.  
            # Note, we need to copy to not overwrite the coefficients
            Zd = np.copy(Z[ind,:])
            Zd[d:] = 0
            Xhati = pca.inverse_transform(Zd)
        else:
            # Reconstruct with SVD
            Xhati = (U[ind,:d]*S[None,:d]).dot(Vtr[:d,:]) + Xmean
            
        plt_pic(Xhati)
        plt.title('d={0:d}'.format(d))
        iplt += 1
    
    # Plot
    plt.subplot(nplt,nd+1,iplt+1)
    plt_pic(X[ind,:])
    plt.title('Full')
    iplt += 1

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

scaler = StandardScaler()
pca = PCA()
svc = SVC(kernel='rbf')
pipe = Pipeline(steps=[('scaler', scaler), ('pca', pca), ('svc', svc)])

ncomp_test = np.arange(3,11)
c = np.array([0,1,2,3,4,5],dtype=float)
c_test = 10**c
g = np.array([-6,-5,-4,-3,-2],dtype=float)
gam_test = 10**g

params = {'pca__n_components': ncomp_test, 'svc__C' : c_test, 'svc__gamma' : gam_test}

estimator = GridSearchCV(pipe, params, cv=5, return_train_score =True, iid=False)
estimator.fit(X,y)

print('Best test score is',estimator.best_score_)
print('Best parameters are',estimator.best_params_)

best_parameters = estimator.best_estimator_.get_params()
C_best = best_parameters['pca__n_components'] - 3
test_score = estimator.cv_results_['mean_test_score']
scores = test_score.reshape(len(ncomp_test),len(c_test),len(gam_test))

plt.imshow(scores[C_best, :, :])
plt.xlabel('Gamma')
plt.ylabel('C')
plt.colorbar()

ax = plt.gca()
n0 = len(c_test)
n1 = len(gam_test)
ax.set_xticks(np.arange(0,n1))
ax.set_xticklabels(gam_test)
ax.set_yticks(np.arange(0,n0))
_ = ax.set_yticklabels(c_test)
plt.show()