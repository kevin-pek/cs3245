import re
from nltk import sent_tokenize, word_tokenize, PorterStemmer
import math
from collections import defaultdict

stemmer = PorterStemmer()

def get_terms(document: str):
    terms = []
    for sentence in sent_tokenize(document):
        sentence = re.sub(r'[-/]', ' ', sentence) # split word based on hyphens and slashes
        for word in word_tokenize(sentence):
            word = re.sub(r'(?<![.\d])\.(?![.\d])|[^\w\d.]', '', word) # remove every non alphanumeric character
            if word: # if removing puntuaction does not remove the whole word we continue
                terms.append(stemmer.stem(word).lower())
    return terms

def normalize_vector(query, dictionary, N):
    tf_idf = defaultdict(float)
    for term in query:
        if term in dictionary:
            df = dictionary[term][0]
            
            idf = math.log(N/df, 10)
            tf = 1 + math.log(query.count(term), 10)
            tf_idf[term] = tf * idf
    
    norm = math.sqrt(sum([x ** 2 for x in tf_idf.values()]))
    if norm == 0:
        return tf_idf
    return {term: weight / norm for term, weight in tf_idf.items()}