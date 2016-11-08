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
	features = None
	
	def __init__(self, tweets):
		self.tweets = tweets
	
	def getAuthors(self):
		if self.authors == None:
			self.authors = {}
			for tweet in self.tweets:
				self.authors[tweet.author.name] = tweet.author
		
		return authors.values()
	
	def sortTweets(self):
		self.tweets.sort(key=lambda tweet : tweet.time)
