import csv
from collections import defaultdict

def convert_queries_to_text(queries_tsv_path, output_queries_txt_path):
    """
    Convert queries from a TSV file to a plain text file with one query per line.
    """
    with open(queries_tsv_path, mode='r', encoding='utf-8') as infile, \
         open(output_queries_txt_path, mode='w', encoding='utf-8') as outfile:
        tsv_reader = csv.reader(infile, delimiter='\t')
        for row in tsv_reader:
            query = row[1]  # Assuming the query is the second column
            outfile.write(f"{query}\n")

def create_expected_output_file(top100_tsv_path, expected_output_txt_path):
    """
    Create a text file with expected docids for each query from the top100 TSV file, organized by qid.
    """
    qid_to_docids = defaultdict(list)

    with open(top100_tsv_path, mode='r', encoding='utf-8') as file:
        tsv_reader = csv.reader(file, delimiter=' ')
        for row in tsv_reader:
            if len(row) < 6:
                continue  # Skip rows that do not have the expected number of elements
            qid, _, docid, _, _, _ = row
            qid_to_docids[qid].append(docid)

    with open(expected_output_txt_path, mode='w', encoding='utf-8') as outfile:
        for qid, docids in qid_to_docids.items():
            # Join the document IDs into a space-separated string
            docids_line = " ".join(docids)
            outfile.write(f"{docids_line}\n")

# Paths to the input and output files
queries_tsv_path = 'docleaderboard-queries.tsv'
output_queries_txt_path = 'queries.txt'
top100_tsv_path = 'docleaderboard-top100.tsv'
expected_output_txt_path = 'expected_output.txt'

# Function calls (commented out for safety)
convert_queries_to_text(queries_tsv_path, output_queries_txt_path)
create_expected_output_file(top100_tsv_path, expected_output_txt_path)
