import json
import os

def save(filename, obj):
    """
    Save *obj* into json file named *filename* 
    """
    with open(filename, 'w') as outfile:
        json.dump(obj, outfile, indent = 1)

# We load up our previously created analysis of the dataset
with open('eurlex_docs_analysis.json', 'r') as infile:
    analysis = json.load(infile)

# Uncomment the one on which you wish to do the classification
# CLASSIFICATOR = 'EUROVOC_descriptors'
CLASSIFICATOR = 'subject_matter'

# We will keep track of our already classified positive and negative examples.
# When we are going through descriptors we will first check whether we have already
# classified this descriptor and if now, we will give user the option to classify it.

POSITIVE = CLASSIFICATOR + '_environment_related_TRUE.json'
NEGATIVE = CLASSIFICATOR + '_environment_related_FALSE.json'

if POSITIVE in os.listdir(os.getcwd()):
    with open(POSITIVE, 'r') as infile:
        positive_examples = set(json.load(infile))
else:
    positive_examples = set()

if NEGATIVE in os.listdir(os.getcwd()):
    with open(NEGATIVE, 'r') as infile:
        negative_examples = set(json.load(infile))
else:
    negative_examples = set()

# All of our avaiable classificators
to_be_determined = analysis[CLASSIFICATOR]

for example in to_be_determined:
    if example not in positive_examples and example not in negative_examples:

        decision = input('Example: {} : If this is a positive examples, press y and return, otherwise press n and return\n'.format(example))
        
        if decision == 'y':
            positive_examples.add(example)
            save(POSITIVE, list(positive_examples))
        elif decision == 'n':
            negative_examples.add(example)
            save(NEGATIVE, list(negative_examples))
        else:
            print('Object {} unclassified since your input didnt match any of (y/n). Your input : {}'.format(example, decision))

