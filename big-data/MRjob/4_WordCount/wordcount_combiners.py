# word count with combiners

# mapper takes a bunch of key / value pairs and pass them to the reducer 
# combiner is kind of like taking out the redundant work required by the mapper
# so it eases the loading of the reducer, this can have overhead as you do not
# need that many communications between mappers and reducers.
# same as saying, now hadoop has the option of doing some of work within the mapper  

# the input of your combiner and reducer must be identical
# though the output of the reducer can differ as it could be passed to another mapper 

# combiners can't include tasks that the reducer did not do,
# as you'll never be sure how many times it might be called upon 

from mrjob.job import MRJob
import re


word_regex = re.compile(r"[\w]+")
# 1. compile : 
# converts the regular expression into a pattern object 
# that can be used with other function 

# 2. \w : 
# refers to any word, numeric character and _
# in [] is equivalent to match all [a-ZA-Z0-9_]

# 3. r :
# indicates that \ should be treated literally not as escape characters
# treats the blackslash inside the subsequent "" 
# this can prevent typing all regex as double backslash \\w 


class MRWordCount(MRJob) :

	def mapper( self, key, line ) :

		# regex.findall : 
		# find matches of the regular expression object
		# returns a tuple 
		words = word_regex.findall(line)

		for word in words :
			yield word.lower(), 1 

	def combiner( self, key, values ) :

		yield key, sum(values)

	def reducer( self, key, values ) :

		yield key, sum(values)

# python wordcount.py book.txt > wordcount.txt
if __name__ == "__main__" :
	MRWordCount.run() 

