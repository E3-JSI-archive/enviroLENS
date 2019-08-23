import json

class Search():
    """
    Class that is used to find documents that contain given terms.

    Attributes:
        doc2id : dict(str, int)
            dictionary that maps document celex numbers to ids
        id2doc : dict(int, str)
            dictionay that maps ids to document celex numbers
    """

    def __init__(self):
        """
        We unload the data from index.json file.
        """

        with open('index.json', 'r', encoding='utf-8') as infile:
            data = json.load(infile)

        self.doc2id = data['doc2id']
        self.id2doc = data['id2doc']
        self.index = data['index']
    
    def test(self):
        print(len(self.doc2id))

mysearch = Search()
mysearch.test()