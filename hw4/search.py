#!/usr/bin/python3

import getopt
import sys
import pickle
from utils.boolean import process_boolean_term, intersect
from utils.compression import load_dict
from utils.preprocessing import get_terms
from utils.vector import normalise_vector
from utils.query import process_query, process_boolean_query
from utils.scoring import calculate_score, total_score

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    # Load dictionary and postings
    dictionary = load_dict(dict_file)
    print("Loaded Dictionary: ")

    with open(f"working/{dict_file}_cit", 'rb') as ds:
        citation_dict = pickle.load(ds)
    print("Loaded Citation Dictionary")

    with open(f"working/{dict_file}_len", 'rb') as n:
        N = pickle.load(n)
    print("Number of documents: ", N)

    with open(queries_file, 'r') as queries, open(results_file, 'w') as results, open(postings_file, 'rb') as p:
        for query in queries:
            terms, year, month_day, is_boolean, is_valid, citation = process_query(query)

            if not is_valid: # skip if query is invalid
                results.write('\n')
                continue

            # if query contains a citation that points directly to a case, add it straightaway
            cit_match = None
            if citation and citation in citation_dict:
                cit_match = citation_dict[citation]
                # print("CITATION MATCHES: ", cit_match)
            # if a year is specifically mentioned we filter cases by its presence
            year_matches = None
            if year in dictionary:
                year_matches = set(d[0] for d in process_boolean_term(dictionary, year, p, mask=0b00100))
                # print("YEAR MATCHES: ", year_matches)
            # same if month-day is specified
            date_matches = None
            if month_day in dictionary:
                date_matches = set(d[0] for d in process_boolean_term(dictionary, month_day, p, mask=0b01000))
                # print("DATE MATCHES: ", date_matches)

            if month_day in dictionary:
                date_matches = set(d[0] for d in process_boolean_term(dictionary, month_day, p, mask=0b01000))
                # print("DATE MATCHES: ", date_matches)

            if is_boolean:
                docs_scores = process_boolean_query(dictionary, terms, p, N)
                # print("DOCUMENTS: ", docs_scores)
                # compute scores
                    # ranked_doc_ids.append((score, doc_id))
                # scores = calculate_score(query_vector, dictionary, p, bool_result=docs)

            else: # is vector
                query_terms = get_terms(query)  # Extract terms from query
                query_vector = normalise_vector(query_terms, dictionary, N)
                # print("FREE TEXT: ", query_vector)
                docs_scores = calculate_score(query_vector, dictionary, p)
                # print("DOCUMENTS: ", docs_scores)

            scores = total_score(docs_scores, cit_match, year_matches, date_matches)
            results.write(' '.join(str(id) for id, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)))
            # heap = []
            # for doc_id, components_scores in scores.items():
            #     total_score = pagerank(components_scores)  # Score each component according to their weights
            #     heapq.heappush(heap, (total_score, doc_id))

            # Extract & sort heap
            # ranked_docs = heapq.nlargest(len(heap), heap)
            # ranked_doc_ids = [str(doc_id) for _, doc_id in ranked_docs]
            # results.write(" ".join(ranked_doc_ids) + "\n")


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
