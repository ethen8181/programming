
# task: obtain the movie that was rated the most number of times 

# pass along a small chunk of data along with process
# in this case the actual movie name that corresponds to each movie id 

from mrjob.job import MRJob
from mrjob.step import MRStep


class MostPopularMovie(MRJob) :

	# add a command line options that sends an external file
	# enter the file name after the "--item" that you specified
	# boiler plate 
	def configure_options(self) :
		
		super( MostPopularMovie, self ).configure_options()
		self.add_file_option( "--items", help = "movie file name" )

	def steps(self) :

		return[

			MRStep( mapper  	 = self.mapperGetRatings,
					reducer_init = self.reducer_init,
					reducer      = self.reducerCountRatings ),
			MRStep( reducer 	 = self.reducerFindMax )
		]

	def mapperGetRatings( self, key, line ) :

		( userID, movieID, rating, timestamp ) = line.split("\t")
		yield movieID, 1 

	
	# the reducer that reads in the pipe delimited files
	# has to be named reducer_init 
	def reducer_init(self) :

		self.movie_names = {}

		with open("u.ITEM") as f :

			for line in f :
				fields = line.split("|")
				self.movie_names[ fields[0] ] = fields[1]
	
	def reducerCountRatings( self, key, values ) : 

		yield None, ( sum(values), self.movie_names[key] )

	def reducerFindMax( self, key, values ) :

		yield max(values)


# python MostPopularmovie.py --items=ml-100k/u.item ml-100k/u.data
if __name__ == "__main__" :
	MostPopularMovie.run()




