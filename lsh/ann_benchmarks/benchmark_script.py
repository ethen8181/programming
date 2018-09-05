import os
import time
import logging
import benchmark_utils as utils
from joblib import dump, load
from logzero import setup_logger


def main():
    MODEL_DIR = 'model'
    DATA_DIR = './datasets/'
    URL = 'http://nlp.stanford.edu/data/glove.twitter.27B.zip'
    kdtree_params = {'topn': 10, 'n_jobs': -1}
    ground_truth_filename = 'ground_truth.pkl'

    start = time.time()
    logger = setup_logger(name=os.path.split(__file__)[1], level=logging.INFO)

    for directory in (DATA_DIR, MODEL_DIR):
        if not os.path.exists(directory):
            os.makedirs(directory, exists_ok=True)

    filename = os.path.join(DATA_DIR, 'glove.twitter.27B.zip')
    if not os.path.exists(filename):
        utils.download(URL, filename)

    X_train, X_test = utils.get_train_test_data(filename)

    ground_truth_filepath = os.path.join(MODEL_DIR, ground_truth_filename)
    print('ground truth filepath: ', ground_truth_filepath)
    if os.path.exists(ground_truth_filepath):
        ground_truth = load(ground_truth_filepath)
    else:
        build_time, search_time, ground_truth = utils.get_ground_truth(
            X_train, X_test, kdtree_params)
        dump(ground_truth, ground_truth_filepath)

    end = time.time()
    elapsed = (end - start) / 60
    logger.info('whole process finished in {} minutes'.format(elapsed))


if __name__ == '__main__':
    main()
