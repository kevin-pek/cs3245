#!/usr/bin/python3

import sys
import getopt
import pickle
from collections import defaultdict
from utils import get_terms, normalize_vector
import heapq

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    # Load dictionary and postings
    with open(dict_file, 'rb') as d, open(f"doclen_{dict_file}", 'rb') as n:
        dictionary = pickle.load(d)
        N = pickle.load(n)

    with open(queries_file, 'r') as queries, open(results_file, 'w') as results, open(postings_file, 'rb') as p:
        for query in queries:
            query_terms = get_terms(query)
            query_vector = normalize_vector(query_terms, dictionary, N)
            scores = defaultdict(float)
            for term, wq in query_vector.items():
                if term in dictionary:
                    offset = dictionary[term][1]
                    p.seek(offset)
                    postings = pickle.load(p)
                    for doc_id, wd in postings:
                        scores[doc_id] += wd * wq
            ranked_docs = heapq.nsmallest(10, scores.items(), key=lambda x: (-x[1], x[0]))
            ranked_doc_ids = [str(doc_id) for doc_id, _ in ranked_docs]
            results.write(" ".join(ranked_doc_ids) + "\n")

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
