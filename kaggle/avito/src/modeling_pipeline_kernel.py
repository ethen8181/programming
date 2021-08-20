import os
import time
import logging
import argparse
from joblib import dump
from logzero import setup_logger
from scipy.sparse import hstack, csr_matrix
from utils_kernel import read_and_clean_data, create_submission
from utils_kernel import ModelPipeline
from utils_kernel import create_vectorizer_pipeline, get_vectorizer_feature_names


def main():
    # -----------------------------------------------------------------------------------
    # Adjustable Parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--text_feature_method', type=str,
                        help='tfidf or fasttext', default='fasttext')
    parser.add_argument('--model_method', type=str,
                        help='lightgbm', default='lightgbm')
    args = parser.parse_args()

    input_dir = 'data'
    ids_col = 'item_id'
    label_col = 'deal_probability'
    cat_cols = ['region', 'city', 'parent_category_name',
                'category_name', 'user_type', 'image_top_1',
                'param_1', 'param_2', 'param_3', 'user_id']

    # prepend a timestamp, e.g. 20180324_113330 for the current model directory;
    # the current model directory will store the model checkpoint and log file
    model_dir = 'model'
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    current_model_dir = args.text_feature_method + '_' + args.model_method + '_{}'.format(timestamp)

    # all of these information/checkpoint will be stored under [model_dir]/[current_model_dir]
    perf_report_path = 'performance_report.txt'
    model_checkpoint = args.model_method + '.pkl'
    if args.text_feature_method == 'tfidf':
        tfidf_checkpoint = args.text_feature_method + '.pkl'

    # random hyperparameter search
    cv = 3
    n_iter = 2
    model_random_state = 1234

    # -----------------------------------------------------------------------------------
    start = time.time()
    current_model_path = os.path.join(model_dir, current_model_dir)
    if not os.path.isdir(current_model_path):
        os.makedirs(current_model_path, exist_ok=True)

    logfile = os.path.join(current_model_path, 'modeling.log')
    logger = setup_logger(name=__name__, logfile=logfile, level=logging.INFO)

    logger.info('preprocessing')
    df, train_index, test_index, y, text_features = read_and_clean_data(
        input_dir, ids_col, label_col, cat_cols)
    logger.info('preprocessed data shape: {} rows, {} columns'.format(*df.shape))
    logger.info('sample preprocessed data:\n{}'.format(df.head()))

    if args.text_feature_method == 'tfidf':
        logger.info('creating tfidf features')
        vectorizer_pipeline = create_vectorizer_pipeline(text_features)
        text = vectorizer_pipeline.fit_transform(df)
        vectorizer_feature_names = get_vectorizer_feature_names(vectorizer_pipeline)
        df = df.drop(text_features, axis=1)

        dump(vectorizer_pipeline, os.path.join(current_model_path, tfidf_checkpoint))
        logger.info('number of vectorized text features: {}'.format(len(vectorizer_feature_names)))

    X = hstack([csr_matrix(df.loc[train_index, :].values), text[:train_index.shape[0]]])
    X_test = hstack([csr_matrix(df.loc[test_index, :].values), text[train_index.shape[0]:]])
    all_feature_names = df.columns.tolist() + vectorizer_feature_names
    logger.info('input training data shape: {} rows, {} columns'.format(*X.shape))
    del df, text

    logger.info('modeling')
    model_pipeline = ModelPipeline(n_iter=n_iter, cv=cv, random_state=model_random_state)
    model_pipeline.fit(X, y, all_feature_names, cat_cols)
    dump(model_pipeline, os.path.join(current_model_path, model_checkpoint))

    # save performance metric and feature importance together
    # in a single text file for ease of later evaluation/inspection
    perf_report_path = os.path.join(current_model_path, perf_report_path)
    with open(perf_report_path, 'w') as f:
        X_groups = (X,), (y,), ('train',)
        for X_subset, y_subset, X_type in zip(*X_groups):
            score = round(model_pipeline.score(X_subset, y_subset), 4)
            message = X_type + ' rmse: {}'.format(score)
            f.write(message + '\n')
            logger.info(message)

        output = 'variable,percentage\n'
        for feature, importance in model_pipeline.get_feature_importance():
            output += (feature + ',' + str(importance) + '\n')

        f.write(output)
        logger.info('Important features:\n' + output)

    logger.info('generating submission')
    prediction = model_pipeline.predict(X_test)
    create_submission(prediction, test_index, ids_col, label_col, current_model_path)

    end = time.time()
    elapse = (end - start) / 60
    logger.info('Took {} minutes to run the end to end pipeline'.format(elapse))


if __name__ == '__main__':
    main()