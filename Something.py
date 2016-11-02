import csv
import nltk
from sklearn.feature_extraction.text import *
import re

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

statement = ["says","saying","said","claims","claimed","claiming","promising","explaining"
             "stated","it is the case","promises","promised","explains","explained","claim","admit","admitted","agree",
             "agreeing","agrees","agreed","reply","replies","replied"]

#preparing the sentiment set
sentiment = positive + negative + emoticons

for i in vulgair:
    if i not in sentiment:
        sentiment.append(i)

sentiment = [x for x in sentiment if x not in verb_noun]

tweetArray = []

with open('tweets.csv', newline='', encoding='UTF-8') as csvfile:
     spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
     for row in spamreader:
         if row[3].find('?') == -1:
             row[3] = " ".join(filter(lambda x: x[0] != '#', row[3].split()))
             row[3] = " ".join(filter(lambda x: x[0] != '@', row[3].split()))
             row[3] = " ".join(filter(lambda x: x[0] != 'http/', row[3].split()))
             row[3] = " ".join(filter(lambda x: x[0: 2] != 'RT', row[3].split()))
             row[3] = " ".join(filter(lambda x: x[0: 4] != 'http', row[3].split()))
             row[3] = " ".join(filter(lambda x: x[0: 3] != '"RT', row[3].split()))

            #filter out question words
             if row[3].lower().find('what') != -1:
                 continue
             if row[3].lower().find('where') != -1:
                 continue
             if row[3].lower().find('how') != -1:
                 continue
             if row[3].lower().find('when') != -1:
                 continue
             if row[3].lower().find('why') != -1:
                 continue
             if row[3].lower().find('who') != -1:
                 continue
             if row[3].lower().find('which') != -1:
                 continue
             if row[3].lower().find('whether') != -1:
                 continue
             if row[3].lower().find('if') != -1:
                 continue


             #print(row[3])
             tweetArray.append(row[3])

#removing sentiment and emoticon from tweets and cleaning out urls
wrong = []
for line in tweetArray:
    tokens = nltk.pos_tag(nltk.word_tokenize(line))
    lowertext = line.lower()
    if tokens[0][0].lower() in auxiliary:
        wrong.append(line)
    elif any(state in lowertext for state in statement):
        continue
    elif any(emotion in lowertext for emotion in sentiment):
        wrong.append(line)
    #removing tags that start with a verb (question removal)

tweetArray = [x for x in tweetArray if x not in wrong]
print(len(tweetArray))
print(tweetArray)
print(wrong)
#preparing for clustering
stemmer = nltk.SnowballStemmer("english")
stopwords = nltk.corpus.stopwords.words('english')

def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
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


vectorizer = TfidfVectorizer(max_df=0.95,
                                 min_df=0, stop_words='english',
                                 use_idf=True, tokenizer=tokenize_only, ngram_range=(1,3))

vector = vectorizer.fit_transform(tweetArray)

#getting the names of the vector
names = vectorizer.get_feature_names()