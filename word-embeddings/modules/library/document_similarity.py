import numpy as np


class DocumentSimilarity:
    """Given a document embedding, provides tools for analysis of document similarity.

    Args:
        embedding (numpy.ndarray): matrix of document embeddings

    """

    def __init__(self, embedding):
        self.embedding = embedding

    def euclid_similarity(self, id1, id2):
        """Calculate the euclid similarity between two embeddings.

        Args:
            id1 (int): index of the embedding of the first document in the embedding matrix
            id2 (int): index of the embedding of the second document in the embedding matrix

        Returns:
            numpy.float32: euclid distance between embeddings of documents with given indices

        """
        return np.linalg.norm(self.embedding[id1, :] - self.embedding[id2, :])

    def k_nearest_neighbors(self, index, k, similarity):
        """Get the k documents with embeddings nerest to the document embedding we chose.

        Args:
            index (int): index of thw chosen document, whose neighbors we are trying to find
            k (int): number of neighbors we want to find
            similarity (function): metric function that we want to use for computing the distance between documents

        Returns:
            list: a list of k indices of the k documents whose embeddings are closest to the chosen embedding in the
            specified metric
        """

        # calculate the similarities and revert it
        sims = [similarity(self.embedding[index], d) for d in self.embedding]

        # sort and get the corresponding indices
        indices = []
        for c, i in enumerate(np.argsort(sims)):
            if c == k:
                break
            indices.append(i)

        # return indices of the neighbors
        return indices
