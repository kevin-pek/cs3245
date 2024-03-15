#!/bin/sh
python index.py -i ~/nltk_data/corpora/reuters/training/ -d dictionary.txt -p postings.txt
# python index.py -i test -d dictionary.txt -p postings.txt
# python search.py -d dictionary.txt -p postings.txt -q test.txt -o results.txt
python search.py -d dictionary.txt -p postings.txt -q sanity-queries.txt -o results.txt