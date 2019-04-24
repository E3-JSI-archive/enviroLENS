import os
import json
from collections import defaultdict

#: Getting the folder of our collected eurlex_docs:
current_path = os.getcwd()
docs_path = os.path.join(current_path, 'eurlex_docs')

# Various statistics that we will calculate

number_of_bad_files = 0
number_of_good_files = 0
number_of_files_EN = 0
number_of_files_DE = 0
number_of_files_SI = 0

date_of_docs = defaultdict(int)

EUROVOC_descriptors = defaultdict(int)
subject_matter = defaultdict(int)

text_lengths = []

counter = 0

#: We iterate through all the documents
for filename in os.listdir(docs_path):
    counter += 1

    if counter % 1000 == 0:
        print(counter)

    #: for each of them we update our statistics counters
    with open(os.path.join(docs_path, filename), 'r') as f:
        file_data = json.load(f)
        #: if the file is completely empty, we will have to try again :D
        if len(file_data) == 0:
            number_of_bad_files += 1
        else:
            #: If the file is not empty, update all the statistics:
            number_of_good_files += 1

            if "translatedTitle_EN" in file_data:
                number_of_files_EN += 1
            if "translatedTitle_DE" in file_data:
                number_of_files_DE += 1
            if "translatedTitle_SI" in file_data:
                number_of_files_SI += 1
            
            if "dateEvents_EN" in file_data:
                if "Date of document" in file_data['dateEvents_EN']:
                    date_of_docs[file_data['dateEvents_EN']["Date of document"][0]] += 1

            if "classification_EN" in file_data:
                classification = file_data["classification_EN"]

                if classification is not None:
                
                    if "EUROVOC descriptor" in classification:
                        for tag in classification["EUROVOC descriptor"]:
                            EUROVOC_descriptors[tag] += 1
                    
                    if "Subject matter" in classification:
                        for tag in classification["Subject matter"]:
                            subject_matter[tag] += 1
            
            if "text_EN" in file_data:
                text_lengths.append(len(file_data["text_EN"]))

#: We wrap all of our collected statistics into a dictionary
analysis = {
    "number_of_good_files" : number_of_good_files,
    "number_of_bad_files" : number_of_bad_files,
    "number_of_files_EN" : number_of_files_EN,
    "number_of_files_DE" : number_of_files_DE,
    "number_of_files_SI" : number_of_files_SI,
    "EUROVOC_descriptors" : EUROVOC_descriptors,
    "subject_matter" : subject_matter,
    "text_lengths" : text_lengths,
}

#: We dump the dictionary into a json file
with open('eurlex_docs_analysis.json', 'w') as outfile:
    json.dump(analysis, outfile, indent=1)


