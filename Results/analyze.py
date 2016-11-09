from enum import Enum
from pathlib import Path
from sklearn.externals import joblib
from datastructures import *

resultWith = joblib.load('Results/with/result.pkl')
allresultsWith = joblib.load('Results/with/allresults.pkl')

resultWithout = joblib.load('Results/without/result.pkl')
allresultsWithout = joblib.load('Results/without/allresults.pkl')

classifierNames = [
	"tree-5",
	"tree-10",
	"tree2",
	"linear-svm",
	"poly-svm", "rbf-svm", "sigmoid-svm"
]

classifierNames2 = []
for n in classifierNames:
	classifierNames2.append(n + '-no5')

names = classifierNames + classifierNames2

complete_results = allresultsWith + allresultsWithout

with open("Results/classified.csv", "w") as f:
	hd = "clusterId,exampleTweet"
	for name in classifierNames:
		hd+= ";"+name
	f.write(hd+"\n")
	
	for cluster, cclass in result.items():
		classif = ""
		for ci in range(0,len(classifiers)):
			classif += ";%s" % (allresults[ci][cluster])
		
		f.write("%s;\"%s\"%s\n" %(cluster.cid, choice(cluster.tweets).statement, classif))
		f.write("%s;\"%s\"%s\n" %(cluster.cid, choice(cluster.tweets).statement, classif))
		f.write("%s;\"%s\"%s\n" %(cluster.cid, choice(cluster.tweets).statement, classif))

	f.close()
