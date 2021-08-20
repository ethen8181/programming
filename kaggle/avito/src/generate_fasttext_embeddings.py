"""
Generate an embedding dataframe for the text features and saves it to a .h5 file
The dataframe will look like the following:

            item_id  description_embedding1  description_embedding2   ...
    0  b912c3c6a6ad                0.046429               -0.004665   ...
    1  2dac0150717d               -0.051861               -0.055021   ...
    2  ba83aefab5dc                0.027891               -0.062700   ...
    3  02996f1dd2ea               -0.101859                0.179240   ...
    4  7c90be56d2ab                0.081251               -0.195440   ...

The table has an item_id so we can join it with the original training or testing data,
followed by an embedding of size 300 for the description column.

The size will always be 300 since this is using pre-trained fasttext embedding.
https://s3-us-west-1.amazonaws.com/fasttext-vectors/wiki.ru.zip

Originally this script was meant to generate embedding for all text features,
but then at mid-point, i'd figured it would be faster to just generate it only for
the description column as it provided the most information out of the 3 text features.

The script takes approx. 15 minutes
"""
import os
import re
import string
import numpy as np
import pandas as pd
from tqdm import tqdm
from time import time
from logzero import setup_logger
from gensim.models import FastText
logger = setup_logger()


def main():
    # -----------------------------------------------------------------------------------
    # Adjustable Parameters
    input_dir = os.path.join('..', 'data')
    output_file = 'text_feature_fasttext_embedding.h5'
    pretrained_fasttext_path = os.path.join(input_dir, 'wiki.ru', 'wiki.ru.bin')
    embedding_size = 300

    # column names, param_col is a new column created by concatenating
    # the three param field
    ids_col = 'item_id'
    title_col = 'title'
    description_col = 'description'
    param_col = 'param_feature'
    param_input_cols = ['param_1', 'param_2', 'param_3']

    # replace the text_features with all three text-related features if so desired
    text_features = [description_col]  # [description_col, title_col, param_col]

    # -----------------------------------------------------------------------------------
    logger.info('reading data (text related features)')
    start = time()

    df = read_data_text_related_features(
        input_dir, ids_col, description_col, title_col, param_input_cols, param_col)
    logger.info('text related features data shape: {}'.format(df.shape))
    logger.info('sample text related features data:\n{}'.format(df.head()))

    logger.info('loading Fasttext pre-trained model')
    model = FastText.load_fasttext_format(pretrained_fasttext_path)
    logger.info('Fasttext pre-trained model loaded successfully')

    logger.info('looking up embeddings from pre-trained model')
    # if we were to look up embedding for all three text features, then most
    # of the time is spent on processing the description column as it contains
    # a lot more text than the title or param_feature column
    df_embeddings = []
    for text_feature in text_features:
        df_embedding = get_embedding_table(df, text_feature, model, embedding_size)
        df_embeddings.append(df_embedding)

    df_embeddings = pd.concat([df[[ids_col]], *df_embeddings], axis=1)
    logger.info('text features embedding data shape: {}'.format(df_embeddings.shape))
    logger.info('sample text features embedding data:\n{}'.format(df_embeddings.head()))

    logger.info('saving text feature embeddings as a .h5 file')
    output_path = os.path.join(input_dir, output_file)
    df_embeddings.to_hdf(output_path, key='embedding', mode='w')

    end = time()
    elapse = (end - start) / 60
    logger.info('Took {} minutes to lookup embeddings from pre-trained Fasttext model'.format(elapse))


def read_data_text_related_features(input_dir, ids_col, description_col,
                                    title_col, param_input_cols, param_col):

    path_train = os.path.join(input_dir, 'train.csv')
    path_test = os.path.join(input_dir, 'test.csv')
    use_cols = [ids_col, description_col, title_col] + param_input_cols

    df_train = pd.read_csv(path_train, usecols=use_cols)
    df_test = pd.read_csv(path_test, usecols=use_cols)
    df = pd.concat([df_train, df_test], ignore_index=True)

    # concatenate the parameters;
    # according to the discussion these are categories, like on amazon when we look
    # at an item, it could belong to category tools or home improvements, and an item
    # might not have all three params since not all of them will have multiple categories
    # https://www.kaggle.com/shivamb/in-depth-analysis-visualisations-avito/code
    concatenated = df[param_input_cols[0]].astype(str)
    for col in param_input_cols[1:]:
        concatenated += (' ' + df[col].astype(str))

    df[param_col] = concatenated
    df = df.drop(param_input_cols, axis=1)
    return df


def get_embedding_table(df, text_feature, model, embedding_size):
    # table used to remove all punctuation marks from a word/string
    table = str.maketrans('', '', string.punctuation)

    doc_embedding = np.zeros((df.shape[0], embedding_size), dtype=np.float32)
    with tqdm(total=df.shape[0], desc='getting word embeddings for ' + text_feature) as pbar:
        for idx, row in enumerate(df.itertuples()):
            raw_text = getattr(row, text_feature)
            word_embedding = get_word_embedding(model, raw_text, table, embedding_size)
            doc_embedding[idx] = word_embedding
            pbar.update(1)

    embedding_cols = [text_feature + '_embedding' + str(idx) for idx in range(1, embedding_size + 1)]
    df_embedding = pd.DataFrame(doc_embedding, columns=embedding_cols)
    return df_embedding


def get_word_embedding(model, raw_text, table, embedding_size):
    """
    Each sentence's embedding is an average of their word's embedding. For words
    whose embeddings can't be found from the model, a zero embedding is used in-place
    of the absent embedding.
    """

    # splitting based on spaces or comma generated text that made sense
    # (based on trial and error)
    tokens = re.split('\\s+|,', str(raw_text).lower())
    zero_embedding = np.zeros(embedding_size)
    if not tokens:
        return zero_embedding

    word_vectors = []
    for word in tokens:
        word = word.translate(table)
        if word.isalpha():
            try:
                word_vector = model.wv[word]
            except KeyError:
                word_vector = zero_embedding

            word_vectors.append(word_vector)

    # all the tokens in the field might all get filtered
    # due to not being valid word
    if not word_vectors:
        return zero_embedding

    return np.mean(word_vectors, axis=0)


if __name__ == '__main__':
    main()
