

# most rated movies 
# how many ratings each movies got and obtain the largest one 

from mrjob.job import MRJob
from mrjob.step import MRStep


class MostRating(MRJob) :

	def steps(self) :

		return [

			MRStep( mapper  = self.mapperGetCount,
					reducer = self.reducerTotalCount ),
			MRStep( reducer = self.reducerFindMax )
		]

	def mapperGetCount( self, key, line ) :

		( userID, movieID, rating, timestamp ) = line.split("\t")

		yield movieID, 1 

	# counts up the total number of ratings per movie 
	# the key returns nothing, while the value 
	def reducerTotalCount( self, movieID, counts ) :

		yield None, ( sum(counts), movieID )

	# the second reducer without a mapper will run
	# on the entire data instead of grouped by each key 
	# the max function will run on the first element of the tuple  
	def reducerFindMax( self, key, value ) :

		yield max(value)

# python MostRating.py ml-100k/u.data 
if __name__ == "__main__" :
    MostRating.run()


# the movie id 50 received 583 ratings in this dataset 



