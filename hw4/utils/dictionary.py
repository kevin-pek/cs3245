import math
import pickle
from utils.compression import compress_and_save_dict, gap_encode, vb_encode

class ZoneIndex():
    """Inverted index that includes fields and zones within the dictionary"""
    postings: dict[str, list[tuple[int, float, float, int, list[int]]]]
    freq: dict[str, int] # for term frequencies during the construction process
    title_freq: dict[str, int] # term frequency for title of case
    posits: dict[str, list[int]] # positional index for phrase queries
    fields: dict[str, int]

    def __init__(self):
        self.freq = {}
        self.title_freq = {}
        self.posits = {}
        self.fields = {}
        self.postings = {}

    def add_term(self, term: str, pos: int):
        if term not in self.freq:
            self.freq[term] = 0
        self.freq[term] += 1
        if term not in self.fields:
            self.fields[term] = 0
        self.fields[term] |= 0b000001
        if term not in self.posits:
            self.posits[term] = []
        self.posits[term].append(pos)

    def add_court(self, court: str):
        if court not in self.fields:
            self.fields[court] = 0
        self.fields[court] |= 0b000010

    def add_year(self, year: int):
        if year not in self.fields:
            self.fields[year] = 0
        self.fields[year] |= 0b000100

    def add_date(self, date: int):
        if date not in self.fields:
            self.fields[date] = 0
        self.fields[date] |= 0b001000

    def add_citation(self, citation: str):
        if citation not in self.fields:
            self.fields[citation] = 0
        self.fields[citation] |= 0b010000

    def add_title(self, title_term: str):
        if title_term not in self.title_freq:
            self.freq[title_term] = 0
        self.freq[title_term] += 1
        if title_term not in self.fields:
            self.fields[title_term] = 0
        self.fields[title_term] |= 0b100000

    def calculate_weights(self, doc_id: str):
        """Finalise the weights for a document by calculating the tf-idf weights
        and posting list."""
        # calculate lnc weights for each term in document
        tf_c = { term: 1 + math.log10(tf) for term, tf in self.freq.items() }
        norm_c = math.sqrt(sum(x ** 2 for x in tf_c.values()))
        tf_t = { term: 1 + math.log10(tf) for term, tf in self.title_freq.items() }
        norm_t = math.sqrt(sum(x ** 2 for x in tf_t.values()))
        for term, w in tf_c.items():
            wc = w / norm_c if norm_c != 0 else 0
            wt = 0
            if term in tf_t:
                wt = tf_t[term] / norm_t if norm_t != 0 else 0
                del tf_t[term] # remove term from title dictionary so we wont need to add it later
            if term not in self.postings:
                self.postings[term] = []
            positions = self.posits[term] if term in self.posits else []
            self.postings[term].append((int(doc_id), wc, wt, self.fields[term], positions))

        # add the remaining terms found in title that were not in the content
        for term, w in tf_t.items():
            wt = w / norm_t if norm_t != 0 else 0
            if term not in self.postings:
                self.postings[term] = []
            self.postings[term].append((int(doc_id), 0, wt, self.fields[term], []))

        # clear memory for the current document too reduce memory usage
        self.freq = {}
        self.title_freq = {}
        self.posits = {}
        self.fields = {}

    def save(self, out_dict: str, out_postings: str):
        """Compress postings list and dictionary and write to disk."""
        dictionary = {}
        with open(out_postings, "wb") as p:
            for term, posting_list in self.postings.items():
                acc = 0
                enc_postings = []
                # sort the doc_id in ascending order for gap encoding
                for posting in sorted(posting_list, key=lambda x: x[0]):
                    doc_id, wc, wt, fields, posits = posting
                    acc = doc_id - acc # calculate gap from previous doc_id
                    enc_doc_id = vb_encode(acc)
                    enc_pos = bytes(byte for gap in gap_encode(posits) for byte in vb_encode(gap))
                    enc_postings.append((enc_doc_id, wc, wt, fields, enc_pos))
                offset = p.tell()
                pickle.dump(enc_postings, p)
                dictionary[term] = (len(enc_postings), offset)

        compress_and_save_dict(dictionary, out_dict)

