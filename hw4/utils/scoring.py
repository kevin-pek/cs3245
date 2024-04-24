import pickle
from collections import defaultdict
from utils.compression import vb_decode

def get_court_w():
    court_w = {
        1: 0.01,
        2: 0.007,
        3: 0.006,
        4: 0.0057,
        5: 0.0055,
        6: 0.0055,
        7: 0.0055,
        8: 0.0055,
        9: ['Singapore International Commercial Court', 'SICC'],
        10: ['SG Privy Council', 'SGPC'],
        11: ['UK High Court', 'EWHC'],
        12: ['Federal Court of Australia', 'FCA'],
        13: ['NSW Court of Appeal', 'NSWCA'],
        14: ['NSW Court of Criminal Appeal', 'NSWCCA'],
        15: ['HK High Court', 'HKHC'],
        16: ['HK Court of First Instance', 'CFI'],
        17: ['UK Crown Court', 'UKCC'],
        18: ['Industrial Relations Court of Australia', 'IRCA'],
        19: ['NSW Administrative Decisions Tribunal (Trial)', 'NSWADT'],
        20: ['NSW Children\'s Court', 'NSWCC'],
        21: ['NSW Civil and Administrative Tribunal', 'NCAT'],
        22: ['NSW District Court', 'NSWDC'],
        23: ['NSW Industrial Court', 'NSWIC'],
        24: ['NSW Industrial Relations Commission', 'NSWIRC'],
        25: ['NSW Land and Environment Court', 'NSWLEC'],
        26: ['NSW Local Court', 'NSWLC'],
        27: ['NSW Medical Tribunal', 'NSWMT'],
        28: ['SG District Court', 'SGDC'],
        29: ['SG Family Court', 'SGFC'],
        30: ['SG Magistrates\' Court', 'SGMC'],
        31: ['UK Military Court', 'UKMC'],
    }


def calculate_score(qv: dict[str, float], q_court_id, dictionary, p):
    
    scores = defaultdict(lambda: defaultdict(float))
    for term, wq in qv.items():
        if term in dictionary:
            offset = dictionary[term][1]
            p.seek(offset)
            postings = pickle.load(p)
            doc_id = 0 # accumulator for doc_id since it is stored using gap encoding
            for enc_doc_id, court_id, w_c, w_t, fields, _, top_terms in postings:
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

