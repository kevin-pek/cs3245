from collections import defaultdict
import math

"""
Functions to handle freetext search queries using the vector space model.
"""

def normalise_vector(query, dictionary, N):
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

