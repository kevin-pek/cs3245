import pickle
import unittest
import tempfile
from collections import defaultdict
import os
from utils.compression import gap_decode, vb_decode, vb_encode, gap_encode


def intersect(p1: list[tuple[int, float, float]], p2: list[tuple[int, float, float]]):
    i, j = 0, 0
    results: list[tuple[int, float, float]] = []
    while i < len(p1) and j < len(p2):
        if p1[i][0] == p2[j][0]:
            results.append(p2[j])
            i += 1
            j += 1
        elif p2[j][0] > p1[i][0]:
            i += 1
        else:
            j += 1
    return results


def intersect_consecutive(p1: list[int], p2: list[int]):
    """Returns positions in p2 that are directly follow from positions in p1."""
    i, j = 0, 0
    results: list[int] = []
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


def process_phrase_term(dictionary, terms: list[str], p, qv: dict[str, float], scores):
    if not terms:
        return []

    # handle first term in the phrase query
    term = terms[0]
    p.seek(dictionary[term][1])
    postings = pickle.load(p)
    acc = {}
    doc_id = 0
    for enc_doc_id, _, w_c, w_t, _, enc_posits in postings:
        doc_id += vb_decode(enc_doc_id)[0]
        positions = gap_decode(vb_decode(enc_posits))
        acc[doc_id] = positions
        scores[doc_id]['content'] += w_c * qv.get(term, 0)
        scores[doc_id]['title'] += w_t * qv.get(term, 0)

    for term in terms[1:]:
        p.seek(dictionary[term][1])
        postings = pickle.load(p)
        doc_id = 0
        for enc_doc_id, enc_court_id, w_c, w_t, _, enc_posits in postings:
            doc_id += vb_decode(enc_doc_id)[0]
            if doc_id in acc: # if document is still in consideration we check if it is still valid based on positional index
                positions = gap_decode(vb_decode(enc_posits))
                matches = intersect_consecutive(acc[doc_id], positions) # TODO: Maybe add some leniency factor
                if matches:
                    acc[doc_id] = matches
                    scores[doc_id]['content'] += w_c * qv.get(term, 0)
                    scores[doc_id]['title'] += w_t * qv.get(term, 0)
                    scores[doc_id]['court'] = vb_decode(enc_court_id)[0]
                else:
                    del acc[doc_id]
                    del scores[doc_id]
    return sorted([(id, w['content'], w['title'], w['content']) for id, w in scores.items()], key=lambda x: x[0])


def process_boolean_term(dictionary, term, p, scores=None, mask=None, qv=None):
    p.seek(dictionary[term][1])
    postings = pickle.load(p)
    if not scores:
        scores = defaultdict(lambda: defaultdict(float))
    doc_id = 0
    for enc_doc_id, enc_court_id, w_c, w_t, fields, _ in postings:
        doc_id += vb_decode(enc_doc_id)[0]
        if mask and not fields & mask: # if posting does not match on a specific field
            continue
        if qv:
            scores[doc_id]['content'] += w_c * qv.get(term, 0)
            scores[doc_id]['title'] += w_t * qv.get(term, 0)
            scores[doc_id]['court'] = vb_decode(enc_court_id)[0]
        else:
            scores[doc_id]['content'] = w_c
            scores[doc_id]['title'] = w_t
            scores[doc_id]['court'] = vb_decode(enc_court_id)[0]
    return sorted([(id, w['content'], w['title'], w['content']) for id, w in scores.items()], key=lambda x: x[0])


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

