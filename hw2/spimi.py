import sys
import linecache
import heapq
import pickle
import os
from linkedlist import LinkedList, union

class SPIMI:
    def __init__(self, blocks_path, memory_limit) -> None:
        self.blocks_path = blocks_path
        self.memory_limit = memory_limit

    def invert(self, pairs: list[tuple[str, int]]) -> None:
        """
        Creates index based on given list of token-id pairs. Writes block to disk
        everytime the index size reaches or exceeds memory limit.
        """
        index = {}
        block_num = 1
        for term, id in pairs:
            postings = index.get(term, set())
            postings.add(id)
            if term not in index:
                index[term] = postings
            if sys.getsizeof(index) >= self.memory_limit:
                self.write_block(index, block_num)
                index = {}
                block_num += 1
        if index: # write last block if there are remaining entries
            self.write_block(index, block_num)

    def write_block(self, index, block_num) -> None:
        """Writes given list of pairs to text file with given block number."""
        pairs = sorted(index.items(), key=lambda x: x[0])
        block = open(f'{self.blocks_path}block-{block_num}.txt', 'w')
        for i, (term, postings) in enumerate(pairs):
            block.write(f'{term}\t{",".join(map(str, sorted(postings)))}')
            if i < len(pairs) - 1: # add newline character if not last entry
                block.write('\n')
        block.close()

    def read_block(self, file, line_no) -> tuple[str, LinkedList] | None:
        """Reads from the blockfile specified and returns the term-posting pair."""
        line = linecache.getline(os.path.join(self.blocks_path, file), line_no)
        if line:
            term, postings_str = line.strip().split('\t')
            postings = LinkedList.from_list(list(map(int, postings_str.split(','))))
            return term, postings

    def merge_blocks(self, out_dict: str, out_postings: str):
        """n-way merge for all blocks, writes merged index into dictionary and postings file."""
        pq = [] # min heap that stores (term, block file index, line number)
        files = [] # list of block file names
        file_ptrs = [] # keep track of line numbers at each file
        # read in the first line of each block
        for i, file in enumerate(os.listdir(self.blocks_path)):
            files.append(file)
            file_ptrs.append(1)
            term = linecache.getline(os.path.join(self.blocks_path, file), 1).split('\t')[0]
            heapq.heappush(pq, (term, i, 1))

        dict = {}
        f_postings = open(out_postings, 'wb')
        while pq:
            # get the current smallest term and postings in the heap
            _, i, line_no = heapq.heappop(pq)
            term, postings = self.read_block(files[i], line_no)

            # check if there are duplicate terms, if so find and merge all of them
            next_term_list = heapq.nsmallest(1, pq, key=lambda x: x[0])
            while next_term_list and next_term_list[0][0] == term: # merge identical terms
                # load the duplicate term from its file and merge the posting lists
                _, j, next_line_no = heapq.heappop(pq)
                _, next_postings = self.read_block(files[j], next_line_no)
                postings = union(postings, next_postings) # join posting list

                # peek at next line in the file and push it to the heap
                file_ptrs[j] += 1
                new_line = self.read_block(files[j], file_ptrs[j])
                if new_line: # if no more terms in file we can ignore it
                    heapq.heappush(pq, (new_line[0], j, file_ptrs[j]))
                next_term_list = heapq.nsmallest(1, pq) # peek at next term to see if loop should continue

            # write posting to disk
            offset = f_postings.tell() # calculate offset for current postings list
            dict[term] = (len(postings), offset)
            pickle.dump(postings.to_list(), f_postings)

            # book keeping
            file_ptrs[i] += 1
            new_line = linecache.getline(os.path.join(self.blocks_path, files[i]), file_ptrs[i])
            if new_line: # if there is still a next line, add it to the pq
                new_term = new_line.strip().split('\t', 1)[0]
                heapq.heappush(pq, (new_term, i, file_ptrs[i]))

        # write dictionary to disk and close files
        f_postings.close()
        f_dict = open(out_dict, 'wb')
        pickle.dump(dict, f_dict)
        f_dict.close()
