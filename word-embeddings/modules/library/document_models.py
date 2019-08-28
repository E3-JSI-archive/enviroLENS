import numpy as np
import operator
from gensim.parsing.preprocessing import preprocess_string, strip_punctuation


class DocumentModels:

    def __init__(self, word_embedding, documents, stopwords):
        self.word_vectors = word_embedding
        self.documents = documents
        self.stopwords = stopwords
        self.embedding = None

    def tokenize(self, text):
        """
        Tokenizes and removes stopwords from the provided text.

        Args:
            text (str): text that we want to tokenize.

        Returns:
            word_sorted (list(tuple(str,int))): A list of tuples ('word', n), where n is the number of times word
            appears in text. The list is sorted by occurrences decreasingly.

        """

        def strip_comments(s):
            s = s.replace('"', '')
            s = s.replace("'", '')
            s = s.replace('“', '')
            s = s.replace('”', '')
            return s

        CUSTOM_FILTERS = [lambda x: x.lower(), strip_punctuation]

        stripped_text = strip_comments(text)
        tokens = preprocess_string(stripped_text, CUSTOM_FILTERS)
        filtered = [w for w in tokens if not w in self.stopwords]

        # get the most frequent words in the document
        count = { }
        for word in filtered:
            if word not in count:
                count[word] = 0
            count[word] += 1

        word_sorted = sorted(count.items(), key=operator.itemgetter(1), reverse=True)
        return word_sorted

    def average_word_embedding(self, text):
        """
        Creates an average of word embeddings of words that appear in given text.

        Args:
            text (str): text, form which we take words and compute their average embedding

        Returns:
            embedding (numpy.ndarray): an average of word embeddings of words that appear in given text.

        """

        embedding = np.zeros(self.word_vectors.vector_size, dtype=np.float32)
        if text is None:
            return embedding

        word_sorted = self.tokenize(text)
        norm = 0
        for token in word_sorted:
            # sum all tokens embeddings of the vector
            if token in self.word_vectors.vocab.keys():
                embedding += self.word_vectors[token]
                norm += 1

        # return the normalized embedding; if not zero
        return embedding if norm == 0 else embedding / norm

    def embed_documents(self, document_embedding=average_word_embedding):
        """
        Creates the dataset embeddings given a document_embedding function and saves it in self.embedding.

        Args:
             document_embedding (method): a method returning a document embedding for a document that it gets as
             an argument. (Default = average_word_embedding)

        """

        self.embedding = np.zeros((len(self.documents), self.word_vectors.vector_size), dtype=np.float32)
        for id, document in enumerate(self.documents):
            text = document['document_text']
            self.embedding[id,:] = document_embedding(text, self.stopwords, self.word_vectors)


