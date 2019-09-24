import psycopg2
import json
import os

import random
from datetime import datetime
import time

"""
With this script we will generate some dummy json responses that will mimic
json responses on the eLens miner microservice. We will sample few documents from 
all of the documents in eurlex environment only database. For each of those documents
we will create a dummy json file that will have the following structure:

{
    "id" : CELEX NUMBER,
    "title" : TITLE OF THE DOCUMENT,
    "description" : Dont yet know, probably short document preview,
    "language" : LANGUAGE OF THE DOCUMENT,
    "url" : LINK TO THE DOCUMENT ON THE EURLEX WEBPAGE,
    "descriptors" : DOCUMENT DESCRIPTORS,
    "geo-locations" : LIST OF GEO LOCATIONS,
    "wikipedia" : LIST OF WIKIPEDIA CONCEPTS (from wikifier)
}

Since we dont have geo-locations and wikipedia concepts yet in the database, those
will have to be added manually after. 
"""

# Connect to the database:
client = psycopg2.connect(user='postgres', password='dbpass',
                        database='eurlex_environment_only')
cursor = client.cursor()

# Get all possible celex numbers
cursor.execute("""
    SELECT document_celex_num FROM documents
""")
documents_celex_numbers = [e[0] for e in cursor.fetchall()]

def create_json_response(celex_number):
    """
    Given celex_number we create dummy json response dictionary
    of that documents.

    Function returns a dictionary with this structure:

    {
    "id" : CELEX NUMBER,
    "title" : TITLE OF THE DOCUMENT,
    "description" : Dont yet know, probably short document preview,
    "language" : LANGUAGE OF THE DOCUMENT,
    "url" : LINK TO THE DOCUMENT ON THE EURLEX WEBPAGE,
    "descriptors" : DOCUMENT DESCRIPTORS,
    "geo-locations" : LIST OF GEO LOCATIONS,
    "wikipedia" : LIST OF WIKIPEDIA CONCEPTS (from wikifier)
    }

    Parameters:
        celex_numbers : strings
            celex number of the document

    Returns:
        Dictionary of document data.
    """

    base_url = r'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:'

    cursor.execute(
        """
        SELECT * FROM documents WHERE document_celex_num='{}'
        """.format(celex_number)
    )

    document = cursor.fetchone()

    cursor.execute("""
        SELECT descriptor_name FROM document_descriptors WHERE document_celex_num='{}'
    """.format(celex_number))

    descriptors = [e[0] for e in cursor.fetchall()]

    data_dictonary = {
        "id" : document[1],
        "title" : document[2],
        "description" : document[-1][:150],
        "language" : "english",
        "url" : base_url + celex_number,
        "descriptors" : descriptors,
        "geo_locations" : [],
        "wikipedia" : [
            {
                "name" : 'test',
                "url" : "test",
                "cosine" : 0.5,
            }
        ]
    }

    return data_dictonary

# JSON responses can contain more documents. In the list below you can choose
# what document sizes do you want in the output.
SAMPLE_SIZES = [2,2,1,4]

for sample_size in SAMPLE_SIZES:

    doc_dictionaries = []
    sample = random.sample(documents_celex_numbers, sample_size)

    for celex_number in sample:
        doc_dictionaries.append(create_json_response(celex_number))
    
    # Save this as a json response. Name will be the unix timestamp.
    filename = str(int(datetime.now().timestamp())) + '.json'
    path = os.path.join(os.getcwd(), 'dummy_json_responses', filename) 
    with open(path, 'w', encoding='utf-8')as outfile:
        json.dump(
            doc_dictionaries, outfile, indent=1
        )

    time.sleep(1)



