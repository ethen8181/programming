import heapq
import numpy as np
import pandas as pd
from scipy.stats import norm
from operator import itemgetter

class BIKNN(object):
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

	Example
	-------
	import pandas as pd
	from BIKNN import BIKNN
	train = pd.read_csv( 'data/u1.base', sep = '\t', header = None )
	train = train.iloc[ :, 0:3 ]
	test  = pd.read_csv( 'data/u1.test', sep = '\t', header = None )
	test  = test.iloc[ :, 0:3 ]

	movie_lens = BIKNN( K = 10, B1 = 5, B2 = 5 )
	movie_lens.fit( data = train, columns = [ 'user_id', 'item_id', 'ratings' ] )
	mae = movie_lens.update( test, iterations = 100 )

	"""
	
	def __init__( self, K = 20, B1 = 5, B2 = 5 ):
		self.K  = K
		self.B1 = B1
		self.B2 = B2
		
	
	def fit( self, data, columns ):
		"""
		Pass in the training data and fits the model, also
		initialize the factors that are required to perform the
		incremental update ( see attributes below )

		Parameters
		----------
		data : DataFrame
			base training data

		columns : a list of strings
			specifying the column name of the DataFrame,
			has to be the combination of[ 'user_id', 'item_id', 'ratings' ]

		Attributes
		----------
		All the following array are square matrix with the size of 
		the unique item count

		F : array
			numerator for the similarity score for every item pair

		G : array
			denominator for the similarity score for every item pair,
			F and G are cached so that you can use F / G to obtain
			the unweighted similarity score

		sup : int array
			similarity support, equals to the number of users who have 
			co-rated the item pair 

		sim_w : array
			the weighted similarity array
		"""
		self.data = data
		self.data.columns = columns

		# mapps the item_id to indices, so they can be represented as an element
		# in an array
		self.item_id_dict = { v : k 
							  for k, v in enumerate( self.data['item_id'].unique() ) }
		self.keys = self.item_id_dict.keys() 
		size = len(self.keys)
		self.F   = np.ones( [ size, size ] )
		self.G   = np.ones( [ size, size ] )
		self.sup = np.ones( [ size, size ], dtype = np.int )

		# loop over all the item pair combinations and fill in the matrices
		# also stores the support for each item pair to calculate the weighted
		# support later
		supports = []
		for item1, i1 in self.item_id_dict.items():
			for item2, i2 in self.item_id_dict.items():
				if i1 < i2:					
					numerator, denominator, support  = self._calculate_similarity( item1, item2 )				
					self.F[i1][i2] = self.F[i2][i1] = numerator
					self.G[i1][i2] = self.G[i2][i1] = denominator
					self.sup[i1][i2] = self.sup[i2][i1] = support
					supports.append(support)

		# calculate the support's info, this is then used to update the 
		# support weight array and the weighted similarity score array
		supports = np.array(supports)
		self.N = supports.shape[0]
		self.mean = np.sum(supports) / self.N
		self.variance = ( np.sum( supports ** 2 ) / self.N ) - self.mean ** 2		

		# initialize and compute the support weight and
		# the weighted similarity array
		self.w 	   = np.ones( [ size, size ] )
		self.sim_w = np.ones( [ size, size ] )	
		self._update_support_weight_and_similarity()

		# initialize linear bias factor
		self._initialize_linear_bias()
		return self


	def _calculate_similarity( self, item1, item2 ):
		"""
		calculate similarity between two items,
		if there're no common users that rated the two items 
		return 0 as their similarity score, note that only the 
		numerators and the denominators are cached

		Parameters
		----------
		item1 : string
			The id of item 1

		item2 : string
			The id of item 2
			
		Returns
		--------
		A tuple
			The first element is the numerator of the similarity score, 
			second being the denominator,
			third is the support number ( number of user that rated both items )
		"""
		common_users = self._get_common_users( item1, item2 )
		support = len(common_users)
		
		if support == 0:
			return 0, 0, 0

		# obtain the sub-dataframe of the common user's ratings
		# for both items and calculate their similarities
		item1_ratings = self._get_item_ratings( item_id = item1, set_of_users = common_users )
		item2_ratings = self._get_item_ratings( item_id = item2, set_of_users = common_users )
		
		numerator 	= item1_ratings.dot(item2_ratings)
		denominator = np.sum( item1_ratings ** 2 ) + np.sum( item2_ratings ** 2 )
		return numerator, denominator, support


	def _get_common_users( self, item1, item2 ):
		"""get the set of users that have rated both items"""

		item1_users  = self.data[ self.data['item_id'] == item1 ]['user_id'].unique()
		item2_users  = self.data[ self.data['item_id'] == item2 ]['user_id'].unique()
		common_users = set(item1_users).intersection(item2_users)
		return common_users
	
	
	def _get_item_ratings( self, item_id, set_of_users ):
		"""
		given a item id and the set of common users that 
		rated the item, return their ratings for the item
		"""
		condition = ( ( self.data['item_id'] == item_id ) & 
					  ( self.data['user_id'].isin(set_of_users) ) )
		reviews = self.data[condition]

		# remove duplicated user id and obtain the ratings value 
		reviews = reviews[ reviews['user_id'].duplicated() == False ]['ratings'].values 
		return reviews

	
	def _update_support_weight_and_similarity(self):
		""" 
		loop over all the item pair combinations and calculate the 
		cumulative distributive weight for each support,
		then use the weight to compute the weighted similarity
		"""
		
		# standard deviation for the normal distribution
		std = np.sqrt(self.variance)
		
		for i1 in self.item_id_dict.values():
			for i2 in self.item_id_dict.values():
				if i1 < i2:
					weight = norm( self.mean, std ).cdf( self.sup[i1][i2] )
					self.w[i1][i2] = self.w[i2][i1] = weight

		self.sim_w = ( self.F / self.G ) * self.w
		return self


	def _initialize_linear_bias(self):
		"""
		compute the cached factor for the linear bias
		1. the current global rating average
		2. total count of the known ratings
		3. sum of ratings of each users / items
		4. count of ratings of each users / items
		"""	
		self.global_avg = self.data['ratings'].mean()
		self.known_ratings_count = self.data['ratings'].count()

		# every items' / users' bias
		self.user_ratings_sum 	= {}
		self.item_ratings_sum 	= {}
		self.user_ratings_count = {} 
		self.item_ratings_count = {}

		unique_item_id = self.data['item_id'].unique()
		for item_id in unique_item_id:
			ratings = self.data[ self.data['item_id'] == item_id ]['ratings']
			self.item_ratings_sum[item_id] 	 = ratings.sum()
			self.item_ratings_count[item_id] = ratings.count()

		unique_user_id = self.data['user_id'].unique()
		for user_id in unique_user_id:
			ratings = self.data[ self.data['user_id'] == user_id ]['ratings']
			self.user_ratings_sum[user_id]   = ratings.sum()
			self.user_ratings_count[user_id] = ratings.count()

		return self


	def update( self, test, iterations = 100 ):
		"""
		loop through all the test data,
		meanwhile update relative information on the way
		and in the end return the MAE (mean absolute error)
		of the test data's rating 
		
		Parameters
		----------
		test : DataFrame
			test data for evaluating the predicted ratings

		iterations : int, default 100
			after this number of iterations ( number of new test data ), 
			the weighted similarity score will be updated
		
		Returns
		-------
		MAE : float
			mean absolute error of the predicted rating on the test data
		"""
		self.test = test
		self.test.columns = self.data.columns
		self.iterations = iterations

		absolute_error = 0
		absolute_error_count = 0
    
		# loop through all the test data's rating
		for index1, user_id1, item_id1, rating1 in test.itertuples():
		
			# predict the rating and store the absolute error
			predicted = self._predict_rating( item_id = item_id1, user_id = user_id1 )
			absolute_error += abs( predicted - rating1 )
			absolute_error_count += 1
			
			# obtain the user's other rating, after that
			# update the user rating database
			other_user = self.data[ self.data['user_id'] == user_id1 ]
			self.data  = pd.concat( [ self.data, test.iloc[ index1:index1 + 1 ] ], 
							  	    ignore_index = True )
			
			# loop through all the user's other rating
			for _, _, item_id2, rating2 in other_user.itertuples():

				# store the item id's index for the array
				i1 = self.item_id_dict[item_id1]
				i2 = self.item_id_dict[item_id2]

				# update the F and G array
				F_new = self.F[i1][i2] + ( rating1 * rating2 )
				G_new = self.G[i1][i2] + ( rating1 ** 2 + rating2 ** 2 )
				self.F[i1][i2], self.F[i2][i1] = F_new, F_new				
				self.G[i1][i2], self.G[i2][i1] = G_new, G_new
				
				
				# obtain the old support for the item pair,
				# compute the new one and the difference between them
				# to compute the new mean and variance for the support
				sup_old = self.sup[i1][i2]
				common_users = self._get_common_users( item_id1, item_id2 )
				sup_new = len(common_users)
				sup_delta = sup_new - sup_old
	
				# after calculating the new mean and variance of the support
				# update them
				mean_new = self.mean + sup_delta / self.N
				variance_new = ( self.variance + 
								 ( 2 * sup_delta * sup_old + sup_delta ** 2 / self.N ) +
								 self.mean ** 2 - mean_new ** 2 )
		
				# update support's array, mean, variance 
				self.sup[i1][i2] = self.sup[i2][i1] = sup_new
				self.mean = mean_new
				self.variance = variance_new

			# ------------------------------------------------------------------
			# update the support weight array and the weighted similarity 
			# score array, after a going through certain number of new ratings,
			# the number is specified by the user
			if index1 % self.iterations == 0:
				self._update_support_weight_and_similarity()


			# update the linear bias's cached factor
			global_avg_new_n = self.global_avg * self.known_ratings_count + rating1
			global_avg_new_d = 1 + self.known_ratings_count			
			self.global_avg  = global_avg_new_n / global_avg_new_d

			self.known_ratings_count += 1
			self.user_ratings_sum[user_id1] += rating1
			self.item_ratings_sum[item_id1] += rating1
			self.user_ratings_count[user_id1] += 1
			self.item_ratings_count[item_id1] += 1

		MAE = absolute_error / absolute_error_count
		return MAE

	
	def _predict_rating( self, item_id, user_id ): 
		"""predict the rating score for the specified item_id and user_id"""

		# calculate the bias for the current item and user
		# these information are then used to calculate the baseline
		user = self.data[ self.data['user_id'] == user_id ]
		user_rated_item_id = user['item_id'].unique()
		item_bias = self._calculate_item_bias(item_id)		
		user_bias = self._calculate_user_bias( user_id, user_rated_item_id )
		baseline  = self.global_avg + item_bias + user_bias

		numerator   = 0.
		denominator = 0.
		nearest = self._knearest_amongst_user_rated( item_id, user_rated_item_id )
		
		for nearest_id, sim in nearest:
			nearest_rating = user[ user['item_id'] == nearest_id ]['ratings'].values[0]
			nearest_item_bias  = self._calculate_item_bias(nearest_id)
			numerator += ( sim * ( nearest_rating - self.global_avg - user_bias - nearest_item_bias ) )
			denominator += sim

		if denominator > 0.:
			rating = baseline + ( numerator / denominator )
		else:
			rating = baseline
		return rating


	def _calculate_item_bias( self, item_id ):
		"""calculate the item bias given a item id"""

		# _n, _d stands for numerator and denominator
		item_bias_n = self.item_ratings_sum[item_id] - self.global_avg * self.item_ratings_count[item_id]
		item_bias_d = self.B1 + self.item_ratings_count[item_id]
		item_bias 	= item_bias_n / item_bias_d
		return item_bias


	def _calculate_user_bias( self, user_id, user_rated_item_id ):
		"""
		calculate the user bias given a user id
		and all the item ids that that user id has rated 
		"""
		item_bias_total = 0
		for other_item_id in user_rated_item_id:
			item_bias_total += self._calculate_item_bias(other_item_id)

		user_bias_n = ( self.user_ratings_sum[user_id] - 
						self.global_avg * self.user_ratings_count[user_id] - 
						item_bias_total )
		user_bias_d = self.B2 + self.user_ratings_count[user_id]
		user_bias 	= user_bias_n / user_bias_d
		return user_bias


	def _knearest_amongst_user_rated( self, item_id, user_rated_item_id ):
		"""
		given an item id and the item ids that the user has rated 
		obtain its knearest item
		  
		Returns
		--------
		(list) 
			A list of tuples ( item_id, similarity ), sorted by
			the top k similar items.
		"""		
		similars = []
		for other_item_id in user_rated_item_id:
			if other_item_id != item_id:
				similarity = self._get_similarity( other_item_id, item_id )
				similars.append( ( other_item_id, similarity ) )

		similars_sorted = heapq.nlargest( self.K, similars, key = itemgetter(1) )
		return similars_sorted

	
	def _get_similarity( self, item1, item2 ):
		"""returns the similarity score given two item ids"""
		sim = self.sim_w[ self.item_id_dict[item1] ][ self.item_id_dict[item2] ]
		return sim

