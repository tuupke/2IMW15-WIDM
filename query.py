from sklearn.externals import joblib
from pathlib import Path
import Something.py

tweetArray = joblib.load('tweets.pkl')
rawTweets = joblib.load('rawTweets.pkl')
resById = joblib.load('allresults.pkl')
clus = joblib.load('clusters.pkl')

def getClosestTweet(evaluatedTweet, originalTweetSet, filteredSet):
    array_of_tweet = []
    array_of_tweet.append(("", evaluatedTweet))
    raw_array = []
    raw_array.append(evaluatedTweet)

    for line in originalTweetSet:
        raw_array.append(line)
    for line in filteredSet:
        array_of_tweet.append(line)

    vector = vectorize_tweet_set(array_of_tweet)
    distanceMatrix = 1 - cosine_similarity(vector)

    distancesToOriginal = distanceMatrix[0]
    distancesToOriginal[0] = 1

    index = argmin(distancesToOriginal)-1 # minus 1 because the search tweet is added
    #print("index of closest tweet = ", index)

    #print(originalTweetSet[index][1])

    return index

#1. prompt voor een zin
print("Enter a tweet-like statement")
query = input("> ")
if query == "exit":
	exit()

#2. return true/false/unknown
tweetIndex = getClosestTweet(query, rawTweets, tweetArray)
print("Your query belongs to the tweet with index %d" %tweetIndex)
