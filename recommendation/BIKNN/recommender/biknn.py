import heapq
import numpy as np
from scipy.stats import norm
from operator import itemgetter
from itertools import combinations


class BIKNN:
    """
    Boosted Incremental K-Nearest Neighborhood 
    Item-Based Recommendation System

    Parameters
    ----------
    K : int, default = 20
        value specifying the number of nearest (similar) items 
        to predicted the unknown ratings
    
    B1 : int, default = 5
        regularization parameter that penalizes the item bias 

    B2 : int, default = 5
        regularization parameter that penalizes the user bias

    iterations : int, default 10000
        in the stage of predicting the newdata,
        after this number of iterations (rows of newdata), 
        the weighted similarity will be updated

    Example
    -------
    import pandas as pd
    from recommender import BIKNN

    # movielens, column order: user id, item id, ratings and timestamp
    # the fourth column is the timestamp, exclude it
    train = pd.read_csv( 'data/u1.base', sep = '\t', header = None )
    train = train.iloc[ :, 0:3 ]
    test  = pd.read_csv( 'data/u1.test', sep = '\t', header = None )
    test  = test.iloc[ :, 0:3 ]
    column_names  = [ 'user_ids', 'item_ids', 'ratings' ]
    train.columns = column_names
    test.columns  = column_names

    # make sure all the items and users that are in the testing data
    # has been seen in training 
    contain_items = test['item_ids'].isin( train['item_ids'].unique() )
    contain_users = test['user_ids'].isin( train['user_ids'].unique() )
    test = test[ contain_users & contain_items ]

    biknn1 = BIKNN( K = 20, B1 = 25, B2 = 25, iterations = 100000 )
    biknn1.fit( data = train, column_names = [ 'user_ids', 'item_ids', 'ratings' ] )
    pred = biknn1.predict(test)
    biknn1.evaluate( pred, test['ratings'] )
    """
    def __init__( self, K = 20, B1 = 5, B2 = 5, iterations = 10000 ):
        self.K  = K
        self.B1 = B1
        self.B2 = B2
        self.iterations = iterations


    def fit( self, data, column_names ):
        """
        Pass in the data and fits the model

        Parameters
        ----------
        data : DataFrame
            base training data

        column_names : list of strings
            specifying the column names of the DataFrame,
            has to be the combination of [ 'user_id', 'item_id', 'ratings' ]
        """

        """
        Factors that are required to perform the incremental update

        All the following array are square matrix with the size of 
        the unique item count

        F : np.array
            numerator for the similarity score for every item pair

        G : np.array
            denominator for the similarity score for every item pair,
            F and G are cached so that you can use F / G to obtain
            the unweighted similarity score

        sup : int np.array
            similarity support, equals to the number of users who have 
            co-rated the item pair 

        sim_w : np.array
            the weighted similarity array
        """
        self.column_names = column_names
        data.columns  = self.column_names
        self.user_ids = np.array(data['user_ids'])
        self.item_ids = np.array(data['item_ids'])
        self.ratings  = np.array(data['ratings'])

        # maps the item_id to indices, so they can be represented as an index
        # in an array, the unique item ids and user ids will both be used later
        # when computing the biases
        self.unique_item_ids = np.unique(self.item_ids)
        self.unique_user_ids = np.unique(self.user_ids)
        self.item_ids_dict = { v: k for k, v in enumerate(self.unique_item_ids) }

        # loop over all item pair combinations and fill in the matrices F, G and sup
        # also stores the support for each item pair to calculate the weighted support later
        size = len(self.item_ids_dict)
        self.array_size = size, size
        self.F = np.ones(self.array_size)
        self.G = np.ones(self.array_size)
        self.sup = np.ones( self.array_size, dtype = np.int )

        supports = []
        for item1, item2 in combinations( self.unique_item_ids, 2 ):
            i1, i2 = self.item_ids_dict[item1], self.item_ids_dict[item2]
            support, numerator, denominator = self._calculate_similarity( item1, item2 )
            self.F[i1][i2] = self.F[i2][i1] = numerator
            self.G[i1][i2] = self.G[i2][i1] = denominator
            self.sup[i1][i2] = self.sup[i2][i1] = support
            supports.append(support)

        # compute the support's info that's needed to update the 
        # support weight array and the weighted similarity score array
        # also initialize the cache factors for linear bias
        supports  = np.array(supports)      
        self.mean = np.mean(supports)
        self.var  = np.var(supports)
        self.N = supports.shape[0]
        self._update_support_weight_and_similarity()
        self._initialize_linear_bias()

        # indicates the model has been fitted
        self.is_fitted = True
        return self
    

    def _calculate_similarity( self, item1, item2 ):
        """
        calculate similarity between two items, the return value is
        a tuple of three element:
        - support (number of user that rated both items)
        - numerator of the similarity score 
        - denominator of the similarity score 
        """

        # get the set of users that have rated both items
        item1_boolean = self.item_ids == item1
        item2_boolean = self.item_ids == item2
        item1_users   = self.user_ids[item1_boolean]
        item2_users   = self.user_ids[item2_boolean]
        common_users  = list( set(item1_users).intersection(item2_users) )

        # if there're no users that rated the two items 
        # return 0 as their similarity score
        if not common_users:
            return 0, 0, 0
        
        # given the set of common users that rated the item, 
        # find their ratings for both item
        match = np.in1d( self.user_ids, common_users )
        item1_ratings = self.ratings[item1_boolean & match]
        item2_ratings = self.ratings[item2_boolean & match]
        
        support = len(common_users)
        numerator = item1_ratings.dot(item2_ratings)
        denominator = np.sum( item1_ratings ** 2 ) + np.sum( item2_ratings ** 2 )       
        return support, numerator, denominator


    def _update_support_weight_and_similarity(self):
        """ 
        loop over all the item pair combinations and calculate the 
        cumulative distributive weight for each support,
        then use the weight to compute the weighted similarity
        """
        
        # standard deviation for the normal distribution
        std = np.sqrt(self.var)

        w = np.ones(self.array_size)
        for i1, i2 in combinations( self.item_ids_dict.values(), 2 ):
            weight = norm.cdf( self.sup[i1][i2], self.mean, std )
            w[i1][i2] = w[i2][i1] = weight

        # sim_w indicates this is the similarity matrix times the weight
        self.sim_w = ( self.F / self.G ) * w
        self.sim_w[ np.isnan(self.sim_w) ] = 0      
        return self


    def _initialize_linear_bias(self):
        """
        compute the cached factor for the linear bias
        - the current global rating average
        - total count of the known ratings
        - sum of ratings of each users / items
        - count of ratings of each users / items
        """ 
        self.global_avg = np.mean(self.ratings)
        self.known_ratings_count = self.ratings.shape[0]

        # every items' / users' bias
        self.user_ratings_sum = {}
        self.item_ratings_sum = {}
        self.user_ratings_count = {} 
        self.item_ratings_count = {}

        for item_id in self.unique_item_ids:
            item_ratings = self.ratings[ self.item_ids == item_id ]
            self.item_ratings_sum[item_id] = np.sum(item_ratings)
            self.item_ratings_count[item_id] = item_ratings.shape[0]
            
        for user_id in self.unique_user_ids:
            user_ratings = self.ratings[ self.user_ids == user_id ]
            self.user_ratings_sum[user_id] = np.sum(user_ratings)
            self.user_ratings_count[user_id] = user_ratings.shape[0]

        return self
    

    def predict( self, newdata ):
        """
        make the prediction for the newdata, the columns'
        ordering should be the same as the training data
        """
        newdata.columns = self.column_names
        newdata = newdata.values
        
        prediction = []
        for idx, ( user_id, item_id1, rating1 ) in enumerate(newdata):
            # obtain all the other items and ratings associated with the user
            # and predict the ratings
            user = self.user_ids == user_id
            user_ratings = self.ratings[user]
            user_item_ids = self.item_ids[user]                     
            predicted = self._predict_rating( user_id, item_id1, user, user_item_ids )
            prediction.append(predicted)
            
            # update a bunch of stuff according to all the 
            # other items and ratings associated with the user
            self._update( item_id1, rating1, user_item_ids, user_ratings )          
            
            # update the support weight array and the weighted similarity 
            # score array, after a going through certain number of new ratings,
            # the number is specified by the user
            if idx % self.iterations == 0:
                self._update_support_weight_and_similarity()

            self._update_linear_bias( user_id, item_id1, rating1 )

        return prediction


    def _predict_rating( self, user_id, item_id, user, user_item_ids ):
        """
        predict the rating for a user_id and item_id,
        the user (index associated with the current user) 
        and user_item_ids and used multiple times, thus
        they're passed in to prevent re-computing them 
        """
        item_bias = self._calculate_item_bias(item_id)
        user_bias = self._calculate_user_bias( user_id, user_item_ids )
        baseline  = self.global_avg + item_bias + user_bias
        
        # obtain the knearest item id and it's similarity score
        # when doing so, make sure that we don't obtain
        # the same item_id
        similars = []
        other_item_ids = set(user_item_ids).difference([item_id])
        for other_item_id in other_item_ids:
            i1 = self.item_ids_dict[item_id]
            i2 = self.item_ids_dict[other_item_id]
            similarity = self.sim_w[i1][i2]
            similars.append( ( other_item_id, similarity ) )

        knearest = heapq.nlargest( self.K, similars, key = itemgetter(1) )
        
        numerator = 0
        denominator = 0
        for nearest_id, sim in knearest:
            # nearest rating is an array with one element, thus we directly retrieve it
            nearest_rating = self.ratings[ ( self.item_ids == nearest_id) & user ][0]
            nearest_item_bias = self._calculate_item_bias(nearest_id)
            numerator += sim * ( nearest_rating - self.global_avg - 
                                 user_bias - nearest_item_bias )
            denominator += sim

        try:
            rating = baseline + ( numerator / denominator )
        except ZeroDivisionError:
            rating = baseline
        return rating


    def _calculate_item_bias( self, item_id ):
        # _n, _d stands for numerator and denominator
        item_bias_n = ( self.item_ratings_sum[item_id] - 
                        self.global_avg * self.item_ratings_count[item_id] )
        item_bias_d = self.B1 + self.item_ratings_count[item_id]
        item_bias = item_bias_n / item_bias_d
        return item_bias


    def _calculate_user_bias( self, user_id, user_item_ids ):
        item_bias_total = 0
        for item_id in user_item_ids:
            item_bias_total += self._calculate_item_bias(item_id)

        user_bias_n = ( self.user_ratings_sum[user_id] - 
                        self.global_avg * self.user_ratings_count[user_id] - 
                        item_bias_total )
        user_bias_d = self.B2 + self.user_ratings_count[user_id]
        user_bias = user_bias_n / user_bias_d
        return user_bias


    def _update( self, item_id1, rating1, user_item_ids, user_ratings ):
        """update F, G array and support"""
        i1 = self.item_ids_dict[item_id1]
        for item_id2, rating2 in zip( user_item_ids, user_ratings ):            
            i2 = self.item_ids_dict[item_id2]

            # update F and G array
            F_new = self.F[i1][i2] + rating1 * rating2
            G_new = self.G[i1][i2] + rating1 ** 2 + rating2 ** 2
            self.F[i1][i2] = self.F[i2][i1] = F_new
            self.G[i1][i2] = self.G[i2][i1] = G_new    
            
            # compute and update the new support's mean, variance and count
            sup_delta = 1
            sup_old  = self.sup[i1][i2]
            sup_new  = sup_old + sup_delta       
            mean_new = self.mean + sup_delta / self.N
            var_new  = ( self.var + 
                         ( 2 * sup_delta * sup_old + sup_delta ** 2 ) / self.N +
                         self.mean ** 2 - mean_new ** 2 )
            
            self.var  = var_new
            self.mean = mean_new
            self.sup[i1][i2] = self.sup[i2][i1] = sup_new

        return self


    def _update_linear_bias( self, user_id, item_id, rating ):
        """
        update the linear bias's cached factor after making the prediction
        for each newdata
        """
        global_avg_new_n = self.global_avg * self.known_ratings_count + rating
        self.known_ratings_count += 1
        global_avg_new_d = self.known_ratings_count
        self.global_avg  = global_avg_new_n / global_avg_new_d
        
        self.user_ratings_sum[user_id] += rating
        self.item_ratings_sum[item_id] += rating
        self.user_ratings_count[user_id] += 1
        self.item_ratings_count[item_id] += 1
        return self


    @staticmethod
    def evaluate( ratings, predictions ):
        """mean absolute error of the predicted ratings"""
        mae = np.abs(ratings - predictions).mean()
        return mae


