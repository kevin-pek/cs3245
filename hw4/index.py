#!/usr/bin/python3
import sys
import getopt
import os
import pickle
from utils.dictionary import ZoneIndex
from utils.preprocessing import get_terms, court_manipulation, extract_citations, extract_date, clean_content
from utils.file import read_pkl_csv, load_pkl

def usage():
    print("usage: " + sys.argv[0] + " -i dataset-csv-file -d dictionary-file -p postings-file")

def build_index(in_file, out_dict, out_postings):
    """
    build index from documents found in input file,
    then output the dictionary file and postings file
    """
    print('indexing...')

    # TODO: Remove this after done with pickle file
    file_path = 'data/documents.pkl'
    if os.path.exists(file_path):
        documents = load_pkl()
    else:
        documents = read_pkl_csv(in_file)
        
    if not os.path.exists('working'): # create a working dir if it doesnt exist
        os.makedirs('working')
    N = 0 # number of documents in the entire collection
    index = ZoneIndex()
    cit_dict = {} # Dictionary for citation

    for doc_id, doc_dict in documents.items():
        N += 1
        # get & process the data
        title, citations = extract_citations(doc_dict['title'], False)

        # process citation and date
        for citation in citations:  
            cit_dict[citation] = int(doc_id)
        year_posted, date_posted = extract_date(doc_dict['date_posted'], False)

        # process court
        court = doc_dict['court']
        if court == 'CA Supreme Court': # This is because supreme court of canada have some unidentified characters before the start of the actual judgment
            content = clean_content(content)
        court_id = court_manipulation().simplify_court(court)
        content = doc_dict['content']

        # get term frequency for each term in current document
        pos = 0 # counter for positional index of term
        for term in get_terms(content):
            index.add_term(term, pos)
            pos += 1
        index.add_year(year_posted)
        index.add_date(date_posted)
        index.add_court(court_id)
        for term in get_terms(title):
            index.add_title(term)

        index.calculate_weights(doc_id, court_id)

    index.save(out_dict, out_postings)
    with open(f"working/{out_dict}_cit", "wb") as ds:
        # compression not needed due to minimal memory usage
        pickle.dump(cit_dict, ds)

    with open(f"working/{out_dict}_len", "wb") as dl:
        # compression doesnt matter for this since its just a number
        pickle.dump(N, dl)


input_file = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_file = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_file == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_file, output_file_dictionary, output_file_postings)
