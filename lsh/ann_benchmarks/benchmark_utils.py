import time
import zipfile
import requests
import numpy as np
from tqdm import trange
from benchmark_algos import KDTree, Hnsw
from sklearn.model_selection import train_test_split


def download(url, filename):
    with open(filename, 'wb') as file:
        response = requests.get(url)
        file.write(response.content)


def get_train_test_data(filename, dimension=25, test_size=0.2, random_state=1234):
    """
    dimension : int, {25, 50, 100, 200}, default 25
        The dataset contains embeddings of different size.
    """
    with zipfile.ZipFile(filename) as f:
        X = []
        zip_filename = 'glove.twitter.27B.{}d.txt'.format(dimension)
        for line in f.open(zip_filename):
            # remove the first index, id field and only get the vectors
            vector = np.array([float(x) for x in line.strip().split()[1:]])
            X.append(vector)

        X_train, X_test = train_test_split(
            np.array(X), test_size=test_size, random_state=random_state)

    # we can downsample for experimentation purpose
    # X_train = X_train[:50000]
    # X_test = X_test[:10000]
    return X_train, X_test


def get_ground_truth(X_train, X_test, kdtree_params):
    """
    Compute the ground truth or so called golden standard, during
    which we'll compute the time to build the index using the
    training set, time to query the nearest neighbors for all
    the data points in the test set. The ground_truth returned
    will be of type list[(ndarray, ndarray)], where the first
    ndarray will be the query vector, and the second ndarray will
    be the corresponding nearest neighbors.
    """
    start = time.time()
    kdtree = KDTree()
    kdtree.fit(X_train)
    build_time = time.time() - start

    start = time.time()
    indices = kdtree.query_batch(X_test)
    query_time = time.time() - start

    ground_truth = [(vector, index) for vector, index in zip(X_test, indices)]
    return build_time, query_time, ground_truth


def run_algo(X_train, X_test, topn, ground_truth, algo_type='hnsw', algo_params=None):
    """
    We can extend this benchmark across multiple algorithm or algorithm's hyperparameter
    by adding more algo_type options. The algo_params can be a dictionary that is passed
    to the algorithm's __init__ method.
    Here only 1 method is included.
    """

    if algo_type == 'hnsw':
        algo = Hnsw()
        if algo_params is not None:
            algo = Hnsw(**algo_params)

    start = time.time()
    algo.fit(X_train)
    build_time = time.time() - start

    total_correct = 0
    total_query_time = 0.0
    n_queries = len(ground_truth)
    for i in trange(n_queries):
        query_vector, correct_indices = ground_truth[i]

        start = time.time()
        found_indices = algo.query(query_vector, topn)
        query_time = time.time() - start
        total_query_time += query_time

        n_correct = len(set(found_indices).intersection(correct_indices))
        total_correct += n_correct

    avg_query_time = total_query_time / n_queries
    avg_precision = total_correct / (n_queries * topn)
    return build_time, avg_query_time, avg_precision
