import numpy as np
from gensim.models import KeyedVectors, FastText


class WordModels:
    """

    Args:

    """

    def __init__(self):
        self.embedding = None
        self.model = None

    def load(self, path, model='word2vec'):
        """
        Load pre-trained word embedding model and save it into embed_words.embedding.

        Args:
            path (str): relative path to the .vec file containing pre-trained model.
            model (str): type of the model - must be one of the following:'word2vec', 'fastText'. (Default = 'word2vec')

        """
        if model == 'word2vec':
            self.model = KeyedVectors
            self.embedding = self.model.load_word2vec_format(path)
        elif model == 'fastText':
            self.model = FastText
            self.embedding = self.model.load(path)
        else:
            raise Exception("Model {} not supported. Cannot load word embedding model.".format(model))

    def train(self, documents, size=300, window=3, min_count=4, epochs=50):
        """
        Train a fastText word embedding model on the sentences provided as an argument.

        Args:
            documents (list(str)): list of documents represented as a stripped lowercase string
            size (int): dimension of the embedding space. (Default = 300)
            window (int): The maximum distance between the current and predicted word within a sentence. (Default = 3)
            min_count (int): The model ignores all words with total frequency lower than min_count. (Default = 4)
            epochs (int): Number of iterations over the corpus. (Default = 50)

        """
        tm = FastText(size=size, window=window, min_count=min_count)
        tm.build_vocab(sentences=documents)
        tm.train(sentences=documents, total_examples=len(documents), epochs=epochs)
        self.model = tm
        self.embedding = tm.wv

    def save(self, file_name):
        """
        Save the (pre-trained) word embedding model in a file.

        Args:
            file_name (str): relative path to the file, in which we want to save the model.

        """
        self.model.save(file_name)
