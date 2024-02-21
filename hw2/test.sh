#!/bin/sh
# source venv/bin/activate
python index.py -i /Users/kevin/nltk_data/corpora/reuters/training/ -d dictionary.txt -p postings.txt
# python search.py -d dictionary.txt -p postings.txt -q sanity-queries.txt -o results.txt
