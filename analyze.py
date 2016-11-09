from enum import Enum
from pathlib import Path
from sklearn.externals import joblib
from datastructures import *
from enum import Enum
from random import choice

allresultsWith = joblib.load('Results/with/allresults.pkl')
clus = joblib.load('Results/with/clusters.pkl')

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
names.append("tree-majority")
names.append("svm-majority")

resByCluster = {}


for cid,results in allresultsWith.items():
	allresultsWithout[cid] += results

allres = allresultsWithout

treeIndices = [0,1,2,7,8,9]

for cid,res in allres.items():
	for ci in range(0,len(res)):
		if res[ci] == ClusterClass.confirmed:
			res[ci] = 1
		else:
			res[ci] = 0
	
	treeSum = 0
	svmSum = 0
	for ci in range(0,len(res)):
		if ci in treeIndices:
			treeSum += res[ci]
		else:
			svmSum += res[ci]
	res.append(round(treeSum/len(treeIndices)))
	res.append(round(svmSum/(len(res)-len(treeIndices))))


deviations = [0] * len(names)

for cid,res in allres.items():
	for ci in range(0,len(res)):
		if ci in treeIndices and res[ci] != res[-2]:
			deviations[ci] += 1
		elif res[ci] != res[-1]:
			deviations[ci] += 1


with open("Results/classified.csv", "w") as f:
	hd = "clusterId;exampleTweet"
	for name in names:
		hd+= ";"+name
	f.write(hd+"\n")
	
	for cid,res in allres.items():
		classif = ""
		for n in res:
			classif += ";%s" % n
		
		f.write("%s;\"%s\"%s\n" %(cid, choice(clus[cid].tweets).statement, classif))
		f.write("%s;\"%s\"%s\n" %(cid, choice(clus[cid].tweets).statement, classif))
		f.write("%s;\"%s\"%s\n" %(cid, choice(clus[cid].tweets).statement, classif))

	f.write("\n\n")
	f.write(';;')
	for dev in deviations:
		f.write(";%d" %(dev))
	f.close()
