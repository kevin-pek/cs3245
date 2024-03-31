import os
import csv
import sys
from collections import defaultdict

def extract_query(queries_tsv_path, output_queries_path):

    with open(queries_tsv_path, mode='r', encoding='utf-8') as infile, \
         open(output_queries_path, mode='w', encoding='utf-8') as outfile:
        tsv_reader = csv.reader(infile, delimiter='\t')
        for row in tsv_reader:
            query = row[1]  # Assuming the query is the second column
            outfile.write(f"{query}\n")

def extract_expected_output(top100_tsv_path, expected_output_path):

    qid_to_docids = defaultdict(list)

    with open(top100_tsv_path, mode='r', encoding='utf-8') as file:
        tsv_reader = csv.reader(file, delimiter=' ')
        for row in tsv_reader:
            if len(row) < 6:
                continue
            qid, _, docid, _, _, _ = row
            qid_to_docids[qid].append(docid)

    with open(expected_output_path, mode='w', encoding='utf-8') as outfile:
        for qid, docids in qid_to_docids.items():
            docids_line = " ".join(docids)
            outfile.write(f"{docids_line}\n")

def extract_msmarco_docs(tsv_file_path):
    # Set a large field size limit
    maxInt = 2147483647
    csv.field_size_limit(maxInt)
    
    # Ensure the 'data' directory exists
    os.makedirs('data', exist_ok=True)

    with open(tsv_file_path, 'r', encoding='utf-8') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        
        for row in reader:
            if len(row) == 4:
                docid, url, title, body = row
                
                file_path = os.path.join('data', docid)
                
                if not os.path.exists(file_path):
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(f"URL: {url}\nTitle: {title}\nBody:\n{body}")
            else:
                print(f"Skipping row with unexpected format: {row}")

# Paths to the input and output files
# queries_tsv_path = 'docleaderboard-queries.tsv'
output_queries_txt_path = 'queries.txt'
# top100_tsv_path = 'docleaderboard-top100.tsv'
expected_output_txt_path = 'expected_output.txt'
tsv_file_path = 'msmarco-docs.tsv'  # Or wherever u put the .tsv

# extract_query(queries_tsv_path, output_queries_txt_path)
# extract_expected_output(top100_tsv_path, expected_output_txt_path)
extract_msmarco_docs(tsv_file_path)
