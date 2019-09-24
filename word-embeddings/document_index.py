import json
from collections import defaultdict

from modules.library.postgresql import PostgresQL

from nltk.corpus import stopwords
from gensim.parsing.preprocessing import preprocess_string, strip_tags, \
     strip_punctuation

import os

class Indexer():
    """
    Class that can be used to index documents from the database.
    """

    def __init__(self, stopwords_language = 'english'):
        """
        We set up the following attributes:

        postgres - will be used to query data from the database
        doc2id - dictionary that maps celex numbers to document_ids
        id2doc - dictionary that maps document_ids to celex numbers
        index - dictionary of indexed words
            keys: words
            values : set of document ids in which the word appears
        stopwords - words that will be ignored. With parameter
        stopwords_language we are able to specify the language
        """

        self.postgres = PostgresQL()
        self.doc2id = {}
        self.id2doc = {}
        self.index = defaultdict(set)
        self.stopwords = stopwords.words(stopwords_language)

    def tokenize_document(self, document):
        """
        Function that takes the document and tokemizes data.

        Parameters:
            document : dict(string, X)
                dictionary of document attributes
                    * document_id
                    * document_title
                    * document_author
                    * document_text
                    * document_form
        Returns:
            list : tokenized words from the documents
        """

        # Column names which we will tokenize
        extract_columns = [
            "document_title",
            "document_author",
            "document_text",
            "document_form"
        ]
        lower = lambda x: x.lower()
        # Function that removes all \u (for example \uf108 empty square) characters from string.
        # It encodes it as ascii and ignores all errors (therefore gets rid of those 
        # characters since in ascii they dont exist). Then decodes it back to utf-8.
        remove_unicode = lambda x: (x.encode('ascii', 'ignore')).decode('utf-8')

        # Collection of all our words
        words = []
        for column_name in extract_columns:
            part = document.get(column_name, None)
            if part is None:
                continue
            # Remove punctuation, make string lower.
            part = preprocess_string(part, [lower, strip_punctuation, remove_unicode])
            words += [w for w in part if w not in self.stopwords]
        
        return words
    
    def get_documents(self, user, password, database, table):
        """
        Function that gets entries from some database table

        Parameters:
            user : string
                user name of the postgres user credentials
            password : string
                password of the postgres user credentials
            database : string
                name of the database to which we want to connect
            table : string
                name of the table from which we will get entries
        
        Returns:
            list of dictionaries (each document represent document)
        """

        # Connect to the database
        self.postgres.connect(
            user = user,
            password = password,
            database = database
        )

        # Fetch all rows from {table} in {database}
        documents = self.postgres.execute(f"SELECT * FROM {table}")

        self.postgres.disconnect()

        return documents
    
    def index_documents(self, grams=1):
        """
        Function that will index all words from given documents.

        This function will iterate through all the documents dataset
        and index every word it encounters. This indexes value can be 
        seen in self.index dictionary

        Parameters:
            grams : int (default = 1)
                max size of word tuples that function should index

        Returns:
            None
        """

        documents = self.get_documents('postgres', 'dbpass',
             'eurlex_environment_only', 'documents')

        for i, document in enumerate(documents):
            document_id = document.get('document_id', None)
            celex_number = document.get('document_celex_num', None)
            
            # We add the connection between document_id and its 
            # celex number
            self.doc2id[celex_number] = document_id
            self.id2doc[document_id] = celex_number

            words = self.tokenize_document(document)
            for word_index in range(len(words)):
                for tuple_length in range(1, grams + 1):
                    # We take together all {grams}-tuples of words
                    word_tuple = tuple(words[word_index+j] for j in range(tuple_length))
                    self.index[word_tuple].add(document_id)
            
            if i % 10000 == 0:
                print(f"""
                    Currently finished {i} documents. The size of index is {len(self.index)} 
                """)
    
    def index_metadata(self, table):
        """
        Function that will index metadata of the documents.

        Function will index descriptors, subjects of the documents.
        Since they are important for the document they will be indexed
        by word and as a whole descriptor/subject.

        Parameters:
            table : string
                name of the table 
        
        Returns:
            None
        """

        documents = self.get_documents('postgres', 'dbpass',
                    'eurlex_environment_only', table)
        
        for i, document in enumerate(documents):
            celex_number = document.get('document_celex_num')
            descriptor_name = document.get('descriptor_name', None)
            subject_name = document.get('subject_name', None)

            document_id = self.doc2id[celex_number]

            if descriptor_name is not None:
                for word in strip_punctuation(descriptor_name).lower().split():
                    if word not in self.stopwords:
                        self.index[word].add(document_id)
            
                # We add the whole  
                self.index[descriptor_name].add(document_id)
                
            if subject_name is not None:
                for word in strip_punctuation(subject_name).lower().split():
                    if word not in self.stopwords:
                        self.index[word].add(document_id)
                
                # We add the whole 
                self.index[subject_name].add(document_id)

            if i % 10000 == 0:
                print(f"""
                    Currently finished {i} documents. The size of index is {len(self.index)} 
                """)

    def start_procedure(self, grams=1):
        """
        Function that will do all the indexing procedures required
        for the eurlex_environment_only database.

        Parameters:
            grams : int
                max length of word tuples
        
        Returns:
            None
        """

        self.index_documents(grams=grams)
        self.index_metadata('document_descriptors')
        self.index_metadata('document_subjects')

    def save(self, output='index.json'):
        """
        Saves the model into .json file.

        Function that takes output as parameter and saves the model
        into that file. Default directory is current working directory.

        Parameters:
            output : string
                name of the output file
        
        Returns:
            None
        """

        # We have to reformat the dictionary since it shouldnt have set() objects
        # keys also need to be of type string.
        index_reformat = {" ".join(k) : sorted(list(v)) for k,v in self.index.items()}

        path = os.getcwd()

        with open(os.path.join(path, output), 'w') as outfile:
            json.dump(
                {
                    'doc2id' : self.doc2id,
                    'id2doc' : self.id2doc,
                    'index' : index_reformat,
                },
                outfile, indent=1
            )

    
if __name__ == '__main__':
    # EXAMPLE USAGE:
    indexer = Indexer()
    indexer.start_procedure()
    indexer.save('index2.json')

    
