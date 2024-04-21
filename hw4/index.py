#!/usr/bin/python3
import sys
import getopt
import os
import pickle
from hw4.utils.dictionary import ZoneIndex
from utils.preprocessing import get_terms, get_title_terms, simplify_court, clean_content
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

    N = 0 # number of documents in the entire collection
    index = ZoneIndex()

    for doc_id, doc_dict in documents.items():
        N += 1
        # get & process the data
        title = doc_dict['title']
        date_posted = doc_dict['date_posted'].split()[0]
        court = simplify_court(doc_dict['court'])
        content = doc_dict['content']
        case = title # extract case id from case

        if court == 'SCR': # This is because supreme court of canada have some unidentified characters before the start of the actual judgment
            content = clean_content(content)

        # get term frequency for each term in current document
        pos = 0 # counter for positional index of term
        for term in get_terms(content):
            index.add_term(term, pos)
            pos += 1
        index.add_date(date_posted)
        index.add_court(court)
        index.add_citation(case)
        for term in get_title_terms(title):
            index.add_title(term)

        index.calculate_weights(doc_id)

    index.save(out_dict, out_postings)

    with open(f"{out_dict}_len", "wb") as dl:
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
