# word count but sort the vocabulary 
# a string-based sort 

from mrjob.job import MRJob
from mrjob.step import MRStep
import re

# sorting and chaining 

word_regex = re.compile(r"[\w]+")

class MRWordFrequencyCount(MRJob) :

	# setting up the sequence of the mapper and reducer
	# specifying which specific functions are the mapper and reducer
	# for each step
	# doing this will feed the output of the first MRStep's reducer to
	# the second MRStep's mapper  
	def steps(self) :

		return [ 

			MRStep( mapper  = self.mapperGetWords,
					reducer = self.reducerCountWords ),

			MRStep( mapper  = self.mapperGetCountKeys, 
					reducer = self.reducerOutputWords )
		]

	# normal word count mapper and reducer 
	def mapperGetWords( self, key, line ) :
		
		words = word_regex.findall(line)

		for word in words : 
			yield word.lower(), 1 

	def reducerCountWords( self, word, values ) :

		yield word, sum(values)

	# obtain the word and its corresponding count 
	# this mapper re-groups the words by the count 
	def mapperGetCountKeys( self, word, count ) :

		# 4 is the total number of digits of %d 
		# 0 replace ones less than four digit with leading zeros
		yield "%04d" % int(count), word

	# prints out the final output as count versus word
	def reducerOutputWords( self, count, words ) :

		for word in words : 
			yield count, word


if __name__ == "__main__" :
	MRWordFrequencyCount.run()


