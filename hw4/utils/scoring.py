import pickle
from collections import defaultdict
from utils.compression import vb_decode


def calculate_score(qv: dict[str, float], dictionary, p):
    scores = defaultdict(lambda: defaultdict(float))
    for term, wq in qv.items():
        if term in dictionary:
            offset = dictionary[term][1]
            p.seek(offset)
            postings = pickle.load(p)
            doc_id = 0 # accumulator for doc_id since it is stored using gap encoding
            for enc_doc_id, w_c, w_t, fields, _ in postings:
                doc_id += vb_decode(enc_doc_id)[0] # decode and add gap value to document id
                if fields & 0b10001: # only add weights if it has either content or title
                    scores[doc_id]['content'] += w_c * wq
                    scores[doc_id]['title'] += w_t * wq
    return [(id, w['content'], w['title']) for id, w in scores.items()]


def total_score(docs_scores: list[tuple[int, float, float]], cit_match: int | None=None, date_matches: set[int] | None=None, year_matches: set[int] | None=None):
    scores = {}
    for doc_id, w_c, w_t in docs_scores:
        # print(doc_id, w_c, w_t)
        score = w_c + w_t
        if cit_match and doc_id == cit_match:
            score += 0.1
        if date_matches and doc_id in date_matches:
            score += 0.015
        if year_matches and doc_id in year_matches:
            score += 0.01
        if score < 0.02: # threshold
            continue
        scores[doc_id] = score
    print("SCORES: ", sorted([(id, w) for id, w in scores.items()], key=lambda x: x[1], reverse=True))
    return scores

