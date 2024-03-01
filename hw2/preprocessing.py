from nltk import PorterStemmer, word_tokenize
from nltk.corpus import stopwords

stemmer = PorterStemmer()

def process_word(text: str) -> str:
    """Does stemming and case folding to given word."""
    return stemmer.stem(text, to_lowercase=True)

def process_document(id: int, document: str) -> list[tuple[int, str]]:
    """Creates list of token-id pairs from given id and raw document string."""
    tokens = word_tokenize(document)
    return [(process_word(token), id) for token in tokens if token.isalnum()]

# FUNCTIONS FOR ESSAY QUESTIONS

def process_document_remove_nums(id: int, document: str) -> list[tuple[int, str]]:
    """Process document but ignores token if it contains symbols or numbers."""
    tokens = word_tokenize(document)
    return [(process_word(token), id) for token in tokens if token.isalpha()]

def process_document_remove_stopwords(id: int, document: str) -> list[tuple[int, str]]:
    """Process token if it is not a stopword or number."""
    tokens = word_tokenize(document)
    stop_words = set(stopwords.words('english'))
    return [(process_word(token), id) for token in tokens if token.lower() not in stop_words and token.isalpha()]
