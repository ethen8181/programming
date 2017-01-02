
# item-based collaborative filtering 


from mrjob.job import MRJob
from mrjob.step import MRStep
from math import sqrt 
from itertools import combinations

class MovieSimilarities(MRJob) :

	# add file so we can convert movie ids to actual movie names  
	def configure_options(self) :
		
		super( MovieSimilarities, self ).configure_options()
		self.add_file_option( "--items", help = "Path to u.item" )

	# set the up movie id and name dictionary 
	def load_movie_names(self) :

		self.movie_names = {}

		with open("u.item") as f :
			for line in f :

				fields = line.split("|")
				self.movie_names[ int(fields[0]) ] = fields[1]


	def steps(self) :

		return[ 

			MRStep( mapper  = self.mapperParseInput,
					reducer = self.reducerRatingsByUsers ), 
			MRStep( mapper  = self.mapperCreateItemPairs,
					reducer = self.reducerComputeSimilarity ),
			MRStep( mapper  = self.mapperSortSimilarity,
					mapper_init = self.load_movie_names,
					reducer = self.reducerOutputSimilarity )
		]

	
	# step 1. obtain each user's movie id and ratings pair
	def mapperParseInput( self, key, line ) :

		( userID, movieID, ratings, timestamp ) = line.split("\t")

		yield userID, ( movieID, float(ratings) )

	
	# note that the value comes into the reducer as an iterable object
	# convert that to list so we can use them for the next mapper 
	def reducerRatingsByUsers( self, userID, item_ratings ) :

		ratings = []

		for movieID, rating in item_ratings :
			ratings.append( ( movieID, rating ) )

		yield userID, ratings

	
	# 1. generate combination pairs of movie and their corresponding ratings
	# 	 this is essentially generating every possible movie pairs for each users.
	# 2. this mapper yields both directions, similarities are bi-directional 
	def mapperCreateItemPairs( self, userID, item_ratings ) :

		for item_rating1, item_rating2 in combinations( item_ratings, 2 ) :

			movieID1 = item_rating1[0]
			movieID2 = item_rating2[0]
			rating1  = item_rating1[1]
			rating2  = item_rating2[1]

			yield ( movieID1, movieID2 ), ( rating1, rating2 )
			yield ( movieID2, movieID1 ), ( rating2, rating1 )

	
	def cosineSimilarity( self, rating_pairs ) :

		num_pairs = 0
		sum_xx = sum_yy = sum_xy = 0

		for rating_x, rating_y in rating_pairs :

			sum_xx += rating_x * rating_x
			sum_yy += rating_y * rating_y
			sum_xy += rating_x * rating_y
			num_pairs += 1

		numerator   = sum_xy
		denominator = sqrt(sum_xx) * sqrt(sum_yy)

		score = 0

		# checking if the float is divided by zero
		if denominator :
			score = numerator / float(denominator)

		return ( score, num_pairs )

	# compute the similarity score between the rating vectors for 
	# each movie pair ( viewed by multiple people )
	def reducerComputeSimilarity( self, movie_pair, rating_pairs ) :

		score, num_pairs = self.cosineSimilarity(rating_pairs)

		# enforce a score and number of pairs threshold
		if score > 0.95 and num_pairs > 10 : 
			yield movie_pair, ( score, num_pairs )

	
	def mapperSortSimilarity( self, movie_pair, scores ) :

		score, n = scores
		movie1, movie2 = movie_pair

		yield ( self.movie_names[ int(movie1) ], score ), ( self.movie_names[ int(movie2) ], n )


	def reducerOutputSimilarity( self, movie_score, similar ) :

		movie1, score = movie_score
		
		for movie2, n in similar :
			yield movie1, ( movie2, score, n )


# python 7_recommendation.py --items=ml-100k/u.item ml-100k/u.data > sims.txt
if __name__ == "__main__" :
	MovieSimilarities.run()








