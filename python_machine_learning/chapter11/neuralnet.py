# http://nbviewer.jupyter.org/github/rasbt/python-machine-learning-book/blob/master/code/ch12/ch12.ipynb

from scipy.special import expit
import numpy as np
import sys

class NeuralNetMLP(object):
	"""
	docstring for ClassName

	Parameters
	----------

	"""
	def __init__( self, n_output, n_features, n_hidden,
				  l1, l2, epochs = 500, eta = 0.001, 
				  alpha = 0.0, decrease_const = 0.0, 
				  shuffle = True, minibatches = 1, 
				  random_state = None ):

		np.random.seed(random_state)
		self.n_output = n_output
		self.n_features = n_features
		self.n_hidden = n_hidden
		self.l1 = l1
		self.l2 = l2
		self.w1, self.w2 = self._initialize_weights()	
		self.eta = eta
		self.alpha = alpha
		self.epochs = epochs	
		self.shuffle = shuffle
		self.minibatches = minibatches
		self.decrease_const = decrease_const

	
	def _initialize_weights(self):
		"""Initialize weights with small random numbers."""
		w1 = np.random.uniform( -1.0, 1.0, size = self.n_hidden * ( self.n_features + 1 ) )
		w1 = w1.reshape( self.n_hidden, self.n_features + 1 )
		w2 = np.random.uniform( -1.0, 1.0, size = self.n_output * ( self.n_hidden + 1 ) )
		w2 = w2.reshape( self.n_output, self.n_hidden + 1 )
		return w1, w2		


	def fit( self, X, y, print_progress = False ):

		self.cost_ = []
		X_data, y_data = X.copy(), y.copy()
		y_enc = self._encode_labels(y)

		delta_w1_prev = np.zeros(self.w1.shape)
		delta_w2_prev = np.zeros(self.w2.shape)

		for i in xrange(self.epochs):

			# an adaptive learning rate that decreases over time
			# for better convergence : eta / ( 1 + t * d )
			self.eta /= ( 1 + self.decrease_const * i )

			if print_progress:
				sys.stderr.write( '\rEpoch: %d/%d' % ( i+1, self.epochs ) )
				sys.stderr.flush()

			# shuffle the training set during every epochs
			if self.shuffle:
				idx = np.random.permutation(y_data.shape[0])
				X_data, y_enc = X_data[idx], y_enc[idx]

			# split the array into minibatches
			# mini is a list of arrays, each containing the splitted index 
			mini = np.array_split( range(y_data.shape[0]), self.minibatches )

			for idx in mini:

				# feedforward 
				a1, z2, a2, z3, a3 = self._feedforward( X_data[idx], self.w1, self.w2 )
				cost = self._get_cost( y_enc = y_enc[ idx, : ], output = a3,
								   	   w1 = self.w1, w2 = self.w2 )
				self.cost_.append(cost)

				# compute gradient via backpropagation
				grad1, grad2 = self._get_gradient( a1 = a1, a2 = a2,
												   a3 = a3, z2 = z2,
												   y_enc = y_enc[ idx, : ],
												   w1 = self.w1,
												   w2 = self.w2 )

				delta_w1, delta_w2 = self.eta * grad1, self.eta * grad2
				self.w1 -= ( delta_w1 + ( self.alpha * delta_w1_prev ) )
				self.w2 -= ( delta_w2 + ( self.alpha * delta_w2_prev ) )
				delta_w1_prev, delta_w2_prev = delta_w1, delta_w2

		return self

	
	def _encode_labels( self, y ):
		"""
		Encode labels into one-hot representation

		Parameters
		----------
		y : array, shape = ( n_samples )
			target values

		Returns
		-------
		onehot : array, shape = ( n_samples, n_output )
		"""
		onehot = np.zeros( ( y.shape[0], self.n_output ) )
		for idx, val in enumerate(y):
			onehot[ idx, val ] = 1.0
		return onehot


	def _feedforward( self, X, w1, w2 ):
		"""
		Compute feed forward step

		Parameters
		----------
		X : array, shape ( n_samples, n_features )
			input layer

		w1 : array, shape ( n_hidden, n_features + 1 )
			weighted matrix for input layer -> hidden layer

		w2 : array, shape ( n_output, n_hidden + 1 )
			weighted matrix for hidden layer -> output layer

		Returns
		-------
		a1 : array, shape( n_samples, n_features + 1 )
			Input values with bias unit

		z2 : array, shape( n_hidden, n_samples )
			Net input of hidden layer

		a2 : array, shape( n_hidden + 1, n_samples )
			Activation of hidden layer

		z3 : array, shape( n_output, n_samples )
			Net input of output layer

		a3 : array, shape( n_output, n_samples )
			Activation of output layer
		"""

		# input -> hidden layer 
		a1 = self._add_bias_unit( X, how = 'column' )
		z2 = w1.dot(a1.T)
		a2 = self._sigmoid(z2)

		# hidden layer -> output layer
		a2 = self._add_bias_unit( a2, how = 'row' )
		z3 = w2.dot(a2)
		a3 = self._sigmoid(z3).T
		return a1, z2, a2, z3, a3
	
	
	def _add_bias_unit( self, X, how ):
		"""Add bias unit (column or row of 1s) to an array"""

		if how == 'column':
			X_new = np.hstack( ( np.ones( [ X.shape[0], 1 ] ), X ) )
		else:
			X_new = np.vstack( ( np.ones( [ 1, X.shape[1] ] ), X ) )
		return X_new


	def _sigmoid( self, z ):
		"""
		compute logistic function (sigmoid)
		expit = 1.0 / ( 1.0 + np.exp(-z) )
		"""		
		return expit(z)


	def _get_cost( self, y_enc, output, w1, w2 ):
		
		term1 = -y_enc * np.log(output)
		term2 = ( 1 - y_enc ) * np.log( 1 - output )
		cost  = np.sum( term1 - term2 )

		# apply regularization, note that we do note regularize the bias unit
		L1_term = self._L1_reg( self.l1, w1, w2 )
		L2_term = self._L2_reg( self.l2, w1, w2 )
		cost = cost + L1_term + L2_term
		return cost

	
	def _L2_reg( self, lambda_, w1, w2 ):
		"""compute L2-regularization cost"""
		return ( lambda_ / 2.0 ) * ( np.sum( w1[:, 1:] ** 2 ) + np.sum( w2[:, 1:] ** 2 ) )

	def _L1_reg( self, lambda_, w1, w2 ):
		"""compute L1-regularization cost"""
		return ( lambda_ / 2.0 ) * ( np.abs( w1[:, 1:] ).sum() + np.abs( w2[:, 1:] ).sum() )

	
	def _get_gradient( self, a1, a2, a3, z2, y_enc, w1, w2 ):

		# error vector of the output layer
		sigma3 = ( a3 - y_enc ).T
		z2 = self._add_bias_unit( z2, how = 'row' )
		# derivative of the sigmoid function 
		sigma2 = w2.T.dot(sigma3) * self._sigmoid_gradient(z2)
		sigma2 = sigma2[1:, :]
		grad1  = sigma2.dot(a1)
		grad2  = sigma3.dot(a2.T)

		# regularize, bias unit does not have regularization 
		grad1[:, 1:] += (w1[:, 1:] * (self.l1 + self.l2))
		grad2[:, 1:] += (w2[:, 1:] * (self.l1 + self.l2))

		return grad1, grad2

	
	def _sigmoid_gradient(self, z):
		"""
		Compute gradient of the logistic function
		http://sambfok.blogspot.tw/2012/08/partial-derivative-logistic-regression.html
		"""
		sg = self._sigmoid(z)
		return sg * (1 - sg)


	def predict( self, X ):
		a1, z2, a2, z3, a3 = self._feedforward( X, self.w1, self.w2 )
		y_pred = np.argmax( z3, axis = 0 )
		return y_pred
	




