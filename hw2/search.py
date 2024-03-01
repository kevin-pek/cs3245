#!/usr/bin/python3
import sys
import getopt

from linkedlist import LinkedList, intersect, union, difference
from preprocessing import process_word
from utils import InvertedIndex, AndHeap, Operand
import time

def evaluate(postfix: list[str], index: InvertedIndex) -> LinkedList | None:
    results = [] # store intermediate results in a stack
    for token in postfix:
        op = None
        if token == 'AND':
            op1 = results.pop()
            op2 = results.pop()
            if isinstance(op1, AndHeap) and isinstance(op2, AndHeap):
                op = AndHeap()
                op.add(op1.evaluate(index), index)
                op.add(op2.evaluate(index), index)
            elif isinstance(op1, AndHeap):
                op1.add(op2, index)
                op = op1
            elif isinstance(op2, AndHeap):
                op2.add(op1, index)
                op = op2
            else: # otherwise we must evaluate the current heap and add its result
                op = AndHeap()
                op.add(op1, index)
                op.add(op2, index)
        elif token == 'OR':
            op1 = results.pop()
            op2 = results.pop()
            if isinstance(op1, AndHeap):
                op1 = op1.evaluate(index)
            if isinstance(op2, AndHeap):
                op2 = op2.evaluate(index)

            postings = None
            if op1.is_neg or op2.is_neg: # apply De Morgan's Law if negative term is present
                op1.is_neg = not op1.is_neg
                op2.is_neg = not op2.is_neg

            if op1.is_neg and op2.is_neg: # NOT X OR NOT Y -> NOT (X AND Y)
                postings = intersect(op1.get_postings(index), op2.get_postings(index))
            elif op1.is_neg: # NOT X OR Y -> NOT (X AND NOT Y)
                postings = difference(op1.get_postings(index), op2.get_postings(index))
            elif op2.is_neg: # X OR NOT Y -> NOT (NOT X AND Y)
                postings = difference(op2.get_postings(index), op1.get_postings(index))
            else:
                postings = union(op1.get_postings(index), op2.get_postings(index))
            op = Operand(is_neg=op1.is_neg or op2.is_neg, postings=postings)
        elif token == 'NOT':
            op = results.pop()
            op.is_neg = not op.is_neg
        else:
            op = Operand(term=token)
        results.append(op)
        print(f'{token}: STACK {results}')
    if len(results) != 1: # final result must be single entry otherwise invalid query
        print(f'Invalid query processed, got final result {results}\n')
        return None
    res = results.pop()
    if isinstance(res, AndHeap):
        res = res.evaluate(index)
    if res:
        if res.is_neg: # if final result has a NOT term, we will need to compute the universe
            postings = res.get_postings(index)
            # print(f'Result posting: {postings}')
            res = difference(postings, index.get_universe())
        else:
            res = res.get_postings(index)
    print(f'Query Result: {res}\n')
    return res

def shunting_yard(query: str) -> list[str]:
    prec = { 'OR': 1, 'AND': 2, 'NOT': 3 }
    ops = []
    queue = []
    for c in query.split(' '):
        if c[0] == '(':
            ops.append(c[0]) # separate open parenthesis from search term
            token = c[1:]
            if token in prec: # NOT query encountered
                ops.append(token)
            else:
                queue.append(process_word(token))
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
        print(query.strip())
        postfix = shunting_yard(query.strip())
        print(postfix)
        result = evaluate(postfix, index)
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
