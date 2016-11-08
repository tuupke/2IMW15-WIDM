import datastructures
import nltk
import nltk.sentiment.vader
import spacy
from nltk import Tree

def get_vulgar_words():
    list = []
    f = open('vulgar_words.txt', 'r')
    for line in f:
        list.append(line.strip())
    return list

def get_abbreviations():
    list = []
    f = open('abbreviations_clean.txt', 'r')
    for line in f:
        list.append(line.strip())
    return list

def negated_feature(tok_tweets):
    negated = 0
    for tok_tweet in tok_tweets:
        if (nltk.sentiment.vader.negated(tok_tweet)):
            negated += 1
    #print(negated)
    if (len(tok_tweets) == 0):
        return 1
    return negated/len(tok_tweets)

def vulgar_feature(tok_tweets, vulgar):
    vulgar_count = 0
    for tok_tweet in tok_tweets:
        for tok in tok_tweet:
            if tok.lower() in vulgar:
                vulgar_count += 1
                break
    #print(vulgar_count)
    if (len(tok_tweets) == 0):
        return 1
    return vulgar_count/len(tok_tweets)

def abbreviation_feature(tok_tweets, abbreviations):
    abbreviation_count = 0
    for tok_tweet in tok_tweets:
        for tok in tok_tweet:
            if tok.lower() in abbreviations:
                abbreviation_count += 1
                break
    #print(abbreviation_count)
    if (len(tok_tweets) == 0):
        return 1
    return abbreviation_count/len(tok_tweets)

def word_complexity_feature(tok_tweets):
    count = 0
    size = 0
    for tok_tweet in tok_tweets:
        for tok in tok_tweet:
            count += 1
            size += len(tok)
    if (len(tok_tweets) == 0):
        return 1
    return count/size


# ---------------------------------
# ---- Sentence complexity --------

en_nlp = spacy.load('en')

def to_nltk_tree(spacy_node):
    if spacy_node.n_lefts + spacy_node.n_rights > 0:
        return Tree(spacy_node.orth_, [to_nltk_tree(child) for child in spacy_node.children])
    else:
        return spacy_node.orth_

def tree_depth(nltk_tree, depth):
    maximum = depth
    for subtree in nltk_tree:
        if type(subtree) == nltk.tree.Tree:
            result = tree_depth(subtree, depth + 1)
            if result > maximum:
                maximum = result
    return maximum

def sentence_complexity_feature(tweets):
    count = 0
    size = 0
    for tweet in tweets:
        sentences = en_nlp(tweet)
        for sent in sentences.sents:
            count += 1
            tree = to_nltk_tree(sent.root)
            if type(tree) != nltk.tree.Tree:
                size += 1
            else:
                #tree.pretty_print()
                #print(tree_depth(tree, 1))
                size += tree_depth(tree, 1)
    if size == 0:
        return 1
    return count/size

# ---- End sentence complexity ----

def influence_feature(tweets_class):
    followers = 0
    count = 0
    for tweet in tweets_class:
        followers += tweet.author.followers
        count += 1
    if followers == 0:
        return 1
    return count/followers

def role_feature(tweets_class):
    role_fraction_count = 0
    count = 0
    for tweet in tweets_class:
        if tweet.author.followees == 0: 
            role_fraction_count += 1
        else:
            role_fraction_count += tweet.author.followers/tweet.author.followees
        count += 1
    if count == 0:
        return 1
    return count/role_fraction_count

vulgar = get_vulgar_words()
abbreviation = get_abbreviations()

def generate_features(tweets):
    str_statements = []
    tok_statements = []
    str_tweets = []
    tok_tweets = []
    count = 0
    for tweet in tweets:
        print(count)        
        count+=1
        str_statements.append(tweet.statement)
        str_tweets.append(tweet.text)
        tok_tweets.append(nltk.word_tokenize(tweet.text))
        tok_statements.append(nltk.word_tokenize(tweet.statement))
    results = []
    results.append(negated_feature(tok_statements))
    results.append(vulgar_feature(tok_tweets, vulgar))
    results.append(abbreviation_feature(tok_statements, abbreviation))
    results.append(word_complexity_feature(tok_statements))
    results.append(sentence_complexity_feature(str_statements))
    results.append(influence_feature(tweets))
    results.append(role_feature(tweets))
    return results
