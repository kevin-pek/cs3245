This is the README file for A0234456A's submission
Email(s): e0726456@u.nus.edu

== Python Version ==

I'm using Python Version 3.10.13 for this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

In index.py, the following steps were done during the creation of the index:
- Load every file in the directory that was provided. Since we are using the
  Reuters dataset, we use the filename of the document as the document ID of the
  document.
- Preprocessing of the document text is done by first putting it through the
  nltk sentence tokeniser, then using regex to remove the less than character
  that is represented using &lt; and to also replace hyphens and slashes with
  whitespaces. This is to make sure that "hyphenated-words" will be tokenised
  correctly, as well as words with slashes between them such as "March/April".
- Use the word tokeniser on the sentence. Every word in the tokeniser will have
  all of the non-alphanumeric characters trimmed, unless it is a number with
  decimals. The word is then stemmed using PorterStemmer, which will also handle
  case-folding to lower case.
- Add the processed terms to the index, which is implemented as a dictionary
  that keeps track of the frequency of the term within the document. We also
  create a separate dictionary that saves the number of terms found within each
  document so that we can normalise the results in search.py.

In search.py, we do the following:
- Use the get_terms function to split the query into its terms using the same
  steps done in the indexing phase.
- Compute the normalised tf-idf weights for each term in the query, using their
  respective formulas for tf and idf.
- Compute the cosine similarity between the query and each document in the
  posting list by adding the term-query weight multiplied by the term-document
  weight to the score of each document in the posting list.
- Normalise the scores for each document by dividing them by the number of terms
  in the respective document.
- Sort the documents to get the highest score followed by lexicographical order,
  and get the top 10 results.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py  - Indexing phase
search.py - Searching phase
utils.py  - contains the get_terms function to process a string document
  into a list of terms, and the normalise_vector function, which returns the
  normalised tf-idf vector based on the given query and dictionary.

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

https://www.rexegg.com/regex-quickstart.html - reference for regex used in index.py
