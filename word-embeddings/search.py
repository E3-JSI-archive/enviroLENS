import json
from collections import defaultdict

class Search():
    """
    Class that is used to find documents that contain given terms.

    Attributes:
        doc2id : dict(str, int)
            dictionary that maps document celex numbers to ids
        id2doc : dict(int, str)
            dictionay that maps ids to document celex numbers
        index : dict(word, list(int))
            dictionary containing words and document ids in which the word appears in
    """

    def __init__(self):
        """
        We unload the data from index.json file.
        """

        with open('index2.json', 'r', encoding='utf-8') as infile:
            data = json.load(infile)

        self.doc2id = data['doc2id']
        self.id2doc = data['id2doc']
        self.index = data['index']
    
    def find_documents_given_query(self, query):
        """
        Function that will based on the given query return document ids that contain it.

        Parameters:
            query : list of strings
                list of words that we are looking for
        
        Returns:
            list of celex number of found documents sorted by best to worst match
        """

        document_id_frequency = defaultdict(int)

        # We iterate through every word and for each document id we count how many of the query words
        # it contatins. The more the better.
        for word in query:
            if word in self.index:
                for document_id in self.index[word]:
                    document_id_frequency[document_id] += 1
        
        highest_frequency = [(freq, doc_id) for doc_id, freq in document_id_frequency.items()]
        highest_frequency.sort(reverse=True)

        # Transform ids to celex
        transformed_to_celex = [self.id2doc[str(docid)] for _,docid in highest_frequency[:10] if str(docid) in self.id2doc]
        
        return transformed_to_celex


if __name__ == '__main__':
    mysearch = Search()
    res = mysearch.find_documents_given_query(['environment', 'water', 'oil'])
    print(res)