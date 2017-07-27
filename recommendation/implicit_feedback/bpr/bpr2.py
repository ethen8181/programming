import sys
import numpy as np
import tensorflow as tf
from tqdm import trange
from itertools import islice
from sklearn.base import BaseEstimator
from sklearn.preprocessing import normalize
from sklearn.neighbors import NearestNeighbors


class BPR(BaseEstimator):
    """
    Bayesian Personalized Ranking (BPR) for implicit feedback data
    using tensorflow as backend

    Inherit scikit-learn's BaseEstimator to get some free stuff
    - class representations, more informative when printing class
    - get, set parameters (it will raise ValueError if we pass in
      illegal parameters, while setattr will simply let it through)

    TODO : remove the scikit-learn dependency

    Parameters
    ----------
    learning_rate : float, default 0.01
        Learning rate for the gradient descent optimizer

    n_factors : int, default 20
        Number/dimension of user and item latent factors

    n_iters : int, default 10
        Number of iterations to train the algorithm

    batch_size : int, default 2000
        Batch size for batch gradient descent, the original paper
        uses stochastic gradient descent (i.e., batch size of 1),
        but this can make the training unstable (very sensitive to
        learning rate)

    reg : int, default 0.01
        Regularization term for the user and item latent factors

    random_state : int, default 1234
        Seed for the randomly initialized user, item latent factors,
        note that internally, this doesn't use numpy's RandomState but
        instead uses tensorflow's random generator

    verbose : bool, default True
        Whether to print progress bar while training

    tensorboard : str, default './graphs/bpr'
        Path for the tensorboard that visualizes loss curve
        and the computation graph

    Attributes
    ----------
    user_factors_ : 2d ndarray [n_users, n_factors]
        User latent factors learned

    item_factors_ : 2d ndarray [n_items, n_factors]
        Item latent factors learned

    item_bias_ : 1d ndarray [n_items]
        Bias term for the items

    history_ : list
        Loss function's history at each iteration, useful
        for evaluating whether the algorithm converged or not

    References
    ----------
    .. [1] `S. Rendle, C. Freudenthaler, Z. Gantner, L. Schmidt-Thieme
            Bayesian Personalized Ranking from Implicit Feedback
            <https://arxiv.org/pdf/1205.2618.pdf>`_
    """
    def __init__(self, learning_rate = 0.01, n_factors = 20, n_iters = 10,
                 batch_size = 2000, reg = 0.01, random_state = 1234, verbose = True,
                 tensorboard = './graphs/bpr'):
        self.reg = reg
        self.verbose = verbose
        self.n_iters = n_iters
        self.n_factors = n_factors
        self.batch_size = batch_size
        self.tensorboard = tensorboard
        self.random_state = random_state
        self.learning_rate = learning_rate

        # to avoid re-computation at predict
        self._prediction = None

    def fit(self, ratings):
        """
        Parameters
        ----------
        ratings : scipy sparse csr_matrix [n_users, n_items]
            sparse matrix of user-item interactions
        """
        # history stores the cost, allows assessing convergence
        self.history_ = []
        indptr = ratings.indptr
        indices = ratings.indices
        n_users, n_items = ratings.shape

        # ensure batch size makes sense, since the algorithm involves
        # for each step randomly sample a user, thus the batch size
        # should be smaller than the total number of users or else
        # we would be sampling the user with replacement
        batch_size = self.batch_size
        if n_users < batch_size:
            batch_size = n_users
            sys.stderr.write('WARNING: Batch size is greater than number of users,'
                             'switching to a batch size of {}\n'.format(n_users))

        batch_iters = n_users // batch_size

        # progress bar for training iteration if verbose is turned on
        loop = range(self.n_iters)
        if self.verbose:
            loop = trange(self.n_iters, desc = self.__class__.__name__)

        self._build_graph(n_users, n_items)
        init = tf.global_variables_initializer()

        with tf.Session() as sess:
            sess.run(init)

            coord = tf.train.Coordinator()
            threads = tf.train.start_queue_runners(coord = coord)
            writer = tf.summary.FileWriter(self.tensorboard, sess.graph)

            for epoch in loop:
                epoch_loss = 0.0
                for _ in range(batch_iters):
                    sampled_users, sampled_pos_items, sampled_neg_items = self._sample(
                        n_users, n_items, indices, indptr)

                    feed_dict = {self._slice_u: sampled_users,
                                 self._slice_i: sampled_pos_items,
                                 self._slice_j: sampled_neg_items}
                    _, loss, summary = sess.run(
                        [self._train_step, self._total_loss, self._summary_op], feed_dict)
                    epoch_loss += loss / self.batch_size

                epoch_loss /= batch_iters
                self.history_.append(epoch_loss)
                writer.add_summary(summary, epoch)

            coord.request_stop()
            coord.join(threads)
            writer.close()

            self.user_factors_ = sess.run(self._user_factors)
            self.item_factors_ = sess.run(self._item_factors)
            self.item_bias_ = sess.run(self._item_bias)

        return self

    def _build_graph(self, n_users, n_items):
        """build the tensorflow computational graph"""
        self._create_placeholders()
        self._create_variables(n_users, n_items)
        self._create_loss()
        self._create_optimizer()
        self._create_summaries()
        return self

    def _create_placeholders(self):
        """
        the input data is the sampled batch of users and
        its corresponding positive items (i) and negative items (j)
        """
        with tf.name_scope('input'):
            self._slice_u = tf.placeholder(tf.int32, self.batch_size, name = 'sampled_users')
            self._slice_i = tf.placeholder(tf.int32, self.batch_size, name = 'sampled_pos_items')
            self._slice_j = tf.placeholder(tf.int32, self.batch_size, name = 'sampled_neg_items')

        queue = tf.FIFOQueue(capacity = 50, dtypes = [tf.int32, tf.int32, tf.int32])
        enqueue_op = queue.enqueue_many([data, target])
        data_sample, label_sample = queue.dequeue()

        # create NUM_THREADS to do enqueue
        queue_runner = tf.train.QueueRunner(queue, [enqueue_op] * N_THREADS)

        return self

    def _create_variables(self, n_users, n_items):
        with tf.name_scope('weights'):
            user_init = tf.truncated_normal((n_users, self.n_factors), seed = self.random_state)
            item_init = tf.truncated_normal((n_items, self.n_factors), seed = self.random_state)
            self._user_factors = tf.Variable(user_init, name = 'user_factors')
            self._item_factors = tf.Variable(item_init, name = 'item_factors')
            self._item_bias = tf.Variable(tf.zeros(n_items), name = 'item_bias')

        return self

    def _create_loss(self):
        with tf.name_scope('loss'):
            # use tf.gather() to select a non-contiguous slice from the tensor,
            # equivalent to tensor[slice] in numpy
            # http://stackoverflow.com/questions/35146444/tensorflow-python-accessing-individual-elements-in-a-tensor
            user_u = tf.gather(self._user_factors, self._slice_u, name = 'users')
            item_i = tf.gather(self._item_factors, self._slice_i, name = 'pos_items')
            item_j = tf.gather(self._item_factors, self._slice_j, name = 'neg_items')
            bias_i = tf.gather(self._item_bias, self._slice_i, name = 'pos_item_bias')
            bias_j = tf.gather(self._item_bias, self._slice_j, name = 'neg_item_bias')

            # decompose the estimator, compute the difference between
            # the score of the positive items i and negative items j;
            #
            # a naive implementation in numpy might look like the following:
            # r_ui = np.diag(user_u.dot(item_i.T))
            # r_uj = np.diag(user_u.dot(item_j.T))
            # r_uij = r_ui - r_uj
            #
            # however, we can do better, so
            # for batch dot product, instead of doing the dot product
            # then only extract the diagonal element (which is the value
            # of that current batch), we perform a hadamard product,
            # i.e. matrix element-wise product then do a sum along the column will
            # be more efficient since it's less operations
            # http://people.revoledu.com/kardi/tutorial/LinearAlgebra/HadamardProduct.html
            # r_ui = np.sum(user_u * item_i, axis = 1)
            #
            # then we can achieve another speedup by doing the difference
            # on the positive and negative item up front instead of computing
            # r_ui and r_uj separately, these two idea will speed up the operations
            r_uij = tf.reduce_sum(user_u * (item_i - item_j), axis = 1)
            diff = bias_i - bias_j + r_uij

            # main loss function
            output = tf.clip_by_value(tf.nn.sigmoid(diff), 1e-10, 1.0)
            loss_uij = tf.reduce_sum(tf.log(output))

            # regularization for the weights
            loss_u = self.reg * tf.reduce_sum(user_u ** 2)
            loss_i = self.reg * tf.reduce_sum(item_i ** 2) + tf.reduce_sum(bias_i ** 2)
            loss_j = self.reg * tf.reduce_sum(item_j ** 2) + tf.reduce_sum(bias_j ** 2)
            self._total_loss = loss_u + loss_i + loss_j - loss_uij

        return self

    def _create_optimizer(self):
        optimizer = tf.train.GradientDescentOptimizer(self.learning_rate)
        self._train_step = optimizer.minimize(self._total_loss)
        return self

    def _create_summaries(self):
        tf.summary.scalar('loss', self._total_loss)
        self._summary_op = tf.summary.merge_all()
        return self

    def _sample(self, n_users, n_items, indices, indptr):
        """sample batches of random triplets u, i, j"""
        sampled_pos_items = np.zeros(self.batch_size, dtype = np.int32)
        sampled_neg_items = np.zeros(self.batch_size, dtype = np.int32)
        sampled_users = np.random.choice(n_users, size = self.batch_size).astype(np.int32)

        for idx, user in enumerate(sampled_users):
            pos_items = indices[indptr[user]:indptr[user + 1]]
            pos_item = np.random.choice(pos_items)
            neg_item = np.random.choice(n_items)
            while neg_item in pos_items:
                neg_item = np.random.choice(n_items)

            sampled_pos_items[idx] = pos_item
            sampled_neg_items[idx] = neg_item

        return sampled_users, sampled_pos_items, sampled_neg_items

    def predict(self):
        """
        Obtain the predicted ratings for every users and items
        by doing a dot product of the learnt user and item vectors.
        The result will be cached to avoid re-computing it every time
        we call predict, thus there will only be an overhead the first
        time we call it. Note, ideally you probably don't need to compute
        this as it returns a dense matrix and may take up huge amounts of
        memory for large datasets
        """
        if self._prediction is None:
            self._prediction = self.user_factors_.dot(self.item_factors_.T) + self.item_bias_

        return self._prediction

    def _predict_user(self, user):
        """
        returns the predicted ratings for the specified user,
        this is mainly used in computing evaluation metric,
        where we avoid computing the whole predicted rating matrix

        TODO : do we even need this in the class?
        """
        user_pred = self.user_factors_[user].dot(self.item_factors_.T) + self.item_bias_
        return user_pred
