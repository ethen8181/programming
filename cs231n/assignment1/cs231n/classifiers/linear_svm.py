import numpy as np

def svm_loss_naive( W, X, y, reg ):
	"""
	Structured SVM loss function, naive implementation (with loops)
	
	Inputs:
	-------
	- W: C x D array of weights (each row represents a class)
	- X: D x N array of data. Data are D-dimensional columns
	- y: 1-dimensional array of length N with labels 0...K-1, for K classes
	- reg: (float) regularization strength
	
	Returns:
	--------
	a tuple of:
		- loss as single float
		- gradient with respect to weights W; an array of same shape as W
	"""

	# initialize the gradient dW as zero
	dW = np.zeros(W.shape)	
	num_train = X.shape[1]
	num_classes = W.shape[0]
		
	# compute the loss and the batch gradient
	loss = 0.0
	for i in range(num_train):

		# the scores of all the classes for one sample
		scores = np.dot( W, X[ :, i ] )
		correct_class = y[i]
		correct_class_score = scores[correct_class]
		
		count = 0
		for j in range(num_classes):
			if j == correct_class:
				index = j
			
			margin = scores[j] - correct_class_score + 1 # note delta = 1
			if margin > 0:
				count += 1
				loss  += margin				
				dW[ j, : ] += X[ :, i ]

		dW[ index, : ] -= count * X[ :, i ]

	# loss is a sum over all training examples, but we want it
	# to be an average instead so we divide by num_train, same with the gradient
	loss /= num_train
	dW   /= num_train

	# add regularization to the loss and gradient
	loss += 0.5 * reg * np.sum(W * W)
	dW   += reg * W		
	
	return loss, dW


def svm_loss_vectorized( W, X, y, reg ):
	"""
	Structured SVM loss function, vectorized implementation.

	Inputs and outputs are the same as svm_loss_naive.
	"""
	
	num_train = X.shape[1]

	# scores [ class, sample ]
	# score for every class and every sample
	scores = np.dot( W, X )

	# optain the best scores for each sample, both are equivalent
	# correct_scores = np.choose( y, scores )
	correct_scores = scores[ y, range(num_train) ]

	# sum up all the margin errors for the data loss
	# remember to account for the j = y_i term we shouldn't count (set it back to 0)
	margin = np.maximum( 0, scores - correct_scores + 1 ) # delta = 1
	margin[ y, range(num_train) ] = 0	
	
	loss_data = np.sum(margin) / num_train
	loss_reg  = 0.5 * reg * np.sum(W * W)
	loss = loss_data + loss_reg

	# initialize the gradient as zero
	dW = np.zeros(scores.shape)
	dW[ margin > 0 ] = 1
	count = np.sum( dW, axis = 0 ) # number of times that the margin is greater than 0
	dW[ y, range(num_train) ] = -count
	
	dW_data = np.dot( dW, X.T ) / num_train
	dW_reg = reg * W
	dW = dW_data + dW_reg
	
	return loss, dW

