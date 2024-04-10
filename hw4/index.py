#!/usr/bin/python3
import sys
import getopt
import os
import pickle
import math
import csv
import re
from collections import defaultdict
from utils.preprocessing import get_terms, simplify_court, clean_content
from utils.file import read_pkl_csv, load_pkl

def usage():
    print("usage: " + sys.argv[0] + " -i dataset-csv-file -d dictionary-file -p postings-file")

def build_index(in_file, out_dict, out_postings):
    """
    build index from documents found in input file,
    then output the dictionary file and postings file
    """
    print('indexing...')

    file_path = 'data/documents.pkl'
    if os.path.exists(file_path):
        documents = load_pkl()
    else:
        documents = read_pkl_csv(in_file)

    postings: dict[str, set[tuple[int, float, tuple[str, str, str]]]] = {} # map each term to set containing (doc_id, lnc) pairs
    N = 0

    for doc_id, doc_dict in documents.items():
        N += 1
        # get & process the data
        title = doc_dict['title']
        date_posted = doc_dict['date_posted'].split()[0]
        court = simplify_court(doc_dict['court'])
        content = doc_dict['content']

        if court == 'SCR':
            content = clean_content(content)

        # get list of terms from document content
        terms = get_terms(content)

        # get term frequency for each term in current document
        freq: dict[str, int] = defaultdict(int)
        for term in terms:
            freq[term] += 1

        # calculate lnc weights for each term in document
        term_freq = defaultdict(float)
        for term, tf in freq.items():
            term_freq[term] = 1 + math.log10(tf)
        norm = math.sqrt(sum([x ** 2 for x in term_freq.values()]))
        for term, w in term_freq.items():
            lnc = w / norm if norm != 0 else 0
            if term not in postings:
                postings[term] = set()
            postings[term].add((doc_id, lnc, (title, date_posted, court)))

    with open(f"doclen_{out_dict}", "wb") as dl:
        pickle.dump(N, dl)

    dictionary: dict[str, tuple[int, int]] = {} # dictionary mapping term to (df, offset)
    with open(out_postings, 'wb') as p: # save postings file
        for token in postings.keys():
            dictionary[token] = (len(postings[token]), p.tell())
            pickle.dump(sorted(postings[token]), p)

    with open(out_dict, 'wb') as d: # save dictionary file
        pickle.dump(dictionary, d)

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
