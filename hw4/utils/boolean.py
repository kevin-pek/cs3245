import pickle
import unittest
import tempfile
import os
from utils.compression import gap_decode, vb_decode, vb_encode, gap_encode


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
        if p2[j] - p1[i] == 1: # curr element in p2 directly follows from current element in p1
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
    acc = {}
    doc_id = 0
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
    docs = []
    doc_id = 0
    for post in postings:
        doc_id += vb_decode(post[0])[0]
        docs.append(doc_id)
    return docs


class TestQuery(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        postings = {
            'apple': [(vb_encode(1), None, None, None, bytes(byte for gap in gap_encode([2, 6]) for byte in vb_encode(gap))), 
                      (vb_encode(4), None, None, None, bytes(byte for gap in gap_encode([7]) for byte in vb_encode(gap)))],
            'banana': [(vb_encode(1), None, None, None, bytes(byte for gap in gap_encode([4, 7]) for byte in vb_encode(gap))), 
                       (vb_encode(4), None, None, None, bytes(byte for gap in gap_encode([8, 15]) for byte in vb_encode(gap)))],
            'cherry': [(vb_encode(4), None, None, None, bytes(byte for gap in gap_encode([8, 10]) for byte in vb_encode(gap)))]
        }
        self.dictionary = {}
        for term, data in postings.items():
            offset = self.temp_file.tell()
            pickle.dump(data, self.temp_file)
            self.dictionary[term] = (len(data), offset)
        self.temp_file.flush()

    def tearDown(self) -> None:
        self.temp_file.close()
        os.remove(self.temp_file.name)

    def test_phrase_queries(self):
        with open(self.temp_file.name, 'rb') as f:
            print(process_phrase_term(self.dictionary, ['apple', 'banana'], f))


if __name__ == '__main__':
    unittest.main()

