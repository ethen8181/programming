from scipy.stats import norm
import pandas as pd
import numpy as np

# train = pd.read_csv( 'data/u1.base', sep = '\t', header = None )

class BIKNN(object):
	"""docstring for ClassName"""
	
	def __init__( self, K = 1, B1 = 1, B2 = 1 ):
		self.K  = K
		self.B1 = B1
		self.B2 = B2
		
	
	def fit( self, data ):
		self.data = data
		self.data.columns = [ 'user_id', 'item_id', 'ratings' ]
		self.item_id_dict = { v : k 
							   for k, v in enumerate( data['item_id'].unique() ) }
		self.keys_ = self.item_id_dict.keys() 
		size = len(self.keys_)
		self.F_ = np.zeros( [ size, size ], dtype = np.int )
		self.G_ = np.zeros( [ size, size ], dtype = np.int )
		self.sup_ = np.zeros( [ size, size ], dtype = np.int )
		self.sim_ = np.zeros( [ size, size ] )

		# loop over all the item pair combinations and fill in the matrices
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
					self.F_[i1][i2], self.F_[i2][i1] = 1, 1
					self.G_[i1][i2], self.G_[i2][i1] = 1, 1
					self.sup_[i1][i2], self.sup_[i2][i1] = 1, 1
					self.sim_[i1][i2], self.sim_[i2][i1] = 1, 1

		# recalculate the support 
		supports = np.array(supports)
		mean = float( np.sum(supports) ) / supports.shape[0]
		std  = np.sqrt( float( np.sum( supports ** 2 ) ) / supports.shape[0] - mean ** 2 )

		self.w_ = np.zeros( [ size, size ] )
		self.sim_w_ = np.zeros( [ size, size ] )
		
		for _, i1 in self.item_id_dict.iteritems():
			for _, i2 in self.item_id_dict.iteritems():
				if i1 < i2:
					weight = norm( mean, std ).cdf( self.sup_[i1][i2] )
					self.w_[i1][i2], self.w_[i2][i1] = weight, weight				
	
				elif i1 == i2:
					self.w_[i1][i2], self.w_[i2][i1] = 1, 1

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
			and the second the numerator, third being the denominator
		"""
		item1_users  = self.data[ self.data['item_id'] == item1 ]['user_id'].unique()
		item2_users  = self.data[ self.data['item_id'] == item2 ]['user_id'].unique()
		common_users = set(item1_users).intersection(item2_users)
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



