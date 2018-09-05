import os
import joblib
import nmslib
import numpy as np
from n2 import HnswIndex
from inspect import signature
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
    """
    Approximate nearest neighborhood using
    Hierarchical Navigable Small World [1]_
    This is a wrapper around the original library's
    API to make it more scikit-learn like.

    Paramters
    ---------
    space : str, default 'cosinesimil'
        The metric space to create for this index.

    index_params : dict, default None
        Dictionary of parameters to use for indexing.

    query_params : dict, default None
        Dictionary of parameters to use for querying nearest neighbors.

    print_progress : bool, default True
        Whether or not to display progress bar when creating index

    Attributes
    ----------
    index_ : nmslib.dist.FloatIndex
        The nmslib index returned by calling nmslib.init.

    index_params_ : dict
        The actual index_params that were used to build the index.
        If the input was None, then the default would be:
        {'M': 16, 'post': 0, 'efConstruction': 400}

    query_params_ : dict
        The actual query_params that were used to query the nearest
        neighbors. If the input was None, then the default would be:
        {'ef': 90}

    Examples
    --------
    import numpy as np

    # replace this with your data
    data = np.random.randn(1000, 10).astype(numpy.float32)

    hnsw = Hnsw()
    hnsw.fit(data)
    print(hnsw.query(data[0], topn=10))

    References
    ----------
    .. [1] `Non-Metric Space Library (NMSLIB) <https://github.com/nmslib/nmslib>`_
    """

    def __init__(self, space='cosinesimil', index_params=None,
                 query_params=None, print_progress=True):
        self.space = space
        self.index_params = index_params
        self.query_params = query_params
        self.print_progress = print_progress

        self._object_filename = 'hnsw.pkl'
        self._index_filename = 'hnsw.bin'

    def fit(self, X):
        index_params = self.index_params
        if index_params is None:
            index_params = {'M': 16, 'post': 0, 'efConstruction': 400}

        query_params = self.query_params
        if query_params is None:
            query_params = {'ef': 90}

        index = nmslib.init(space=self.space, method='hnsw')
        index.addDataPointBatch(X)
        index.createIndex(index_params, print_progress=self.print_progress)
        index.setQueryTimeParams(query_params)

        self.index_ = index
        self.index_params_ = index_params
        self.query_params_ = query_params
        return self

    def query_batch(self, X, topn=10, n_jobs=-1):
        _n_jobs = joblib.cpu_count()
        if _n_jobs > n_jobs > 0:
            _n_jobs = n_jobs

        indices_and_distances = self.index_.knnQueryBatch(X, k=topn, num_threads=_n_jobs)

        # each element in the indices_and_distances is a tuple of
        # indice, distance 1d ndarray, we're discarding the distance for now
        indice, _ = indices_and_distances[0]
        indices = np.zeros((X.shape[0], topn), dtype=indice.dtype)
        for i, row in enumerate(indices_and_distances):
            indice, _ = row
            indices[i] = indice

        return indices

    def query(self, vector, topn):
        indices, _ = self.index_.knnQuery(vector, k=topn)
        return indices

    def save(self, folder_name):
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name, exist_ok=True)

        # make nmslib None so it won't try to pickle nmslib object
        # remember to set it back afterwards
        index = self.index_
        self.index_ = None
        joblib.dump(self, os.path.join(folder_name, self._object_filename))
        index.saveIndex(os.path.join(folder_name, self._index_filename))
        self.index_ = index
        return self

    @classmethod
    def load(cls, folder_name):
        hnsw = cls()
        hnsw = joblib.load(os.path.join(folder_name, hnsw._object_filename))

        index = nmslib.init(space=hnsw.space, method='hnsw')
        index.loadIndex(os.path.join(folder_name, hnsw._index_filename))
        index.setQueryTimeParams(hnsw.query_params_)
        hnsw.index_ = index
        return hnsw

    def get_params(self):
        """
        Get parameters (arguments in the __init__ method)
        for this estimator.

        Returns
        -------
        valid_params : dict
            Parameter names mapped to their values.
        """
        valid_params = {}
        init_signature = signature(self.__init__)
        paramters = init_signature.parameters.values()
        params = sorted([p.name for p in paramters if p.name != 'self'])
        for param in params:
            value = getattr(self, param, None)
            valid_params[param] = value

        return valid_params

    def set_params(self, **params):
        """
        Set the parameters of this estimator.

        Parameters
        ----------
        params : dict
            Dictionary containing the parameter and its corresponding
            updated value.

        Returns
        -------
        self
        """
        valid_params = self.get_params()
        for key, value in params.items():
            if key not in valid_params:
                raise ValueError('Invalid parameter %s for estimator %s. '
                                 'Check the list of available parameters '
                                 'with `estimator.get_params().keys()`.' %
                                 (key, self))

            setattr(self, key, value)

        return self


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
