from sklearn import tree
from numpy.random import normal
from numpy.random import random

#generate random
sampleSize   = int(normal(1000, 100))
featureCount = int(max(4, normal(10, 5)))
featureDistributions = [[(random(), random()/2)for x in range(0,featureCount)] for label in range(0,2)] 
labels = [random()<0.5 for x in range(0,sampleSize)]
samples = [[min(1,max(0,normal(d[0], d[1]))) for d in featureDistributions[label]] for label in labels]
#samples = [[min(1,max(0,normal(d[label][0], d[label][1]))) for label in labels] for d in featureDistributions]

"""
samples = [
	[cluster1.feature1, cluster1.feature2, ...],
	[cluster2.feature1, cluster2.feature2, ...],
	...
]

labels = [
	True, # cluster1 is True
	False, # cluster2 is False
	...
]
"""

clf = tree.DecisionTreeClassifier()
clf = clf.fit(samples, labels)
with open("tree.dot", 'w') as f:
	f = tree.export_graphviz(clf, out_file=f)