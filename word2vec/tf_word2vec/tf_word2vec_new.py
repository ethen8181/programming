import numpy as np
import tensorflow as tf
from tqdm import trange
from sklearn.preprocessing import normalize


class TfWord2vec:

    def __init__(self, batch_size, embed_size, vocab_size, window_size,
                 num_neg_samples, epochs, learning_rate, method):
        self.epochs = epochs
        self.batch_size = batch_size
        self.vocab_size = vocab_size
        self.embed_size = embed_size
        self.window_size = window_size
        self.num_neg_samples = num_neg_samples
        self.learning_rate = learning_rate
        self.method = method

    def fit(self, indexed_texts):
        self._create_graph()
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            self.history_ = []
            for epoch in trange(self.epochs):
                centers, targets = generate_batch_data(
                    indexed_texts, self.batch_size, self.window_size, self.method)

                # for _ in range(batch_iters):
                # try:
                feed_dict = {self._centers: centers, self._targets: targets}
                _, loss = sess.run([self._optimizer, self._loss], feed_dict)

                # writer.add_summary(summary, epoch)
                self.history_.append(loss)

        # writer.close()
            self.embed_in_ = sess.run(self._embed_in)
            self.embed_out_ = sess.run(self._embed_out)

        return self

    def _create_graph(self):
        tf.reset_default_graph()
        self._create_placeholders()
        self._create_variables()
        self._create_loss()
        self._create_optimizer()
        # self._create_summaries()
        return self

    def _create_placeholders(self):
        with tf.name_scope('inputs'):
            self._centers = tf.placeholder(tf.int32, shape=[self.batch_size], name='centers')
            self._targets = tf.placeholder(tf.int32, shape=[self.batch_size, 1], name='targets')

        return self

    def _create_variables(self):
        with tf.name_scope('weights'):
            stddev = 1.0 / np.sqrt(self.embed_size)
            embed_init = tf.truncated_normal([self.vocab_size, self.embed_size], stddev=stddev)
            self._embed_in = tf.Variable(embed_init, name='embed_in')
            self._embed_out = tf.Variable(embed_init, name='embed_out')
            self._embed_out_bias = tf.Variable(tf.zeros([self.vocab_size]), name='embed_out_bias')

        return self

    def _create_loss(self):
        with tf.name_scope('loss'):
            centers_embed_in = tf.nn.embedding_lookup(self._embed_in, self._centers, name='embed')
            self._loss = tf.reduce_mean(tf.nn.nce_loss(
                weights=self._embed_out,
                biases=self._embed_out_bias,
                labels=self._targets,
                inputs=centers_embed_in,
                num_sampled=self.num_neg_samples,
                num_classes=self.vocab_size), name='loss')

        return self

    def _create_optimizer(self):
        self._optimizer = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(self._loss)
        return self


def generate_batch_data(indexed_texts, batch_size, window_size, method='skip_gram'):
    batch_data = []
    batch_label = []
    while len(batch_data) < batch_size:
        # list[int]
        rand_indexed_texts = np.random.choice(indexed_texts)

        # print(rand_indexed_texts)
        for i in range(len(rand_indexed_texts)):
            window, label = create_window_and_label(rand_indexed_texts, window_size, i)
            # print(window, label)
            center, context = window[label], window[:label] + window[(label + 1):]
            center = [center] * len(context)
            if method == 'skip_gram':
                batch_data.extend(center)
                batch_label.extend(context)
            elif method == 'cbow':
                batch_data.extend(context)
                batch_label.extend(center)

    # trim batch and label at the end and convert to numpy array
    batch_data = np.array(batch_data[:batch_size])
    batch_label = np.array(batch_label[:batch_size]).reshape(-1, 1)
    return batch_data, batch_label


def create_window_and_label(indexed_texts, window_size, i):
    start_slice = max(i - window_size, 0)
    end_slice = i + window_size + 1
    window = indexed_texts[start_slice:end_slice]
    label = i if i < window_size else window_size
    return window, label


def most_similar(word_vectors, word2index, index2word, positive, negative=None, topn=10):

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
        word_index = word2index[word]
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
