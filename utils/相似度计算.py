from sklearn.metrics import pairwise_distances
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import distance


# md = distance.cdist(Xtest, Xtrain.mean(axis=0).reshape(1,-1), 'mahalanobis',
#                     VI=np.linalg.inv(np.cov(Xtrain,rowvar=False)))
#
# dt = pd.date_range('9/10/2018','9/19/2018')
# dt = dt.strftime('%Y-%m-%d')
#
# n = len(Xtest)
# l1, = plt.plot(np.arange(n),np.ones(n)*4,'r')
# l2, = plt.plot(np.ones(12)*120,np.arange(12),'k--')
# l3, = plt.plot(md[:])
# plt.legend([l3,l1],['马氏距离','异常阀值'])
# plt.ylabel('马氏距离')
# plt.xticks(range(1,121,12),dt,rotation=30)
# plt.show()
