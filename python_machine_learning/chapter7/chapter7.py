from sklearn.base import clone
from sklearn.pipeline import _name_estimators

class MajorityVoteClassifier( BaseEstimator, ClassifierMixin ):

	def __init__( self, classifier, vote = "classlabel", weights = None ) :

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

		Returns
		-------
		self : object

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
		self.lablenc_ = LabelEncoder()
		self.lablenc_.fit(y)
		self.classes_ = self.lablenc_.classes_ # obtains the class label of the LabelEncoder
		
		# fit the estimators
		self.classifiers_ = []
		for clf in self.classifiers:
			fitted_clf = clone(clf).fit( X, self.lablenc_.transform(y) )
			self.classifiers_.append(fitted_clf)

	def predict( self, X ):

		# collect predictions for each estimator
		predictions = np.array( [ clf.predict(X) for clf in self.classifiers_ ] ).T





