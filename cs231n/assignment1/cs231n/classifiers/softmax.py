import numpy as np

def softmax_loss_vectorized( W, X, y, reg ):
	"""
	Softmax loss function, vectorized version.

	Inputs:
	- W: C x D array of weights
	- X: D x N array of data. Data are D-dimensional columns
	- y: 1-dimensional array of length N with labels 0...K-1, for K classes
	- reg: (float) regularization strength
	
	Returns:
	a tuple of:
		- loss as single float
		- gradient with respect to weights W, an array of same size as W
	"""
	num_train = X.shape[1]
	scores = np.dot( W, X )

	# for numerical stability of softmax
	# shift the values of the scores for each sample
	# so that the highest number is 0
	scores -= np.max( scores, axis = 0 ) 
	scores  = np.exp(scores)
	softmax = scores / np.sum( scores, axis = 0 ) # array shape [ class, sample ]
	
	loss_data = np.mean( -np.log( softmax[ y, range(num_train) ] ) )
	loss_reg  = 0.5 * reg * np.sum( W * W )
	loss = loss_data + loss_reg

	# gradient of each weight
	error = softmax
	error[ y, range(num_train) ] -= 1
	dW_data = np.dot( error, X.T ) / num_train
	dW_reg  = reg * W
	dW = dW_data + dW_reg
	
	return loss, dW


