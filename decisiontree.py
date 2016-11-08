from sklearn import tree
from numpy.random import normal
from numpy.random import random
from numpy.random import choice
from scipy.stats  import f
from sklearn.metrics import classification_report
from sklearn.metrics import f1_score

def treeClassify(clf, sample, prune):
	currentNode = 0
	nextNode = 0
	while nextNode != tree._tree.TREE_LEAF:
		currentNode = nextNode
		if sample[clf.tree_.feature[currentNode]] <= clf.tree_.threshold[currentNode]:
			nextNode = clf.tree_.children_left[currentNode]
		else:
			nextNode = clf.tree_.children_right[currentNode]
		#prune:
		if min(clf.tree_.value[currentNode][0][0], clf.tree_.value[currentNode][0][1]) < prune:
			nextNode = tree._tree.TREE_LEAF
	return clf.tree_.value[currentNode][0][0] < clf.tree_.value[currentNode][0][1] # prefers false

def treeClassifyAll(clf, samples, prune):
	labels = []
	for sample in samples:
		labels.append(treeClassify(clf, sample, prune))
	return labels

def treeClassify2(clf, sample, verificationSet, verificationLabels):
	currentNode = 0
	nextNode = 0
	presence = [1 for x in verificationLabels]
	
	while nextNode != tree._tree.TREE_LEAF:
		currentNode = nextNode
		goLeft = True
		if sample[clf.tree_.feature[currentNode]] <= clf.tree_.threshold[currentNode]:
			nextNode = clf.tree_.children_left[currentNode]
		else:
			nextNode = clf.tree_.children_right[currentNode]
			goLeft = False
		
		tally = [0,0]
		for index, verificationSample in enumerate(verificationSet):
			if verificationSample[clf.tree_.feature[currentNode]] <= clf.tree_.threshold[currentNode] and not goLeft:
				presence[index] = 0
			elif presence[index] == 1:
				tally[verificationLabels[index]] += 1
		#prune:
		if abs(clf.tree_.value[currentNode][0][0]/(clf.tree_.value[currentNode][0][0] + clf.tree_.value[currentNode][0][1])-(tally[0]/(tally[0]+tally[1]))) > 0.2:
			nextNode = tree._tree.TREE_LEAF
	return clf.tree_.value[currentNode][0][0] < clf.tree_.value[currentNode][0][1] # prefers false

def treeClassifyAll2(clf, samples, verificationSet, verificationLabels):
	labels = []
	for sample in samples:
		labels.append(treeClassify2(clf, sample, verificationSet, verificationLabels))
	return labels

class DecisionTreeClassifier:
	def train(self, samples, labels):
		self.clf = tree.DecisionTreeClassifier()
		self.clf = self.clf.fit(samples, labels)
	
	def classifyAll(self, samples):
		return treeClassifyAll(self.clf, samples, 5)
	
	def toDotFile(self):
		with open("tree.dot", 'w') as f:
			f = tree.export_graphviz(self.clf, out_file=f)
		# terminal> dot -Tpdf tree.dot -o tree.pdf

#-------------------------------------------------------------
# testing below
"""

#generate random
sampleSize   = int(normal(1000, 100))
featureCount = int(max(4, normal(10, 5)))
featureDistributions = [[(random(), random()+0.5)for x in range(0,featureCount)] for label in range(0,2)] 
labels = [random()<0.2 for x in range(0,sampleSize)]
samples = [[min(1,max(0,normal(d[0], d[1]))) for d in featureDistributions[label]] for label in labels]
#samples = [[min(1,max(0,normal(d[label][0], d[label][1]))) for label in labels] for d in featureDistributions]

clf = tree.DecisionTreeClassifier()
clf = clf.fit(samples, labels)
with open("tree.dot", 'w') as f:
	f = tree.export_graphviz(clf, out_file=f)

verifySize = 500
verifyLabels = [random()<0.2 for x in range(0,verifySize)]
verifyunlabeled = [[min(1,max(0,normal(d[0], d[1]))) for d in featureDistributions[label]] for label in verifyLabels]


testSize = 500
testLabels = [random()<0.2 for x in range(0,testSize)]
unlabeled = [[min(1,max(0,normal(d[0], d[1]))) for d in featureDistributions[label]] for label in testLabels]

predicted = treeClassifyAll2(clf, unlabeled, verifyunlabeled, verifyLabels)

prune = 10
print(classification_report(testLabels,treeClassifyAll(clf, unlabeled, prune)))
print(classification_report(testLabels,predicted))
print(classification_report(testLabels,clf.predict(unlabeled)))
"""
