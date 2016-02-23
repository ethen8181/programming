# recommendation system
# http://nbviewer.jupyter.org/github/cs109/content/blob/master/HW4_solutions.ipynb

def recompute_frame(df):
	"""
	Takes the review DataFrame and recompute the review average and review count
	for both the user and business and returns the recomputed DataFrame
	"""
	
	# recomputing
	df_u = df.groupby('user_id')
	df_b = df.groupby('business_id')
	avg_u, review_count_u = df_u['stars'].mean(), df_u['review_id'].count()
	avg_b, review_count_b = df_b['stars'].mean(), df_b['review_id'].count()

	"""
	# using the merge way 
	
	# remove the original column 
	df.drop( [ 'user_avg', 'user_review_count' ], axis = 1, inplace = True )
	df.drop( [ 'business_avg', 'business_review_count' ], axis = 1, inplace = True )

	user = pd.concat( [ avg_u, review_count_u ], axis = 1 )
	user.columns = [ 'user_avg', 'user_review_count' ]
	business = pd.concat( [ avg_b, review_count_b ], axis = 1 )
	business.columns = [ 'business_avg', 'business_review_count' ]

	df = df.merge( user, left_on = 'user_id', right_index = True )
	df = df.merge( business, left_on = 'business_id', right_index = True )
	"""
	
	df = df.copy() # revent copy warning 

	# assign the value back according to the index
	df.set_index( ['business_id'], inplace = True )
	df['business_avg'] = avg_b
	df['business_review_count'] = review_count_b
	df.reset_index( inplace = True )
	df.set_index( ['user_id'], inplace = True )
	df['user_avg'] = avg_u
	df['user_review_count'] = review_count_u
	df.reset_index( inplace = True )

	return df


# --------------------------------------------------------------------------------------

from scipy.stats.stats import pearsonr
import numpy as np
from operator import itemgetter

class DataBase(object):
	"""
	DataBase for the recommendation system

	Common Method Parameters
	----------
	These are common parameters that appears in the methods of this class
	and is documented here so it doesn't pop up in every method's docstring

	restaurant_id : string
		The id of the restaurant whose nearest neighbors we want

	user_id : string
		The id of the user, in whose reviewed restaurants we want to find the neighbors

	k : int, default 7
		the number of nearest neighbors desired

	reg: float, default 3.0
		the regularization to penalize the similarity score

	"""

	def __init__( self, df ):
		self.df = df

		# generate a index for each id to be match in the array 
		self.unique_biz_id = { v : k for k, v in enumerate( df.business_id.unique() ) }
		self.keys = self.unique_biz_id.keys()

		# initialzie the similarity and support array 
		l_keys = len(self.keys)
		self.database_sim = np.zeros( [ l_keys, l_keys ] )
		self.database_sup = np.zeros( [ l_keys, l_keys ], dtype = int )


	def recommend(self):
		"""
		calculates the similarity score and number of support for every
		pair of business id ( restaurant id )
		"""
		
		items = self.unique_biz_id.items()

		# business id is essentially restaurant id, replace the naming 
		for rest1, i1 in items:
			for rest2, i2 in items:
				if i1 < i2:
					sim, nsup = self.calculate_similarity( rest1 = rest1, rest2 = rest2 )
					self.database_sim[i1][i2] = sim
					self.database_sim[i2][i1] = sim
					self.database_sup[i1][i2] = nsup
					self.database_sup[i2][i1] = nsup
				elif i1 == i2:
					nsup = self.df[ self.df['business_id'] == rest1 ].user_id.count()
					self.database_sim[i1][i1] = 1.0
					self.database_sup[i1][i1] = nsup


	def get( self, b1, b2 ):
		"""returns a tuple of similarity, common_support given two business ids"""

		sim  = self.database_sim[ self.unique_biz_id[b1] ][ self.unique_biz_id[b2] ]
		nsup = self.database_sup[ self.unique_biz_id[b1] ][ self.unique_biz_id[b2] ]
		return ( sim, nsup ) 


	def calculate_similarity( self, rest1, rest2 ):
		"""
		Main function that does the computation work,
		calculate similarity between two restaurants

		Parameters
		----------
		rest1 : string
			The id of restaurant 1

		rest2 : string
			The id of restaurant 2
			
		Returns
		--------
		A tuple
			The first element of the tuple is the similarity score 
			and the second the common support n_common. 
		"""

		# obtain the number of common (same) reviewers 
		rest1_reviewers  = self.df[ self.df['business_id'] == rest1 ].user_id.unique()
		rest2_reviewers  = self.df[ self.df['business_id'] == rest2 ].user_id.unique()
		common_reviewers = set(rest1_reviewers).intersection(rest2_reviewers)
		n_common = len(common_reviewers)

		# obtain the sub-dataframe of the common reviewer's reviews
		# and calculate the pearson similiarity 
		rest1_reviews = self.get_restaurant_reviews( restaurant_id = rest1, 
													 set_of_users  = common_reviewers )
		rest2_reviews = self.get_restaurant_reviews( restaurant_id = rest2, 
													 set_of_users  = common_reviewers )
		sim = self.pearson_sim( n_common = n_common, 
								rest1_reviews = rest1_reviews, 
								rest2_reviews = rest2_reviews )
		return sim, n_common

	
	def get_restaurant_reviews( self, restaurant_id, set_of_users ):
		"""
		given a restaurant id and set of users that rated that restaurant
		return the sub-dataframe of their reviews 
		"""

		condition = ( ( self.df['business_id'] == restaurant_id ) & 
					  ( self.df['user_id'].isin(set_of_users)   ) )
		reviews = self.df[condition]

		# double check for duplicated user id 
		reviews[ reviews['user_id'].duplicated() == False ] 
		return reviews

	
	def pearson_sim( self, n_common, rest1_reviews, rest2_reviews ):
		"""
		Given a subframe of restaurant 1 reviews and a subframe of restaurant 2 reviews,
		where the reviewers are those who have reviewed both restaurants, return 
		the pearson correlation coefficient between the user average subtracted ratings.
		The similarity for zero common reviewers is treated as 0.
		As for the pearson correlation, note that it return a NaN if any of the 
		individual variances are 0, since the denominator of the pearson correlation 
		is the variance. In this case also returns a 0
		"""

		if n_common == 0:
			rho = 0
		else: 
			# subtract user ratings if their averages 
			# This makes the above ratings by the two users more comparable
			diff1 = rest1_reviews['stars'] - rest1_reviews['user_avg']
			diff2 = rest2_reviews['stars'] - rest2_reviews['user_avg']
			rho = pearsonr( diff1, diff2 )[0]

			if np.isnan(rho):
				rho = 0
				
		return rho


	def knearest( self, restaurant_id, set_of_restaurants, k = 7, reg = 3.0 ):
		"""
		Given a restaurant_id get a sorted list of the k most similar 
		restaurants from the entire database ( the set of restaurants ). 
		The similarity score between the two restaurants is penalized by a 
		regularization score, so it won't be biased if the numbers of common raters
		are too few

		Parameters
		----------
		set_of_restaurants : array
			The set of restaurants from which we want to find the nearest neighbors
		  
		Returns
		--------
		A sorted list
			of the top k similar restaurants. The list is a list of tuples
			( business_id, shrunken similarity, common support ).	
		"""
		
		similar = []		
		for other_rest_id in set_of_restaurants:
			if other_rest_id != restaurant_id:
				sim, n_common = self.get( other_rest_id, restaurant_id )
				sim = self.shrunk_sim( sim = sim, n_common = n_common, reg = reg )
				similar.append( ( other_rest_id, sim, n_common ) )

		similars = sorted( similar, key = itemgetter(1), reverse = True )	
		return similars[0:k]

	
	def shrunk_sim( self, sim, n_common, reg ):
		"""takes a similarity and shrinks it down by using the regularization"""
		sim = ( n_common * sim ) / ( n_common + reg )
		return sim


	def get_top_recommendations_for_user( self, user_id, n = 5, k = 7, reg = 3.0 ):
		"""
		Parameters
		----------
		n : int, default 5
			the top n restaurants of the user ( sorted by star rating )
		  
		Returns
		--------
		A sorted list
			top recommendations. The list is a list of tuples
			( business_id, business_avg ). This is essentially 
			combining the k-nearest recommendations for each of the user's n top choices, 
			removing duplicates and the ones the user has already rated.
		"""

		top_choices = self.get_user_top_choices( user_id = user_id, n = n )
		biz_ids = top_choices['business_id'].values
		rated_by_users = self.df[ self.df['user_id'] == user_id ]['business_id'].values

		# obtain all the user's top rated restaurant's neighbor's business id, 
		# note that we should not include restaurants that are already known to the user
		top_biz_ids = []	
		for biz_id in biz_ids:
			tops = self.knearest( restaurant_id = biz_id, 
								  set_of_restaurants = self.df.business_id.unique(), 
								  k = k, reg = reg )
			for biz, _, _ in tops:
				if biz not in rated_by_users:
					top_biz_ids.append(biz)

		# remove duplicated restaurants in the list and 
		# obtain each restaurant's corresponding average rating
		condition = self.df['business_id'].isin( set(top_biz_ids) )
		recommendation = self.df[['business_id', 'business_avg']][condition].drop_duplicates()

		# if top_recommendation only has 1 but you asked for 5 
		# .head() will return the 1 recommendation 
		top_recommendation = ( recommendation
							   .sort_values( ['business_avg'], ascending = False )
							   .head(n)
							   .values )

		r = [ ( biz_id, biz_avg ) for biz_id, biz_avg in top_recommendation ]
		return r


	def get_user_top_choices( self, user_id, n = 5 ):
		"""
		get the sorted top # of restaurants for a user by the star 
		rating the user gave them
		"""
		
		user_df = ( self.df[ self.df['user_id'] == user_id ][[ 'business_id', 'stars' ]]
					.sort_values( ['stars'], ascending = False )
					.head(n) )
		return user_df

	
	def rating( self, restaurant_id, user_id, k, reg ):
		"""
		returns the predicted rating for a user and an item
		  
		Returns
		--------
		A float
			which is the imputed rating that we predict that user_id will make 
			for the given restaurant_id
		"""

		# extract the reviews of the user and recalculate the baseline rating 
		user_reviews = self.df[ self.df['user_id'] == user_id ]
		mean_all  = self.df['stars'].mean()
		mean_user = user_reviews['user_avg'].values[0]
		mean_item = self.df['business_avg'][ self.df['business_id'] == restaurant_id ].values[0]
		baseline  = mean_user + mean_item - mean_all

		scores_numerator   = []
		scores_denominator = []
		nearest = self.knearest_amongst_user_rated( restaurant_id, user_id, k = 7, reg = 3.0 )

		for biz_id, sim, _ in nearest:
			reviews = user_reviews[ user_reviews['business_id'] == biz_id ]
			reviews_avg   = reviews['business_avg'].values[0]
			reviews_stars = reviews['stars'].values[0]			
			reviews_baseline = mean_user + reviews_avg - mean_all
			scores_numerator.append( sim * ( reviews_stars - reviews_baseline ) )
			scores_denominator.append(sim)

		scores = baseline + sum(scores_numerator) / sum(scores_denominator)
		return scores


	def knearest_amongst_user_rated( self, restaurant_id, user_id, k = 7, reg = 3.0 ):
		"""
		obtain the knearest restaurants, but this time also supply a user id
		so when can only obtain the restaurants that the user has rated 
		  
		Returns
		--------
		A sorted list
			of the top k similar restaurants. The list is a list of tuples
			( business_id, shrunken similarity, common support ).
		"""

		user_rated = self.df[ self.df['user_id'] == user_id ]['business_id'].unique()
		return self.knearest( restaurant_id = restaurant_id, 
							  set_of_restaurants = user_rated, k = k, reg = reg )

	@staticmethod
	def lookup_business_name( df, biz_id ):
		return df['biz_name'][ df['business_id'] == biz_id ].values[0]


	@staticmethod
	def lookup_user_name( df, user_id ):
		return df['user_name'][ df['user_id'] == user_id ].values[0]


	@staticmethod
	def get_other_ratings( df, restaurant_id, user_id ):
		"""get a user's rating for a restaurant and the restaurant's average rating"""
		choice = df[ ( df['business_id'] == restaurant_id ) & ( df['user_id'] == user_id ) ]
		users_score   = choice['stars'].values[0]
		average_score = choice['business_avg'].values[0]
		return users_score, average_score


# ------------------------------------------------------------------------------------------
from itertools import izip

def make_results_plot( df, k, reg ):
	"""
	takes a set of actual ratings, and a set of predicted ratings, 
	and plots the latter against the former for comparison
	"""

	uid = smalldf['user_id'].values
	bid = smalldf['business_id'].values
	actual = smalldf['stars'].values
	predicted = np.zeros( len(actual) )
	counter = 0
	for biz_id, user_id in izip( bid, uid ):
		predicted[counter] = rating( biz_id, user_id, k = k, reg = reg ) 
		counter = counter + 1
	# compare_results( actual, predicted )
