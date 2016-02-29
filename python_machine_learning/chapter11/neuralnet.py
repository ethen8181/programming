
import numpy as np

class Network(object):
	"""
	docstring for ClassName

	Parameters
	----------

	"""
	


	def __init__( self, sizes ):


	def _encode_labels( self, y, k ):
		"""
		Encode labels into one-hot representation

		Parameters
		----------
		y : array, shape = ( # of samples )
			target values

		Returns
		-------
		onehot : array, shape = ( # of labels, # of samples )
		"""
		onehot = np.zeros( (k, y.shape[0]) ) # change the shape ???
		for idx, val in enumerate(y):
			onehot[ val, idx ] = 1.0
		return onehot

	def fit( self, X, y, print_progress = False ):

		cost = []

		X_data, y_data = X.copy(), y.copy()
		y_enc = self._encode_labels( y, 3 ) # change the 3 ???