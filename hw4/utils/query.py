import unittest
from utils.preprocessing import extract_citations

def process_query(raw_query: str) -> tuple[list[str], bool, bool]:
    """
    Single pass through the query to determine type of query and process terms.
    Returns a list of terms and phrases to search for, and boolean representing
    the type of search query.

    Returns:
     - terms: list[str], List of string terms extracted from the query.
     - is_boolean: bool, True if query is a boolean query, False if free text.
     - is_valid: bool, True if query is a valid.
    """
    citation = extract_citations(raw_query)
    if citation:
        pass    #TODO implememnt code to fetch citation from dictionary
    raw_terms = raw_query.split()
    if not raw_terms:
        return [], False, False
    is_boolean = False
    is_freetext = False
    is_valid = True
    i = 0
    terms = []
    while i < len(raw_terms):
        term = raw_terms[i]
        if term[0] == '"': # start of phrase query
            if is_freetext or len(term) == 1 or term == '""':
                # if term is single double quote or empty phrase, invalid query
                is_valid = False
                break
            elif i > 0 and raw_terms[i - 1] != 'AND':
                # if not first term and not preceded by an AND, invalid query
                is_valid = False
                break
            is_boolean = True # phrase query only supported in boolean retrieval
            term = term[1:] # remove first double quote character from the word
            phrase = []
            while i < len(raw_terms):
                if term[-1] == '"':
                    # end of phrase, add term without including the double quote
                    phrase.append(term[:-1])
                    break
                elif i == len(raw_terms) - 1:
                    # if last term but phrase is not closed, invalid query
                    is_valid = False
                    break
                phrase.append(term) # add term to phrase if not last term
                i += 1
                term = raw_terms[i]
            if not is_valid: # escape hatch for invalid queries
                break
            terms.append(phrase)
        elif term == "AND":
            if is_freetext or i == 0 or i == len(raw_terms) - 1:
                # if AND does not appear between 2 terms, invalid query
                is_valid = False
                break
            elif raw_terms[i - 1] == 'AND':
                # if 2 consecutive ANDs appear, invalid query
                is_valid = False
                break
            is_boolean = True
        else:
            # single word term encountered
            if not is_freetext and i > 0 and raw_terms[i - 1] != 'AND':
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
    return terms, is_boolean, is_valid


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

