import pickle
import heapq
from linkedlist import LinkedList, difference, intersect, union

class InvertedIndex:
    index: dict[str, tuple[int, int]]
    universe: LinkedList

    def __init__(self, dict_file, postings_file):
        self.universe = None
        f_dict = open(dict_file, 'rb')
        self.index = pickle.load(f_dict)
        f_dict.close()
        self.f_postings = open(postings_file, 'rb')

    def get_universe(self):
        if not self.universe:
            u = set()
            for _, offset in self.index.values():
                self.f_postings.seek(offset)
                for id in pickle.load(self.f_postings):
                    u.add(id)
            self.universe = LinkedList.from_list(sorted(u))
        return self.universe

    def read_postings(self, term: str) -> LinkedList | None:
        if term not in self.index:
            return None
        _, offset = self.index[term]
        self.f_postings.seek(offset)
        postings = LinkedList.from_list(pickle.load(self.f_postings))
        postings.add_skip_pointers()
        return postings

class Operand:
    """
    Class to represent an operand for boolean operations. It store a boolean to
    indicate whether a term is negated for optimisations with De Morgan's Law,
    and will contain either a term if not retrieved, or the intermediate posting
    linked list which will be used with subsequent operations.
    """
    is_neg: bool
    term: str
    postings: LinkedList

    def __init__(self, term=None, is_neg=False, postings=None):
        self.term = term
        self.is_neg = is_neg
        self.postings = postings

    def __lt__(self, other): # introduced to fix comparisons between operands in the heap
        return True
    
    def __repr__(self) -> str:
        return f'{"NOT " if self.is_neg else ""}{self.term if self.term else self.postings}'

    def get_postings(self, index: InvertedIndex):
        if not self.postings and self.term:
            self.postings = index.read_postings(self.term)
        return self.postings

class AndHeap:
    """
    Stores a heap of terms included in a chained AND query and sorts them in order
    of term frequency.
    """
    heap: list[tuple[int, Operand]]
    is_neg: bool

    def __init__(self, is_neg=False) -> None:
        self.heap = []
        self.is_neg = is_neg

    def __repr__(self) -> str:
        return f'{"NOT " if self.is_neg else ""}HEAP'

    def add(self, op: Operand, index: InvertedIndex):
        if op.postings: # posting list exists, intermediate result
            heapq.heappush(self.heap, (op.postings.length, Operand(is_neg=op.is_neg, postings=op.postings)))
        elif op.term and op.term in index.index: # operand has not been accessed yet and is in the dictionary
            freq = index.index[op.term][0]
            heapq.heappush(self.heap, (freq, Operand(is_neg=op.is_neg, term=op.term)))
        else: # if neither term or posting list exists means it is a None term
            heapq.heappush(self.heap, (0, Operand(is_neg=op.is_neg)))

    def evaluate(self, index: InvertedIndex):
        """Evaluate the chain of AND terms in ascending order of term frequency."""
        result = None
        while self.heap:
            _, op1 = heapq.heappop(self.heap)
            _, op2 = heapq.heappop(self.heap)
            postings = None
            if op1.is_neg and op2.is_neg: # apply De Morgan's Law to reduce NOT operations
                postings = union(op1.get_postings(index), op2.get_postings(index))
            elif op1.is_neg: # take complement based on other operand
                postings = difference(op1.get_postings(index), op2.get_postings(index))
            elif op2.is_neg:
                postings = difference(op2.get_postings(index), op1.get_postings(index))
            else:
                postings = intersect(op1.get_postings(index), op2.get_postings(index))
            result = Operand(is_neg=op1.is_neg and op2.is_neg, postings=postings)
            if len(self.heap) > 0: # if there are still operands in the heap, push this result back in
                self.add(result, index)
        result.is_neg = result.is_neg ^ self.is_neg # invert the value of the result if heap is negative
        return result
