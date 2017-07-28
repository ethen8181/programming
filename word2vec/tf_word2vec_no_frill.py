import numpy as np
import tensorflow as tf
from tqdm import trange


# def tf_word2vec(batch_gen, epochs, learning_rate, num_sampled,
#                 batch_size, embed_size, vocab_size, tensorboard):
def tf_word2vec(data, epochs, learning_rate, num_sampled, window_size,
                batch_size, embed_size, vocab_size, tensorboard):
    """
    Word2vec skipgram model with negative sample loss using
    Tensorflow as backend

    Parameters
    ----------

    References
    ----------
    https://github.com/chiphuyen/tf-stanford-tutorials/blob/master/examples/04_word2vec_no_frills.py
    """

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

    optimizer = tf.train.GradientDescentOptimizer(learning_rate)
    train_step = optimizer.minimize(total_loss)
    init = tf.global_variables_initializer()

    batch_iters = len(data) // batch_size
    with tf.Session() as sess:
        sess.run(init)

        # record the average loss in the last skip_step steps
        history = []
        writer = tf.summary.FileWriter(tensorboard, sess.graph)
        for _ in trange(epochs):
            iterator = generate_sample(indexed_words = data, window = window_size)
            batch_gen = get_batch(iterator, batch_size)

            for _ in range(batch_iters):
                centers, targets = next(batch_gen)
                feed_dict = {center_words: centers, target_words: targets}
                _, loss, summary = sess.run([train_step, total_loss, summary_op], feed_dict)
                history.append(loss / batch_size)

        writer.close()
        word_vectors = sess.run(embed_matrix)

    return word_vectors, history


def generate_sample(indexed_words, window):
    """
    Form training pairs according to the skip-gram model

    Parameters
    ----------
    indexed_words : list
        list of index that represents the words, e.g. [5243, 3083, 11],
        and 5243 might represent the word "Today"

    window : int
        window size of the skip-gram model, where word is sampled before
        and after the center word according to this window size
    """
    for index, center in enumerate(indexed_words):
        # random integers from `low` (inclusive) to `high` (exclusive)
        context = np.random.randint(1, window + 1)

        # get a random target before the center word
        for target in indexed_words[max(0, index - context):index]:
            yield center, target

        # get a random target after the center word
        for target in indexed_words[(index + 1):(index + 1 + context)]:
            yield center, target


def get_batch(iterator, batch_size):
    """
    Group a numerical stream of centered and targeted
    word into batches and yield them as Numpy arrays
    """
    while True:
        center_batch = np.zeros(batch_size, dtype = np.int32)
        target_batch = np.zeros((batch_size, 1), dtype = np.int32)
        for index in range(batch_size):
            center_batch[index], target_batch[index] = next(iterator)

        yield center_batch, target_batch
