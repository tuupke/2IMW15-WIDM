import csv
import nltk
from sklearn.feature_extraction.text import *
import re
from sklearn.externals import joblib
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import linkage, dendrogram
import langdetect as ld
#import matplotlib.pyplot as plt
from pathlib import Path
from scipy.cluster.hierarchy import fcluster
import pymysql
from numpy import bincount
from numpy import argmax
from numpy import argmin
from numpy import rot90

pymysql.install_as_MySQLdb()

def filterTweets(originalTweets):
    verb_noun = []


    with open('positive-words.txt') as f:
        positive = f.read().splitlines()

    for word in positive:
        tokens = nltk.pos_tag(nltk.word_tokenize(word))
        if tokens[0][1].startswith("V") | tokens[0][1].startswith("N"):
            verb_noun.append(word)

    with open('negative.txt', 'r') as f:
        negative = f.read().splitlines()

    for word in negative:
        tokens = nltk.pos_tag(nltk.word_tokenize(word))
        if tokens[0][1].startswith("V") | tokens[0][1].startswith("N"):
            verb_noun.append(word)

    with open('vulgair.txt') as f:
        vulgair = f.read().splitlines()

    emoticons = ["*O", "*-*", "*O*", "*o*", "* *",
                 ":P", ":D", ":d", ":p",
                 ";P", ";D", ";d", ";p",
                 ":-)", ";-)", ":=)", ";=)",
                 ":<)", ":>)", ";>)", ";=)",
                 "=}", ":)", "(:;)",
                 "(;", ":}", "{:", ";}",
                 "{;:]",
                 "[;", ":')", ";')", ":-3",
                 "{;", ":]",
                 ";-3", ":-x", ";-x", ":-X",
                 ";-X", ":-}", ";-=}", ":-]",
                 ";-]", ":-.)",
                 "^_^", "^-^", ":(", ";(", ":'(",
                 "=(", "={", "):", ");",
                 ")':", ")';", ")=", "}=",
                 ";-{{", ";-{", ":-{{", ":-{",
                 ":-(", ";-(",
                 ":,)", ":'{",
                 "[:", ";]"
                 ]

    auxiliary = ["be", "is", "are", "was", "were", "isn't", "aren't", "weren't",
                 "can", "can't",
                 "could", "couldn't",
                 "do", "doesn't", "does", "don't",
                 "have", "has", "had", "haven't", "hasn't",
                 "may",
                 "might",
                 "must", "mustn't",
                 "shall",
                 "should", "shouldn't",
                 "will", "won't",
                 "would", "wouldn't"]

    statement = ["says", "saying", "said", "claims", "claimed", "claiming", "promising", "explaining", "say",
                 "stated", "it is the case", "promises", "promised", "explains", "explained", "claim", "admit", "admitted",
                 "agree",
                 "agreeing", "agrees", "agreed", "reply", "replies", "replied"]

    # preparing the sentiment set
    sentiment = positive + negative + emoticons

    for i in vulgair:
        if i not in sentiment:
            sentiment.append(i)

    sentiment = [x for x in sentiment if x not in verb_noun]

    raw_tweets = [];
    tweet_array = [];

    for row in originalTweets:

        tweet = row[1]

        if tweet.find('?') == -1:

            filtered = re.sub("(^((\"|'|\s+)?RT:?\s*))|(http[^\s]+)|(@[^\s]+\s?)|#", "", tweet).lower()

            # filter out question words
            if filtered.find('what') != -1:
                continue
            if filtered.find('where') != -1:
                continue
            if filtered.find('how') != -1:
                continue
            if filtered.find('when') != -1:
                continue
            if filtered.find('why') != -1:
                continue
            if filtered.find('who') != -1:
                continue
            if filtered.find('whether') != -1:
                continue
            if filtered.find('if') != -1:
                continue
            if len(filtered.split()) < 3:
                continue

            raw_tweets.append(row)
            tweet_array.append(filtered)

    print('Question: ', len(tweet_array))

    print("starting sentiment analysis")

    # removing sentiment and emoticon from tweets and cleaning out urls
    wrong = []

    for i, line in enumerate(tweet_array):
        lowertext = line.lower()
        # tokens = nltk.pos_tag(nltk.word_tokenize(line))
        try:
            if (ld.detect(lowertext) != "en"):
                wrong.append(i)
        except ld.lang_detect_exception.LangDetectException:
            wrong.append(i)
        if tokens[0][0].lower() in auxiliary:
            wrong.append(line)
        elif any(state in lowertext for state in statement):
            continue
        elif any(emotion in lowertext for emotion in sentiment):
            wrong.append(i)
            # removing tags that start with a verb (question removal)

    tweet_array = [x for i, x in enumerate(tweet_array) if i not in wrong]
    raw_tweets = [x for i, x in enumerate(raw_tweets) if i not in wrong]

    return tweet_array, raw_tweets


def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems

def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens

def vectorize_tweet_set(tweetArray):
    vectorizer = TfidfVectorizer(max_df=0.95,
                                 min_df=0, stop_words='english', strip_accents="ascii", smooth_idf=True,
                                 use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1, 3))

    return vectorizer.fit_transform(tweetArray)

def make_linkage_matrix(vector):
    dist = 1 - cosine_similarity(vector)
    return linkage(dist, method='complete', metric='euclidean')

def make_dendrogram(linkage_matrix, threshold, name):
    fig, ax = plt.subplots(figsize=(20, 40))  # set size
    ax = dendrogram(linkage_matrix, show_leaf_counts=True, color_threshold=threshold,
                    truncate_mode="level", p=15, orientation="right", labels=rot90(rawTweets)[5], leaf_font_size=8);
    plt.savefig(name + '.png', dpi=300, bbox_inches='tight')  # save figure as ward_clusters

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

my_file = Path("tweets.pkl")
if not my_file.is_file():
    cnx = pymysql.connect(user='chiara', passwd='',
                 host='131.155.69.222', db='wirdm', charset="utf8mb4")

    cursor = cnx.cursor()
    cursor.execute("select * from tweets")
    databaseTweets = cursor.fetchall()
    (tweetArray, rawTweets) = filterTweets(databaseTweets);
    print(len(tweetArray))
    joblib.dump(tweetArray, 'tweets.pkl')
    joblib.dump(rawTweets, 'rawTweets.pkl')
else:
    tweetArray = joblib.load('tweets.pkl')
    rawTweets = joblib.load('rawTweets.pkl')

print("tweetsread")

#preparing for clustering
stemmer = nltk.SnowballStemmer("english")
stopwords = nltk.corpus.stopwords.words('english')


vector = []
my_file = Path("vector.pkl")
if not my_file.is_file():
    vector = vectorize_tweet_set(tweetArray)
    joblib.dump(vector, 'vector.pkl')
else:
    vector = joblib.load('vector.pkl')

print("vectorized")


my_file = Path("linkageMatrix.pkl")
if not my_file.is_file():
    linkage_matrix = make_linkage_matrix(vector)
    joblib.dump(linkage_matrix, 'linkageMatrix.pkl')
else:
    linkage_matrix = joblib.load('linkageMatrix.pkl')


print("matrix created")

topThreshold = 0.2* max(linkage_matrix[:,2])
make_dendrogram(linkage_matrix, topThreshold, "topDendrogram")
clusterOrderning = fcluster(linkage_matrix, topThreshold, criterion="distance")

originalCount = bincount(clusterOrderning)
print("amount of clusters: ", len(originalCount)-1, " amount in each: ", originalCount)

clusterToFind = argmax(originalCount)
print("find cluster: ", clusterToFind)

newTweets = []
newRawTweets = []
for id, val in enumerate(clusterOrderning):
    if val == clusterToFind:
        newTweets.append(tweetArray[id])
        newRawTweets.append(rawTweets[id])

newVector = vectorize_tweet_set(newTweets)
newLinkage = make_linkage_matrix(newVector)

bottomThreshold = 0.50* max(newLinkage[:,2])
make_dendrogram(newLinkage, bottomThreshold, "bottomDendrogram")
detailedClustering = fcluster(newLinkage, bottomThreshold, criterion="distance")

count = bincount(detailedClustering)
print("amount of detailed clusters: ", len(count)-1, " amount in each: ", count)

numberOfOriginalClusters = len(originalCount)-1
i = 0;
for id, val in enumerate(clusterOrderning):
    if val == clusterToFind:
        clusterOrderning[id] = detailedClustering[i] + numberOfOriginalClusters
        i += 1

for id, val in enumerate(clusterOrderning):
    if val>clusterToFind:
        clusterOrderning[id] = val - 1

clusterToFind = argmax(count)
for id, val in enumerate(clusterOrderning):
    if val == clusterToFind:
        clusterOrderning[id] = 0
    elif val>clusterToFind:
        clusterOrderning[id] = val -1

count = bincount(clusterOrderning)
print("amount of clusters total: ", len(count), " amount in each: ", count)
getClosestTweet("Aleppo has been bombed", rawTweets, tweetArray)
joblib.dump(clusterOrderning, 'clusterList.pkl')
