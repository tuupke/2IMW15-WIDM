from enum import Enum

#################
#<dummy classes>

class Tweet:
	def __init__(self, author, text, time):
		self.author = author
		self.text   = text
		self.time   = time

class Cluster:
	authors = None
	tweets  = None
	
	def __init__(self, tweets):
		self.tweets = tweets
	
	def getAuthors(self):
		if self.authors == None:
			self.authors = {}
			for tweet in self.tweets:
				self.authors.add(tweet.author)
		
		return authors

def getReliabilityScore(author):
	return 0.5

#</dummy classes>
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
	#config:
	minReliableAuthors = 10
	minTotalReliability = 0.8*minReliableAuthors
	
	
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
		authors = cluster.getAuthors()
		reliableAuthors = []
		for author in authors:
			score = getReliabilityScore(author)
			if len(reliableAuthors) < self.minReliableAuthors or reliableAuthors[0] < score:
				reliableAuthors.append(score)
				reliableAuthors.sort()
				if len(reliableAuthors) > self.minReliableAuthors:
					del reliableAuthors[0]
			if sum(reliableAuthors) > self.minTotalReliability:
				return True
		return False
	
	def deniedTest(self, cluster):
		# as of yet, we have no way to conclude that the cluster should be classified as 'denied'
		return False
	
	def analizeConfirmed(self, cluster):
		# this cluster was classified as confirmed
		# let's see why and try to learn from it
		# store what we learned in instance vars so that self.deniedTest can use the knowledge
		pass