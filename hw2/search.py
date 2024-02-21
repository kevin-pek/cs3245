#!/usr/bin/python3
import re
import nltk
import sys
import getopt

import pickle

def linear_merge(d1, d2, index):
    p1 = index[d1]
    p2 = index[d2]

def parse_queries(query: str):
    # shunting-yard algorithm
    def apply_op(op, second, first):
        if op == 'AND': linear_merge(first, second)
        if op == 'OR': pass
        if op == 'NOT': pass

    prec = { 'AND': 2, 'OR': 2, 'NOT': 1 }
    ops = []
    terms = []
    for c in query.split(' '):
        if c[0] == '(':
            terms.append(c[0]) # separate open parenthesis from search term
            terms.append(c[1:])
        elif c[-1] == ')':
            terms.append(c[:-1]) # separate close parenthesis from search term
            while terms[-1] != '(': # apply all operations within parentheses
                apply_op(ops.pop(), terms.pop(), terms.pop())
        elif c in prec: # if term is an operation
            if prec[ops[-1]] <= prec[c]:
                apply_op(ops[-1], terms.pop(), terms.pop())
            ops.append(c)
        else:
            terms.append(c)

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    token_dict = pickle.load(dict_file)
    print(token_dict)
    index = pickle.load(postings_file)
    print(index)
    with open(queries_file, 'r') as query_file:
        queries = query_file.readlines()
    for query in queries:
        parse_queries(query)

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

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
