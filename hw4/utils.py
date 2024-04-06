import re
import csv
from nltk import sent_tokenize, word_tokenize, PorterStemmer
import math
from collections import defaultdict

stemmer = PorterStemmer()

def get_terms(document: str):
    terms = []
    for sentence in sent_tokenize(document):
        sentence = re.sub(r'&lt;', '', sentence) # remove less than character &lt;
        sentence = re.sub(r'[-/]', ' ', sentence) # split word based on hyphens and slashes
        for word in word_tokenize(sentence):
            # remove non alphanumeric character, but keep periods that are found
            # between 2 numbers as they are likely part of a decimal number
            word = re.sub(r'(?<!\d)\.(?!\d)|[^\w\d.]', '', word)
            if word:
                terms.append(stemmer.stem(word, to_lowercase=True))
    return terms

def normalize_vector(query, dictionary, N):
    tf_idf = defaultdict(float)
    for term in query:
        if term in dictionary:
            df = dictionary[term][0]
            idf = math.log(N / df, 10) if df != 0 and N != 0 else 0
            tf = 1 + math.log(query.count(term), 10)
            tf_idf[term] = tf * idf
    
    norm = math.sqrt(sum([x ** 2 for x in tf_idf.values()]))
    if norm == 0:
        return tf_idf
    return {term: weight / norm for term, weight in tf_idf.items()}

def read_csv(file_path):
    documents = {}
    max_len = 2**31 - 1 # max len for c-long
    csv.field_size_limit(max_len) # bypass field limit for csv.DictReader
    with open(file_path, mode='r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            court = row['court']
            date_posted = row['date_posted']
            content = re.sub(r'\W+', ' ', row['content']).lower()
            documents[row['document_id']] = {'court': court, 'date_posted': date_posted, 'content': content}
    return documents