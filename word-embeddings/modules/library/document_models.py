import numpy as np
import operator
import string
from gensim.parsing.preprocessing import preprocess_string, strip_punctuation
from nltk.corpus import stopwords as sw
from sklearn.manifold import TSNE

# embedding_2D (numpy.ndarray): a N by 2 matrix (N = number of documents) where i-th line
#     is the reduced document embedding of i-th document in the list 'documents', prepared
#     in order to plot the embedding.
# embedding_3D (numpy.ndarray): a N by 3 matrix (N = number of documents) where i-th line
#     is the reduced document embedding of i-th document in the list 'documents', prepared
#     in order to plot the embedding.


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
        embed_documents(): Creates the embedding for documents given at initialization and saves it in the attribute
            'embedding'.

    Methods:
        tokenize(text): Tokenizes and removes stopwords from the provided text.
        average_word_embedding(text): Creates a document embedding as the average of word embeddings of words that
            appear in given text.
        embed_list_of_documents(docs): Returns a document embedding of documents given as an argument.
        add_documents(docs): Appends given documents to the model's attribute 'documents' and adds lines for document
            embeddings of those documents at the end of the matrix 'embedding'.
        remove_documents(docs): Removes given documents from the model's attribute 'documents' and removes lines for
            their embeddings from the matrix 'embedding'.
        reduce_dimension(dimension=2): Reduces the dimension of the embedding to 'dimension'.
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
        # self.embedding_2D = None
        # self.embedding_3D = None

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
        Creates a document embedding as an average of word embeddings of words that appear in given text.

        Args:
            text (str): text, form which we take words and compute their average embedding

        Returns:
            (numpy.ndarray): an average of word embeddings of words that appear in
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

    def embed_list_of_documents(self, docs):
        """
        Returns a document embedding of documents given as an argument.

        Args:
            docs (list(string)): list of documents we want to embed

        Returns:
             numpy.ndarray: matrix of document embeddings, where i-th line is the embedding of i-th document of the
                 list 'docs'.
        """

        embedding = np.zeros((len(docs), self.word_vectors.vector_size), dtype=np.float32)
        # embed individual documents:
        for id, document in enumerate(docs):
            embedding[id,:] = self.average_word_embedding(document)
        return embedding

    def embed_documents(self):
        """
        Creates the dataset embeddings for documents given at initialization and saves it in the attribute 'embedding'.
        """

        self.embedding = self.embed_list_of_documents(self.documents)

    def add_documents(self, docs):
        """
        Appends given documents to the model's attribute 'documents' and adds lines for document embeddings of those
        documents at the end of the matrix 'embedding'.

        Args:
            docs (list(str)): List of documents we want to add to our model
        """

        docs = [d for d in docs if d not in self.documents]
        new_embedding = self.embed_list_of_documents(docs)
        self.documents = self.documents + docs
        self.embedding = np.concatenate((self.embedding, new_embedding))

    def remove_documents(self, docs):
        """
        Removes given documents from the model's attribute 'documents' and removes lines for their embeddings from the
        matrix 'embedding'.

        Args:
            docs (list(str)): List of documents we want to remove from our model
        """

        for doc in docs:
            if doc in self.documents:
                index = self.documents.index(doc)
                self.documents.remove(doc)
                self.embedding = np.concatenate((self.embedding[0:index, :], self.embedding[index+1:, :]))

    def reduce_dimension(self, dimension=2):
        """
        Reduces the dimension of the embedding to 'dimension'.

        Args:
            dimension (int): The dimension to which we want to reduce the embedding. (Default = 2)

        Returns:
            numpy.ndarray: N*dimension matrix of document embeddings with reduced dimension, where N is the number of
                documents in 'documents'.
        """

        if self.embedding is None:
            self.embed_documents()
        return TSNE(n_components=dimension).fit_transform(self.embedding)
