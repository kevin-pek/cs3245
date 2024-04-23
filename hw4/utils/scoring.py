import pickle
from utils.compression import gap_decode, vb_decode


component_weights = {
    'title': 0.6,
    'content': 0.4,
}

def calculate_score(scores, query_vector, dictionary, p, bool_result = None, tfidf_threshold=0.1):

    for term, wq in query_vector.items():
        if term in dictionary and wq >= tfidf_threshold:  # Apply TF-IDF thresholding
            offset = dictionary[term][1]
            p.seek(offset)
            postings = pickle.load(p)
            doc_id = 0 # accumulator for doc_id since it is stored using gap encoding
            # NOTE: Similar process needs to be done for interpreting postional index
            #       When handling phrase queries if we are dealing with boolean queries
            #       By passing it through gap_decode(vb_decode(position_idx))
            for enc_doc_id, w_c, w_t, fields, position_idx in postings:
                gap_doc_id = vb_decode(enc_doc_id)[0] # decode and add gap value to document id
                print("Document ID Gap: ", gap_doc_id)
                doc_id += gap_doc_id
                if bool_result:         # if boolean/date: rank only existing results
                    if doc_id in bool_result:
                        pass
                    else:
                        continue
                print("Loaded Postings: ", (doc_id, w_c, w_t, fields, gap_decode(vb_decode(position_idx))))
                scores[doc_id]['content'] += w_c * wq
                scores[doc_id]['title'] += w_t * wq

                # TODO: handle fields & positional index
                scores[doc_id]['court'] = None
    return scores

def pagerank(scores, component_weights= component_weights):
    total_score = 0
    for component, weight in component_weights.items():
        total_score += scores.get(component, 0) * weight
    return total_score

