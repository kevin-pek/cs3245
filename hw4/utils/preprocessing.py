import re
from nltk import sent_tokenize, word_tokenize, PorterStemmer

"""
Functions to preprocess dataset and extract information from text to help with
index construction and query handling.
"""

stemmer = PorterStemmer()

def get_terms(document: str):
    terms = []
    for sentence in sent_tokenize(document):
        sentence = re.sub(r'[-/]', ' ', sentence) # split word based on hyphens and slashes
        for word in word_tokenize(sentence):
            # remove non alphanumeric character, but keep periods that are found
            # between 2 numbers as they are likely part of a decimal number
            word = re.sub(r'(?<!\d)\.(?!\d)|[^\w\d.]', '', word)
            if word:
                terms.append(stemmer.stem(word, to_lowercase=True))
    return terms

