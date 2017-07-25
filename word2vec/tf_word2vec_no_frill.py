import tensorflow as tf


def tf_word2vec(batch_gen, epochs, learning_rate, num_sampled,
                batch_size, embed_size, vocab_size, tensorboard):
    """
    Build the graph for word2vec model and train it

    References
    ----------
    https://github.com/chiphuyen/tf-stanford-tutorials/blob/master/examples/04_word2vec_no_frills.py
    """

    # when building out tensorflow's computation graph, it's a good practice to
    # group nodes/operations that have similar purposes together using name_scope;
    # this additional step will give us nicer graph representation in Tensorboard,
    # which is tool that gives us nice graphical representation of the computation
    # graph we have defined
    with tf.name_scope('data'):
        # for target_words:
        # we will use it with tensorflow's NCE loss later, and the function requires rank 2
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
        nce_weight = tf.Variable(
            tf.truncated_normal([vocab_size, embed_size], stddev = stddev), name = 'nce_weight')

        nce_bias = tf.Variable(tf.zeros([vocab_size]), name = 'nce_bias')

        # hidden layer -> output layer + NCE loss
        loss = tf.reduce_mean(tf.nn.nce_loss(weights = nce_weight,
                                             biases = nce_bias,
                                             labels = target_words,
                                             inputs = embed,
                                             num_sampled = num_sampled,
                                             num_classes = vocab_size), name = 'avg_loss')

    optimizer = tf.train.GradientDescentOptimizer(learning_rate)
    train_step = optimizer.minimize(loss)
    init = tf.global_variables_initializer()

    with tf.Session() as sess:
        sess.run(init)

        # record the average loss in the last skip_step steps
        history = []
        writer = tf.summary.FileWriter(tensorboard, sess.graph)
        for _ in range(epochs):
            centers, targets = next(batch_gen)
            loss_batch, _ = sess.run(
                [loss, train_step], feed_dict = {center_words: centers, target_words: targets})

            history.append(loss_batch / batch_size)

        writer.close()
        word_vectors = sess.run(embed_matrix)

    return word_vectors, history
