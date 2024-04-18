import re
from nltk import sent_tokenize, word_tokenize, PorterStemmer

"""
Functions to preprocess dataset and extract information from text to help with
index construction and query handling.
"""

stemmer = PorterStemmer()

def get_terms(document: str):
    stop_words = ['appellant', 'respondent', 'plaintiff', 'defendant', 'mr', 'dr', 'mdm', 'court','version', 'case', 'court', 'statement', 'line', 'para', 'fact']    #not sure if useful, but added these common words to all judgments
    terms = []
    for sentence in sent_tokenize(document):
        sentence = re.sub(r'[-/]', ' ', sentence) # split word based on hyphens and slashes
        for word in word_tokenize(sentence):
            # remove non alphanumeric character, but keep periods that are found
            # between 2 numbers as they are likely part of a decimal number
            word = re.sub(r'(?<!\d)\.(?!\d)|[^\w\d.]', '', word)

            if word not in stop_words and word.isalnum():
                terms.append(stemmer.stem(word, to_lowercase=True))
    return terms

def simplify_court(court):
    court_abbreviations = {
        'CA Supreme Court': 'SCR',
        'Federal Court of Australia': 'FCA',
        'HK Court of First Instance': 'CFI',
        'HK High Court': 'HKHC',
        'High Court of Australia': 'HCA',
        'Industrial Relations Court of Australia': 'IRCA',
        'NSW Administrative Decisions Tribunal (Trial)': 'NSWADT',
        'NSW Children\'s Court': 'NSWCC',
        'NSW Civil and Administrative Tribunal': 'NCAT',
        'NSW Court of Appeal': 'NSWCA',
        'NSW Court of Criminal Appeal': 'NSWCCA',
        'NSW District Court': 'NSWDC',
        'NSW Industrial Court': 'NSWIC',
        'NSW Industrial Relations Commission': 'NSWIRC',
        'NSW Land and Environment Court': 'NSWLEC',
        'NSW Local Court': 'NSWLC',
        'NSW Medical Tribunal': 'NSWMT',
        'NSW Supreme Court': 'NSWSC',
        'SG Court of Appeal': 'SGCA',
        'SG District Court': 'SGDC',
        'SG Family Court': 'SGFC',
        'SG High Court': 'SGHC',
        'SG Magistrates\' Court': 'SGMC',
        'SG Privy Council': 'SGPC',
        'Singapore International Commercial Court': 'SICC',
        'UK Court of Appeal': 'EWCA',
        'UK Crown Court': 'UKCC',
        'UK High Court': 'EWHC',
        'UK House of Lords': 'UKHL',
        'UK Military Court': 'UKMC',
        'UK Supreme Court': 'UKSC',
    }
    return court_abbreviations.get(court, court)

def clean_content(text, keyword="supreme court of canada citation"):
    # Find the position of the keyword in the text
    pos = text.lower().find(keyword.lower())
    # If the keyword is found, slice the text from the keyword onwards
    if pos != -1:
        return text[pos:]
    else:
        return text