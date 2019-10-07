import numpy as np


class DocumentSimilarity:
    """Given a document embedding, provides tools for analysis of document similarity.

    Args:
        embedding (numpy.ndarray): matrix of document embeddings

    Methods:
        euclid_similarity(emb1, emb2): Calculate the Euclid similarity between two embeddings.
        k_nearest_neighbors(index, k, similarity): Get the k documents with embeddings nerest to the document embedding
            we chose.
    """

    def __init__(self, embedding):
        self.embedding = embedding

    def euclid_similarity(self, emb1, emb2):
        """Calculate the Euclid similarity between two embeddings.

        Args:
            emb1 (numpy.ndarray): the first embedding of the embeddings we want to compare
            emb2 (numpy.ndarray): the first embedding of the embeddings we want to compare

        Returns:
            numpy.float32: euclid distance between embeddings of documents with given indices
        """

        return np.linalg.norm(emb1 - emb2)

    def k_nearest_neighbors(self, emb, k, similarity):
        """Get the k documents with embeddings nerest to the document embedding we chose.

        Args:
            emb (numpy.ndarray): embedding of the chosen document, whose neighbors we are trying to find
            k (int): number of neighbors we want to find
            similarity (function): metric function that we want to use for computing the distance between documents

        Returns:
            list: a list of k indices of the k documents whose embeddings are closest to the chosen embedding in the
            specified metric
        """

        # calculate the similarities and revert it
        sims = [similarity(emb, d) for d in self.embedding]

        # sort and get the corresponding indices
        indices = []
        for c, i in enumerate(np.argsort(sims)):
            if c == k:
                break
            indices.append(i)

        # return indices of the neighbors
        return indices
