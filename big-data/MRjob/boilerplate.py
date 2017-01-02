

from mrjob.job import MRJob

class ClassName(MRJob) :

	def mapper( self, key, line ) :

		line.split(" ")

		yield 

	def reducer( self ) :

		yield 


if __name__ == "__main__" :
    ClassName.run() 

