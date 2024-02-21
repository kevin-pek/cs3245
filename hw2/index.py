#!/usr/bin/python3
import re
import nltk
import sys
import getopt

import os
from nltk.corpus import reuters
from nltk.tokenize import word_tokenize
import pickle
import linecache

stemmer = nltk.PorterStemmer()

def generate_pairs(doc_id: str, document: str):
    """
    Gets list of tokens from raw document string and returns token docId pairs.
    Remove numbers from the document text.
    """
    tokens = word_tokenize(document)
    tokens = list(map(lambda x: stemmer.stem(x, to_lowercase=True), tokens))
    return [(token, doc_id) for token in tokens if not token.isdigit()]

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    documents = [filename for filename in os.listdir(in_dir)]
    # generate (token, docId) pairs
    pairs = []
    for i in range(10):# for doc_id in documents:
        doc_id = documents[i]
        # TODO: Add check for more memory
        pairs.extend(generate_pairs(doc_id, reuters.raw(in_dir + doc_id)))
    print(pairs)

    # hash the pairs
    index = {}
    for token, doc_id in pairs:
        postings = index.get(token, [])
        postings.append(doc_id)
        if token not in index:
            index[token] = postings
    print(index)

    with open(out_postings, 'wb') as f_postings, open(out_dict, 'wb') as f_dict:
        pickle.dump(index, f_postings)

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
