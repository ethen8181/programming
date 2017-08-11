import numpy as np
import tensorflow as tf
from tqdm import trange


# def tf_word2vec(batch_gen, epochs, learning_rate, num_sampled,
#                 batch_size, embed_size, vocab_size, tensorboard):
# def tf_word2vec(data, epochs, learning_rate, num_sampled, window_size,
#                 batch_size, embed_size, vocab_size, tensorboard):
def tf_word2vec(sentences, vocab, epochs, learning_rate, num_sampled,
                window_size, batch_size, embed_size, tensorboard):
    """
    Word2vec skipgram model with negative sample loss using
    Tensorflow as backend

    Parameters
    ----------

    References
    ----------
    https://github.com/chiphuyen/tf-stanford-tutorials/blob/master/examples/04_word2vec_no_frills.py
    """
    vocab_size = len(vocab)

    # Clears the default graph stack and resets the global default graph;
    # this line is crucial if we want to re-run the class in interactive
    # environment such as jupyter notebook
    tf.reset_default_graph()

    # when building out tensorflow's computation graph, it's a good practice to
    # group nodes/operations that have similar purposes together using name_scope;
    # this additional step will give us nicer graph representation in Tensorboard,
    # which is tool that gives us nice graphical representation of the computation
    # graph we have defined
    with tf.name_scope('data'):
        # for target_words:
        # we will use it with tensorflow's loss later, and the function requires rank 2
        # input, that's why there's an extra dimension in the shape
        center_words = tf.placeholder(tf.int32, shape = [batch_size], name = 'center_words')
        target_words = tf.placeholder(tf.int32, shape = [batch_size, 1], name = 'target_words')

    with tf.name_scope('embedding_matrix'):
        # the actual word vectors
        embed_matrix = tf.Variable(
            tf.random_uniform([vocab_size, embed_size], -1.0, 1.0), name = 'embed_matrix')

    with tf.name_scope('loss'):
        # input -> hidden layer
        embed = tf.nn.embedding_lookup(embed_matrix, center_words, name = 'embed')

        # hidden layer -> output layer's weights
        stddev = 1.0 / embed_size ** 0.5
        output_weight = tf.Variable(
            tf.truncated_normal([vocab_size, embed_size], stddev = stddev), name = 'output_weight')

        output_bias = tf.Variable(tf.zeros([vocab_size]), name = 'output_bias')

        # hidden layer -> output layer + sampled softmax loss
        total_loss = tf.reduce_mean(tf.nn.sampled_softmax_loss(  # tf.nn.nce_loss(
            weights = output_weight, biases = output_bias,
            labels = target_words, inputs = embed,
            num_sampled = num_sampled, num_classes = vocab_size), name = 'loss')

    # create a summary scalar that reports the loss
    tf.summary.scalar('total_loss', total_loss)
    summary_op = tf.summary.merge_all()

    optimizer = tf.train.AdagradOptimizer(learning_rate)
    train_step = optimizer.minimize(total_loss)
    init = tf.global_variables_initializer()

    # batch_iters = len(data) // batch_size
    with tf.Session() as sess:
        sess.run(init)

        # record the average loss in the last skip_step steps
        history = []
        writer = tf.summary.FileWriter(tensorboard, sess.graph)
        for epoch in trange(epochs):
            iterator = generate_sample(sentences, vocab, window = window_size)
            batch_gen = get_batch(iterator, batch_size)

            # for _ in range(batch_iters):
            # try:
            centers, targets = next(batch_gen)
            feed_dict = {center_words: centers, target_words: targets}
            _, loss, summary = sess.run([train_step, total_loss, summary_op], feed_dict)

            writer.add_summary(summary, epoch)
            history.append(loss)

        writer.close()
        word_vectors = sess.run(embed_matrix)

    return word_vectors, history


def build_vocab(sentences, sample = 0.001, min_count = 5):
    raw_vocab = {}
    for index, sentence in enumerate(sentences, 1):
        for word in sentence:
            if word not in raw_vocab:
                raw_vocab[word] = 0
            else:
                raw_vocab[word] += 1

    # corpus_count = index

    # keep track of the total number of retained
    # words to perform subsampling later
    vocab = {}
    index2word = []
    count_total = 0
    for word, count in raw_vocab.items():
        if count >= min_count:
            count_total += count
            vocab[word] = {'count': count}
            index2word.append(word)

    del raw_vocab

    # sort vocabulary's index by descending word count and create the reverse index
    index2word.sort(key = lambda word: vocab[word]['count'], reverse = True)
    for index, word in enumerate(index2word):
        vocab[word]['index'] = index

    # precalculate each vocabulary item's threshold for down sampling
    threshold_count = sample * count_total
    for word in index2word:
        count = vocab[word]['count']

        # word2vec's formula for the probability of down sampling
        prob = np.sqrt(count / threshold_count + 1) * threshold_count / count
        vocab[word]['prob'] = min(prob, 1.0)

    return vocab, index2word


def generate_sample(sentences, vocab, window):
    """
    Form training pairs according to the skip-gram model

    Parameters
    ----------
    indexed_words : list
        List of index that represents the words, e.g. [5243, 3083, 11],
        and 5243 might represent the word "Today"

    window : int
        Window size of the skip-gram model, where word is sampled before
        and after the center word according to this window size
    """
    for sentence in sentences:
        word_vocabs = [vocab[w] for w in sentence if w in vocab and
                       vocab[w]['prob'] > np.random.rand()]

        for index, word in enumerate(word_vocabs):
            center = word['index']
            reduced_window = np.random.randint(1, window + 1)

            # words before the center word
            for context in word_vocabs[max(0, index - reduced_window):index]:
                target = context['index']
                yield center, target

            # words after the center word
            for context in word_vocabs[(index + 1):(index + 1 + reduced_window)]:
                target = context['index']
                yield center, target


def get_batch(iterator, batch_size):
    """
    Group a numerical stream of centered and context
    word into batches and yield them as numpy arrays
    """
    while True:
        center_batch = np.zeros(batch_size, dtype = np.uint32)
        target_batch = np.zeros((batch_size, 1), dtype = np.uint32)
        for index in range(batch_size):
            center_batch[index], target_batch[index] = next(iterator)

        yield center_batch, target_batch
