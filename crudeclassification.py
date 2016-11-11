from enum import Enum
import pymysql
from sklearn.externals import joblib
from pathlib import Path
from datastructures import *
from decisiontree import *
from svm import *
from random import choice

WITH_INFLUENCE = False

pymysql.install_as_MySQLdb()
#################
#<database connection>
#cnx = pymysql.connect(user='chiara', passwd='',
#             host='131.155.69.222', db='wirdm', charset="utf8mb4")
#cursor = cnx.cursor()



#</dummy classes>
##################
#<helper classes>

def create_author(name):
	sql = "select id,verified,created_at,COMPUTED/(select max(COMPUTED) from users),follower_count,friend_count from users where username=%s"
	cursor.execute(sql, (name, ))
	if cursor.rowcount != 1:
		results = (0, 0, 0, 0, 0, 0)
	else:
		results = cursor.fetchone()
	return Author(name, results[2], results[1], results[4], results[5], results[3]) 

cluster_file = Path("cluster_collection.pkl")
if not cluster_file.is_file():

	tweetMatrix = joblib.load('rawTweets.pkl')
	sentences = joblib.load('tweets.pkl')
	clusterAssignments = joblib.load('clusterList.pkl')

	print(clusterAssignments)

	print("len: ", len(sentences))

	authors = {}
	clusters = {}

	count = 0
	for (tweet, sentence, cluster_id) in zip(tweetMatrix, sentences, clusterAssignments):
		#print("count", count)
		count += 1
		if not tweet[4] in authors:
			authors[tweet[4]] = create_author(tweet[4])
		tweet_class = Tweet(authors[tweet[4]], tweet[1], sentence, tweet[5], tweet[3], tweet[2])
		if not cluster_id in clusters:
			clusters[cluster_id] = []
		clusters[cluster_id].append(tweet_class)
	print(len(clusters))
	cluster_list = []

	# The zero cluster is the biggest, which we delete
	del(clusters[0])

	for cid,tweets in clusters.items():
		cluster_list.append(Cluster(tweets,cid))

	joblib.dump(cluster_list, 'cluster_collection.pkl')
else:
	cluster_list = joblib.load('cluster_collection.pkl')

feature_file = Path("cluster_features.pkl")
if not feature_file.is_file():
	from features import generate_features
	cluster_features = []
	for cluster in cluster_list:
		cluster_features.append(generate_features(cluster.tweets))
	joblib.dump(cluster_features, 'cluster_features.pkl')
else:
	cluster_features = joblib.load('cluster_features.pkl')

if not WITH_INFLUENCE:
	for feat in cluster_features:
		del feat[5]
for index, cluster in enumerate(cluster_list):
	cluster.features = cluster_features[index]

print(len(cluster_list))

# returns a list, the ith value in the list corresponds to
# the value of func given tweets up to start+i*interval (timestamp)
# func accepts one tweet at a time and a state
# func returns a pair (value, newState)
def calculateTimeSeries(sortedTweets, interval, func):
	state = None
	mark = -1
	result = []
	value = None
	for tweet in sortedTweets:
		if mark == -1:
			mark = tweet.time
		if tweet.time > mark:
			result.append(value)
			mark += interval
		(value, state) = func(tweet, state)
	
	result.append(value)
	
	return result
	

#config:
minReliableAuthors = 3
minTotalReliability = 0.4*minReliableAuthors
unreliability = 0.2*minReliableAuthors

def calculateClusterReliability(cluster, threshold):
	state = {}
	for tweet in cluster.tweets:
		value, state = calculateClusterReliability_stream(tweet, state)
		if value >= threshold:
			return value
	
	return value

def calculateClusterReliability_stream(tweet, state):
	if state is None:
		state = {}
	if tweet.author not in state.keys():
		score = tweet.author.reliability
		if score is None: # too small to calculate...
			score = 0
		if len(state) < minReliableAuthors or min(state.values()) < score:
			state[tweet.author] = score
			while len(state) > minReliableAuthors:
				# list of most reliable authors is too long
				# remove least reliable author
				del state[min(state, key=state.get)]
	
	return sum(state.values()), state

def counter_stream(tweet, state):
	if state is None:
		state = 0
	return state+1, state+1
#</helper classes>
##################


# Picks out some clusters that are 'obviously' true or false, leaves the rest unclassified
class CrudeClassifier:
	
	
	# @param clusters a set of objects of type Cluster
	# @returns a dict mapping all these clusters to exactly one class ('unclassified', 'confirmed' or 'denied')
	def classify(self, clusters):
		# 1. pick out clusters the are confirmed by reliable users
		# 2. analise volume and reliability over time of each of the confirmed clusters
		# 3. determine at what point in time a rumour should have been confirmed if it were true, based on tweet volume and reliability of users tweeting
		# 4. pick out the clusters that have not been confirmed, but should have been if they were true. These are classified 'denied'
		
		classification = {}
		for cluster in clusters:
			# 1. pick out clusters that are confirmed
			if self.confirmedTest(cluster):
				classification[cluster] = ClusterClass.confirmed
				# 2. analise the confirmed clusters
				self.analizeConfirmed(cluster)
			else:
				classification[cluster] = ClusterClass.unclassified
		
		for cluster in clusters:
			if classification[cluster] == ClusterClass.unclassified:
				# 4. pick out the clusters that should've been confirmed, but are not.
				if self.deniedTest(cluster):
					classification[cluster] = ClusterClass.denied
		
		return classification
		
	def confirmedTest(self, cluster):
		rel = calculateClusterReliability(cluster, threshold=minTotalReliability)
		return minTotalReliability < rel
	
	def deniedTest(self, cluster):
		# as of yet, we have no way to conclude that the cluster should be classified as 'denied'
		rel = calculateClusterReliability(cluster, threshold=minTotalReliability)
		return rel < unreliability
	
	def analizeConfirmed(self, cluster):
		# this cluster was classified as confirmed
		# let's see why and try to learn from it
		# store what we learned in instance vars so that self.deniedTest can use the knowledge
		
		cluster.sortTweets()
		interval = 1000*60*30 # 30 minutes?
		volume = calculateTimeSeries(cluster.tweets, interval, counter_stream)
		reliability = calculateTimeSeries(cluster.tweets, interval, calculateClusterReliability_stream)
		
		# TODO: plot volume and reliability over time, hope that there's a good (combination of) features
		# in the curves that can be used
		pass

cc = CrudeClassifier()
result = cc.classify(cluster_list)

tally = {ClusterClass.unclassified: 0, ClusterClass.confirmed: 0, ClusterClass.denied: 0}
for r in result.values():
	tally[r] += 1

print(tally)

labels = []
labeled = []
unlabeled = []
unlabeled_clusters = []
for cluster, cclass in result.items():
	if not cclass == ClusterClass.unclassified:
		labels.append(cclass == ClusterClass.confirmed)
		labeled.append(cluster.features)
	else:
		unlabeled.append(cluster.features)
		unlabeled_clusters.append(cluster)
classifiers = [
	DecisionTreeClassifier(5),
	DecisionTreeClassifier(10),
	DecisionTreeClassifier2(),
	SVMClassifier("linear"),
	SVMClassifier("poly"),
	SVMClassifier("rbf"),
	SVMClassifier("sigmoid"),
]
classifierNames = [
	"tree-5",
	"tree-10",
	"tree2",
	"linear-svm",
	"poly-svm", "rbf-svm", "sigmoid-svm"
]

predicted = [None] * len(classifiers)
allresults = [None] * len(classifiers)

for ci, classifier in enumerate(classifiers):
	classifier.train(labeled, labels)
	classifier.toDotFile()
	predicted[ci] = classifier.classifyAll(unlabeled)
	allresults[ci] = result.copy()
	
	for index, sample in enumerate(unlabeled_clusters):
		if predicted[ci][index]:
			allresults[ci][sample] = ClusterClass.confirmed
		else:
			allresults[ci][sample] = ClusterClass.denied
	
	tally = {ClusterClass.unclassified: 0, ClusterClass.confirmed: 0, ClusterClass.denied: 0}
	for r in allresults[ci].values():
		tally[r] += 1
	
	print(tally)

resById = {}
for cluster, cclass in result.items():
	resById[cluster.cid] = []
	for ci in range(0,len(classifiers)):
		resById[cluster.cid].append(allresults[ci][cluster])

clus = {}
for cluster, cclass in result.items():
	clus[cluster.cid] = cluster

joblib.dump(resById, 'allresults.pkl')
joblib.dump(clus, 'clusters.pkl')


with open("classified.csv", "w") as f:
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
