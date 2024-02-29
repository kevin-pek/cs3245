#!/usr/bin/python3
import nltk
import sys
import getopt

import os
from nltk.downloader import shutil
from utils import process_document, process_document_remove_nums, process_document_remove_stopwords
from spimi import SPIMI
import time

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    print('indexing...')
    if in_dir[-1] != '/': # add trailing slash to dir if not present
        in_dir = in_dir + '/'

    blocks_path = 'blocks/'
    memory_limit = 500 * 1024 # set 0.5MB limit for index size
    os.makedirs(blocks_path, exist_ok=True) # make directory for blocks

    # generate token id pairs
    pairs = []
    start = time.time()
    for filename in os.listdir(in_dir):
        filepath = os.path.join(in_dir, filename)
        if not os.path.isfile(filepath):
            print(f'{filename} is not a file!')
            continue
        id = int(filename)
        file = open(filepath, 'r')
        document = file.read()
        pairs.extend(process_document_remove_stopwords(id, document))
        file.close()
    print(f'Pair generation: {time.time() - start}')
    spimi = SPIMI(blocks_path, memory_limit)
    start = time.time()
    spimi.invert(pairs)
    print(f'SPIMI-Invert: {time.time() - start}')
    start = time.time()
    spimi.merge_blocks(out_dict, out_postings)
    print(f'Merge Blocks: {time.time() - start}')
    shutil.rmtree(blocks_path) # cleanup intermediate block files

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
