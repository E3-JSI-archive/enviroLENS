import json

class Indexer():
    """
    Class that can be used to index documents from the database.
    """

    def __init__(self):
        """
        We unload the data from index.json file.
        """
        with open('index.json', 'w') as infile:
            data = json.load(infile)
        self.doc2id = data['doc2id']
        self.id2doc = data['id2doc']
        self.index = data['index']
    
    