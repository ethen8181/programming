from operator import itemgetter
from scipy.stats import norm
import pandas as pd
import numpy as np

class BIKNN(object):
	"""
	Boosted Incremental Knearest neighborhood item-based recommendation system

	Parameters
	----------
	K : int, default = 10
		value specifying the number of nearest (similar) items 
		to predicted the unknown ratings
	
	B1 : int, default = 5
		regularization parameter that penalizes the item bias 

	B2 : int, default = 5
		regularization parameter that penalizes the user bias 
	"""
	
	def __init__( self, K = 10, B1 = 5, B2 = 5 ):
		self.K  = K
		self.B1 = B1
		self.B2 = B2
		
	
	def fit( self, data ):
		"""
		Pass in the training data and fits the model, also
		initialize the factors that are required to perform the
		incremental update ( see attributes below )

		Attributes
		----------
		All the following array are square matrix with the size of 
		the unique item count

		F_ : int array
			numerator for the similarity score for every item pair

		G_ : int array
			denominator for the similarity score for every item pair 

		sup_ : int array
			similarity support, equals to the number of users who have 
			co-rated the item pair 

		sim_ :

		sim_w_ :


		"""
		self.data = data
		self.data.columns = [ 'user_id', 'item_id', 'ratings' ]
		self.item_id_dict = { v : k 
							  for k, v in enumerate( data['item_id'].unique() ) }
		self.keys_ = self.item_id_dict.keys() 
		size = len(self.keys_)
		self.F_   = np.ones( [ size, size ], dtype = np.int )
		self.G_   = np.ones( [ size, size ], dtype = np.int )
		self.sup_ = np.ones( [ size, size ], dtype = np.int )
		self.sim_ = np.ones( [ size, size ] )

		# loop over all the item pair combinations and fill in the matrices
		# also stores the support for each item pair to calculate the weighted
		# support later
		supports = []
		for item1, i1 in self.item_id_dict.iteritems():
			for item2, i2 in self.item_id_dict.iteritems():
				if i1 < i2:					
					similarity, numerator, denominator, support = \
					self.calculate_similarity( item1, item2 )				
					self.F_[i1][i2], self.F_[i2][i1] = numerator, numerator
					self.G_[i1][i2], self.G_[i2][i1] = denominator, denominator
					self.sup_[i1][i2], self.sup_[i2][i1] = support, support
					self.sim_[i1][i2], self.sim_[i2][i1] = similarity, similarity
					supports.append(support)

				elif i1 == i2:
					continue

		# recalculate the support 
		supports = np.asarray(supports)
		self.N = supports.shape[0]
		self.mean = float( np.sum(supports) ) / self.N
		self.variance = ( float( np.sum( supports ** 2 ) ) / self.N ) - self.mean ** 2
		std = np.sqrt(self.variance)

		self.w_ 	= np.ones( [ size, size ] )
		self.sim_w_ = np.ones( [ size, size ] )
		
		# loop over all the item pair combinations and calculate the 
		# cumulative distributive weight for each support 
		for _, i1 in self.item_id_dict.iteritems():
			for _, i2 in self.item_id_dict.iteritems():
				if i1 < i2:
					weight = norm( self.mean, std ).cdf( self.sup_[i1][i2] )
					self.w_[i1][i2], self.w_[i2][i1] = weight, weight				
	
				elif i1 == i2:
					continue

		self.sim_w_ = self.sim_ * self.w_
		return self


	def calculate_similarity( self, item1, item2 ):
		"""
		calculate similarity between two items,
		if there're no common users that rated the two items 
		return 0 as their similarity score 

		Parameters
		----------
		item1 : string
			The id of item 1

		item2 : string
			The id of item 2
			
		Returns
		--------
		A tuple
			The first element of the tuple is the similarity score,
			second is the numerator that calculated the score, 
			third being the denominator,
			fourth is the support number ( number of user that rated both items )
		"""
		common_users = self.get_common_users( item1, item2 )
		support = len(common_users)
		
		if support == 0:
			return 0, 0, 0, 0

		# obtain the sub-dataframe of the common user's ratings
		# for both items and calculate their similarities
		item1_ratings = self.get_item_ratings( item_id = item1, set_of_users = common_users )
		item2_ratings = self.get_item_ratings( item_id = item2, set_of_users = common_users )
		
		numerator 	= item1_ratings.dot(item2_ratings)
		denominator = np.sum( item1_ratings ** 2 ) + np.sum( item2_ratings ** 2 )
		similarity  = float(numerator) / denominator
		return similarity, numerator, denominator, support


	def get_common_users( self, item1, item2 ):
		"""get the set of users that have rated both items"""

		item1_users  = self.data[ self.data['item_id'] == item1 ]['user_id'].unique()
		item2_users  = self.data[ self.data['item_id'] == item2 ]['user_id'].unique()
		common_users = set(item1_users).intersection(item2_users)
		return common_users
	
	
	def get_item_ratings( self, item_id, set_of_users ):
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


	def predict_rating( self, item_id, user_id ): 
		"""predict the rating score for the specified item_id and user_id"""

		# extract the information to calculate the bias for the item
		# and user, these information are then used to calculate the baseline 
		item = self.data[ self.data['item_id'] == item_id ] 
		user = self.data[ self.data['user_id'] == user_id ]
		item_count   = item['ratings'].count()
		user_count   = user['ratings'].count()
		item_ratings = item['ratings'].values
		user_ratings = user['ratings'].values
		global_avg   = self.data['ratings'].mean()

		item_bias = float( np.sum( item_ratings - global_avg ) ) / ( self.B1 + item_count )
		user_bias = float( np.sum( user_ratings - global_avg - item_bias ) ) / ( self.B2 + user_count )
		baseline  = global_avg + item_bias + user_bias
		
		numerator   = 0.
		denominator = 0.
		nearest = self.knearest_amongst_user_rated( item_id, user_id )
		
		for nearest_id, sim in nearest:
			nearest_rating = user[ user['item_id'] == nearest_id ]['ratings'].values[0]
			nearest_item_count = self.data[ self.data['item_id'] == nearest_id ]['ratings'].count()
			nearest_item_bias  = ( nearest_rating - global_avg ) / ( self.B1 + nearest_item_count )
			numerator += ( sim * ( nearest_rating - global_avg - user_bias - nearest_item_bias ) )
			denominator += sim

		if denominator > 0.:
			score = baseline + ( numerator / denominator )
		else:
			score = baseline
		return score


	def knearest_amongst_user_rated( self, item_id, user_id ):
		"""
		given an item_id obtain its knearest item, 
		also supply a user id so that we will only look 
		from all the other restaurants that the user has rated 
		  
		Returns
		--------
		A sorted list
			of the top k similar restaurants. The list is a list of tuples
			( item_id, similarity ).
		"""
		user_rated = self.data[ self.data['user_id'] == user_id ]['item_id'].unique()
		
		similars = []
		for other_item_id in user_rated:
			if other_item_id != item_id:
				similarity = self.get_similarity( other_item_id, item_id )
				similars.append( ( other_item_id, similarity ) )

		similars_sorted = sorted( similars, key = itemgetter(1), reverse = True )	
		return similars_sorted[0:self.K] 

	
	def get_similarity( self, item1, item2 ):
		"""returns the similarity score given two item ids"""
		sim = self.sim_w_[ self.item_id_dict[item1] ][ self.item_id_dict[item2] ]
		return sim






# train = pd.read_csv( 'data/u1.base', sep = '\t', header = None )

