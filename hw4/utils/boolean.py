import pickle
from utils.compression import gap_decode, vb_decode


def intersect(p1, p2):
    i, j = 0, 0
    results = []
    while i < len(p1) and j < len(p2):
        if p1[i] == p2[j]:
            results.append(p2[j])
            i += 1
            j += 1
        elif p2[j] > p1[i]:
            i += 1
        else:
            j += 1
    return results


def intersect_consecutive(p1, p2):
    """Returns positions in p2 that are directly follow from positions in p1."""
    i, j = 0, 0
    results = []
    while i < len(p1) and j < len(p2):
        if p1[i] - p2[j] == 1: # curr element in p2 directly follows from current element in p1
            results.append(p2[j])
            i += 1
            j += 1
        elif p2[j] - p1[i] > 1: # gap between current p2 element is more than 1
            i += 1
        else: # current p1 element is higher than current p2 element
            j += 1
    return results


def process_phrase_term(dictionary, terms, p):
    if not terms:
        return []

    # handle first term in the phrase query
    p.seek(dictionary[terms[0]][1])
    postings = pickle.load(p)
    doc_id = 0
    acc = {}
    for enc_doc_id, _, _, _, enc_posits in postings:
        doc_id += vb_decode(enc_doc_id)[0]
        positions = gap_decode(vb_decode(enc_posits))
        acc[doc_id] = positions

    for term in terms[1:]:
        p.seek(dictionary[term][1])
        postings = pickle.load(p)
        doc_id = 0
        for enc_doc_id, _, _, _, enc_posits in postings:
            doc_id += vb_decode(enc_doc_id)[0]
            if doc_id in acc: # if document is still in consideration we check if it is still valid based on positional index
                positions = gap_decode(vb_decode(enc_posits))
                matches = intersect_consecutive(acc[doc_id], positions)
                if matches:
                    acc[doc_id] = matches
                else:
                    del acc[doc_id]
    return sorted(acc.keys())


def process_boolean_term(dictionary, term, p):
    p.seek(dictionary[term][1])
    postings = pickle.load(p)
    doc_id = 0
    docs = []
    for post in postings:
        doc_id += vb_decode(post[0])[0]
        docs.append(doc_id)
    return docs

