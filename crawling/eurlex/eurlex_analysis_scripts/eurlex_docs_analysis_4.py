import os
import json
from collections import defaultdict

#: Getting the folder of our collected eurlex_docs:
current_path = os.path.dirname(os.getcwd())
docs_path = os.path.join(current_path, 'eurlex_docs_small')

# Various statistics that we will calculate. Aggregated on year basis.

statistics = defaultdict(int)

counter = 0

countries = set()

with open('countries.txt', 'r') as infile:
    for line in infile:
        line = line.strip().split('|')
        countries.add(line[1].lower())

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
            pass
        else:
            if "classification_EN" in file_data:
                classification = file_data["classification_EN"]

                if classification is not None:
                    if 'EUROVOC descriptor' in classification:
                        if 'forest' in classification['EUROVOC descriptor']:
                            if 'text_EN' in file_data:
                                if len(file_data['text_EN']) > 67:
                                    print(filename)
                    




#: We wrap all of our collected statistics into a dictionary
analysis = {
    "statistics" : statistics
}

#: We dump the dictionary into a json file
with open('eurlex_docs_analysis_4.json', 'w') as outfile:
    json.dump(analysis, outfile, indent=1)
