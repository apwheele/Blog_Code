import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import decomposition
from sklearn.preprocessing import scale

os.chdir(r'C:\Users\e009156\Desktop\TexasCensus')

sdet = pd.read_csv('SocialDet_TexCT.csv', index_col='LOGRECNO')
sdet.corr()

scale_det = pd.DataFrame(scale(sdet), columns=list(sdet))
scale_det.corr()

# Via https://scentellegher.github.io/machine-learning/2020/01/27/pca-loadings-sklearn.html
def loadings(data,pca):
    comps = pca.components_.T
    cols = ['PC' + str(i+1) for i in range(comps.shape[0])]
    load_dat = pd.DataFrame(comps,columns=cols,index=list(data))
    return load_dat

#Scatterplot matrix
axes = pd.plotting.scatter_matrix(scale_det, alpha=0.2)

sq = np.sqrt(np.abs(scale_det))*np.sign(scale_det)
pd.plotting.scatter_matrix(sq, alpha=0.2)
sq.corr()


pca = decomposition.PCA()
pca.fit(scale_det)
res = pca.transform(scale_det)

print(pca.explained_variance_ratio_)
print(pca.explained_variance_) #eigen values

print(pca.singular_values_)
print(pca.components_)

diag = np.diagonal(pd.DataFrame(res).cov())
diag/sum(diag)


load_dat = loadings(scale_det,pca)

(scale_det*load_dat['PC1']).sum(axis=1)

res[:,0]

