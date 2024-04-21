import re
from nltk import sent_tokenize, word_tokenize, PorterStemmer

"""
Functions to preprocess dataset and extract information from text to help with
index construction and query handling.
"""

stemmer = PorterStemmer()

def get_terms(document: str):
    stop_words = ['appellant', 'respondent', 'plaintiff', 'defendant', 'mr', 'dr', 'mdm', 'court', 
                  'version', 'case', 'court', 'statement', 'line', 'para', 'fact']
    terms = []
    for sentence in sent_tokenize(document):
        sentence = re.sub(r'[-/]', ' ', sentence)  # Split words based on hyphens and slashes
        for word in word_tokenize(sentence):
            # remove non alphanumeric character, but keep periods that are found
            # between 2 numbers as they are likely part of a decimal number
            word = re.sub(r'(?<!\d)\.(?!\d)|[^\w\d.]', '', word)

            # Check if word is ASCII to ensure it's likely English
            if word.isascii() and word not in stop_words and word.isalnum():
                terms.append(stemmer.stem(word.lower()))
    return terms

def simplify_court(court):
    court_abbreviations = {
        'CA Supreme Court': 'SCR',
        'Federal Court of Australia': 'FCA',
        'HK Court of First Instance': 'CFI',
        'HK High Court': 'HKHC',
        'High Court of Australia': 'HCA',
        'Industrial Relations Court of Australia': 'IRCA',
        'NSW Administrative Decisions Tribunal (Trial)': 'NSWADT',
        'NSW Children\'s Court': 'NSWCC',
        'NSW Civil and Administrative Tribunal': 'NCAT',
        'NSW Court of Appeal': 'NSWCA',
        'NSW Court of Criminal Appeal': 'NSWCCA',
        'NSW District Court': 'NSWDC',
        'NSW Industrial Court': 'NSWIC',
        'NSW Industrial Relations Commission': 'NSWIRC',
        'NSW Land and Environment Court': 'NSWLEC',
        'NSW Local Court': 'NSWLC',
        'NSW Medical Tribunal': 'NSWMT',
        'NSW Supreme Court': 'NSWSC',
        'SG Court of Appeal': 'SGCA',
        'SG District Court': 'SGDC',
        'SG Family Court': 'SGFC',
        'SG High Court': 'SGHC',
        'SG Magistrates\' Court': 'SGMC',
        'SG Privy Council': 'SGPC',
        'Singapore International Commercial Court': 'SICC',
        'UK Court of Appeal': 'EWCA',
        'UK Crown Court': 'UKCC',
        'UK High Court': 'EWHC',
        'UK House of Lords': 'UKHL',
        'UK Military Court': 'UKMC',
        'UK Supreme Court': 'UKSC',
    }
    return court_abbreviations.get(court, court)

def clean_content(text, keyword="supreme court of canada citation"):
    # Find the position of the keyword in the text
    pos = text.lower().find(keyword.lower())
    # If the keyword is found, slice the text from the keyword onwards
    if pos != -1:
        return text[pos:]
    else:
        return text


def extract_citations(legal_case):
    patterns = [
        r"\[(\d{4})\] ([A-Z]+(?:\([A-Z]+\))? \d+)",     # Basic [YYYY] CourtAbbr Number
        r"\((\d{4})\) (\d+) ([A-Z]+ \d+)",               # (YYYY) Number CourtAbbr Number
        r"(\d{4}) ([A-Z]+(?: [A-Z]+)? \d+)(?:;|,|\sand\s)?", # YYYY CourtAbbr Number with optional end separators
        r"(\d{4}) ([A-Z]+ \d+); \[(\d{4})\] (\d+ [A-Z]+ \d+)",  # Multi citations
        r"\[([\d]{4})\] ([A-Z]+(?:[A-Za-z]*[ ]?[A-Z]*[a-z]*)* \d+)",  # Advanced pattern for EWCA Civ or Crim scenario
        r"\[([\d]{4})\] (\d+ [A-Z]+(?:\([A-Z]+\))? \d+)"    # [YYYY] Number CourtAbbr Number, for non-English char
    ]

    result = {}

    # start by finding the yyyy to split
    split_position = re.search(r"\d{4}", legal_case).start() - 2
    case_name = legal_case[:split_position].strip()
    citation_part = legal_case[split_position:]

    citations = []

    # Apply patterns and extract citations
    for pattern in patterns:
        matches = re.finditer(pattern, citation_part)
        for match in matches:
            matched = match.group(0)
            if matched == '':
                continue
            if ';' in matched:
                matched1, matched2 = matched.split(';')
                if matched1 != '':
                    citations.append(matched1.strip().upper())
                if matched2 != '':
                    citations.append(matched2.strip().upper())
                continue

            citations.append(matched.upper())
            

    
    result[case_name] = list(set(citations)) # Remove duplicates

    return result

def test_extract_citations(): # for testing purposes
    test_cases = [
        ("Morin v. The Queen (1890) 18 SCR 407", ["(1890) 18 SCR 407"]),
        ("R. v. R.L. 2013 SCC 54; [2013] 3 SCR 418", ["2013 SCC 54", "[2013] 3 SCR 418"]),
        ("Carratt v R [2016] NSWDC 7", ["[2016] NSWDC 7"]),
        ("R v Watson-Wood, Daniel [2017] NSWDC 410", ["[2017] NSWDC 410"]),
        ("Troy Robert Dunning v Neata Glass Service Pty Ltd [1995] IRCA 630", ["[1995] IRCA 630"]),
        ("M v The Queen [1994] HCA 63", ["[1994] HCA 63"]),
        ("香港特別行政區 訴 港銀財務有限公司  [2016] 3 HKLRD 477", ["[2016] 3 HKLRD 477"]),
        ("Rhodes v OPO & Anor [2015] UKSC 32", ["[2015] UKSC 32"]),
        ("G Ravichander v Public Prosecutor [2002] SGHC 167", ["[2002] SGHC 167"]),
        ("Jeyaretnam JB v Goh Chok Tong [1989] SGPC 2", ["[1989] SGPC 2"]),
        ("Burstow R v. Ireland, R v. [1997] UKHL 34", ["[1997] UKHL 34"]),
        ("Scott Herden and Tearoc Pty Ltd [2007] NSWIRComm 1051", ["[2007] NSWIRComm 1051"]),
        ("Public Prosecutor v Soh Sim Teck [2005] SGMC 35", ["[2005] SGMC 35"]),
        ("Sharari v Director General, Transport NSW [2011] NSWADT 196", ["[2011] NSWADT 196"]),
        ("R v Adam Easton [2017] NSWLC 19", ["[2017] NSWLC 19"]),
        ("CPIT Investments Ltd v Qilin World Capital Ltd and another [2017] SGHC(I) 5", ["[2017] SGHC(I) 5"]),
        ("Trinh v R [2016] NSWCCA 110", ["[2016] NSWCCA 110"]),
        ("R v Cornwell [2016] NSWSC 767", ["[2016] NSWSC 767"]),
        ("Agius v The Queen [2013] HCA 27", ["[2013] HCA 27"]),
        ("Lim Swee Thong v Public Prosecutor [1994] SGCA 40", ["[1994] SGCA 40"]),
        ("Citation Resources Ltd v Landau [2016] FCA 1114", ["[2016] FCA 1114"]),
        ("R v Carl McManaman [2016] EWCA CRIM 3", ["[2016] EWCA CRIM 3"]),
        ("The Queen on the application of The Friends of Finsbury Park v Haringey London Borough Council and Others [2017] EWCA Civ 1831", ["[2017] EWCA CIV 1831"]),
        ("R v Bhadresh Babulal Gohil and R v Ellias Nimoh Prek [2018] EWCA Crim 140", ["[2018] EWCA CRIM 140"]),
        ("ITN News and Others v R [2013] EWHC 773", ["[2013] EWHC 773"]),
        ("Attorney General v Ho Tee Ming [1969] SGFC 2", ["[1969] SGFC 2"]),
        ("Garrett v Freeman (No. 3) [2007] NSWLEC 139", ["[2007] NSWLEC 139"]),
        ("Police v DH [2014] NSWChC 3", ["[2014] NSWChC 3"]),
        ("Health Care Complaints Commission v Rolleston [2013] NSWMT 12", ["[2013] NSWMT 12"]),
        ("Dinh v Commissioner for Fair Trading [2016] NSWCATOD 72", ["[2016] NSWCATOD 72"])
    ]

    results = {}
    for case, expected in test_cases:
        result = extract_citations(case)
        case_name = list(result.keys())[0]
        extracted_citations = result[case_name]
        test_result = expected==extracted_citations
        if test_result == False:
            print(f"Case: {case}\nExpected: {expected}\nActual: {extracted_citations}\n")