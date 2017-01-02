
"""
1. install mrjob
pip install mrjob

2. dataset: movielens, movie ratings 
http://grouplens.org/datasets/movielens/

3. variable dictionary: 
@userID
@movieID
@ratings
@timestamp

4. Basic MapReduce concepts

the MAPPER converts raw source data into key value pairs,
while the reducer groups the data by the key and combines the 
results together 

"""

# Task: histogram of the ratings
# e.g. how many 1 ~ 5 ratings are there respectively


from mrjob.job import MRJob

# class of the MRJob 
class MRRatingCounter(MRJob) : 
    
    # @line: each raw unprocessed input line of your data 
    # mapper will be called once for every line of data
    # here return every rating and the value tells that it occured once.
    # right now the key argument goes unused, you can also write it as _
    # the key becomes useful when combining multiple mapper 
    def mapper( self, key, line ) :
        ( userID, movieID, rating, timestamp ) = line.split("\t")
        yield rating, 1
    
    # takes the grouped key value pairs 
    # and sum them up, the value is named occurences 
    def reducer( self, rating, occurences ) :
        yield rating, sum(occurences)

# execute 
if __name__ == "__main__" :
    MRRatingCounter.run() 








