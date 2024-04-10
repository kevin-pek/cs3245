from math import sqrt

"""
Functions to handle boolean retrieval and phrase query logic.
"""

class Node:
    def __init__(self, id, next = None):
        self.id = id
        self.next = next
        self.skip = None

class LinkedList:
    def __init__(self, head = None):
        self.head = head
        self.length = 0

    @classmethod
    def from_list(cls, postings):
        llist = cls(Node(-1))
        curr = llist.head
        for p in postings:
            node = Node(p)
            curr.next = node
            curr = curr.next
            llist.length += 1
        llist.head = llist.head.next
        return llist

    def to_list(self) -> list[str]:
        result = []
        curr = self.head
        while curr:
            result.append(curr.id)
            curr = curr.next
        return result

    def add_skip_pointers(self):
        """Add skip pointers from scratch for the LinkedList."""
        if self.length <= 2: # if list has length 2 or less no pointers needed
            return
        curr, jump_point = self.head, self.head
        skip_len = self.length // sqrt(self.length)
        i = 0
        while curr:
            if curr.skip: # remove old skip pointers
                curr.skip = None
            if i == skip_len: # if we have gone past enough entries we add a skip pointer
                jump_point.skip = curr
                jump_point = curr
                i = 0
            i += 1
            curr = curr.next

    def __repr__(self) -> str:
        return 'LinkedList: ' + str(self.length)

    def __len__(self):
        return self.length

def intersect(p1: LinkedList | None, p2: LinkedList | None):
    if not p1 or not p2:
        return None
    ans = LinkedList(Node(-1)) # initialise LinkedList with a dummy node
    h1, h2 = p1.head, p2.head
    curr = ans.head
    while h1 and h2:
        if h1.id < h2.id:
            if not h1.skip or h1.skip.id > h2.id:
                h1 = h1.next
                continue
            while h1.skip and h1.skip.id <= h2.id:
                h1 = h1.skip
        elif h1.id > h2.id:
            if not h2.skip or h2.skip.id > h1.id:
                h2 = h2.next
                continue
            while h2.skip and h2.skip.id <= h1.id:
                h2 = h2.skip
        else: # when postings are identical, add it to the answer
            curr.next = Node(h1.id)
            ans.length += 1
            curr = curr.next
            h1 = h1.next
            h2 = h2.next
    ans.head = ans.head.next # remove dummy head
    return ans

