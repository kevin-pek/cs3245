#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
from typing import Dict
import sys
import getopt
import math
import string
import nltk

nltk.download('punkt')

n = 4 # 4-gram LM based on question
pad = '@' # character for padding
# padding for start and end, so we have "@@@words in the file@@@" for n = 4
padding = ''.join([pad for _ in range(n - 1)])

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print("building language models...")
    model: Dict[str, Dict[str, float]] = {} # keep track of counts for each language
    vocab = set() # keep track of every unique token we have encountered
    with open(in_file, "r") as file:
        for line in file:
            words = re.sub(r'\d+\s*|[' + string.punctuation + ']', '', line) # remove numbers and subsequent whitespaces
            words = nltk.word_tokenize(words)
            label = words[0]
            if label not in model: # init list for language if it is new
                model[label] = {}
            words = ' '.join(words[1:])
            chars = padding + words + padding
            for i in range(len(chars) - n + 1): # no padded ngrams
                ngram = chars[i:i + n]
                vocab.add(ngram)
                if ngram not in model[label]:
                    model[label][ngram] = 0
                model[label][ngram] += 1
    # implement add one smoothing for all existing models
    for lang_model in model.values():
        for ngram in vocab:
            if ngram not in lang_model:
                lang_model[ngram] = 0
            lang_model[ngram] += 1
    return model

def test_LM(in_file, out_file, LM: Dict[str, Dict[str, float]]):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")
    labels = []
    with open(in_file, "r") as file:
        for line in file:
            words = re.sub(r'\d+\s*|[' + string.punctuation + ']', '', line) # remove numbers and subsequent whitespaces
            words = nltk.word_tokenize(words)
            chars = padding + ' '.join(words) + padding
            max_score = -math.inf # default values for max likelihood score, will be overriden
            max_lang = "none"

            # get the score for each language by adding up the ngram counts
            for lang, lang_model in LM.items():
                n_aliens = 0 # keep track of the number of unknown tokens
                total_grams = 0
                score = 0
                for i in range(len(chars) - n + 1):
                    ngram = chars[i:i + n]
                    total_grams += 1
                    if ngram not in lang_model: # skip if ngram is alien
                        n_aliens += 1
                        continue
                    score += math.log(lang_model[ngram] / sum(lang_model.values()))
                if n_aliens / total_grams >= 0.75: # set threshold for other category
                    max_lang = 'other'
                    break
                # update max score language
                if score > max_score:
                    max_score = score
                    max_lang = lang
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
