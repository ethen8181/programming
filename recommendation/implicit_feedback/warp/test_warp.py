import numpy as np
from warp_fast import warp_sample, apply_updates


class WARPBatchUpdate:
    """Collection of arrays to hold a batch of WARP sgd updates."""

    def __init__(self, batch_size, d):
        self.u = np.zeros(batch_size, dtype='int32')
        self.dU = np.zeros((batch_size, d), order='F')
        self.v_pos = np.zeros(batch_size, dtype='int32')
        self.dV_pos = np.zeros((batch_size, d))
        self.v_neg = np.zeros(batch_size, dtype='int32')
        self.dV_neg = np.zeros((batch_size, d))

    def clear(self):
        pass

    def set_update(self, ix, update):
        u, v_pos, v_neg, dU, dV_pos, dV_neg = update
        self.u[ix] = u
        self.dU[ix] = dU
        self.v_pos[ix] = v_pos
        self.dV_pos[ix] = dV_pos
        self.v_neg[ix] = v_neg
        self.dV_neg[ix] = dV_neg


class WARPDecomposition:

    def __init__(self, n_rows, n_cols, d):
        # initialize factors to small random values
        self.U = d ** -0.5 * np.random.random_sample((n_rows, d))
        self.V = d ** -0.5 * np.random.random_sample((n_cols, d))
        # ensure memory layout avoids extra allocation in dot product
        self.U = np.asfortranarray(self.U)


class Warp:

    def __init__(self, d, gamma, C, max_trials, batch_size, positive_thresh = 0):
        self.d = d  # dimension of the factors
        self.gamma = gamma  # learning rate
        self.C = C  # regularization constant
        self.max_trials = max_trials
        self.batch_size = batch_size
        self.positive_thresh = positive_thresh

    def fit(self, train, validation):
        n_rows, n_cols = train.shape
        decomposition = WARPDecomposition(n_rows, n_cols, self.d)
        updates = WARPBatchUpdate(self.batch_size, self.d)

        self._fit(decomposition, updates, train, validation)

        self.U_ = decomposition.U
        self.V_ = decomposition.V
        return self

    def _fit(self, decomposition, updates, train, validation):

        for it in range(self.max_iters):
            self.compute_updates(train, decomposition, updates)

    def compute_updates(self, train, decomposition, updates):
        updates.clear()

        warp_sample(decomposition.U,
                    decomposition.V,
                    train.data,
                    train.indices,
                    train.indptr,
                    self.positive_thresh,
                    self.max_trials)
