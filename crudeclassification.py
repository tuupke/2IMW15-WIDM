from enum import Enum
import pymysql
from sklearn.externals import joblib
from pathlib import Path

pymysql.install_as_MySQLdb()
#################
#<database connection>
cnx = pymysql.connect(user='chiara', passwd='',
             host='131.155.69.222', db='wirdm', charset="utf8mb4")
cursor = cnx.cursor()

#################
#<dummy classes>

class Author:
	def __init__(self, name, account_created, verified, followers, followees, reliability):
		self.name = name
		self.account_created = account_created
		self.verified = verified
		self.followers = followers
		self.followees = followees
		self.reliability = reliability

class Tweet:
	def __init__(self, author, text, statement, time, favCount, retCount):
		self.author          = author
		self.text            = text
		self.statement       = statement
		self.time            = time
		self.favCount        = favCount
		self.retCount        = retCount

class Cluster:
	authors = None
	tweets  = None
	
	def __init__(self, tweets):
		self.tweets = tweets
	
	def getAuthors(self):
		if self.authors == None:
			self.authors = {}
			for tweet in self.tweets:
				self.authors[tweet.author.name] = tweet.author
		
		return authors.values()
	
	def sortTweets(self):
		self.tweets.sort(lambda tweet : tweet.time)

#</dummy classes>
##################
#<helper classes>

def create_author(name):
	sql = "select id,verified,created_at,COMPUTED/max(COMPUTED) from users where username=%s"
	cursor.execute(sql, (name, ))
	if cursor.rowcount != 1:
		print("error")
		raise
	results = cursor.fetchone()
	sql = "select count from follow_counts where follower_id=%s"
	cursor.execute(sql, (results[0], ))
	if cursor.rowcount != 1:
		followees = 0
	else:
		followees = cursor.fetchone()[0]
	sql = "select count from follower_counts where follower_id=%s"
	cursor.execute(sql, (results[0], ))
	if cursor.rowcount != 1:
		followers = 0
	else:
		followers = cursor.fetchone()[0]
	return Author(name, results[2], results[1], followers, followees, results[3]) 

cluster_file = Path("cluster_collection.pkl")
if not cluster_file.is_file():

	tweetMatrix = joblib.load('rawTweets.pkl')
	sentences = joblib.load('tweets.pkl')
	clusterAssignments = joblib.load('clusterList.pkl')

	print("len: ", len(sentences))

	authors = {}
	tweets = []
	clusters = {}

	count = 0
	for (tweet, sentence, cluster_id) in zip(tweetMatrix, sentences, clusterAssignments):
		print("count", count)
		count += 1
		if not tweet[4] in authors:
			authors[tweet[4]] = create_author(tweet[4])
		tweet_class = Tweet(authors[tweet[4]], tweet[1], sentence, tweet[5], tweet[3], tweet[2])
		if not cluster_id in clusters:
			clusters[cluster_id] = []
		clusters[cluster_id].append(tweet_class)
	print(len(clusters))
	cluster_list = []
	for cid,tweets in clusters.items():
		cluster_list.append(Cluster(tweets))

	joblib.dump(cluster_list, 'cluster_collection.pkl')
else:
	cluster_list = joblib.load('cluster_collection.pkl')

# returns a list, the ith value in the list corresponds to
# the value of func given tweets up to start+i*interval (timestamp)
# func accepts one tweet at a time and a state
# func returns a pair (value, newState)
def calculateTimeSeries(sortedTweets, start, interval, func):
	state = None
	mark = start
	result = []
	value = None
	for tweet in sortedTweets:
		if tweet.time > mark:
			result.append(value)
			mark += interval
		(value, state) = func(tweet, state)
	
	result.append(value)
	
	return result
	

#config:
minReliableAuthors = 10
minTotalReliability = 0.8*minReliableAuthors

def calculateClusterReliability(cluster, threshold):
	state = {}
	for tweet in cluster.tweets:
		value, state = calculateClusterReliability_stream(tweet, state)
		if value >= threshold:
			return value
	
	return value

def calculateClusterReliability_stream(tweet, state):
	if tweet.author not in state.keys():
		score = getReliabilityScore(tweet.author)
		if len(state) < minReliableAuthors or min(state.values) < score:
			state[auth] = score
			while len(state) > minReliableAuthors:
				# list of most reliable authors is too long
				# remove least reliable author
				del state[min(state, key=state.get)]
	
	return sum(state), state
#</helper classes>
##################

class ClusterClass(Enum):
	# Not yet classified
	unclassified = 0
	# Confirmed, or likely to be confirmed
	confirmed = 1
	# Unlikely to be confirmed (or even explicitly denied)
	denied    = 2


# Picks out some clusters that are 'obviously' true or false, leaves the rest unclassified
class CrudeClassifyer:
	
	
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
		return minTotalReliability < self.calculateClusterReliability(cluster, threshold=minTotalReliability)
	
	def deniedTest(self, cluster):
		# as of yet, we have no way to conclude that the cluster should be classified as 'denied'
		return False
	
	def analizeConfirmed(self, cluster):
		# this cluster was classified as confirmed
		# let's see why and try to learn from it
		# store what we learned in instance vars so that self.deniedTest can use the knowledge
		
		cluster.sortTweets()
		volume = calculateTimeSeries(cluster, start, interval, lambda tweet, state: 1)
		reliability = calculateTimeSeries(cluster, start, interval, calculateClusterReliability_stream)
		
		# TODO: plot volume and reliability over time, hope that there's a good (combination of) features
		# in the curves that can be used
		pass
