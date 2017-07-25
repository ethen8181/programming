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
        learning rate for the Adam optimizer

    n_factors : int, default 20
        Number/dimension of user and item latent factors

    n_iters : int, default 10
        Number of iterations to train the algorithm

    batch_size : int, default 2000
        batch size for batch gradient descent, the original paper
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
                 batch_size = 2000, reg = 0.01, random_state = 1234, verbose = True):
        self.reg = reg
        self.verbose = verbose
        self.n_iters = n_iters
        self.n_factors = n_factors
        self.batch_size = batch_size
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

        # ensure batch size makes sense
        batch_size = self.batch_size
        if ratings.nnz < batch_size:
            batch_size = ratings.nnz
            sys.stderr.write('WARNING: Batch size is greater than number of training interactions,'
                             'switching to a batch size of {}\n'.format(ratings.nnz))

        batch_iters = ratings.nnz // batch_size

        # progress bar for training iteration if verbose is turned on
        loop = range(self.n_iters)
        if self.verbose:
            loop = trange(self.n_iters, desc = self.__class__.__name__)

        self._build_graph(n_users, n_items)
        init = tf.global_variables_initializer()

        with tf.Session() as sess:
            sess.run(init)

            for _ in loop:
                iteration_cost = 0.0
                for _ in range(batch_iters):
                    sampled = self._sample(n_users, n_items, indices, indptr)
                    sampled_users, sampled_pos_items, sampled_neg_items = sampled
                    feed_dict = {self._slice_u: sampled_users,
                                 self._slice_i: sampled_pos_items,
                                 self._slice_j: sampled_neg_items}
                    _, cost = sess.run([self._train_step, self._total_cost], feed_dict)
                    iteration_cost += cost / self.batch_size

                iteration_cost /= batch_iters
                self.history_.append(iteration_cost)

            self.user_factors_ = sess.run(self.user_factors)
            self.item_factors_ = sess.run(self.item_factors)
            self.item_bias_ = sess.run(self.item_bias)

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

    def _build_graph(self, n_users, n_items):
        """build the tensorflow computational graph"""
        # initialize random weights
        user_init = tf.truncated_normal((n_users, self.n_factors), seed = self.random_state)
        item_init = tf.truncated_normal((n_items, self.n_factors), seed = self.random_state)
        self.user_factors = tf.Variable(user_init, name = 'user_factors')
        self.item_factors = tf.Variable(item_init, name = 'item_factors')
        self.item_bias = tf.Variable(tf.zeros(n_items), name = 'item_bias')

        # the input data is the sampled batch of users and
        # its corresponding positive items (i) and negative items (j)
        self._slice_u = tf.placeholder(tf.int32, self.batch_size)
        self._slice_i = tf.placeholder(tf.int32, self.batch_size)
        self._slice_j = tf.placeholder(tf.int32, self.batch_size)

        # use tf.gather() to select a non-contiguous slice from the tensor
        # http://stackoverflow.com/questions/35146444/tensorflow-python-accessing-individual-elements-in-a-tensor
        user_u = tf.gather(self.user_factors, self._slice_u)
        item_i = tf.gather(self.item_factors, self._slice_i)
        item_j = tf.gather(self.item_factors, self._slice_j)
        bias_i = tf.gather(self.item_bias, self._slice_i)
        bias_j = tf.gather(self.item_bias, self._slice_j)

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

        # minimize the cost
        cost_u = self.reg * tf.reduce_sum(user_u ** 2)
        cost_i = self.reg * tf.reduce_sum(item_i ** 2) + tf.reduce_sum(bias_i ** 2)
        cost_j = self.reg * tf.reduce_sum(item_j ** 2) + tf.reduce_sum(bias_j ** 2)
        output = tf.clip_by_value(tf.nn.sigmoid(diff), 1e-10, 1.0)
        cost_uij = tf.reduce_sum(tf.log(output))
        self._total_cost = cost_u + cost_i + cost_j - cost_uij

        optimizer = tf.train.AdamOptimizer(self.learning_rate)
        self._train_step = optimizer.minimize(self._total_cost)
        return self

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

    def recommend(self, ratings, N = 5, user_ids = None):
        """
        Returns the top N ranked items for given user id,
        excluding the ones that the user already liked

        Parameters
        ----------
        ratings : scipy sparse csr_matrix [n_users, n_items]
            sparse matrix of user-item interactions

        N : int, default 5
            top-N similar items' N

        user_ids : 1d iterator, e.g. list or numpy array, default None
            users' id that we wish to find top-N recommended for,
            default None will find it for all users

        Returns
        -------
        recommendation : 2d numpy array [number of query users_ids, N]
            each row is the top-N ranked item for each query user
        """
        if user_ids is not None:
            recommendation = np.zeros((len(user_ids), N), dtype = np.int)
            for idx, user in enumerate(user_ids):
                top_n = self._recommend_user(ratings, user, N)
                recommendation[idx] = top_n
        else:
            n_users = ratings.shape[0]
            recommendation = np.zeros((n_users, N), dtype = np.int)
            for user in range(n_users):
                top_n = self._recommend_user(ratings, user, N)
                recommendation[user] = top_n

        return recommendation

    def _recommend_user(self, ratings, user, N):
        """the top-N ranked items for a given user"""
        scores = self._predict_user(user)

        # compute the top N items, removing the items that the user already liked
        # from the result and ensure that we don't get out of bounds error when
        # we ask for more recommendations than that are available
        liked = set(ratings[user].indices)
        count = N + len(liked)
        if count < scores.shape[0]:

            # when trying to obtain the top-N indices from the score,
            # using argpartition to retrieve the top-N indices in
            # unsorted order and then sort them will be faster than doing
            # straight up argort on the entire score
            # http://stackoverflow.com/questions/42184499/cannot-understand-numpy-argpartition-output
            ids = np.argpartition(scores, -count)[-count:]
            best_ids = np.argsort(scores[ids])[::-1]
            best = ids[best_ids]
        else:
            best = np.argsort(scores)[::-1]

        top_n = list(islice((rec for rec in best if rec not in liked), N))
        return top_n

    def get_similar_items(self, N = 5, item_ids = None):
        """
        return the top N similar items for itemid, where
        cosine distance is used as the distance metric

        Parameters
        ----------
        N : int, default 5
            top-N similar items' N

        item_ids : 1d iterator, e.g. list or numpy array, default None
            the item ids that we wish to find the similar items
            of, the default None will compute the similar items
            for all the items

        Returns
        -------
        similar_items : 2d numpy array [number of query item_ids, N]
            each row is the top-N most similar item id for each
            query item id
        """
        # cosine distance is proportional to normalized euclidean distance,
        # thus we normalize the item vectors and use euclidean metric so
        # we can use the more efficient kd-tree for nearest neighbor search;
        # also the item will always to nearest to itself, so we add 1 to =
        # get an additional nearest item and remove itself at the end
        normed_item_factors = normalize(self.item_factors_)
        knn = NearestNeighbors(n_neighbors = N + 1, metric = 'euclidean')
        knn.fit(normed_item_factors)

        # returns a distance, index tuple,
        # we don't actually need the distance
        if item_ids is not None:
            normed_item_factors = normed_item_factors[item_ids]

        _, items = knn.kneighbors(normed_item_factors)
        similar_items = items[:, 1:].astype(np.int32)
        return similar_items
