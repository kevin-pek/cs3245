This is the README file for A0234456A's submission
Email(s): e0726456@u.nus.edu

== Python Version ==

I'm using Python Version 3.10.13 for
this assignment.

== General Notes about this assignment ==

The indexing phaae of the program does the following:

1. Read all files from the given directory and generate the full list of (term-docID) pairs.
   This is done by tokenizing each word in a document, followed by stemming and case-folding.
   This step assumes that the filenames in directory are all numbered document ids, as done 
   in the Reuters dataset.
2. Run the SPIMI-Invert function with the generated pairs and a specified memory limit. This 
   function constructs an index by creating a Python dictionary that maps a term to its 
   postings list. The posting list is implemented as a set in this step, since we are only 
   concerned with ensuring uniqueness of each posting. This allows efficient insertion and 
   membership checking of all terms in each document. Whenever the memory limit is exceeded,
   it will write the current index to disk by calling the write_block function.
3. The write_block function converts the posting set into a sorted list and stores the entry
   in the index as a tab separated pair between the term and its posting list. The posting 
   list is stored as a comma separated string.
3. Once all (term-docID) pairs have been processed, merge the different blocks together. 
   This is done by reading all of the block files and doing an n-way merge, where n is the 
   number of block files. This is done by using a minimum priority queue of size n, sorted
   in lexicographical order. If a duplicate term is encountered, we will merge the posting
   lists together.
4. The final dictionary and postings are written to their respective files using pickle.

The search phase of the program does the following:

1. Load the dictionary from the dictionary file.
2. Open the query file, and for each line in the file, apply the shunting-yard algorithm
   to convert the query into postfix expression.
3. Evaluate the postfix expression by loading the term's postings list from the posting
   file, then applying the respective AND, OR or NOT operations. To speed up NOT queries,
   the universe of postings are loaded into a set before all queries are processed. This
   allows for O(1) removal from the universe set when trying to get the result from a NOT
   query.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0234456A, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

== References ==

https://www.nltk.org/howto/corpus.html - reference for how to load reuters dataset
https://www.nltk.org/howto/stem.html - reference for stemmer usage
https://www.nltk.org/howto/tokenize.html - reference for tokenizer usage
https://en.wikipedia.org/wiki/Shunting_yard_algorithm - reference for shunting-yard