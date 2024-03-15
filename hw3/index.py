#!/usr/bin/python3
import sys
import getopt

import os
import pickle

from preprocessing import get_terms

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    if in_dir[-1] != '/': # add trailing slash to dir if not present
        in_dir = in_dir + '/'

    postings: dict[str, set[tuple[int, int]]] = {} # map each term to set containing (doc_id, tf) pairs
    doc_lengths: dict[int, int] = {} # map each document id to its length

    for filename in os.listdir(in_dir):
        filepath = os.path.join(in_dir, filename)

        if not os.path.isfile(filepath): # handle case where item is not a file
            print(f'{filename} is not a file!')
            continue

        try: # handle case where document name cannot be cast to integer
            id = int(filename)
        except:
            print(f'{filename} cannot be cast as integer, skipping file!')
            continue

        with open(filepath, 'r') as file: # get list of terms from document
            terms = get_terms(file.read())

        doc_lengths[id] = len(terms)  # store document length for normalising search results later
        freq: dict[str, int] = {}
        for term in terms: # get term frequency for each term in current document
            if term not in freq:
                freq[term] = 0
            freq[term] += 1

        for term in terms: # add term frequencies into global postings list
            if term not in postings:
                postings[term] = set()
            pair = (id, freq[term])
            postings[term].add(pair)

    with open(out_postings, 'wb') as p: # save postings file
        dictionary: dict[str, tuple[int, int]] = {}
        for token in postings.keys():
            dictionary[token] = (len(postings[token]), p.tell())
            pickle.dump(sorted(postings[token]), p)

    with open(out_dict, 'wb') as d: # save dictionary file
        pickle.dump(dictionary, d)

    with open(f"doclen_{out_dict}", 'wb') as dlen: # save document length file
        pickle.dump(doc_lengths, dlen)

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
