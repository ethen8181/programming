import numpy as np


def build_vocab(sentences, sample = 0.001, min_count = 5):
    raw_vocab = {}
    for idx, sentence in enumerate(sentences, 1):
        for word in sentence:
            if word not in raw_vocab:
                raw_vocab[word] = 0
            else:
                raw_vocab[word] += 1

    # corpus_count = idx

    # keep track of the total number of retained
    # words to perform subsampling later
    vocab = {}
    index2word = []
    retain_total = 0
    for word, count in raw_vocab.items():
        if count >= min_count:
            retain_total += count
            vocab[word] = {'count': count}
            index2word.append(word)

    del raw_vocab

    # sort vocabulary's index by count and create the reverse index
    index2word.sort(key = lambda word: vocab[word]['count'], reverse = True)
    for idx, word in enumerate(index2word):
        vocab[word]['index'] = idx

    # precalculate each vocabulary item's threshold for sub-sampling
    threshold_count = sample * retain_total
    for word in index2word:
        count = vocab[word]['count']

        # word2vec's formula for the probability of down sampling
        prob = np.sqrt(count / threshold_count + 1) * threshold_count / count
        vocab[word]['prob'] = min(prob, 1.0)

    return vocab, index2word


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
