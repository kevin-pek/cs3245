#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
from typing import Dict, List, Tuple
import nltk
import sys
import getopt

nltk.download("punkt")
nltk.download("stopwords")

n = 4 # 4-gram LM based on question

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print("building language models...")
    model: Dict[str, Dict[Tuple, float]] = {} # keep track of counts for each language
    vocab = set() # keep track of every unique token we have encountered
    with open(in_file, "r") as file:
        for line in file:
            words = nltk.word_tokenize(line.lower())
            label = words[0]
            if label not in model: # init list for language if it is new
                model[label] = {}
            words = words[1:]
            chars = ''.join(words)
            for i in range(len(chars) - n): # no padded ngrams
                ngram = tuple(chars[i:i + n])
                vocab.add(ngram)
                if ngram not in model[label]:
                    model[label][ngram] = 0
                model[label][ngram] += 1
    for lang_model in model.values():
        for ngram in vocab:
            if ngram not in lang_model:
                lang_model[ngram] = 0
            lang_model[ngram] += 1 # add one smoothing
            lang_model[ngram] = lang_model[ngram] / len(vocab) # normalise
    return model

def test_LM(in_file, out_file, LM: Dict[str, Dict[Tuple, float]]):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")
    labels = []
    with open(in_file, "r") as file:
        for line in file:
            words = nltk.word_tokenize(line.lower())
            chars = ''.join(words)
            max_score = -1
            max_lang = "None"
            for lang, lang_model in LM.items():
                # compute probability score for each language
                score = 1
                for i in range(len(chars) - n): # no padded ngrams
                    ngram = tuple(chars[i:i + n])
                    score *= lang_model.get(ngram, 0) # put 0 if ngram not present
                if score > max_score:
                    max_score = score
                    max_lang = lang
                    print(max_lang, max_score)
            labels.append(max_lang)
    with open(out_file, "w") as file:
        file.write('\n'.join(labels))

def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"
    )


input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], "b:t:o:")
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == "-b":
        input_file_b = a
    elif o == "-t":
        input_file_t = a
    elif o == "-o":
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
