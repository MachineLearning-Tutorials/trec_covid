"""
Get various stats for TREC_COVID
"""

import os
import argparse
import json
import csv


def read_docids(docid_list):
    required_docids = set()
    count = 0
    with open(docid_list) as f:
        for line in f:
            docid = line.strip()
            #if docid in required_docids:
            #    print (f'redundant: {docid}')
            required_docids.add(docid)
            count += 1

    print (f'\tProcessed {count} lines and found {len(required_docids)} docids')
    return required_docids


def has_info(row, file_path):
    has_title = False           
    has_abstract = False            
    has_fulltext = False            

    if row['title']:
        has_title = True

    if row['abstract']:
        has_abstract = True

    if file_path:
        try:
            file_data = json.load(open(file_path))
        except Exception as e:
            print (f'Warning: error when parsing {file_path}')
        else:
            if 'metadata' in file_data:
                if (
                    'title' in file_data['metadata'] 
                    and file_data['metadata']['title']
                ):
                    has_title = True

                if (
                    'abstract' in file_data['metadata'] 
                    and file_data['metadata']['abstract']
                ):
                    has_abstract = True

            if (
                'body_text' in file_data 
                and file_data['body_text']
            ):
                has_fulltext = True
            
    return has_title, has_abstract, has_fulltext

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data_dir')
    parser.add_argument('docid_list')
    args=parser.parse_args()

    print (f'Process docids {args.docid_list}')
    required_docids = read_docids(args.docid_list)

    meta_file = os.path.join(args.data_dir, 'metadata.csv')
    not_covered_count = 0
    pmc_only_count = 0
    pdf_only_count = 0
    both_json_count = 0
    no_json_count = 0
    title_count = 0
    abstract_count = 0
    fulltext_count = 0

    with open(meta_file, newline='') as csvfile:
        meta_reader = csv.DictReader(csvfile)
        for row in meta_reader:
            cord_uid = row['cord_uid']
            if cord_uid not in required_docids:
                not_covered_count += 1
                continue

            required_docids.discard(cord_uid)

            #check pdf conditions
            file_path = None
            if row['has_pmc_xml_parse'] == 'True':
                file_path = os.path.join(
                    args.data_dir, 
                    row['full_text_file'],
                    'pmc_json', 
                    f'{row["pmcid"]}.xml.json'
                )
                if row['has_pdf_parse'] == 'True':
                    both_json_count += 1
                else:
                    pmc_only_count += 1
            elif row['has_pdf_parse'] == 'True':
                sha = row['sha'].split(';')[0]
                file_path = os.path.join(
                    args.data_dir, 
                    row['full_text_file'],
                    'pdf_json', 
                    f'{sha}.json'
                )
                pdf_only_count += 1
            else:
                no_json_count += 1

            #check abstract and full text
            
            has_title, has_abstract, has_fulltext = has_info(row, file_path)
            
            if has_title:
                title_count += 1
            if has_abstract:
                abstract_count += 1
            if has_fulltext:
                fulltext_count += 1

    print (f'There are {not_covered_count} documents are not in the list')
    print (f'There are {len(required_docids)} documents are missing')
    print (f'Missing documents are {required_docids}')

    print (f'There are {title_count} documents have title')
    print (f'There are {abstract_count} documents have abstract')
    print (f'There are {fulltext_count} documents have fulltext')




if __name__=='__main__':
    main()


