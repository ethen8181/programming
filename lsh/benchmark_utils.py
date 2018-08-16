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


def get_train_test_data(filename):
    dimension = 25  # valid values 25, 50, 100, 200
    test_size = 0.2
    random_state = 1234

    with zipfile.ZipFile(filename) as f:
        X = []
        zip_filename = 'glove.twitter.27B.{}d.txt'.format(dimension)
        for line in f.open(zip_filename):
            # remove the first index (id field) and only get the vectors
            vector = np.array([float(x) for x in line.strip().split()[1:]])
            X.append(vector)

        X_train, X_test = train_test_split(
            np.array(X), test_size=test_size, random_state=random_state)

    return X_train, X_test


def get_ground_truth(X_train, X_test, kdtree_params):
    start = time.time()
    kdtree = KDTree()
    kdtree.fit(X_train)
    build_time = time.time() - start

    start = time.time()
    indices = kdtree.query_batch(X_test)
    search_time = time.time() - start

    ground_truth = [(vector, index) for vector, index in zip(X_test, indices)]
    return build_time, search_time, ground_truth


def run_algo(X_train, X_test, topn, ground_truth, algo_name):

    start = time.time()
    algo = Hnsw()
    algo.fit(X_train)
    build_time = time.time() - start

    total_correct = 0
    total_search_time = 0.0
    n_queries = len(ground_truth)
    for i in trange(n_queries):
        query_vector, correct_indices = ground_truth[i]

        start = time.time()
        found_indices = algo.query(query_vector, topn)
        search_time = time.time() - start
        total_search_time += search_time

        n_correct = len(set(found_indices).intersection(correct_indices))
        total_correct += n_correct

    avg_search_time = total_search_time / n_queries
    avg_precision = total_correct / (n_queries * topn)
    return build_time, avg_search_time, avg_precision
