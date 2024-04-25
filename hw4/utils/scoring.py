import pickle
from collections import defaultdict
from utils.compression import vb_decode

court_w = {
    1: 0.01,
    2: 0.007,
    3: 0.006,
    4: 0.0057,
    5: 0.0055,
    6: 0.0055,
    7: 0.0055,
    8: 0.0055,
    9: 0.005,
    10: 0.005,
    11: 0.005,
    12: 0.004,
    13: 0.004,
    14: 0.004,
    15: 0.003,
    16: 0.002,
    17: 0.002,
    18: 0.002,
    19: 0,
    20: 0,
    21: 0,
    22: 0,
    23: 0,
    24: 0,
    25: 0,
    26: 0,
    27: 0,
    28: 0.005,
    29: 0.005,
    30: 0.005,
    31: 0,
}

def calculate_score(qv: dict[str, float], dictionary, p):
    scores = defaultdict(lambda: defaultdict(float))
    for term, wq in qv.items():
        if term in dictionary:
            offset = dictionary[term][1]
            p.seek(offset)
            postings = pickle.load(p)
            doc_id = 0 # accumulator for doc_id since it is stored using gap encoding
            for enc_doc_id, enc_court_id, w_c, w_t, fields, _ in postings:
                doc_id += vb_decode(enc_doc_id)[0] # decode and add gap value to document id
                if fields & 0b0011: # only add weights if it has either content or title
                    scores[doc_id]['content'] += w_c * wq
                    scores[doc_id]['title'] += w_t * wq
                    scores[doc_id]['court'] = vb_decode(enc_court_id)[0]
    return [(id, w['content'], w['title'], w['court']) for id, w in scores.items()]


def total_score(docs_scores: list[tuple[int, float, float, int]], cit_match: int | None=None, date_matches: set[int] | None=None, year_matches: set[int] | None=None, score_threshold= 0.01):
    scores = {}
    for doc_id, w_c, w_t, court_id in docs_scores:
        # print(doc_id, w_c, w_t)
        score = 0.7 * w_c + 0.9 * w_t
        score += court_w.get(court_id, 0) * 1.5
        if cit_match and doc_id == cit_match:
            score += 0.1
        if date_matches and doc_id in date_matches:
            score += 0.015
        if year_matches and doc_id in year_matches:
            score += 0.01
        if score < score_threshold: # threshold
            continue
        scores[doc_id] = score
    # print("SCORES: ", sorted([(id, w) for id, w in scores.items()], key=lambda x: x[1], reverse=True))
    return scores

