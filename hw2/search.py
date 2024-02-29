#!/usr/bin/python3
import sys
import getopt

import pickle

from linkedlist import LinkedList, intersect, union, complement
from utils import process_word
import time

class InvertedIndex:
    index: dict[str, tuple[int, int]]
    set: set[int]

    def __init__(self, dict_file, postings_file):
        self.universe = None
        f_dict = open(dict_file, 'rb')
        self.index = pickle.load(f_dict)
        f_dict.close()
        self.f_postings = open(postings_file, 'rb')

    def get_universe(self):
        print('retrieving universe...')
        start = time.time()
        self.universe = set()
        for _, offset in self.index.values():
            self.f_postings.seek(offset)
            for id in pickle.load(self.f_postings):
                self.universe.add(id)
        print(f'Universe construction took {time.time() - start}')
        print(f'got universe of size {len(self.universe)}')

    def read_postings(self, term: str) -> LinkedList | None:
        if term not in self.index:
            return None
        _, offset = self.index[term]
        self.f_postings.seek(offset)
        postings = LinkedList.from_list(pickle.load(self.f_postings))
        postings.add_skip_pointers()
        return postings

class Operand:
    def __init__(self, term=None, is_neg=False, postings=None):
        self.term = term
        self.is_neg = is_neg
        self.postings = postings

    def evaluate(self, universe):
        if self.is_neg:
            return complement(self.postings, universe)
        return self.postings


def shunting_yard(query: str) -> list[str]:
    prec = { 'OR': 1, 'AND': 2, 'NOT': 3 }
    ops = []
    queue = []
    for c in query.split(' '):
        if c[0] == '(':
            ops.append(c[0]) # separate open parenthesis from search term
            queue.append(process_word(c[1:]))
        elif c[-1] == ')':
            queue.append(process_word(c[:-1])) # separate close parenthesis from search term
            token = ops.pop()
            while token != '(': # apply all operations within parentheses
                queue.append(token)
                token = ops.pop()
        elif c in prec: # if term is an operation
            while ops and prec.get(ops[-1], 0) >= prec[c]:
                queue.append(ops.pop())
            ops.append(c)
        else:
            term = process_word(c)
            if not term:
                print(f'Invalid term given: {c}')
                return None
            queue.append(term)
    while ops:
        queue.append(ops.pop())
    return queue

def evaluate(postfix: list[str], index: InvertedIndex) -> LinkedList | None:
    ops = { 'OR', 'AND', 'NOT' }
    results = [] # store intermediate results in a stack
    for token in postfix:
        if token in ops:
            result = None
            if token == 'AND':
                op1 = results.pop()
                op2 = results.pop()
                p1 = op1 if isinstance(op1, LinkedList) else index.read_postings(op1)
                p2 = op2 if isinstance(op2, LinkedList) else index.read_postings(op2)
                result = intersect(p1, p2)
            elif token == 'OR':
                op1 = results.pop()
                op2 = results.pop()
                p1 = op1 if isinstance(op1, LinkedList) else index.read_postings(op1)
                p2 = op2 if isinstance(op2, LinkedList) else index.read_postings(op2)
                result = union(p1, p2)
            else: # NOT operations
                op = results.pop()
                if not index.universe: # if there is no current result, we need to get the universe
                    index.get_universe()
                postings = op if isinstance(op, LinkedList) else index.read_postings(op)
                result = complement(postings, index.universe)
            results.append(result)
        else:
            results.append(token)
    if len(results) != 1: # final result must be single entry otherwise invalid query
        print(f'Invalid query processed, got final result {results}')
        return None
    res = results.pop()
    return index.read_postings(res) if isinstance(res, str) else res

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    print('running search on the queries...')
    f_results = open(results_file, 'w')
    f_query = open(queries_file, 'r')
    index = InvertedIndex(dict_file, postings_file)
    start = time.time()
    query = f_query.readline()
    while query:
        # print(f'Query: {query.strip()}')
        postfix = shunting_yard(query.strip())
        # print(f'Postfix: {postfix}')
        result = evaluate(postfix, index)
        # print(f'Result: {result}')
        if result:
            f_results.write(' '.join(map(str, result.to_list())))
        query = f_query.readline()
        if query: # if there is still a next line, add a newline char
            f_results.write('\n')
    print(f'Total evaluation time: {time.time() - start}')
    f_results.close()
    index.f_postings.close()
    f_query.close()

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
