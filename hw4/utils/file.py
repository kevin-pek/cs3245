import re
import csv
import pickle

"""
Functions to save and load files to/from disk, and compression techniques to
reduce disk space usage.
"""

def read_csv(file_path: str) -> dict[str, list[str]]:
    """
    Read csv file and return dictionary with keys corresponding to each column.
    """
    documents = {}
    max_len = 2**31 - 1 # max len for c-long
    csv.field_size_limit(max_len) # bypass field limit for csv.DictReader
    with open(file_path, mode='r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            court = row['court']
            date_posted = row['date_posted']
            content = re.sub(r'\W+', ' ', row['content']).lower()
            title = row['title']    # need to do further processing to seperate the case name from case identifier, and maybe do sth about chinese cases
            documents[row['document_id']] = {'court': court, 'date_posted': date_posted, 'content': content, 'title': title}
    return documents


def save_pkl(documents):
    """Save object to pickle file."""
    pkl_file_path = 'data/documents.pkl'
    with open(pkl_file_path, 'wb') as pf:
        pickle.dump(documents, pf)
    return documents


def load_pkl(pkl_file_path) -> dict[str, list[str]]:
    """Load pickle file from filepath"""
    with open(pkl_file_path, 'rb') as pf:
        documents = pickle.load(pf)
    return documents

