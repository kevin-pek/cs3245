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


QUERY REFINEMENT:


== Files included with this submission ==

index.py  - indexing phase
utils.py  - contains get_terms function to process string to list of terms,
            process_terms function to convert list of terms to processed form,
            normalize_vector to do cosine normalisation for tf-idf vectors
search.py - searching phase
query.py  - contains process_query function to handle processing of queries


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

