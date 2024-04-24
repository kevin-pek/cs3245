import unittest
from io import BufferedReader
import nltk
import math
from collections import defaultdict
from nltk.corpus import wordnet
from utils.boolean import process_boolean_term, process_phrase_term, intersect
from utils.preprocessing import process_term, extract_citations, extract_date, court_manipulation

nltk.download('wordnet')
nltk.download('omw-1.4')

def process_query(raw_query: str) -> tuple[list[str], bool, bool]:
    """
    Single pass through the query to determine type of query and process terms.
    Returns a list of terms and phrases to search for, and boolean representing
    the type of search query.

    Returns:
     - terms: list[str], List of string terms extracted from the query.
     - is_boolean: bool, True if query is a boolean query, False if free text.
     - is_valid: bool, True if query is a valid.
     - citation: str, Case citation contained in the query.
    """
    citation, raw_query = extract_citations(raw_query)

    year, month_day = extract_date(raw_query)

    court_id = court_manipulation().extract_court(raw_query)
    
    raw_terms = raw_query.split()
    if not raw_terms:
        return [], year, month_day, False, False, citation, court_id
    expanded_terms = query_expansion(raw_terms)
    is_boolean = False
    is_freetext = False
    is_valid = True
    i = 0
    terms = []
    while i < len(expanded_terms):
        term = expanded_terms[i]
        if term[0] == '"': # start of phrase query
            if is_freetext or len(term) == 1 or term == '""':
                # if term is single double quote or empty phrase, invalid query
                is_valid = False
                break
            elif i > 0 and expanded_terms[i - 1] != 'AND':
                # if not first term and not preceded by an AND, invalid query
                is_valid = False
                break
            is_boolean = True # phrase query only supported in boolean retrieval
            term = term[1:] # remove first double quote character from the word
            phrase = []
            while i < len(expanded_terms):
                if term[-1] == '"':
                    # end of phrase, add term without including the double quote
                    phrase.append(term[:-1])
                    break
                elif i == len(expanded_terms) - 1:
                    # if last term but phrase is not closed, invalid query
                    is_valid = False
                    break
                phrase.append(term) # add term to phrase if not last term
                i += 1
                term = expanded_terms[i]
            if not is_valid: # escape hatch for invalid queries
                break
            terms.append(phrase)
        elif term == "AND":
            if is_freetext or i == 0 or i == len(expanded_terms) - 1:
                # if AND does not appear between 2 terms, invalid query
                is_valid = False
                break
            elif expanded_terms[i - 1] == 'AND':
                # if 2 consecutive ANDs appear, invalid query
                is_valid = False
                break
            is_boolean = True
        else:
            # single word term encountered
            if not is_freetext and i > 0 and expanded_terms[i - 1] != 'AND':
                # if 2 consecutive single terms are encountered, freetext
                is_freetext = True
                if is_boolean:
                    # but if we know it is a boolean query, invalid query
                    is_valid = False
                    break
            terms.append(term)
        i += 1
    if is_freetext and is_boolean:
        is_valid = False
    if not is_valid:
        print(f"Invalid query: {raw_query}")
    return terms, year, month_day, is_boolean, is_valid, citation, court_id


def process_boolean_query(dictionary, terms, p: BufferedReader, N) -> list[tuple[int, float, float]]:
    processed_terms = [] # we initialise a heap to intersect in order of lowest df
    idf = {}
    for term in terms:
        if isinstance(term, list): # phrase query
            df_max = 0 # for phrase queries we use the term with lowest df
            term = [process_term(t) for t in term]
            for t in term:
                if t not in dictionary:
                    df_max = 0
                    break
                df = dictionary[t][0]
                if df == 0: # if a phrase query term doesnt appear treat it as 0
                    df_max = 0
                    break
                idf[t] = math.log(N / df, 10) if df != 0 and N != 0 else 0
                df_max = max(df_max, df)
            if df_max == 0: # stop query processing if it does not even exist in dictionary
                processed_terms = []
                break
            processed_terms.append((df_max, term))
        else:
            term = process_term(term)
            if term in dictionary:
                df = dictionary[term][0]
                idf[term] = math.log(N / df, 10) if df != 0 and N != 0 else 0
                processed_terms.append((dictionary[term][0], term))
            else:
                processed_terms = []
                break
    norm = math.sqrt(sum(x ** 2 for x in idf.values()))
    qv = { term: weight / norm for term, weight in idf.items() }
    if not processed_terms: # if we have no processed terms means no result
        return []

    # initialise results with the first item in processed term
    processed_terms.sort()
    term = processed_terms[0][1]
    scores = defaultdict(lambda: defaultdict(float))
    if isinstance(term, list):
        docs = process_phrase_term(dictionary, term, p, qv, scores)
    else:
        docs = process_boolean_term(dictionary, term, p, qv=qv, scores=scores)
    # do intersection in order of term document frequency
    for df, term in processed_terms[1:]:
        if isinstance(term, list): # phrase query
            docs = intersect(docs, process_phrase_term(dictionary, term, p, qv, scores))
        else:
            docs = intersect(docs, process_boolean_term(dictionary, term, p, qv=qv, scores=scores))
    return docs


def query_expansion(query_terms):
    expanded_query = set(query_terms)
    
    for word in query_terms:
        synsets = wordnet.synsets(word)[:5] 
        
        for synset in wordnet.synsets(word):
            # Add all lemmas of the synset
            expanded_query.update([lemma.name() for lemma in synset.lemmas()])
            
            for hypernym in synset.hypernyms():
                expanded_query.update([lemma.name() for lemma in hypernym.lemmas()])
            for hyponym in synset.hyponyms():
                expanded_query.update([lemma.name() for lemma in hyponym.lemmas()])
    print("Expanded query: ", expanded_query)
    return list(expanded_query)



class TestProcessQuery(unittest.TestCase):
    def test_process_query(self):
        """Runs a series of test cases for process_query."""
        test_queries = {
            'quiet phone call': (['quiet', 'phone', 'call'], False, True),
            '"fertility treatment" AND damages': ([['fertility', 'treatment'], 'damages'], True, True),  # Valid Boolean
            '"fertility treatment" "damages"': ([], True, False),  # Invalid: consecutive phrases without AND
            '"fertility treatment" damage': ([], True, False),  # Invalid: phrase followed by term without AND
            'AND quiet': ([], True, False),  # Invalid: AND at the start
            'quiet AND': ([], True, False),  # Invalid: AND at the end
            '"fertility treatment AND damages': ([], True, False),  # Invalid: unclosed quote
            '"" empty': ([], True, False),  # Invalid: empty quote
            'quiet AND phone AND call': (['quiet', 'phone', 'call'], True, True),  # Valid Boolean
            'quiet phone': (['quiet', 'phone'], False, True),  # Valid free text
            '"quiet phone" call': ([], True, False),  # Mix of boolean and free text
            '"A quote "inside" another quote"': ([], True, False),  # Nested phrases
            '   term1 term2    ': (['term1', 'term2'], False, True),  # Leading and trailing spaces
            '"term1  AND    term2"': ([['term1', 'AND', 'term2']], True, True),  # Multiple consecutive spaces within a phrase
            '"term1!" AND "term?2"': ([['term1!'], ['term?2']], True, True),  # Special characters
            '"term"': ([['term']], True, True),  # Single word with quotes
            '"term1 AND term2"': ([['term1', 'AND', 'term2']], True, True),  # Boolean operator within quotes
            '': ([], False, False),  # Empty query
        }

        for query, expected in test_queries.items():
            with self.subTest(query=query):
                result = process_query(query)
                if expected[2]:  # if the query is expected to be valid
                    self.assertEqual(result, expected, f"Failed for query: {query}")
                else:  # if the query is expected to be invalid
                    self.assertEqual(result[2], expected[2], f"Failed for query: {query}")


if __name__ == '__main__':
    unittest.main()
