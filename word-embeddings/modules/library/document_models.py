import numpy as np
import operator
import string
from gensim.parsing.preprocessing import preprocess_string, strip_punctuation
from nltk.corpus import stopwords as sw
from sklearn.manifold import TSNE


class DocumentModels:
    """
    A class to represent documents as document embeddings.

    Attributes:
        word_vectors (gensim.models.keyedvectors.*): word embedding we want to use to
            construct document embeddings
        documents (list(string)): list of documents we want to embed
        stopwords (list(string)): list of words we want to remove from documents' texts.
        embedding (numpy.ndarray): a matrix where i-th line is the document embedding of
            i-th document in the list 'documents'.
        embedding_2D (numpy.ndarray): a N by 2 matrix (N = number of documents) where i-th line
            is the reduced document embedding of i-th document in the list 'documents', prepared
            in order to plot the embedding.
        embedding_3D (numpy.ndarray): a N by 3 matrix (N = number of documents) where i-th line
            is the reduced document embedding of i-th document in the list 'documents', prepared
            in order to plot the embedding.
    """

    def __init__(self, word_embedding, documents, stopwords=None):
        """
        Args:
             word_embedding (gensim.models.keyedvectors.*): word embedding we want to use to
                 construct document embeddings
             documents (list(string)): list of documents we want to embed
             stopwords (list(string)): list of words we want to remove from documents' texts.
                 (Default = customized list of english stopwords from module nltk)
        """
        self.word_vectors = word_embedding
        self.documents = documents
        if stopwords is None:
            self.stopwords = sw.words('english') + list(string.punctuation)
        else:
            try:
                self.stopwords = stopwords
            except ImportError:
                print("There was an error loading stopwords from module nltk.")
        self.embedding = None
        self.embedding_2D = None
        self.embedding_3D = None

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

        # Strip the text of comments
        stripped_text = strip_comments(text)

        # Strip punctuation and make everything lowercase
        CUSTOM_FILTERS = [lambda x: x.lower(), strip_punctuation]
        tokens = preprocess_string(stripped_text, CUSTOM_FILTERS)

        # Filter through tokens and remove stopwords
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
            embedding (numpy.ndarray): an average of word embeddings of words that appear in
            given text.

        """

        embedding = np.zeros(self.word_vectors.vector_size, dtype=np.float32)
        if text is None:
            return embedding

        word_sorted = self.tokenize(text)
        norm = 0
        for token, number_of_appearances in word_sorted:
            # sum all tokens embeddings of the vector
            if token in self.word_vectors.vocab.keys():
                embedding += self.word_vectors[token]
                norm += 1

        # return the normalized embedding; if not zero
        return embedding if norm == 0 else embedding / norm

    def embed_documents(self):
        """
        Creates the dataset embeddings given a document_embedding function and saves it in self.embedding.

        """

        #Args:
        #     document_embedding (method): a method returning a document embedding for a document that it gets as
        #     an argument. (Default = average_word_embedding)

        self.embedding = np.zeros((len(self.documents), self.word_vectors.vector_size), dtype=np.float32)
        for id, document in enumerate(self.documents):
            self.embedding[id,:] = self.average_word_embedding(document)

    def reduce_dimension(self, dimension=2):
        """
        Reduces the dimension of the embedding to 2 or 3. Saves the result in attribute
        embedding_2D or embedding_3D, respectively.

        Args:
            dimension (int): The dimension to which we want to reduce the embedding. (Default = 2)

        Returns:
            N*dimension matrix (numpy.ndarray) of document embeddings with reduced dimension,
            where N is the number of documents in 'documents'.

        """
        if self.embedding is None:
            self.embed_documents()
        return TSNE(n_components=dimension).fit_transform(self.embedding)
