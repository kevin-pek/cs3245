import csv
import pickle

"""
Functions to save and load files to/from disk, and compression techniques to
reduce disk space usage.
"""

def read_pkl_csv(file_path: str) -> dict[str, dict[str, str | dict]]:
    documents = {}
    max_len = 2**31 - 1 # max len for c-long
    csv.field_size_limit(max_len) # bypass field limit for csv.DictReader
    with open(file_path, mode='r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            court = row['court']
            date_posted = row['date_posted']
            content = row['content'] # re.sub(r'\W+', ' ', row['content']).lower()
            title = row['title']    # need to do further processing to seperate the case name from case identifier, and maybe do sth about chinese cases
            documents[int(row['document_id'])] = {'court': court, 'date_posted': date_posted, 'content': content, 'title': title}

    pkl_file_path = 'data/documents.pkl'
    with open(pkl_file_path, 'wb') as pf:
        pickle.dump(documents, pf)
    return documents


def load_pkl(pkl_file_path = 'data/documents.pkl') -> dict[str, list[str]]:
    """Load pickle file from filepath"""
    with open(pkl_file_path, 'rb') as pf:
        documents = pickle.load(pf)
    return documents

