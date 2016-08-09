import numpy as np


def affine_forward( x, w, b ):
	"""
	Computes the forward pass for an affine (fully-connected) layer.

	The input x has shape (N, d_1, ..., d_k) and contains a minibatch of N
	examples, where each example x[i] has shape (d_1, ..., d_k). We will
	reshape each input into a vector of dimension D = d_1 * ... * d_k, and
	then transform it to an output vector of dimension M.

	Inputs:
	- x: A numpy array containing input data, of shape (N, d_1, ..., d_k)
	- w: A numpy array of weights, of shape (D, M), M number of class
	- b: A numpy array of biases, of shape (M,)
	
	Returns a tuple of:
	- out: output, of shape (N, M)
	- cache: (x, w, b)
	"""
	out = np.dot( x.reshape( x.shape[0], -1 ), w ) + b
	cache = x, w, b
	return out, cache


def affine_backward( dout, cache ):
	"""
	Computes the backward pass for an affine layer.

	Inputs:
	- dout: Upstream derivative, of shape (N, M), M is the number of classes
	- cache: Tuple of:
	- x: Input data, of shape (N, d_1, ... d_k)
	- w: Weights, of shape (D, M)

	Returns a tuple of:
	- dx: Gradient with respect to x, of shape (N, d1, ..., d_k)
	- dw: Gradient with respect to w, of shape (D, M)
	- db: Gradient with respect to b, of shape (M,)
	"""
	x, w, b = cache

	# gradient of w, b can be computed by matrix multiplication
	# with the dout. Just be careful with the dimensions of the output,
	# e.g. we know that the gradient on the weights dw must be of the same size as 
	# the w matrix after it is computed
	dx = np.dot( dout, w.T ).reshape(x.shape)
	dw = np.dot( x.reshape( x.shape[0], -1 ).T, dout )

	# gradient of for each class's bias is simply the sum of the errors
	db = np.sum( dout, axis = 0 )	
	return dx, dw, db


def relu_forward(x):
	"""
	Computes the forward pass for a layer of rectified linear units (ReLUs).

	Input:
	- x: Inputs, of any shape

	Returns a tuple of:
	- out: Output, of the same shape as x
	- cache: x
	"""
	out = np.maximum( 0, x )
	cache = x
	return out, cache


def relu_backward( dout, cache ):
	"""
	Computes the backward pass for a layer of rectified linear units (ReLUs).

	Input:
	- dout: Upstream derivatives, of any shape
	- cache: Input x, of same shape as dout

	Returns:
	- dx: Gradient with respect to x
	"""
	dx = np.where( cache > 0, dout, 0 )
	return dx


def batchnorm_forward( x, gamma, beta, bn_param ):
	"""
	Forward pass for batch normalization.
	
	During training the sample mean and (uncorrected) sample variance are
	computed from minibatch statistics and used to normalize the incoming data.
	During training we also keep an exponentially decaying running mean of the mean
	and variance of each feature, and these averages are used to normalize data
	at test-time.

	At each timestep we update the running averages for mean and variance using
	an exponential decay based on the momentum parameter:

	running_mean = momentum * running_mean + (1 - momentum) * sample_mean
	running_var = momentum * running_var + (1 - momentum) * sample_var

	Note that the batch normalization paper suggests a different test-time
	behavior: they compute sample mean and variance for each feature using a
	large number of training images rather than using a running average. For
	this implementation we have chosen to use running averages instead since
	they do not require an additional estimation step; the torch7 implementation
	of batch normalization also uses running averages.

	Input:
	- x: Data of shape (N, D)
	- gamma: Scale parameter of shape (D,)
	- beta: Shift paremeter of shape (D,)
	- bn_param: Dictionary with the following keys:
		- mode: 'train' or 'test'; required
		- eps: Constant for numeric stability
		- momentum: Constant for running mean / variance.
		- running_mean: Array of shape (D,) giving running mean of features
		- running_var Array of shape (D,) giving running variance of features

	Returns a tuple of:
	- out: of shape (N, D)
	- cache: A tuple of values needed in the backward pass
	"""
	mode = bn_param['mode']
	eps  = bn_param.get( 'eps', 1e-5 )
	momentum = bn_param.get( 'momentum', 0.9 )

	N, D = x.shape
	running_mean = bn_param.get( 'running_mean', np.zeros( D, dtype = x.dtype ) )
	running_var  = bn_param.get( 'running_var' , np.zeros( D, dtype = x.dtype ) )

	if mode == 'train':
		# training-time forward pass for batch normalization
		# Use minibatch statistics to compute the mean and variance, use these
		# statistics to normalize the incoming data, and scale and shift the
		# normalized data using gamma and beta
		
		# store the output in the variable out. Any intermediates that
		# you need for the backward pass should be stored in the cache variable

		# Also use the computed sample mean and variance together with
		# the momentum variable to update the running mean and running variance,
		# storing your result in the running_mean and running_var variables
		
		# step 1: calculate mean
		mu = np.mean( x, axis = 0 )

		# step 2: subtract the mean vector of every input data
		# from the data
		x_mu = x - mu

		# step 3: following the lower branch - calculation denominator
		squared = x_mu ** 2

		# step 4: calculate variance
		variance = np.mean( squared, axis = 0 )

		# step 5: add eps for numerical stability, then sqrt
		sqrtvar = np.sqrt( variance + eps )

		# step 6: invert sqrtvar
		sqrtvar_invert = 1 / sqrtvar

		# step 7: execute normalization
		x_hat = x_mu * sqrtvar_invert

		# step 8: transformation step 1
		gammax = gamma * x_hat

		# step 9 transformation step 2
		out = gammax + beta

		cache = x_hat, gamma, x_mu, sqrtvar_invert, sqrtvar, variance, eps

		running_mean = momentum * running_mean + ( 1 - momentum ) * x_mu
		running_var  = momentum * running_var  + ( 1 - momentum ) * variance

	elif mode == 'test':
		# test-time forward pass for batch normalization. Use the running mean and 
		# variance to normalize the incoming data, then scale and shift the normalized 
		# data using gamma and beta. Store the result in the out variable
		mu  = running_mean
		var = running_var
		x_hat = ( x - mu ) / np.sqrt(var + eps)
		out   = gamma * x_hat + beta
		cache = mu, var, x_hat, gamma, beta, eps

	else:
		raise ValueError( 'Invalid forward batchnorm mode "%s"' % mode )

	# Store the updated running means back into bn_param
	bn_param['running_mean'] = running_mean
	bn_param['running_var']  = running_var

	return out, cache


def batchnorm_backward( dout, cache ):
	"""
	Backward pass for batch normalization.
	
	For this implementation, you should write out a computation graph for
	batch normalization on paper and propagate gradients backward through
	intermediate nodes.
	
	Inputs:
	- dout: Upstream derivatives, of shape (N, D)
	- cache: Variable of intermediates from batchnorm_forward.
	
	Returns a tuple of:
	- dx: Gradient with respect to inputs x, of shape (N, D)
	- dgamma: Gradient with respect to scale parameter gamma, of shape (D,)
	- dbeta: Gradient with respect to shift parameter beta, of shape (D,)
	"""

	# backward pass for batch normalization. Store the
	# results in the dx, dgamma, and dbeta variables
	x_hat, gamma, x_mu, sqrtvar_invert, sqrtvar, variance, eps = cache
	N, D = dout.shape

	# step 9
	# because the summation of beta during the forward pass 
	# is a row-wise summation, during the backward pass we 
	# need to sum up the gradient, this easier to understand if you've
	# print out the shape
	dbeta = np.sum( dout, axis = 0 )
	dgammax = dout # not necessary, but more understandable

	# step 8
	dgamma = np.sum( dgammax * x_hat, axis = 0 )
	dx_hat = dgammax * gamma

	# step 7
	dx_mu1 = dx_hat * sqrtvar_invert
	dsqrtvar_invert = np.sum( dx_hat * x_mu, axis = 0 )

	# step 6
	dsqrtvar = - sqrtvar ** -2 * dsqrtvar_invert

	# step 5
	dvariance = 0.5 * ( variance + eps ) ** -0.5 * dsqrtvar

	# step 4
	dsquared = 1 / N * np.ones(( N, D )) * dvariance

	# step 3
	dx_mu2 = 2 * x_mu * dsquared

	# step 2
	dx1 = dx_mu1 + dx_mu2
	dmu = -1 * np.sum( dx_mu1 + dx_mu2, axis = 0 )

	# step 1
	dx2 = 1 / N * np.ones(( N, D )) * dmu

	# step 0
	dx = dx1 + dx2

	return dx, dgamma, dbeta


def dropout_forward( x, dropout_param ):
	"""
	Performs the forward pass for (inverted) dropout.

	Inputs:
	- x: Input data, of any shape
	- dropout_param: A dictionary with the following keys:
		- p: Dropout parameter. We drop each neuron output with probability p.
		- mode: 'test' or 'train'. If the mode is train, then perform dropout;
				if the mode is test, then just return the input.
	- seed: Seed for the random number generator. Passing seed makes this
			function deterministic, which is needed for gradient checking but not in
			real networks.

	Outputs:
	- out: Array of the same shape as x.
	- cache: A tuple (dropout_param, mask). In training mode, mask is the dropout
			 mask that was used to multiply the input; in test mode, mask is None.
	"""
	p, mode = dropout_param['p'], dropout_param['mode']
	if 'seed' in dropout_param:
		np.random.seed(dropout_param['seed'])

	# training and testing phase forward pass for inverted dropout
	# store the dropout mask in the mask variable
	if mode == 'train':
		mask = ( np.random.rand(*x.shape) < p ) / p
		out  = x * mask

	elif mode == 'test':
		mask = None
		out = x

	cache = dropout_param, mask
	out = out.astype( x.dtype, copy = False )

	return out, cache


def dropout_backward( dout, cache ):
	"""
	Perform the backward pass for (inverted) dropout.

	Inputs:
	- dout: Upstream derivatives, of any shape
	- cache: (dropout_param, mask) from dropout_forward.
	"""
	dropout_param, mask = cache
	mode = dropout_param['mode']
	
	if mode == 'train':
		dx = mask * dout

	elif mode == 'test':
		dx = dout
	
	return dx




def svm_loss( x, y ):
	"""
	Computes the loss and gradient using for multiclass SVM classification.

	Inputs:
	- x: Input data, of shape (N, C) where x[i, j] is the score for the jth class
		 for the ith input.
	- y: Vector of labels, of shape (N,) where y[i] is the label for x[i] and
		 0 <= y[i] < C

	Returns a tuple of:
	- loss: Scalar giving the loss
	- dx: Gradient of the loss with respect to x
	"""
	N = x.shape[0]
	correct_class_scores = x[np.arange(N), y]
	margins = np.maximum(0, x - correct_class_scores[:, np.newaxis] + 1.0)
	margins[np.arange(N), y] = 0
	loss = np.sum(margins) / N
	num_pos = np.sum(margins > 0, axis = 1)
	dx = np.zeros_like(x)
	dx[margins > 0] = 1
	dx[np.arange(N), y] -= num_pos
	dx /= N

	return loss, dx


def softmax_loss( x, y ):
	"""
	Computes the loss and gradient for softmax classification.

	Inputs:
	- x: Input data, of shape (N, C) where x[i, j] is the score for the jth class
	  for the ith input.
	- y: Vector of labels, of shape (N,) where y[i] is the label for x[i] and
	  0 <= y[i] < C

	Returns a tuple of:
	- loss: Scalar giving the loss
	- dx: Gradient of the loss with respect to x
	"""
	probs = np.exp( x - np.max(x, axis = 1, keepdims = True) )
	probs /= np.sum( probs, axis = 1, keepdims = True )
	N = x.shape[0]
	loss = -np.sum(np.log(probs[np.arange(N), y])) / N
	dx = probs.copy()
	dx[np.arange(N), y] -= 1
	dx /= N
	return loss, dx


