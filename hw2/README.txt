This is the README file for A0234456A's submission
Email(s): e0726456@u.nus.edu

== Python Version ==

I'm using Python Version 3.10.13 for this assignment.

== General Notes about this assignment ==

The indexing phase of the program does the following:

1. Read all files from the given directory and generate the full list of (term-docID) pairs.
   This is done by tokenizing each word in a document, followed by stemming and case-folding.
   This step assumes that the filenames in directory are all numbered document ids, as done 
   in the Reuters dataset.
2. Run the SPIMI-Invert function with the generated pairs and a specified memory limit. This 
   function constructs an index by creating a Python dictionary that maps a term to its 
   postings list. Whenever the memory limit is exceeded, it will write the current index to
   disk by calling the write_block function.
3. The write_block function converts the posting set into a sorted list and stores the entry
   in the index as a tab separated pair between the term and its posting list. The posting 
   list is stored as a comma separated string.
3. Once all (term-docID) pairs have been processed, merge the different blocks together. 
   This is done by reading all of the block files and doing an n-way merge, where n is the 
   number of block files. This is done by using a minimum priority queue of size n, sorted
   in lexicographical order. If a duplicate term is encountered, we will merge the posting
   lists together before writing it to disk using pickle.
4. Once all the blocks have been written, the final dictionary will also be written to disk
   using pickle.

The search phase of the program does the following:

1. Load the dictionary from the dictionary file.
2. Open the query file, and for each line in the file, apply the shunting-yard algorithm
   to convert the query into postfix expression.
3. Evaluate the postfix expression by loading the term's postings list from the posting
   file, then applying the respective AND, OR or NOT operations.

During the evaluation of the postfix query, I employed a few strategies to speed up the
search process:
1. Delay the evaluation of NOT queries. Instead we wrap each operand in a class that
   stores whether it is a negated search term, using the boolean attribute is_neg.
   Delaying the evaluation of NOT queries also allows us to introduce a few more
   optimisations in the next step.
2. Use De Morgan's Law where applicable to maximise the number of AND queries, since we
   can use skip pointers to speed up the queries and avoid computing the universe posting
   list. This is done by applying it in the following cases:
   - NOT X AND NOT Y -> NOT (X OR  Y)
   - NOT X OR  NOT Y -> NOT (X AND Y)
   - NOT X OR  Y     -> NOT (X AND NOT Y) and vice versa
3. Introduce an AndHeap class to store sequential AND queries. This class contains a min
   heap that stores operands for the AND query, sorting them based on the term frequency.
   This will delay the evaluation of AND queries until it is necessary to do so.
   When this occurs, the operands in the AND heap are all evaluated in ascending order of
   their term frequency, and the result is pushed onto the results stack before subsequent
   operations are processed.
4. Do not load the universe set of postings until it is necessary. With the previous
   optimisations, this is left to the end of the evaluation, where if the term is
   a negative term, we will load the universe set to get the result.

== Files included with this submission ==

index.py         - Indexing phase
search.py        - Searching phase
linkedlist.py    - Implementation of LinkedList class and boolean operations
preprocessing.py - Text processing functions
spimi.py         - class for SPIMI functions used in indexing phase
utils.py         - Contains Index, Operand and AndHeap class for processing boolean queries

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