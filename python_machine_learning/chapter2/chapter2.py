
import numpy as np

# naming convention : add an underscore (_) to attributes
# that are not being created upon the initialization

class Perceptron(object) :

	def __init__( self, eta = 0.01, n_iter = 10 ) :
		self.eta = eta
		self.n_iter = n_iter

	def fit( self, x, y ) :
		# 1. initialize the weights of 0 : # of features + 1
		# 2. collect the number of missclassifaction to identify the training progress
		self.w_ = np.zeros( 1 + x.shape[1] ) 
		self.errors_ = []

		# train for a fix number of iterations 
		for _ in range( self.n_iter ) :
			
			error = 0
			for x_i, target in zip( x, y ) :

				update = self.eta * ( target - self.predict(x_i) )
				self.w_[1:] += update * x_i
				self.w_[0]  += update
				error += int( update != 0.0 )
			self.errors_.append(error)

		return self

	def net_input( self, x ) :		
		# linear activation function 
		return np.dot( x, self.w_[1:] ) + self.w_[0]

	def predict( self, x ) :
		# if output of the activation function is
		# larger than threshold ( 0 ) return 1 or else -1 
		return np.where( self.net_input(x) >= 0.0, 1, -1 )


class AdaGrad(object) :

	def __init__( self, eta = 0.01, n_iter = 10 ) :
		self.eta = eta
		self.n_iter = n_iter

	def fit( self, x, y ) :
		self.w_ = np.zeros( 1 + x.shape[1] )
		self.costs_ = []

		for _ in range( self.n_iter ) :
			
			# update weights using all observations
			errors = y - self.net_input(x)			
			self.w_[1:] += self.eta * x.T.dot(errors)
			self.w_[0]  += self.eta * errors.sum()
			
			# compute costs
			cost = ( errors ** 2 ).sum() / 2.0		
			self.costs_.append(cost)

		return self

	def net_input( self, x ) :		
		# linear activation function 
		return np.dot( x, self.w_[1:] ) + self.w_[0]

	def predict( self, x ) :
		# if output of the activation function is
		# larger than threshold (0) return 1 or else -1 
		return np.where( self.net_input(x) >= 0.0, 1, -1 )


class AdaSGD(object) :

	"""

	Parameters 
	----------
	@eta : float
		learning rate between 0 ~ 1
	@n_iter : int 
		passes over the training data
	@w_ : 1d-array
		weights after fitting
	@shuffle : boolean ( default = True )
		whether to shuffle the training data before each epoch to prevent cycles

	"""

	def __init__( self, eta, n_iter, shuffle = True, random_state = None ) :
		self.eta = eta
		self.n_iter = n_iter
		self.w_initialized = False
		self.shuffle = shuffle
		if random_state :
			np.random.seed(random_state) # setting the seed for shuffle 

	def fit( self, x, y ) :
		# costs_ = average costs of the training samples in each epoch

		self.initialize_weights( x.shape[1] )
		self.costs_ = []

		for i in range( self.n_iter ) :

			if self.shuffle :
				x, y = self.shuffle_data( x, y )

			cost = []
			for x_i, target in zip( x, y ) :
				cost.append( self.update_weights( x_i, target ) )

			avg_cost = sum(cost) / len(cost)
			self.costs_.append(avg_cost)
		return self

	def initialize_weights( self, n ) :
		# initialize weights to 0
		self.w_ = np.zeros( 1 + n )
		self.w_initialized = True

	def shuffle_data( self, x, y ) :
		# generate a random permutated index and return
		# the permutated ordered dataset
		r = np.random.permutation( len(y) )
		return ( x[r], y[r] )

	def update_weights( self, x_i, target ) :
		# stochastic gradient descent

		error = target - self.net_input(x_i)
		self.w_[1:] += self.eta * x_i.dot(error)
		self.w_[0]  += self.eta * error

		cost = 0.5 * ( error ** 2 )
		return cost

	def net_input( self, x ) :		
		# linear activation function 
		return np.dot( x, self.w_[1:] ) + self.w_[0]

	def predict( self, x ) :
		# if output of the activation function is
		# larger than threshold (0) return 1 or else -1 
		return np.where( self.net_input(x) >= 0.0, 1, -1 )

