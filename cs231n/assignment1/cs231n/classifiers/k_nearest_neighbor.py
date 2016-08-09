import numpy as np

class KNearestNeighbor(object):
	""" a kNN classifier with L2 distance """

	def __init__(self):
		pass

	def train( self, X, y ):
		"""
		Train the classifier. For k-nearest neighbors this is just 
		memorizing the training data.

		Input:
		X - A num_train x dimension array where each row is a training point.
		y - A vector of length num_train, where y[i] is the label for X[i, :]
		"""
		self.X_train = X
		self.y_train = y
		
	
	def predict( self, X, k = 1, num_loops = 0 ):
		"""
		Predict labels for test data using this classifier.

		Input:
		X - A num_test x dimension array where each row is a test point.
		k - The number of nearest neighbors that vote for predicted label
		num_loops - Determines which method to use to compute distances
					between training points and test points.

		Output:
		y - A vector of length num_test, where y[i] is the predicted label for the
			test point X[i, :].
		"""
		if num_loops == 0:
			dists = self.compute_distances_no_loops(X)
		elif num_loops == 1:
			dists = self.compute_distances_one_loop(X)
		elif num_loops == 2:
			dists = self.compute_distances_two_loops(X)
		else:
			raise ValueError( 'Invalid value %d for num_loops' % num_loops )

		return self.predict_labels( dists, k = k )

	
	def compute_distances_two_loops( self, X_test ):
		"""
		Compute the distance between each test point and each training point
		in self.X_train using a nested loop over both the training data and the 
		test data.

		Input:
		X - An num_test x dimension array where each row is a test point.

		Output:
		dists - A num_test x num_train array where dists[i, j] is the distance
				between the ith test point and the jth training point.
		"""
		num_test = X_test.shape[0]
		num_train = self.X_train.shape[0]
		dists = np.zeros(( num_test, num_train ))
		for i in range(num_test):
			for j in range(num_train):
				
				# naive way of euclidean distance
				# distance = np.sqrt( np.sum( ( X_test[ i, : ] - self.X_train[ j, : ] ) ** 2 ) )

				# or simply
				distance = np.linalg.norm( X_test[ i, : ] - self.X_train[ j, : ] )
				dists[ i, j ] = distance

		return dists

	
	def compute_distances_one_loop( self, X_test ):
		"""
		Compute the distance between each test point and each training point
		in self.X_train using a single loop over the test data.

		Input / Output: Same as compute_distances_two_loops
		"""
		num_test = X_test.shape[0]
		num_train = self.X_train.shape[0]
		dists = np.zeros(( num_test, num_train ))
		for i in range(num_test):

			# naive way of euclidean distance
			# distance = np.sqrt( np.sum( ( X_test[ i, : ] - self.X_train ) ** 2, axis = 1 ) )

			# or simply
			distance = np.linalg.norm( X_test[ i, : ] - self.X_train, axis = 1 )
			dists[ i, : ] = distance

		return dists


	def compute_distances_no_loops( self, X_test ):
		"""
		Compute the distance between each test point and each training point
		in self.X_train using no explicit loops.

		Input / Output: Same as compute_distances_two_loops
		"""
		num_test = X_test.shape[0]
		num_train = self.X_train.shape[0]
		dists = np.zeros(( num_test, num_train ))

		# (x - y)^2 = x^2 -2xy + y^2 
		# for matrices, xy = matrix multiplication
		test_sum = np.sum( X_test ** 2, axis = 1 )
		train_sum = np.sum( self.X_train ** 2, axis = 1 )
		inner_product = np.dot( X_test, self.X_train.T )
		dists = np.sqrt( -2 * inner_product + test_sum.reshape( -1, 1 ) + train_sum )
		return dists

	
	def predict_labels( self, dists, k = 1 ):
		"""
		Given a matrix of distances between test points and training points,
		predict a label for each test point.

		Input:
		dists - A num_test x num_train array where dists[i, j] gives the distance
				between the ith test point and the jth training point.

		Output:
		y - A vector of length num_test where y[i] is the predicted label for the
			ith test point.
		"""
		num_test = dists.shape[0]
		y_pred = np.zeros(num_test)
		for i in range(num_test):
			k_nearest = np.argsort( dists[ i, : ] )[:k]
			closest_y = self.y_train[k_nearest]
			y_pred[i] = np.argmax( np.bincount(closest_y) )
		
		return y_pred


