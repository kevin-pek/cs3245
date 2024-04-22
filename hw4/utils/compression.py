import os
import unittest
import pickle


"""Contains code for compressing and decompressing both the posting list using
gap and variable byte encoding, and compressing the dictionary by representing
it as a string and using frontcoding."""


def gap_encode(num_list: list[int]) -> list[int]:
    """Converts list of numbers sorted in ascending order into list of numbers
    that represent the gap between consecutive items."""
    if not num_list:
        return []
    nums = [num_list[0]]
    for i in range(1, len(num_list)):
        nums.append(num_list[i] - num_list[i - 1])
    return nums


def vb_encode(number: int) -> bytes:
    """Encode number into byte array using variable encoding."""
    if number == 0:
        return bytes([0])
    byte_arr = bytearray()
    while number > 0:
        byte_arr.append(number % 128)
        number = number >> 7
    byte_arr[0] |= 128 # for last byte, set the leftmost bit to 1
    byte_arr.reverse() # reverse list since we were appending to the list
    return byte_arr


def vb_decode(byte_arr: bytes) -> list[int]:
    """Decode variable encoded bytes into original list of integers."""
    nums = []
    curr = 0
    for byte in byte_arr:
        if byte & 128: # if continuation bit is present means last byte
            curr = (curr << 7) | (byte & 0x7F)
            nums.append(curr)
            curr = 0
        else: # add the bits from the next byte to the number
            curr = (curr << 7) | (byte & 0x7F)
    return nums # return number directly if theres only one


def gap_decode(num_list: list[int]) -> list[int]:
    if not num_list:
        return []
    nums = [num_list[0]]
    for n in num_list[1:]:
        nums.append(nums[-1] + n)
    return nums


def compress_and_save_dict(dictionary: dict[str, tuple[int, int]], out_dict: str):
    """Save dictionary terms as a string in a separate file with frontcoding."""
    with open(out_dict, "wb") as d, open(f"{out_dict}_str", "w") as ds:
        terms = sorted(dictionary.keys())
        prev = terms[0]
        dict_entries = [dictionary[terms[0]]]
        ds.write(f"0:{prev}\n")
        for term in terms[1:]:
            prefix_len = 0
            for i in range(min(len(prev), len(term))):
                if term[i] != prev[i]:
                    break
                prefix_len += 1
            suffix = term[prefix_len:]
            ds.write(f"{prefix_len}:{suffix}\n") # each new term begins at "0"
            df, offset = dictionary[term]
            dict_entries.append((df, offset))
            prev = term
        # save list of dictionary entries without the terms in a separate file
        pickle.dump(dict_entries, d)


def load_dict(dict_file: str) -> dict[str, tuple[int, int]]:
    with open(dict_file, "rb") as d, open(f"{dict_file}_str", "r") as ds:
        index = {}
        prev = ""
        for entry in pickle.load(d):
            df, posting_offset = entry
            line = ds.readline().strip()
            prefix_len_str, suffix = line.split(":")
            prefix_len = int(prefix_len_str)
            if prefix_len == 0: # if prefix len is 0 we have a full term
                term = suffix
            else: # otherwise we add the suffix to the common prefix of the previous term
                term = prev[:prefix_len] + suffix
            index[term] = (df, posting_offset)
            prev = term
    return index


# TESTS FOR GAP AND VARIABLE BYTE ENCODING DECODING
class TestPostingCompression(unittest.TestCase):
    def test_vb_encode_decode(self):
        test_cases = [1, 127, 128, 300, 16384, 2097151, 268435455]
        for number in test_cases:
            with self.subTest(number=number):
                encoded = vb_encode(number)
                decoded = vb_decode(encoded)
                print(f"EXPECTED: {number}")
                print(f"RECEIVED: {decoded[0]}")
                self.assertEqual(decoded[0], number, "Failed variable byte encoding")

    def test_delta_encode_decode(self):
        test_cases = [
            [1, 2, 3, 4, 5],
            [100, 105, 110, 115, 120],
            [1000, 1010, 1025, 1050, 1100]
        ]
        for numbers in test_cases:
            with self.subTest(numbers=numbers):
                encoded = list(gap_encode(numbers))
                decoded = gap_decode(encoded)
                print(f"EXPECTED: {numbers}")
                print(f"RECEIVED: {decoded}")
                self.assertEqual(decoded, numbers, "Failed gap encoding")

    def test_combined_vb_delta_encode_decode(self):
        numbers = [100, 228, 300, 23000, 23100]
        deltas = gap_encode(numbers)
        vb_encoded_deltas = bytes(b for delta in deltas for b in vb_encode(delta))
        vb_decoded_deltas = vb_decode(vb_encoded_deltas)
        decoded_numbers = gap_decode(vb_decoded_deltas)
        print(f"EXPECTED: {numbers}")
        print(f"RECEIVED: {decoded_numbers}")
        self.assertEqual(decoded_numbers, numbers, "Failed combining variable and gap encoding")


class TestDictionaryCompression(unittest.TestCase):
    def setUp(self):
        self.test_dict = {
            'apple': (10, 100),
            'applet': (5, 150),
            'banana': (20, 200),
            'band': (7, 250)
        }
        self.dict_file = 'test_dict'

    def tearDown(self):
        os.remove(self.dict_file)
        os.remove(f"{self.dict_file}_str")

    def test_compress_and_load_dict(self):
        compress_and_save_dict(self.test_dict, self.dict_file)
        loaded_dict = load_dict(self.dict_file)
        print("EXPECTED: ", self.test_dict)
        print("RECEIVED: ", loaded_dict)
        self.assertEqual(self.test_dict, loaded_dict, "Loaded dictionary should match the original")


if __name__ == "__main__":
    unittest.main()

