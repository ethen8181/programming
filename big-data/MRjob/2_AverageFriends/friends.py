# Task: what's the average number of friends by age 

# dataset: fake social network 
# @UserID
# @Name
# @Age
# @Number of Friends 

from mrjob.job import MRJob

class MRFriendsByAge(MRJob) : 

	# key / value = age / friend 
	# specify the friend is a float type 
	def mapper( self, key, line ) :
		
		( UserID, Name, Age, Friends ) = line.split(",")
		yield Age, float(Friends)

	# calculate the average 
	def reducer( self, Age, Friends ) :
	
		total = 0
		count = 0

		for friend in Friends :
			total += friend 
			count += 1
		
		average = total / count 

		# python format, five digits in total, 2 values on the right of the deciaml 
		yield Age, "{:5.2f}".format(average)  
		

# shell command: 
# > redirects the output to a .txt file  
# python friends.py fakefriends.csv > friendsbyage.txt
if __name__ == "__main__" :
    MRFriendsByAge.run() 



