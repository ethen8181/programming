import numpy as np


def kos(user_factors, item_factors, indices, indptr, u, k):
    user = user_factors[u]
    pos_items = indices[indptr[u]:indptr[u + 1]]

    # compute positive item score, and select the k_th one
    pos_score = np.dot(item_factors[pos_items], user)

    # should be argpartition and check the number of positive
    # items to ensure it doesn't go out of bound
    sorted_pos_idx = np.argsort(pos_score)[::-1]
    pos_item = sorted_pos_idx[min(k, pos_items.shape[0])]
    pos = item_factors[pos_item]
    return pos
