import numpy as np
import cs231n.layers as layers
# import cs231n.layer_utils as layer_utils


class TwoLayerNet(object):
	"""
	A two-layer fully-connected neural network with ReLU nonlinearity and
	softmax loss that uses a modular layer design. We assume an input dimension
	of D, a hidden dimension of H, and perform classification over C classes.
	
	The architecure should be affine - relu - affine - softmax.

	Note that this class does not implement gradient descent; instead, it
	will interact with a separate Solver object that is responsible for running
	optimization.

	The learnable parameters of the model are stored in the dictionary
	self.params that maps parameter names to numpy arrays
	"""	
	def __init__( self, input_dim = 3 * 32 * 32, hidden_dim = 100, num_classes = 10,
				  weight_scale = 1e-3, reg = 0.0 ):
		"""
		Initialize a new network

		Inputs:
		- input_dim: An integer giving the size of the input
		- hidden_dim: An integer giving the size of the hidden layer
		- num_classes: An integer giving the number of classes to classify
		- dropout: Scalar between 0 and 1 giving dropout strength.
		- weight_scale: Scalar giving the standard deviation for random
						initialization of the weights.
		- reg: Scalar giving L2 regularization strength.
		"""
		self.reg = reg

		# initialize the weights and biases of the two-layer net. Weights
		# should be initialized from a Gaussian with standard deviation equal to
		# weight_scale, and biases should be initialized to zero. All weights and
		# biases should be stored in the dictionary self.params, with first layer
		# weights and biases using the keys 'W1' and 'b1' and second layer weights
		# and biases using the keys 'W2' and 'b2'
		W1 = np.random.normal( scale = weight_scale, size = ( input_dim, hidden_dim ) )
		W2 = np.random.normal( scale = weight_scale, size = ( hidden_dim, num_classes ) )
		b1 = np.zeros(hidden_dim)
		b2 = np.zeros(num_classes)

		self.params = {
			'W1': W1,
			'W2': W2,
			'b1': b1,
			'b2': b2
		}


	def loss( self, X, y = None ):
		"""
		Compute loss and gradient for a minibatch of data.

		Inputs:
		- X: Array of input data of shape (N, d_1, ..., d_k)
		- y: Array of labels, of shape (N,). y[i] gives the label for X[i].

		Returns:
		If y is None, then run a test-time forward pass of the model and return:
		- scores: Array of shape (N, C) giving classification scores, where
				  scores[i, c] is the classification score for X[i] and class c.

		If y is not None, then run a training-time forward and backward pass and
		return a tuple of:
		- loss: Scalar value giving the loss
		- grads: Dictionary with the same keys as self.params, mapping parameter
				 names to gradients of the loss with respect to those parameters.
		"""  

		# forward pass for the two-layer net, compute the class scores for X 
		# X = X.reshape( X.shape[0], -1 )
		z1, z1_cache = layers.affine_forward( X, self.params['W1'], self.params['b1'] )
		a1, a1_cache = layers.relu_forward(z1)
		scores, scores_cache = layers.affine_forward( a1, self.params['W2'], self.params['b2'] )

		# If y is None then we are in test mode so just return scores
		if y is None:
			return scores
    
		# backward pass for the two-layer net. Store the loss in the loss variable 
		# and gradients in the grads dictionary. Compute data loss using softmax 
		# and make sure that grads[k] holds the gradients for self.params[k]
		loss, dout = layers.softmax_loss( scores, y )
		da1, dW2, db2 = layers.affine_backward( dout, scores_cache )
		dz1 = layers.relu_backward( da1, a1_cache )
		dx1, dW1, db1 = layers.affine_backward( dz1, z1_cache )

		# add the l2 regularization to the loss and gradient
		dW2 += self.reg * self.params['W2']
		dW1 += self.reg * self.params['W1']		
		weight_sum = np.sum( self.params['W1'] ** 2 ) + np.sum( self.params['W2'] ** 2 )
		loss += 0.5 * self.reg * weight_sum

		grads = {
			'W2': dW2,
			'W1': dW1,
			'b2': db2,
			'b1': db1
		}
		
		return loss, grads


class FullyConnectedNet(object):
	"""
	A fully-connected neural network with an arbitrary number of hidden layers,
	ReLU nonlinearities, and a softmax loss function. This will also implement
	dropout and batch normalization as options. For a network with L layers,
	the architecture will be
	
	{affine - [batch norm] - relu - [dropout]} x (L - 1) - affine - softmax
	
	where batch normalization and dropout are optional, and the {...} block is
	repeated L - 1 times.
	
	Similar to the TwoLayerNet above, learnable parameters are stored in the
	self.params dictionary and will be learned using the Solver class.
	"""

	def __init__( self, hidden_dims, input_dim = 3 * 32 * 32, num_classes = 10,
				  dropout = 0, use_batchnorm = False, reg = 0.0,
				  weight_scale = 1e-2, dtype = np.float32, seed = None ):
		"""
		Initialize a new FullyConnectedNet
		
		Inputs:
		- hidden_dims: A list of integers giving the size of each hidden layer.
		- input_dim: An integer giving the size of the input.
		- num_classes: An integer giving the number of classes to classify.
		- dropout: Scalar between 0 and 1 giving dropout strength. If dropout = 0 then
		  		   the network should not use dropout at all.
		- use_batchnorm: Whether or not the network should use batch normalization.
		- reg: Scalar giving L2 regularization strength.
		- weight_scale: Scalar giving the standard deviation for random
		  				initialization of the weights.
		- dtype: A numpy datatype object; all computations will be performed using
		  		 this datatype. float32 is faster but less accurate, so you should use
		  		 float64 for numeric gradient checking.
		- seed: If not None, then pass this random seed to the dropout layers. This
		  		will make the dropout layers deteriminstic so we can gradient check the
		  		model.
		"""
		self.use_batchnorm = use_batchnorm
		self.use_dropout = dropout > 0
		self.reg = reg
		self.num_layers = 1 + len(hidden_dims)
		self.dtype = dtype
		self.params = {}

		############################################################################
		# TODO: Initialize the parameters of the network, storing all values in    #
		# the self.params dictionary. Store weights and biases for the first layer #
		# in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
		# initialized from a normal distribution with standard deviation equal to  #
		# weight_scale and biases should be initialized to zero.                   #
		#                                                                          #
		# When using batch normalization, store scale and shift parameters for the #
		# first layer in gamma1 and beta1; for the second layer use gamma2 and     #
		# beta2, etc. Scale parameters should be initialized to one and shift      #
		# parameters should be initialized to zero.                                #
		############################################################################
		previous_dim = input_dim
		layer_dim = hidden_dims + [num_classes]

		for layer, dim in enumerate(layer_dim):
			W = np.random.normal( scale = weight_scale, size = ( previous_dim, dim ) )
			b = np.zeros(dim)
			self.params['W' + str(layer + 1)] = W
			self.params['b' + str(layer + 1)] = b
			previous_dim = dim


		


		# When using dropout we need to pass a dropout_param dictionary to each
		# dropout layer so that the layer knows the dropout probability and the mode
		# (train / test). You can pass the same dropout_param to each dropout layer.
		self.dropout_param = {}
		if self.use_dropout:
			self.dropout_param = { 'mode': 'train', 'p': dropout }
			if seed is not None:
				self.dropout_param['seed'] = seed
    
		# With batch normalization we need to keep track of running means and
		# variances, so we need to pass a special bn_param object to each batch
		# normalization layer. You should pass self.bn_params[0] to the forward pass
		# of the first batch normalization layer, self.bn_params[1] to the forward
		# pass of the second batch normalization layer, etc.
		self.bn_params = []
		if self.use_batchnorm:
			self.bn_params = [ {'mode': 'train'} for i in range(self.num_layers - 1) ]
    
		# Cast all parameters to the correct datatype
		for k, v in self.params.items():
			self.params[k] = v.astype(dtype)


	def loss( self, X, y = None ):
		"""
		Compute loss and gradient for the fully-connected net.

		Input / output: Same as TwoLayerNet above.
		"""
		X = X.astype(self.dtype)
		mode = 'test' if y is None else 'train'

		# Set train/test mode for batchnorm params and dropout param since they
		# behave differently during training and testing.
		if self.dropout_param is not None:
			self.dropout_param['mode'] = mode   
		if self.use_batchnorm:
			for bn_param in self.bn_params:
				bn_param[mode] = mode


		############################################################################
		# TODO: Implement the forward pass for the fully-connected net, computing  #
		# the class scores for X and storing them in the scores variable.          #
		#                                                                          #
		# When using dropout, you'll need to pass self.dropout_param to each       #
		# dropout forward pass.                                                    #
		#                                                                          #
		# When using batch normalization, you'll need to pass self.bn_params[0] to #
		# the forward pass for the first batch normalization layer, pass           #
		# self.bn_params[1] to the forward pass for the second batch normalization #
		# layer, etc.                                                              #

		z_scores = []
		z_caches = []
		a_scores = []
		a_caches = []
		X_for_this_layer = X
		
		for layer in range( 1, self.num_layers + 1 ):
			W = self.params['W' + str(layer)]
			b = self.params['b' + str(layer)]
			
			# feed-forward
			z_score, z_cache = layers.affine_forward( X_for_this_layer, W, b )
			z_scores.append(z_score)
			z_caches.append(z_cache)
			
			# the last layer does not have an activation function
			if layer == self.num_layers:
				break
		    
			# activation
			a_score, a_cache = layers.relu_forward(z_score)	
			a_scores.append(a_score)
			a_caches.append(a_cache)
			
			# the activation score is the input X for the next layer
			X_for_this_layer = a_score

		scores = z_scores[self.num_layers - 1]

		# If test mode return early
		if mode == 'test':
			return scores

		############################################################################
		# TODO: Implement the backward pass for the fully-connected net. Store the #
		# loss in the loss variable and gradients in the grads dictionary. Compute #
		# data loss using softmax, and make sure that grads[k] holds the gradients #
		# for self.params[k]. Don't forget to add L2 regularization!               #
		#                                                                          #
		# When using batch normalization, you don't need to regularize the scale   #
		# and shift parameters.                                                    #
		#                                                                          #
		# NOTE: To ensure that your implementation matches ours and you pass the   #
		# automated tests, make sure that your L2 regularization includes a factor #
		# of 0.5 to simplify the expression for the gradient.                      #
		
		loss, dout = layers.softmax_loss( scores, y )
		for layer in range( 1, self.num_layers + 1 ):
			W = self.params['W' + str(layer)]
			l2_penalty = 0.5 * self.reg * np.sum(W ** 2)
			loss += l2_penalty

		grads = {}

		# compute the backpropagation for the output layer (softmax)
		z_cache = z_caches[self.num_layers - 1]
		da, dW, db = layers.affine_backward( dout, z_cache )

		W = self.params['W' + str(self.num_layers)]
		dW += self.reg * W
		grads['W' + str(self.num_layers)] = dW
		grads['b' + str(self.num_layers)] = db

		# then the backpropagation is simply a fixed seqeunce of relu - affine
		for layer in reversed( range( 1, self.num_layers ) ):		    
			a_cache = a_caches[layer - 1]
			dz = layers.relu_backward( da, a_cache )			
			
			z_cache = z_caches[layer - 1]
			da, dW, db = layers.affine_backward( dz, z_cache )

			# add regularization to the weight only
			W = self.params['W' + str(layer)]
			dW += self.reg * W
			grads['W' + str(layer)] = dW
			grads['b' + str(layer)] = db

		return loss, grads

