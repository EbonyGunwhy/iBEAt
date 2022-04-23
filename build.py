import weasel

#weasel.doc()
#weasel.install()

# The folder "iBEAt" (and any other physical subfolders)
# should be included in the data_folders keyword argument
# as there might be icons and other non .py files that are required for the specific analysis pipeline

#hidden = ['xnat', 'requests', 'dipy', 'dipy.data', 'matplotlib', 'lmfit', 'fpdf', 'reportlab', 'reportlab.platypus', 'joblib', 'cv2', 'SimpleITK ', 'itk', 'ukat', 'mdreg', 'mdreg.models', 'sklearn.utils._typedefs', 'sklearn.utils._cython_blas', 'sklearn.neighbors.typedefs', 'sklearn.neighbors.quad_tree', 'sklearn.tree._utils', 'sklearn.neighbors._partition_nodes']
weasel.build('', terminal=False, onefile=True, data_folders=['iBEAt'])#, hidden_modules=hidden])