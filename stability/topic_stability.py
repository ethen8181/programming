import numpy as np
from scipy.optimize import linear_sum_assignment


class TopicStability:
    """
    Compute topic stability for scikit-learn's LDA model,
    we could possibly support different vectorizer and models
    
    Parameters
    ----------
    vec: scikit-learn's CountVectorizer or TfidfVectorizer
    
    lda_model: scikit-learn's LatentDirichletAllocation
    
    n_top_words: int
        number of top words that represents each topic
    
    n_topics_range: sequence such as a list or 1d-numpy array
        search for the optimal topic number within this range
    
    n_sample_frac: float 0 ~ 1
        percentage of documents to sample for each sample set
    
    n_sample_time: int
        number of times to perform the sampling

    Reference
    ---------
    https://arxiv.org/abs/1404.4606
    """

    def __init__(self, vec, lda_model, n_top_words, n_topics_range, 
                 n_sample_time, n_sample_frac, bootstrap):
        self.vec = vec
        self.lda_model = lda_model
        self.bootstrap = bootstrap
        self.n_top_words = n_top_words
        self.n_sample_time = n_sample_time
        self.n_sample_frac = n_sample_frac    
        self.n_topics_range = n_topics_range


    def fit(self, X):        
        topics = len(self.n_topics_range)
        self.avg_agreements = np.zeros(topics)
        self.max_probs = np.zeros(( topics, len(X) ))

        if not self.bootstrap:
            n_sample_size = int(X.shape[0] * self.n_sample_frac)
    
        for idx, k in enumerate(self.n_topics_range):
            X_dtm = self.vec.fit_transform(X)
            features = self.vec.get_feature_names()
            
            # apply LDA to the complete dataset and 
            # obtain the reference rank set 
            self.lda_model.n_topics = k
            doc_topic_distr = self.lda_model.fit_transform(X_dtm)
            S_reference = self._get_rank_set(features)
            
            # for each document we'll also store the probability of belonging
            # to the most likely topic (maximum probability), this will be
            # used to visualize the histogram of the max probability later;
            # we'll also normalize the document-topic distribution, because
            # the current verson of the probability is not normalized (0.17)    
            doc_topic_distr /= np.sum(doc_topic_distr, axis = 1, keepdims = 1)
            self.max_probs[idx] = np.max(doc_topic_distr, axis = 1)
            
            # apply LDA to each samples and obtain each samples' rank set
            S_samples = []
            for _ in range(self.n_sample_time):
                if self.bootstrap: 
                    sample = np.random.choice(X, size = X.shape[0])
                else:
                    sample = np.random.choice(X, size = n_sample_size, replace = False)
                
                sample_dtm = self.vec.transform(sample)
                self.lda_model.fit(sample_dtm)
                S_sample = self._get_rank_set(features)
                S_samples.append(S_sample)
            
            # compute average agreement score between reference and samples
            agreements = np.zeros(self.n_sample_time)
            for s in range(self.n_sample_time):
                agreements[s] = self._compute_agreement(S_reference, S_samples[s])

            self.avg_agreements[idx] = np.mean(agreements)
        
        self.best_n_topic = self.n_topics_range[ np.argmax(self.avg_agreements) ]
        return self


    def _get_rank_set(self, features):
        """
        the rank set for the topic model is simply the top words
        for each topic (a list of list)
        """
        S = []
        for topic in self.lda_model.components_:
            top_terms = [ features[i] for i in np.argsort(topic)[-self.n_top_words:] ]
            S.append(top_terms)
            
        return S


    def _compute_agreement(self, S1, S2):
        """
        measuring the agreement between two different 
        k-way topic models, represented as two rank sets;
        the rank set is simply the top words for each topic
        """
        
        # compute the similarity matrix
        n_topic = len(S1)
        sim_mat = np.zeros(( n_topic, n_topic ))
        for row in range(n_topic):
            for col in range(n_topic):
                sim_mat[row, col] = self._compute_avg_jaccard(S1[row], S2[col])    
        
        # solve for the optimal permutation using hungarian algorithm,
        # for the scipy implement, each element is presented as cost
        # hence we use the negative sign of the similarity matrix as input
        row_ind, col_ind = linear_sum_assignment(-sim_mat)
        agreement = np.mean( sim_mat[row_ind, col_ind] )
        return agreement    


    def _compute_avg_jaccard(self, ranking1, ranking2):
        """
        weighted version of jaccard similarity, 
        which takes into account rank positions
        """
        total = 0
        k = len(ranking1)
        for i in range(1, k + 1):
            total += self._compute_jaccard( ranking1[:i], ranking2[:i] )

        avg_jaccard_sim = total / k
        return avg_jaccard_sim


    def _compute_jaccard(self, ranking1, ranking2):
        """
        compute jaccard similarity that does not take into account 
        rank positions and indefinite list
        """
        set1 = set(ranking1)
        set2 = set(ranking2)
        numerator = len( set1.intersection(set2) )
        if not numerator:
            return 0

        denominator = len( set1.union(set2) )
        jaccard_sim = numerator / denominator
        return jaccard_sim