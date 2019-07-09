import os
import json
from collections import defaultdict

#: Getting the folder of our collected eurlex_docs:
current_path = os.path.dirname(os.getcwd())
docs_path = os.path.join(current_path, 'eurlex_docs')

#: environmental documents
with open('environment_documents.json', 'r') as infile:
    environment_documents = set(json.load(infile))

# Various statistics that we will calculate. Aggregated on year basis.

statistics = {}

counter = 0

#: We iterate through all the documents
for filename in os.listdir(docs_path):

    if filename[:-5] not in environment_documents:
        continue

    counter += 1

    if counter % 1000 == 0:
        print(counter)

    #: for each of them we update our statistics counters
    with open(os.path.join(docs_path, filename), 'r') as f:
        file_data = json.load(f)
        #: if the file is completely empty, we will have to try again :D
        if len(file_data) == 0:
            pass
        else:
            #: If the file is not empty, update all the statistics:
            try:
                date_of_docs = file_data['dateEvents_EN']["Date of document"][0]
                year_of_document = int(date_of_docs.split('/')[2])

                # In case this is the first time we encounter this particular year, we have to create a new dict
                if year_of_document not in statistics:
                    statistics[year_of_document] = {
                        "count_docs" : 0,
                        "number_of_files_EN" : 0,
                        "number_of_files_DE" : 0,
                        "number_of_files_SI" : 0,
                        "num_of_descriptors" : 0,
                        "num_of_subjects" : 0,
                        "text_lengths" : []
                    }

                statistics[year_of_document]['count_docs'] += 1
                
                if "translatedTitle_EN" in file_data:
                    statistics[year_of_document]["number_of_files_EN"] += 1
                if "translatedTitle_DE" in file_data:
                    statistics[year_of_document]["number_of_files_DE"] += 1
                if "translatedTitle_SI" in file_data:
                    statistics[year_of_document]["number_of_files_SI"] += 1

                if "classification_EN" in file_data:
                    classification = file_data["classification_EN"]

                    if classification is not None:
                        if "EUROVOC descriptor" in classification:
                            statistics[year_of_document]["num_of_descriptors"] += len(classification["EUROVOC descriptor"])
                        if "Subject matter" in classification:
                            statistics[year_of_document]["num_of_subjects"] += len(classification["Subject matter"])
                
                if "text_EN" in file_data:
                    statistics[year_of_document]["text_lengths"].append(len(file_data["text_EN"]))

            except:
                # We only care about the documents that have their date given.
                pass


#: We wrap all of our collected statistics into a dictionary
analysis = {
    "statistics" : statistics
}

#: We dump the dictionary into a json file
with open('eurlex_analysis_2_environment.json', 'w') as outfile:
    json.dump(analysis, outfile, indent=1)
