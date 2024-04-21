#!/usr/bin/python3

import getopt
import sys
import pickle
from collections import defaultdict
import heapq

from utils.preprocessing import get_terms
from utils.vector import normalise_vector
from utils.query import process_query
from utils.scoring import calculate_score

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def run_search(dict_file, postings_file, queries_file, results_file, k=10, tfidf_threshold=0.1):
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
            terms, is_boolean, is_valid = process_query(query)
            if not is_valid: # skip if query is invalid
                results.write('\n')
                continue
            # TODO: Handle boolean retrieval and vector based retrieval logic separately
            query_terms = get_terms(query)
            query_vector = normalise_vector(query_terms, dictionary, N)
            scores = defaultdict(lambda: defaultdict(float))
            for term, wq in query_vector.items():
                if term in dictionary and wq >= tfidf_threshold:  # Apply TF-IDF thresholding
                    offset = dictionary[term][1]
                    p.seek(offset)
                    postings = pickle.load(p)
                    for doc_id, w_c, w_t, fields, position_idx in postings:
                        scores[doc_id]['content'] += w_c * wq
                        scores[doc_id]['title'] += w_t * wq

                        # TODO: handle fields & positional index
                        scores[doc_id]['citation'] = None
                        scores[doc_id]['date'] = None
                        scores[doc_id]['court'] = None


            min_heap = []
            # early push to heap if heap is not full
            for doc_id, components_scores in scores.items():
                total_score = calculate_score(components_scores)  # Score each component according to their weights
                if len(min_heap) < k:
                    heapq.heappush(min_heap, (total_score, doc_id))
                else:
                    # Only push to heap if score is greater than the smallest score in the heap
                    if total_score > min_heap[0][0]:
                        heapq.heappushpop(min_heap, (total_score, doc_id))

            # Extract top-K results from the heap
            ranked_docs = heapq.nlargest(k, min_heap)
            ranked_doc_ids = [str(doc_id) for _, doc_id in ranked_docs]
            results.write(" ".join(ranked_doc_ids) + "\n")


dictionary_file = postings_file = file_of_queries = file_of_output = None

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
