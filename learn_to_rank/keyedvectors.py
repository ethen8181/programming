import numpy as np
from sklearn.preprocessing import normalize


def most_similar(word_vectors, vocab, index2word, positive, negative=None, topn=5):

    # normalize word vectors to make the cosine distance calculation easier
    # normed_vectors = vectors / np.sqrt((word_vectors ** 2).sum(axis=-1))[..., np.newaxis]
    # ?? whether to cache the normed vector or replace the original one to speed up computation
    normed_vectors = normalize(word_vectors)

    # assign weight to positive and negative query words
    positive = [] if positive is None else [(word, 1.0) for word in positive]
    negative = [] if negative is None else [(word, -1.0) for word in negative]

    # compute the weighted average of all the query words
    queries = []
    all_word_index = set()
    for word, weight in positive + negative:
        # gensim's Word2vec word2vec.wv.vocab
        # stores the index of a given word
        word_index = vocab[word].index
        word_vector = normed_vectors[word_index]
        queries.append(weight * word_vector)
        all_word_index.add(word_index)

    if not queries:
        raise ValueError('cannot compute similarity with no input')

    query_vector = np.mean(queries, axis=0).reshape(1, -1)
    normed_query_vector = normalize(query_vector).ravel()

    # cosine similarity between the query vector and all the existing word vectors
    scores = np.dot(normed_vectors, normed_query_vector)

    actual_len = topn + len(all_word_index)
    sorted_index = np.argpartition(scores, -actual_len)[-actual_len:]
    best = sorted_index[np.argsort(scores[sorted_index])[::-1]]

    result = [(index2word[index], scores[index]) for index in best if index not in all_word_index]
    return result[:topn]
