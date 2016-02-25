
from sklearn.base import clone
from sklearn.base import BaseEstimator
from sklearn.base import ClassifierMixin
from sklearn.externals import six
from sklearn.pipeline import _name_estimators
from sklearn.preprocessing import LabelEncoder

# the BaseEstimator, ClassifierMixin parent class
# is used to get some base functionality including 
# get_params and set_params to set and return the classifier's 
# parameters as well as the score method to calculate the prediction accuracy

# the six is used to make the it compatible with python2, python3  

class MajorityVoteClassifier( BaseEstimator, ClassifierMixin ):
	""" 
	A majority vote ensemble classifier

	Parameters
	----------
	classifiers : array-like, shape = [n_classifiers]
		Different classifiers for the ensemble

	vote : str, {'classlabel', 'probability'} ( default = 'classlabel' )
		If 'classlabel' the prediction is based on the argmax of
		class labels. Else if 'probability', the argmax of
		the sum of probabilities is used to predict the class label
		( recommended for calibrated classifiers ).

	weights : array-like, shape = [n_classifiers], optional ( default = None )
		If a list of int or float values are provided, the classifiers
		are weighted by importance; Uses None for uniform weights .

    """
	def __init__( self, classifier, vote = "classlabel", weights = None ):

		self.classifier = classifier
		self.named_classifiers = { key : value 
								   for key, value in _name_estimators(classifier) }
		self.vote = vote
		self.weights = weights

	
	def fit( self, X, y ):
		"""
		Description
		-----------
		Fit Classifiers

		Parameters
		----------
		X : array, shape = [ n_samples, n_features ]
			Matrix of training samples.

        y : array, shape = [n_samples]
			Vector of target class labels.
		"""

		# sanity check for value and weights 
		if self.vote not in ( "probability", "classlabel" ):
			raise ValueError( "vote has to be 'probability' or 'classlabel'"
							  "; got ( %r )" % self.value )
		
		# in python, any object can be evaluated as True or FALSE
		# http://stackoverflow.com/questions/1452489/evaluation-of-boolean-expressions-in-python
		# here None will be evaluated as FALSE 
		if self.weights and len(self.weights) != len(self.classifier):
			raise ValueError( "Number of classifiers and weights must be equal"
							  "; got %d weights, %d classifiers" %
							  ( len(self.weights), len(self.classifiers) ) )

		# label encode the output column
		# then use .classes_ to obtain the class label of the LabelEncoder
		self.lablenc_ = LabelEncoder()
		self.lablenc_.fit(y)
		self.classes_ = self.lablenc_.classes_
		
		# fit the estimators
		self.classifiers_ = []
		for clf in self.classifiers:
			fitted_clf = clone(clf).fit( X, self.lablenc_.transform(y) )
			self.classifiers_.append(fitted_clf)

		return self

	def predict( self, X ):

		if self.vote == 'probability':

		else: # 'classlabel'
			# collect predictions for each estimator
			predictions = np.asarray( [ clf.predict(X) for clf in self.classifiers_ ] ).T
			maj_vote = np.apply_along_axis( lambda x :
											np.argmax( np.bincount( x, weights = self.weights ) ),
											axis = 1,
											arr = predictions )
		maj_vote = self.lablenc_.inverse_transform(maj_vote)
		return maj_vote

	def predict_proba( self, X ):



	def get_params( self, deep = True ):
		""" Get classifier parameter names for GridSearch"""
		if not deep:
			return super( MajorityVoteClassifier, self ).get_params( deep = False )
		else:
			out = self.named_classifiers.copy()
			for name, step in six.iteritems(self.named_classifiers):
				for key, value in six.iteritems(step.get_params(deep=True)):
					out['%s__%s' % (name, key)] = value
			return out

