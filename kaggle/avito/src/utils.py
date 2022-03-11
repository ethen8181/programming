import os
import string
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from lightgbm import LGBMRegressor
from scipy.stats import randint, uniform
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.model_selection import RandomizedSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from mlutils.transformers import ColumnExtractor


def read_and_clean_data(input_dir, cat_cols, user_col, ids_col, text_feature_method, data_type):

    activation_col = 'activation_date'
    cat_dtypes = {col: 'category' for col in cat_cols}
    input_path = os.path.join(input_dir, data_type + '.csv')
    df = pd.read_csv(input_path, dtype=cat_dtypes, parse_dates=[activation_col])

    week_day_col = 'week_day'
    week_of_year_col = 'week_of_year'
    day_of_month_col = 'day_of_month'
    date_cols = [week_day_col, day_of_month_col, week_of_year_col]
    df[week_day_col] = df[activation_col].dt.weekday
    df[week_of_year_col] = df[activation_col].dt.week
    df[day_of_month_col] = df[activation_col].dt.day
    df = df.drop([activation_col, 'image'], axis=1)

    na_flag = -999
    price_col = 'price'
    df[price_col] = np.log(df[price_col] + 0.001)
    df[price_col] = df[price_col].fillna(na_flag)

    # param_col is a new column created by concatenating the three param field
    # according to the discussion these are categories, like on amazon when we look
    # at an item, it could belong to category tools or home improvements, and an item
    # might not have all three params since not all of them will have multiple categories
    # https://www.kaggle.com/shivamb/in-depth-analysis-visualisations-avito/code
    param_col = 'param_feature'
    param_input_cols = ['param_1', 'param_2', 'param_3']
    concatenated = df[param_input_cols[0]].astype(str)
    for col in param_input_cols[1:]:
        concatenated += (' ' + df[col].astype(str))

    df[param_col] = concatenated
    df = df.drop(param_input_cols, axis=1)

    # basic text feature engineering
    # Lowercase all text, so that capitalized words don't get treated differently
    text_features = ['description', 'title', param_col]
    for col in text_features:
        df[col] = df[col].astype(str).fillna('NA')
        df[col] = df[col].str.lower()
        df[col + '_num_words'] = df[col].str.count(r'\w{1,}')

    # replace description with embeddings from pre-trained fasttext model; the description
    # embedding should already be generated from generate_fasttext_embedding.py
    fasttext_embedding_path = os.path.join(input_dir, 'text_feature_fasttext_embedding.h5')
    if text_feature_method == 'fasttext' and os.path.isfile(fasttext_embedding_path):
        df = df.drop(text_features, axis=1)

        # the embeddings's group in the HDFStore is fixed to be 'embedding', this is
        # hard-coded from the generate_fasttext_embedding.py script
        df_embedding = pd.read_hdf(fasttext_embedding_path, key='embedding')
        df = df.merge(df_embedding, on=ids_col, how='inner')

    # merge user aggregated stats generated by generate_user_aggregated_features.py
    user_agg_features_path = os.path.join(input_dir, 'aggregated_user_features.parquet')
    if os.path.isfile(user_agg_features_path):
        df_user_agg_features = pd.read_parquet(user_agg_features_path)
        agg_cols = ['days_up_sum_mean', 'days_up_sum_std',
                    'times_put_up_mean', 'times_put_up_std', 'user_item_count']
        df = df.merge(df_user_agg_features, on=user_col, how='left')
        df[agg_cols] = df[agg_cols].fillna(na_flag)

    # user_col is not converted to category type immediately when reading in the data
    # since we might be doing a merge/join with the user aggregated stats and after
    # performing the join, the type would be lost, thus we convert only after performing
    # the merge
    df[user_col] = df[user_col].astype('category')

    # replace categorical features with its actual categorical code
    for cat_col in cat_cols + [user_col]:
        df[cat_col] = df[cat_col].cat.codes

    categorical_features = cat_cols + date_cols
    return df, categorical_features, text_features


def create_tfidf_pipeline(text_features):
    # stop_words:
    # the param_features column contains a lot of 'nan' since not all items have all
    # three param fields, resulting in nan being generated for those empty fields
    stop_words = set(stopwords.words('russian')) | set(string.punctuation) | set(['nan'])
    tfidf_param = {
        'norm': 'l2',
        'min_df': 2,
        'max_df': .9,
        'analyzer': 'word',
        'smooth_idf': True,
        'sublinear_tf': True,
        'ngram_range': (1, 2),
        'token_pattern': r'\w{1,}',
        'stop_words': stop_words
    }

    pipelines = []
    for feature_name in text_features:
        if feature_name == 'description':
            tfidf = TfidfVectorizer(max_features=16000, **tfidf_param)
        else:
            tfidf = TfidfVectorizer(**tfidf_param)

        pipeline = Pipeline([
            ('extractor', ColumnExtractor(col=feature_name)),
            ('tfidf', tfidf)
        ])
        pipelines.append((feature_name, pipeline))

    return FeatureUnion(pipelines)


def get_text_feature_names(tfidf_pipeline):
    text_feature_names = []
    for _, pipeline in tfidf_pipeline.transformer_list:
        tfidf = pipeline.named_steps['tfidf']
        text_feature_names.extend(tfidf.get_feature_names())

    return text_feature_names


class LightGBMPipeline:
    """Build a RandomSearchCV LightGBM regression model that optimizes for rmse."""

    def __init__(self, n_iter=2, cv=10, random_state=1234):
        self.cv = cv
        self.n_iter = n_iter
        self.random_state = random_state

    def fit(self, data, label, feature_name, categorical_feature, eval_set):
        # for gbm, set number of estimator to a large number
        # and the learning rate to be a small number, we'll simply
        # let early stopping decide when to stop training
        # https://lightgbm.readthedocs.io/en/latest/Parameters-Tuning.html
        lgb_params_fixed = {
            'n_jobs': -1,
            'metric': 'rmse',
            'objective': 'rmse',
            'learning_rate': 0.01,
            'min_data_in_leaf': 500,
            'n_estimators': 500
        }
        lgb = LGBMRegressor(**lgb_params_fixed)

        # set up random search hyperparameters:
        # subsample, colsample_bytree and max_depth are presumably the most
        # common way to control under/overfitting for tree-based models
        lgb_tuned_params = {
            'max_depth': randint(low=3, high=12),
            'colsample_bytree': uniform(loc=0.8, scale=0.2),
            'subsample': uniform(loc=0.8, scale=0.2)
        }

        lgb_fit_params = {
            'verbose': 100,
            'eval_set': eval_set,
            'early_stopping_rounds': 3,
            'feature_name': feature_name,
            'categorical_feature': categorical_feature
        }

        # return_train_score = False
        # computing the scores on the training set can be computationally
        # expensive and is not strictly required to select the parameters
        # that yield the best generalization performance.
        lgb_tuned = RandomizedSearchCV(
            estimator=lgb,
            param_distributions=lgb_tuned_params,
            cv=self.cv,
            n_iter=self.n_iter,
            n_jobs=-1,
            verbose=1,
            scoring='neg_mean_squared_error',
            random_state=self.random_state,
            return_train_score=False
        ).fit(data, label, **lgb_fit_params)
        self.lgb_tuned_ = lgb_tuned
        return self

    def get_feature_importance(self, threshold=1e-2):
        """
        Sort the feature importance based on decreasing order of the
        normalized gain. Features that has a normalized gain smaller
        than the specified ``threshold`` will not be returned.
        """
        booster = self.lgb_tuned_.best_estimator_.booster_
        importance = booster.feature_importance(importance_type='gain')
        importance /= importance.sum()
        feature_name = np.array(booster.feature_name())

        mask = importance > threshold
        importance = importance[mask]
        feature_name = feature_name[mask]
        idx = np.argsort(importance)[::-1]
        return list(zip(feature_name[idx], np.round(importance[idx], 4)))

    def predict(self, data):
        best = self.lgb_tuned_.best_estimator_
        return best.predict(data, num_iteration=best.best_iteration_)

    def score(self, data, label):
        prediction = self.predict(data)
        rmse = np.sqrt(mean_squared_error(label, prediction))
        return rmse


def create_submission(model, data, ids, current_model_dir, ids_col, label_col):
    prediction = model.predict(data)
    submission = pd.DataFrame({
        ids_col: ids,
        label_col: prediction
    }, columns=[ids_col, 'deal_probability'])
    submission[label_col] = submission[label_col].clip(0.0, 1.0)
    submission_path = os.path.join(current_model_dir, 'submission.csv')
    submission.to_csv(submission_path, index=False, header=True)