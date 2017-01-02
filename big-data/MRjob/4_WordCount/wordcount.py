# word count 

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

	def reducer( self, key, values ) :

		yield key, sum(values)

# python wordcount.py book.txt > wordcount.txt
if __name__ == "__main__" :
	MRWordCount.run() 

