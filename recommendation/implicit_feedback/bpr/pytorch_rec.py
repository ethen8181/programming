import torch
import numpy as np
import torch.nn as nn
import torch.utils.data as data


class Interactions(data.Dataset):
    """
    Hold data in the form of an interactions matrix.
    Typical use-case is like a ratings matrix:
    - Users are the rows
    - Items are the columns
    - Elements of the matrix are the ratings given by a user for an item.

    Used with Pytorch's DataLoader (must override __getitem__ and __len__)

    References
    ----------
    http://pytorch.org/docs/master/data.html#torch.utils.data.Dataset
    """

    def __init__(self, ratings):
        self.ratings = ratings.astype(np.float32).tocoo()
        self.n_users = self.ratings.shape[0]
        self.n_items = self.ratings.shape[1]

    def __getitem__(self, index):
        # For keeping track of indices, int32 might not be enough for large models
        # so int64 (long) is preferred
        # https://discuss.pytorch.org/t/problems-with-target-arrays-of-int-int32-types-in-loss-functions/140/2
        row = self.ratings.row[index].astype(np.int64)
        col = self.ratings.col[index].astype(np.int64)
        val = self.ratings.data[index]
        return row, col, val

    def __len__(self):
        return self.ratings.nnz


class BaseModule(nn.Module):
    """
    Base module for explicit matrix factorization

    Parameters
    ----------
    n_users : int
        Number of users

    n_items : int
        Number of items

    n_factors : int
        Number of latent factors (or embeddings or whatever you want to
        call it)

    sparse : bool
        Whether or not to treat embeddings as sparse. NOTE: cannot use
        weight decay on the optimizer if sparse=True. Also, can only use
        Adagrad.
    """
    def __init__(self, n_users, n_items, n_factors, sparse):
        super().__init__()
        self.n_factors = n_factors
        self.user_bias = nn.Embedding(n_users, 1, sparse = sparse)
        self.item_bias = nn.Embedding(n_items, 1, sparse = sparse)
        self.user_factors = nn.Embedding(n_users, n_factors, sparse = sparse)
        self.item_factors = nn.Embedding(n_items, n_factors, sparse = sparse)

    def forward(self, user_ids, item_ids):
        """
        Forward pass through the model. For a single user and item, this
        looks like:
        user_bias + item_bias + user_embeddings.dot(item_embeddings)

        Parameters
        ----------
        user_ids : tensor
            Tensor of user indices

        item_ids : tensor
            Tensor of item indices

        Returns
        -------
        prediction : tensor
            Predicted ratings/interactions
        """

        # view is similar to numpy's reshape, except unlike reshape, the new tensor
        # returned by "view" shares the underlying data with the original tensor,
        # so it is really a view into the old tensor instead of creating a brand new one
        # https://stackoverflow.com/questions/42479902/how-view-method-works-for-tensor-in-torch
        user_factor = self.user_factors(user_ids).view(-1, self.n_factors)
        item_factor = self.item_factors(item_ids).view(-1, self.n_factors)
        user_bias = self.user_bias(user_ids).view(-1, 1)
        item_bias = self.item_bias(item_ids).view(-1, 1)

        # for batch dot product, instead of doing the dot product
        # then only extract the diagonal element (which is the value
        # of that current batch), i.e.
        #
        # torch.diag(user_factor.mm(item_factor.T))
        #
        # performing a hadamard product, i.e. matrix element-wise product
        # then do a sum along the column will be more efficient since it's less operations
        # http://people.revoledu.com/kardi/tutorial/LinearAlgebra/HadamardProduct.html
        dot = torch.sum(user_factor * item_factor, dim = 1)
        prediction = user_bias + item_bias + dot
        return prediction
