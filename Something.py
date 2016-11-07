import csv
import nltk
from sklearn.feature_extraction.text import *
import re
from sklearn.externals import joblib
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import linkage, dendrogram
import langdetect as ld
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.cluster.hierarchy import fcluster
import pymysql
from numpy import bincount

pymysql.install_as_MySQLdb()
tweetArray = []
rawTweets = []

my_file = Path("tweets.pkl")
if not my_file.is_file():
    cnx = pymysql.connect(user='chiara', passwd='',
                 host='131.155.69.222', db='wirdm', charset="utf8mb4")

    cursor = cnx.cursor()

    verb_noun = []

    with open('positive-words.txt') as f:
        positive = f.read().splitlines()

    for word in positive:
        tokens = nltk.pos_tag(nltk.word_tokenize(word))
        if tokens[0][1].startswith("V") | tokens[0][1].startswith("N"):
          verb_noun.append(word)

    with open('negative.txt','r') as f:
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

    auxiliary = ["be", "is", "are","was","were","isn't","aren't","weren't",
    "can","can't",
    "could","couldn't",
    "do","doesn't","does","don't",
    "have","has","had","haven't","hasn't",
    "may",
    "might",
    "must","mustn't",
    "shall",
    "should","shouldn't",
    "will","won't",
    "would","wouldn't"]

    statement = ["says","saying","said","claims","claimed","claiming","promising","explaining","say",
                 "stated","it is the case","promises","promised","explains","explained","claim","admit","admitted","agree",
                 "agreeing","agrees","agreed","reply","replies","replied"]

    #preparing the sentiment set
    sentiment = positive + negative+ emoticons


    for i in vulgair:
        if i not in sentiment:
            sentiment.append(i)

    sentiment = [x for x in sentiment if x not in verb_noun]

    cursor.execute("select * from tweets")
    rawTweets = [];


    for row in cursor.fetchall():

        tweet = row[1]

        if tweet.find('?') == -1:

            filtered = re.sub("(^((\"|'|\s+)?RT:?\s*))|(http[^\s]+)|(@[^\s]+\s?)|#", "", tweet).lower()

           #filter out question words
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

            rawTweets.append(row)
            tweetArray.append(filtered)

    print('Question: ', len(tweetArray))

    print("starting sentiment analysis")

    #removing sentiment and emoticon from tweets and cleaning out urls
    wrong = []

    for i,line in enumerate(tweetArray):
        lowertext = line.lower()
        #tokens = nltk.pos_tag(nltk.word_tokenize(line))
        try:
            if(ld.detect(lowertext)!= "en"):
                    wrong.append(i)
        except ld.lang_detect_exception.LangDetectException:
            wrong.append(i)
        verb = False
        if tokens[0][0].lower() in auxiliary:
            wrong.append(line)
        elif any(state in lowertext for state in statement):
            continue
        elif any(emotion in lowertext for emotion in sentiment):
            wrong.append(i)
        #removing tags that start with a verb (question removal)

    tweetArray = [x for i,x in enumerate(tweetArray) if i not in wrong]
    rawTweets = [x for i,x in enumerate(rawTweets) if i not in wrong]
    joblib.dump(tweetArray, 'tweets.pkl')
    joblib.dump(rawTweets, 'rawTweets.pkl')
else:
    tweetArray = joblib.load('tweets.pkl')
    rawTweets = joblib.load('rawTweets.pkl')

print("tweetsread")

#preparing for clustering
stemmer = nltk.SnowballStemmer("english")
stopwords = nltk.corpus.stopwords.words('english')

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

vector = []
my_file = Path("vector.pkl")
if not my_file.is_file():
    vectorizer = TfidfVectorizer(max_df=0.95,
                                 min_df=0, stop_words='english', strip_accents="ascii", smooth_idf=True,
                                 use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1, 3))

    vector = vectorizer.fit_transform(tweetArray)
    joblib.dump(vector, 'vector.pkl')
else:
    vector = joblib.load('vector.pkl')

print("vectorized")


my_file = Path("linkageMatrix.pkl")
if not my_file.is_file():
    dist = 1 - cosine_similarity(vector)
    linkage_matrix = linkage(dist, method='complete', metric='euclidean')
    joblib.dump(linkage_matrix, 'linkageMatrix.pkl')
else:
    linkage_matrix = joblib.load('linkageMatrix.pkl')


print("matrix created")


fig, ax = plt.subplots(figsize=(60, 80)) # set size
ax = dendrogram(linkage_matrix, show_leaf_counts=True, truncate_mode="level", p=20, orientation="right", labels=rawTweets);
plt.tight_layout() #show plot with tight layout

#uncomment below to save figure
plt.savefig('Dendrogram.png', dpi=200) #save figure as ward_clusters

clusterOrderning = fcluster(linkage_matrix, 0.7* max(linkage_matrix[:,2]), criterion="distance")
joblib.dump(clusterOrderning, 'clusterList.pkl')
print (clusterOrderning)
print(max(linkage_matrix[:, 2]) * 0.7)
print(bincount(clusterOrderning))
