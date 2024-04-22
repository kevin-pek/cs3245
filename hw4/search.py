#!/usr/bin/python3

import getopt
from io import BufferedReader
import sys
import pickle
from collections import defaultdict
import heapq
from utils.boolean import process_boolean_term, process_phrase_query, intersect
from utils.compression import gap_decode, load_dict, vb_decode
from utils.preprocessing import get_terms
from utils.vector import normalise_vector
from utils.query import process_query
from utils.scoring import calculate_score

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def process_boolean_query(dictionary, terms, p: BufferedReader):
    pass

def run_search(dict_file, postings_file, queries_file, results_file, k=10, tfidf_threshold=0.1):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    # Load dictionary and postings
    dictionary = load_dict(dict_file)
    print("Loaded Dictionary: ", dictionary)

    with open(f"working/{dict_file}_cit", 'rb') as ds:
        citation_dict = pickle.load(ds)
    print("Loaded Citation Dictionary")

    with open(f"working/{dict_file}_len", 'rb') as n:
        N = pickle.load(n)
    print("Number of documents: ", N)

    with open(queries_file, 'r') as queries, open(results_file, 'w') as results, open(postings_file, 'rb') as p:
        for query in queries:
            terms, year, month_day, is_boolean, is_valid, citation = process_query(query)
            if citation:
                results.write(str(citation_dict[citation]) + ' ')
            if not is_valid: # skip if query is invalid
                results.write('\n')
                continue
            if year:
                if month_day:
                    pass #TODO handle date retrieval with month and day
                else:
                    pass #TODO handle date retrieval with only year
                
            # TODO: Handle boolean retrieval and vector based retrieval logic separately
            if is_boolean:
                processed_terms = [] # we initialise a heap to intersect in order of lowest df
                for term in terms:
                    if isinstance(term, list): # phrase query
                        df_max = 0 # for phrase queries we use the term with lowest df
                        for t in [process_term(t) for t in term]:
                            df = dictionary[t][0]
                            if df == 0: # if a phrase query term doesnt appear treat it as 0
                                df_max = 0
                                break
                            df_max = max(df_max, df)
                        if df_max == 0: # stop query processing if it does not even exist in dictionary
                            processed_terms = []
                            break
                        processed_terms.append((df_max, term))
                    else:
                        term = process_term(term)
                        if term in dictionary:
                            processed_terms.append((dictionary[term][0], term))
                        else:
                            processed_terms = []
                            break

                if not processed_terms: # if we have no processed terms means no result
                    results.write('\n')
                    continue

                # initialise results with the first item in processed term
                processed_terms.sort()
                term = processed_terms[0]
                if isinstance(term, list):
                    docs = process_phrase_query(dictionary, term, p)
                else:
                    docs = process_boolean_term(dictionary, term, p)

                # do intersection in order of term document frequency
                for df, term in processed_terms[1:]:
                    if isinstance(term, list): # phrase query
                        docs = intersect(docs, process_phrase_query(dictionary, term, p))
                    else:
                        docs = intersect(docs, process_boolean_term(dictionary, term, p))

                results.write(' '.join(docs) + '\n')
            else:
                query_terms = get_terms(query)
                query_vector = normalise_vector(query_terms, dictionary, N)
                scores = defaultdict(lambda: defaultdict(float))
                for term, wq in query_vector.items():
                    if term in dictionary and wq >= tfidf_threshold:  # Apply TF-IDF thresholding
                        offset = dictionary[term][1]
                        p.seek(offset)
                        postings = pickle.load(p)
                        doc_id = 0 # accumulator for doc_id since it is stored using gap encoding
                        # NOTE: Similar process needs to be done for interpreting postional index
                        #       When handling phrase queries if we are dealing with boolean queries
                        #       By passing it through gap_decode(vb_decode(position_idx))
                        for enc_doc_id, w_c, w_t, fields, position_idx in postings:
                            gap_doc_id = vb_decode(enc_doc_id)[0] # decode and add gap value to document id
                            print("Document ID Gap: ", gap_doc_id)
                            doc_id += gap_doc_id
                            print("Loaded Postings: ", (doc_id, w_c, w_t, fields, gap_decode(vb_decode(position_idx))))
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
