

class DecisionTree(object):
    
	def __init__( self, max_depth ):
		self.max_depth = max_depth


	def train( self, data, features, target ):
		