import nltk

grammar1 = nltk.CFG.fromstring("""
  S -> NP VP
  VP -> V NP | V NP PP | V S
  PP -> P NP
  V -> "saw" | "ate" | "walked"
  NP -> "John" | "Mary" | "Bob" | Det N | Det N PP
  Det -> "a" | "an" | "the" | "my"
  N -> "man" | "dog" | "cat" | "telescope" | "park"
  P -> "in" | "on" | "by" | "with"
  """)

sentence = 'John saw the cat walked the dog'.split()

sent = "Mary saw Bob".split()
rd_parser = nltk.RecursiveDescentParser(grammar1)
for tree in rd_parser.parse(sent):
    print(tree)

for tree in rd_parser.parse(sentence):
    print(tree)

sentence = "John saw that the cat walked the dog. He is cool"
tokens = nltk.word_tokenize(sentence)
tagged = nltk.pos_tag(tokens)
print(nltk.chunk.ne_chunk(tagged))
print(nltk.sent_tokenize(sentence))