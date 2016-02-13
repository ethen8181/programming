from sklearn.base import clone 
from itertools import combinations
from sklearn.cross_validation import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np


class SBS(object) :

	def __init__( self, estimator, k_features, scoring = accuracy_score, 
				  test_size = 0.25, random_state = 1 ) :

		self.scoring 	  = scoring
		self.estimator 	  = clone(estimator) # clone the estimator without copying the dataset
		self.k_features   = k_features
		self.test_size 	  = test_size
		self.random_state = random_state

	def fit( self, x, y ) :

		# split the training set further into train / valid 
		x_train, x_test, y_train, y_test = train_test_split( 
			x, y, test_size = self.test_size, random_state = self.random_state 
		)

		# scores_ and subsets_ records the best score and corresponding indices
		# in each round 
		dim = x_train.shape[1]
		self.indices_ = tuple( range(dim) )
		self.subsets_ = [self.indices_]
		score = self.calc_score( x_train, x_test, y_train, y_test, self.indices_ )
		self.scores_ = [score]

		while dim > self.k_features :

			scores  = []
			subsets = []

			for i in combinations( self.indices_, dim - 1 ) :
				score = self.calc_score( x_train, x_test, y_train, y_test, i )
				scores.append(score)
				subsets.append(i)

			# obtain the best score and use the best scores' indices to train the 
			# next combination 
			best = np.argmax(scores)
			self.indices_ = subsets[best]
			self.subsets_.append(self.indices_)
			self.scores_.append(scores[best])
			dim -= 1

		return self

	def transform( self, x ) :
		return x[ :, self.indices_ ]

	def calc_score( self, x_train, x_test, y_train, y_test, indices ) :
		# fit the model using the chosen indices
		# and return the prediction acurracy score
		self.estimator.fit( x_train[ :, indices ], y_train )
		pred  = self.estimator.predict( x_test[ :, indices ] )
		score = self.scoring( pred, y_test )
		return score


