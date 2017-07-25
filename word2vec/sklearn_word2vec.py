import numpy as np
from joblib import cpu_count
from gensim.models import Word2Vec
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer


class Word2Vectorizer(BaseEstimator, TransformerMixin):
    """
    Sklearn wrapper for gensim's Word2Vec model

    Parameters
    ----------
    sg : int, default 0
        Defines the training algorithm; if sg = 0 CBOW is used.
        Otherwise (sg = 1), skip-gram is employed

    size : int, default 100
        The dimensionality of the feature vectors

    window : int, default 5
        Maximum distance between the current and predicted word within a sentence

    alpha : float, default 0.025
        Initial learning rate (will linearly drop to min_alpha as training progresses)

    seed : int, default 1
        Random number generator. Initial vectors for each word are seeded with a hash of the
        concatenation of word + str(seed). Note that for a fully deterministically-reproducible run,
        you must also limit the model to a single worker thread, to eliminate ordering jitter
        from OS thread scheduling (In Python 3, reproducibility between interpreter launches
        also requires use of the PYTHONHASHSEED environment variable to control hash randomization)

    min_count : int, default 5
        Ignore all words with total frequency lower than this

    max_vocab_size, int, default None
        Limit RAM during vocabulary building; if there are more unique words than this,
        then prune the infrequent ones. Every 10 million word types need about 1GB of RAM.
        Set to None for no limit

    sample : float, default 1e-3
        Threshold for randomly downsampled higher-frequency words, useful range is (0, 1e-5)

    workers : int, default -1
        Worker threads to train the model, faster training with multicore machines; same idea
        as scikit-learn's n_jobs where default -1 means use all

    hs : int, default 0
        If set to 0 (default), and negative is non-zero, negative sampling will be used;
        if 1, hierarchical softmax will be used for model training.

    negative : int, default 5
        If > 0, negative sampling will be used. It specifies how many “noise words”
        should be drawn (usually between 5-20). If set to 0, no negative samping is used

    cbow_mean : int, default 1
        If 0, use the sum of the context word vectors. If 1 (default) use the mean.
        Only applies when cbow is used

    hashfxn : callable, default hash
        hash function to use to randomly initialize weights, for increased training reproducibility.
        Default is Python’s rudimentary built in hash function

    iter : int, default 5
        Number of iterations (epochs) over the corpus

    trim_rule : default None
        Vocabulary trimming rule, specifies whether certain words should remain in the vocabulary,
        be trimmed away, or handled using the default (discard if word count < min_count).
        Can be None (min_count will be used), or a callable that accepts parameters
        (word, count, min_count) and returns either utils.RULE_DISCARD, utils.RULE_KEEP or
        utils.RULE_DEFAULT. Note: The rule, if given, is only used to prune vocabulary during
        build_vocab() and is not stored as part of the model

    sorted_vocab : int, default 1
        If 1 (default), sort the vocabulary by descending frequency before assigning word indexes

    batch_words : int, default 10000
        Target size (in words) for batches of examples passed to worker threads
        (and thus cython routines). (Larger batches will be passed if individual
        texts are longer than 10000 words, but the standard cython code truncates
        to that maximum)

    w2v : str, default None
        If str, then it's assumed to be the path to the pre-trained word vectors, default None
        simply assumes we'll train the word vectors from scratch

    tfidf : bool, default True
        When combining the word vectors to a document level, whether to multiply the word vector's
        weight by the idf (inverse document frequency) before taking the average

    Attributes
    ----------
    w2v_ : dict
        word vector dictionary, where the key is the vocabulary in the corpus,
        value is its corresponding word vectors

    w2idf_ : dict
        word inverse document frequency dictionary, where the key is the vocabulary
        in the corpus, value is its corresponding inverse document frequency weight.
        Only available when the `tfidf` parameter if set to True

    References
    ----------
    Gensim Documentation: Model word2vec
    https://radimrehurek.com/gensim/models/word2vec.html
    """
    def __init__(self, sg = 0, hs = 0, size = 100, alpha = 0.025, window = 5, min_count = 5,
                 max_vocab_size = None, sample = 1e-3, seed = 1, workers = -1, min_alpha = 0.0001,
                 negative = 5, cbow_mean = 1, hashfxn = hash, iter = 5, null_word = 0,
                 trim_rule = None, sorted_vocab = 1, batch_words = 10000, w2v = None, tfidf = True):
        # gensim Word2Vec's parameter
        self.sg = sg
        self.hs = hs
        self.seed = seed
        self.iter = iter
        self.size = size
        self.alpha = alpha
        self.sample = sample
        self.window = window
        self.hashfxn = hashfxn
        self.workers = workers
        self.negative = negative
        self.cbow_mean = cbow_mean
        self.min_count = min_count
        self.min_alpha = min_alpha
        self.null_word = null_word
        self.trim_rule = trim_rule
        self.batch_words = batch_words
        self.sorted_vocab = sorted_vocab
        self.max_vocab_size = max_vocab_size

        # extra parameter
        self.w2v = w2v
        self.tfidf = tfidf

    def fit(self, X, y = None):
        """
        Fit the model according to the given training data

        Parameters
        ----------
        X : list or nd.array of words
            data
        """
        workers = cpu_count()
        if self.workers > 0 and self.workers < workers:
            workers = self.workers

        if self.w2v is None:
            word2vec = Word2Vec(
                sentences = X, size = self.size, alpha = self.alpha, window = self.window,
                min_count = self.min_count, max_vocab_size = self.max_vocab_size,
                sample = self.sample, seed = self.seed, workers = workers,
                min_alpha = self.min_alpha, sg = self.sg, hs = self.hs, negative = self.negative,
                cbow_mean = self.cbow_mean, hashfxn = self.hashfxn, iter = self.iter,
                null_word = self.null_word, trim_rule = self.trim_rule,
                sorted_vocab = self.sorted_vocab, batch_words = self.batch_words)

            # once we’re finished training the model (i.e. no more updates, only querying)
            # we can store the word vectors and delete the model to trim unneeded model memory
            self.w2v_ = {w: vec for w, vec in zip(word2vec.wv.index2word, word2vec.wv.syn0)}
        else:
            # TODO : ??? is assuming w2v a file path generalizable
            self.w2v_ = {}
            all_words = set(w for words in X for w in words)

            # GLOVE pretrained weight's format
            with open(self.w2v) as f:
                for line in f:
                    splitted = line.split()
                    w = splitted[0]
                    vector = [float(x) for x in splitted[1:]]
                    if w in all_words:
                        self.w2v_[w] = np.asarray(vector)

        if self.tfidf:
            tfidf_vec = TfidfVectorizer(analyzer = lambda x: x)
            tfidf_vec.fit(X)
            self.w2idf_ = {w: tfidf_vec.idf_[i] for w, i in tfidf_vec.vocabulary_.items()}

        return self

    def transform(self, X):
        mean_embeddings = np.asarray([self._get_mean_embedding(words) for words in X])
        return mean_embeddings

    def _get_mean_embedding(self, words):
        """
        Average word vectors for all words in a text, if a word does not exist
        in the word embedding, its vector is filled with 0
        """

        # ensure the size still matches if it's loaded from pretrained word vectors
        size = self.size
        if self.w2v is not None:
            size = next(iter(self.w2v_.values())).size

        zero = np.zeros(size)
        if self.tfidf:
            embedding = np.mean([self.w2v_[w] * self.w2idf_[w]
                                 if w in self.w2v_ else zero for w in words], axis = 0)
        else:
            embedding = np.mean([self.w2v_.get(w, zero) for w in words], axis = 0)

        return embedding
