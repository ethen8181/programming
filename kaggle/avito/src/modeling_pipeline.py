"""
Adjust n_iter, cv and n_estimators for the lightgbm pipeline
"""
import os
import time
import logging
import argparse
import numpy as np
from joblib import dump
from logzero import setup_logger
from scipy.sparse import hstack, csr_matrix
from sklearn.model_selection import train_test_split
from utils import read_and_clean_data, create_tfidf_pipeline, get_text_feature_names
from utils import LightGBMPipeline, create_submission


def main():
    # -----------------------------------------------------------------------------------
    # Adjustable Parameters

    parser = argparse.ArgumentParser()
    parser.add_argument('--text_feature_method', type=str,
                        help='tfidf or fasttext', default='fasttext')
    args = parser.parse_args()

    input_dir = os.path.join('..', 'data')
    ids_col = 'item_id'
    user_col = 'user_id'
    label_col = 'deal_probability'
    cat_cols = ['region', 'city', 'parent_category_name',
                'category_name', 'user_type', 'image_top_1']

    # prepend a timestamp, e.g. 20180324_113330 for the current model directory;
    # the current model directory will store the model checkpoint and log file
    model_dir = os.path.join('..', 'model')
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    current_model_dir = args.text_feature_method + '_lightgbm_{}'.format(timestamp)

    # all of these information/checkpoint will be stored under [model_dir]/[current_model_dir]
    perf_report_path = 'performance_report.txt'
    lgb_checkpoint = 'lgb.pkl'
    if args.text_feature_method == 'tfidf':
        tfidf_checkpoint = 'tfidf.pkl'

    # train/validation/test split
    val_size = 0.2
    test_size = 0.1
    split_random_state = 23

    # random hyperparameter search
    cv = 3
    n_iter = 2
    model_random_state = 1234

    # -----------------------------------------------------------------------------------
    model_path = os.path.join(model_dir, current_model_dir)
    if not os.path.isdir(model_path):
        os.makedirs(model_path, exist_ok=True)

    logfile = os.path.join(model_path, 'modeling.log')
    logger = setup_logger(name=__name__, logfile=logfile, level=logging.INFO)

    logger.info('preprocessing')
    df, categorical_features, text_features = read_and_clean_data(
        input_dir, cat_cols, user_col, ids_col, args.text_feature_method, data_type='train')
    label = df[label_col].values
    ids = df[ids_col].values
    df = df.drop([ids_col, label_col], axis=1)
    logger.info('raw data shape: {} rows, {} columns'.format(*df.shape))

    # train/test split twice to achieve train/validation/test three way split
    df_train, df_test, y_train, y_test, ids_train, ids_test = train_test_split(
        df, label, ids, test_size=test_size, random_state=split_random_state)
    df_train, df_val, y_train, y_val, ids_train, ids_val = train_test_split(
        df_train, y_train, ids_train, test_size=val_size, random_state=split_random_state)
    del df

    df_groups = (df_train, df_val, df_test), ('train', 'validation', 'test')
    for df_subset, df_type in zip(*df_groups):
        logger.info(df_type + ' data shape: {} rows, {} columns'.format(*df_subset.shape))

    if args.text_feature_method == 'tfidf':
        # replace raw text features (description, title and params) with tfidf
        logger.info('creating tfidf features')
        tfidf_pipeline = create_tfidf_pipeline(text_features)

        text_train = tfidf_pipeline.fit_transform(df_train)
        text_val = tfidf_pipeline.transform(df_val)
        text_test = tfidf_pipeline.transform(df_test)

        df_train = df_train.drop(text_features, axis=1)
        df_val = df_val.drop(text_features, axis=1)
        df_test = df_test.drop(text_features, axis=1)

        text_feature_names = get_text_feature_names(tfidf_pipeline)
        dump(tfidf_pipeline, os.path.join(model_path, tfidf_checkpoint))
        logger.info('number of tfidf features: {}'.format(len(text_feature_names)))

        # concatenate the dense features with tfidf features
        X_train = hstack([csr_matrix(df_train.values), text_train])
        X_val = hstack([csr_matrix(df_val.values), text_val])
        X_test = hstack([csr_matrix(df_test.values), text_test])
        X_features = df_train.columns.tolist() + text_feature_names
    else:  # assumed to be fasttext
        X_train = df_train.values
        X_val = df_val.values
        X_test = df_test.values
        X_features = df_train.columns.tolist()

    logger.info('modeling')
    lgb_pipeline = LightGBMPipeline(n_iter=n_iter, cv=cv, random_state=model_random_state)
    eval_set = [(X_train, y_train), (X_val, y_val)]
    lgb_pipeline.fit(X_train, y_train, X_features, categorical_features, eval_set)
    dump(lgb_pipeline, os.path.join(model_path, lgb_checkpoint))
    logger.info('best parameters: {}'.format(lgb_pipeline.lgb_tuned_.best_params_))

    # save performance metric and feature importance together
    # in a single text file for ease of later evaluation/inspection
    perf_report_path = os.path.join(model_path, perf_report_path)
    with open(perf_report_path, 'w') as f:
        X_groups = (X_train, X_val, X_test), (y_train, y_val, y_test), ('train', 'validation', 'test')
        for X_subset, y_subset, X_type in zip(*X_groups):
            score = round(lgb_pipeline.score(X_subset, y_subset), 4)
            message = X_type + ' rmse: {}'.format(score)
            f.write(message + '\n')
            logger.info(message)

        output = 'variable,percentage\n'
        for feature, importance in lgb_pipeline.get_feature_importance():
            output += (feature + ',' + str(importance) + '\n')

        f.write(output)
        logger.info('Important features:\n' + output)

    logger.info('generating submission')
    df, categorical_features, text_features = read_and_clean_data(
        input_dir, cat_cols, user_col, ids_col, args.text_feature_method, data_type='test')
    ids = df[ids_col].values
    df = df.drop(ids_col, axis=1)

    if args.text_feature_method == 'tfidf':
        text = tfidf_pipeline.transform(df)
        df = df.drop(text_features, axis=1)
        X = hstack([csr_matrix(df.values), text])
    else:  # assumed to be fasttext
        X = df.values

    create_submission(lgb_pipeline, X, ids, model_path, ids_col, label_col)


if __name__ == '__main__':
    main()
