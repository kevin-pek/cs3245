This is the README file for A0234456A-A0290349X submission
Email(s): e0726456@u.nus.edu, e1324842@u.nus.edu

== Python Version ==

We're using Python Version 3.10.12 for this assignment.

== General Notes about this assignment ==

In the indexing phase, we construct the inverted index and posting list based
on the vector space model. However we also include positional indices to allow
for phrase queries, and also build zone and field indexes for case specific
information.

INVERTED INDEX

- Index maps terms to gap encoded posting list, with each posting being
  represented by a tuple with the following data in sequence:
   - variable & gap encoded doc_id
   - tf-idf content weight w lnc weighing
   - tf-idf title weight w lnc weighing
   - fields byte representing presence of term in each zone/field of document
   - gap & variable encoded positional list for term occurrences within document

- Fields is a byte indicating zones/fields, title, citation, date, court, content
    00001 - term appears in contents zone of the document
    00010 - term appears in court field
    00100 - term appears in date field
    01000 - term appears in citation field
    10000 - term appears in title zone
  Note that a term can be present in multiple zones/fields at once so the fields
  bit can have multiple 1s.


In the searching phase, we first validate and determine the type of query that
is given. If it is an invalid query we immediately skip the query. Boolean
queries and freetext queries are handled separately.

We first use regex to detect the presence of dates, years and citations within
the search query. The presence of these will allow us to greatly narrow our
search to specific years, dates or citations using specific fields.

For years, dates, and courts, we use their corresponding fields to match the
detected terms. For citations, we use the auxiliary index to map the case
citation to the corresponding documents.

BOOLEAN QUERIES:
- Our approach for boolean queries is to handle terms in order of increasing
  document frequency. Phrase queries are sorted based on the largest document
  frequency within the phrase, since that would be the performance bottleneck
  during the searching process.
- We stop searching and return nothing if there are no matches given for a term.
- When a boolean query is given we will begin with handling any phrase queries
  as we expect them to yield a lesser number of results. Results are retrieved
  through the positional index of the terms. At the same time we maintain a set
  that keeps track of terms we have already retrieved.

FREETEXT QUERIES:
- Our approach for freetext queries uses a vector space model using TF-IDF for 
  ranking the documents based on their cosine similarity to the query vector. 
- We first weigh the TF-IDF weight of each term in the query, then we normalise 
  the query vector and compute the TF-IDF scores of the title and content of each
  document. We also award more scores if the document contains any citation, date,
  or year from the query, and award more scores if it comes from a more important 
  court as well.

QUERY REFINEMENT:
- Query refinement in our system is designed to enhance the effectiveness and 
  relevance of the search results by modifying the original query based on additional 
  insights derived from initial results or through semantic expansion techniques. 
- We implemented query expansion using the wordnet module from NLTK. This method 
  broadens the query to include semantically related terms like synonyms, hypernyms, 
  and hyponyms. It captures a wider array of relevant documents that might not have 
  been retrieved otherwise.
- We also implemented relevance feedback by taking the top-k most frequent terms of
  the top-k documents with the highest scores. The system refines the query based on 
  simulated user feedback from initial results. The system adds key terms from these 
  top-k documents to the query to enhance the query.


== Files included with this submission ==

index.py          - indexing phase
utils.py          - contains get_terms function to process string to list of terms,
                  process_terms function to convert list of terms to processed form,
                  normalize_vector to do cosine normalisation for tf-idf vectors
search.py         - searching phase
query.py          - contains process_query function to handle processing of queries

utils/preprocessing.py  - contains convert_pos function to map part-of-speech tags from NLTK to WordNet compatible tags for lemmatization.
                  process_term function to clean, lemmatize, and filter words based on custom and NLTK stop words.
                  get_terms function to tokenize, tag, and process text into terms for indexing.
                  court_manipulation class which manages court information and extraction from text using a predefined dictionary of court names and abbreviations.
                  clean_content function to truncate a text starting from a specific keyword.
                  extract_citations function to identify and extract legal citation patterns from case titles.
                  test_extract_citations function for testing the accuracy of the citation extraction logic.
                  extract_date function to detect and parse date patterns in queries or documents.
utils/dictionary.py     - contains the ZoneIndex class, which contains add_term function to add a term along with its position to the index, updating frequency and field information.
                  add_court function to register a court's presence and updates its corresponding field bit.
                  add_year function to add a year as a term, updating its frequency and field information.
                  add_date function to add a date as a term, similarly updating frequency and field information.
                  add_title function to add terms specifically from titles, updating both their general and title-specific frequencies, as well as field information.
                  calculate_weights function to compute the tf-idf weights for terms in a document, constructs the postings list including top-k terms, and manages normalization.
                  save function to compress and save the postings list and term dictionary to disk using various encoding techniques.
utils/compression.py    - contains gap_encode function to convert a sorted list of integers into their respective gaps.
                  vb_encode function to encode an integer into a byte array using variable byte encoding.
                  vb_decode function to decode a byte array back into a list of integers using variable byte encoding.
                  gap_decode function to convert a list of gap-encoded integers back into the original list of integers.
                  compress_and_save_dict function to compress and save a dictionary of terms using frontcoding and pickle serialization.
                  load_dict function to load and decode a compressed dictionary from disk using frontcoding and pickle deserialization.
                  TestPostingCompression class for unittests that verify the functionality of gap encoding/decoding and variable byte encoding/decoding, including combined operations.
                  TestDictionaryCompression class for unittests that verify the functionality of compressing and loading dictionaries, ensuring the integrity of saved and retrieved data.
utils/query.py          - contains process_query function to parse and process the input query, determining if it's a boolean or free text query and validating its structure.
                  process_boolean_query function to process boolean queries, handling term intersection and phrase queries using a document frequency-based approach.
                  query_expansion function to perform query expansion using WordNet synsets, hypernyms, and hyponyms to enrich the query with semantically similar terms.
                  TestProcessQuery class, a unittest.TestCase subclass, providing various test cases for validating the process_query function.
utils/scoring.py        - contains get_court_w function which retrieves a weight for a court ID from a predefined dictionary, 
                  calculate_score function which calculates document scores using a query vector, term dictionary, and a file pointer for postings,
                  total_score function which computes final scores for documents, adjusts for matches, and filters by a threshold.
utils/boolean.py        - contains intersect function, which returns the intersection of two sorted lists based on the first element.
                  intersect_consecutive function which finds positions in p2 directly following positions in p1.
                  process_phrase_term function which processes phrase queries by checking consecutive term appearance in documents, updating scores based on term weights.
                  process_boolean_term function which processes a boolean term, updating document scores based on term weights and field filters.
                  TestQuery class which contains test cases to verify the correct functioning of the phrase query processing using unittest framework. 
utils/vector.py         - contains normalise_vector function to compute the TF-IDF normalized vector for a given query against a dictionary of document frequencies and total document count.
utils/file.py           - contains read_pkl_csv function, which reads a CSV file, parses its contents into a dictionary, and then pickles it to a file for storage.
                  load_pkl function loads a pickle file containing documents and returns it as a dictionary.

working/dictionary.txt_cit  - contains document ID to citation dictionary
working/dictionary.txt_len  - contains the total number of documents in the corpus

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0234456A-A0290349X, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

== References ==

