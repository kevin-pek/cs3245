#!/usr/bin/python3
import sys
import getopt
import os
import pickle
import math
from collections import defaultdict
from utils import get_terms, read_csv

def usage():
    print("usage: " + sys.argv[0] + " -i dataset-csv-file -d dictionary-file -p postings-file")

def build_index(in_file, out_dict, out_postings):
    """
    build index from documents found in input file,
    then output the dictionary file and postings file
    """
    print('indexing...')

    documents = read_csv(in_file)

    postings: dict[str, set[tuple[str, float]]] = {} # map each term to set containing (doc_id, lnc) pairs
    N = 0

    for filename in os.listdir(in_file):
        filepath = os.path.join(in_file, filename)

        if not os.path.isfile(filepath): # handle case where item is not a file
            print(f'{filename} is not a file!')
            continue

        doc_id = filename
        N += 1

        with open(filepath, 'r') as file: # get list of terms from document
            terms = get_terms(file.read())

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
            postings[term].add((doc_id, lnc))

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
