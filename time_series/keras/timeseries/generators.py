import numpy as np


def time_series_generator(X, label_index, lookback, delay, min_index, max_index,
                          shuffle=False, batch_size=128, step=6):
    """
    TODO https://stanford.edu/~shervine/blog/keras-how-to-generate-data-on-the-fly.html
    https://keunwoochoi.wordpress.com/2017/08/24/tip-fit_generator-in-keras-how-to-parallelise-correctly/
    """
    if max_index is None:
        max_index = len(X) - delay - 1

    i = min_index + lookback
    while True:
        if shuffle:
            rows = np.random.randint(
                min_index + lookback, max_index, size=batch_size)
        else:
            if i + batch_size >= max_index:
                i = min_index + lookback

            # TODO why min is needed
            rows = np.arange(i, min(i + batch_size, max_index))
            i += len(rows)

        # shape [batch_size, time_step, num_features]
        samples = np.zeros((len(rows), lookback // step, X.shape[1]))
        targets = np.zeros((len(rows),))
        for j, row in enumerate(rows):
            indices = range(row - lookback, row, step)
            samples[j] = X[indices]
            targets[j] = X[row + delay, label_index]

        yield samples, targets
