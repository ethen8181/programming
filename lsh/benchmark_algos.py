import nmslib
import numpy as np
from n2 import HnswIndex
from sklearn.preprocessing import normalize
from sklearn.neighbors import NearestNeighbors


class BruteForce:

    def __init__(self):
        pass

    def fit(self, X):
        lens = (X ** 2).sum(axis=-1)
        index = X / np.sqrt(lens)[:, np.newaxis]
        self.index_ = np.ascontiguousarray(index, dtype=np.float32)
        return self

    def query(self, vector, topn):
        """Find indices of `n` most similar vectors from the index to query vector `v`."""

        # argmax_a dot(a, b) / |a||b| = argmin_a -dot(a, b)
        dists = -np.dot(self.index_, vector)
        indices = np.argpartition(dists, topn)[:topn]
        return sorted(indices, key=lambda index: dists[index])


class KDTree:

    def __init__(self, topn=10, n_jobs=-1):
        self.topn = topn
        self.n_jobs = n_jobs

    def fit(self, X):
        X_normed = normalize(X)
        index = NearestNeighbors(
            n_neighbors=self.topn, metric='euclidean', n_jobs=self.n_jobs)
        index.fit(X_normed)
        self.index_ = index
        return self

    def query_batch(self, X):
        X_normed = normalize(X)
        _, indices = self.index_.kneighbors(X_normed)
        return indices

    def query(self, vector):
        """Find indices of `n` most similar vectors from the index to query vector `v`."""
        vector_normed = normalize(vector.reshape(1, -1))
        _, indices = self.index_.kneighbors(vector_normed)
        return indices.ravel()


class Hnsw:

    def __init__(self, index_params=None, query_params=None, print_progress=True):
        self.index_params = index_params
        self.query_params = query_params
        self.print_progress = print_progress

    def fit(self, X):
        index_params = self.index_params
        if index_params is None:
            index_params = {'M': 16, 'post': 0, 'efConstruction': 400}

        query_params = self.query_params
        if query_params is None:
            query_params = {'ef': 90}

        index = nmslib.init(space='cosinesimil', method='hnsw')
        index.addDataPointBatch(X)
        index.createIndex(index_params, print_progress=self.print_progress)
        index.setQueryTimeParams(query_params)

        self.index_ = index
        self.index_params_ = index_params
        self.query_params_ = query_params
        return self

    def query(self, vector, topn):
        indices, _ = self.index_.knnQuery(vector, k=topn)
        return indices


class N2:

    def __init__(self):
        pass

    def fit(self, X):
        index = HnswIndex(dimension=X.shape[1])
        for vector in X:
            index.add_data(vector)

        index.build(m=5, n_threads=8)
        self.index_ = index
        return self

    def query(self, vector, topn):
        indices = self.index_.search_by_vector(vector, k=topn)
        return indices
