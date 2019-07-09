import json
import os

with open('environmental_descriptors.json', 'r') as infile:
    environment_descriptors = set(json.load(infile).keys())

def is_document_environment_related(doc):
    """
    Function that takes a document data (dictionary in our regular format) as input
    and checks whether any of documents descriptors are contained inside environment
    descriptors.
    """

    if 'classification_EN' in doc:
        if 'EUROVOC descriptor' in doc['classification_EN']:
            for descriptor in doc['classification_EN']['EUROVOC descriptor']:
                if descriptor in environment_descriptors:
                    return True
    
    return False

datafolder = 'testdata'
path = os.getcwd()
datapath = os.path.join(path, datafolder)

environment_documents = []

for fname in os.listdir(datapath):
    with open(os.path.join(datapath, fname), 'r') as infile:
        document = json.load(infile)

        if is_document_environment_related(document):
            celex_num = fname[:-5]
            environment_documents.append(celex_num)

with open('environment_documents.json', 'w') as outfile:
    json.dump(environment_documents, outfile, indent=1)
