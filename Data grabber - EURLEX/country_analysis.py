import json 
import os
from collections import defaultdict

def get_attribute_or_none(object, name):
    try:
        return object[name]
    except:
        return []
    
##COUNTRY = ['albania']
##COUNTRY = ['macedonia']
##COUNTRY = ['montenegro']
##COUNTRY = ['armenia']
COUNTRY = ['georgia']

PATH = os.getcwd()
DOCS_PATH = os.path.join(PATH, 'eurlex_docs')

number_of_files = 0
number_of_files_EN = 0
number_of_files_DE = 0
number_of_files_SI = 0

date_of_docs = defaultdict(int)

EUROVOC_descriptors = defaultdict(int)
subject_matter = defaultdict(int)

celex = []

text_lengths = []

# Load up environment related documents:
with open('environment_documents.json', 'r') as infile:
    environment_docs = set(json.load(infile))

for filename in os.listdir(DOCS_PATH):

    if filename[:-5] not in environment_docs:
        continue

    with open(os.path.join(DOCS_PATH, filename), 'r') as infile:
        document_data = json.load(infile)
    
    title = get_attribute_or_none(document_data, 'translatedTitle_EN')
    classification = get_attribute_or_none(document_data, 'classification_EN')
    descriptors = get_attribute_or_none(classification, 'EUROVOC descriptor')
    subjects = get_attribute_or_none(classification, 'Subject matter')
    text = get_attribute_or_none(document_data, 'text_EN')

    descriptors = [e.lower() for e in descriptors]
    subjects = [e.lower() for e in subjects]

    is_document_interesting = False

    for country in COUNTRY:
        if country in title.lower():
            is_document_interesting = True
        if country in descriptors:
            is_document_interesting = True
        if country in subjects:
            is_document_interesting = True
    
    # Document is environment related and it contains word Albania
    if is_document_interesting:

        celex.append(filename[:-5])

        number_of_files += 1

        if "translatedTitle_EN" in document_data:
            number_of_files_EN += 1
        if "translatedTitle_DE" in document_data:
            number_of_files_DE += 1
        if "translatedTitle_SI" in document_data:
            number_of_files_SI += 1

        if "dateEvents_EN" in document_data:
            if "Date of document" in document_data['dateEvents_EN']:
                date_of_docs[document_data['dateEvents_EN']["Date of document"][0]] += 1

        if "classification_EN" in document_data:
            classification = document_data["classification_EN"]

            if classification is not None:
            
                if "EUROVOC descriptor" in classification:
                    for tag in classification["EUROVOC descriptor"]:
                        EUROVOC_descriptors[tag] += 1
                
                if "Subject matter" in classification:
                    for tag in classification["Subject matter"]:
                        subject_matter[tag] += 1
        
        if "text_EN" in document_data:
            text_lengths.append(len(document_data["text_EN"]))

statistics = {
    'number_of_files' : number_of_files,
    'number_of_files_EN' : number_of_files_EN,
    'number_of_files_DE' : number_of_files_DE,
    'number_of_files_SI' : number_of_files_SI,
    'dates' : date_of_docs,
    'EUROVOC_descriptors' : EUROVOC_descriptors,
    'subject_matter' : subject_matter,
    'text_lengths' : text_lengths,
    'celex_nums' : celex
}

with open(f'analysis_{COUNTRY[0]}.json', 'w') as outfile:
    json.dump(statistics, outfile, indent=1)
