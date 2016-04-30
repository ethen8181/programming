import random
from BIKNN import BIKNN
from collections import namedtuple


def ga( pop_size, chromo_len, lower_bound, upper_bound,
		retain, mutate, generation, K, data, columns, test, iterations ):
	"""
	genetic algorithm with BIKNN, the genetic algorithm is used to tune
	BIKNN's B1 (regularization parameter that penalizes the item bias) and 
	B2 (regularization parameter that penalizes the user bias)

	Genetic Algorithm's Parameters
	------------------------------
	pop_size : int
		number of chromosomes in the population

	chromo_len : int
		number of possible values per chromosome

	lower_bound, upper_bound : int
		lower_bound and upper_bound possible value of the randomly generated chromosome

	retain : float
		the fraction of the best chromosome to retain. used to mate
		the children for the next generation

	mutate : float
		the probability that each chromosome will mutate

	generation : int
		number of iterations to train the algorithm

	BIKNN's Parameters
	------------------
	K : int
		value specifying the number of nearest (similar) items 
		to predicted the unknown ratings
	
	data : DataFrame
		base training data

	columns : a list of strings
		specifying the column name of the DataFrame,
		has to be the combination of[ 'user_id', 'item_id', 'ratings' ]
	
	test : DataFrame
		test data for evaluating the predicted ratings

	iterations : int
		after this number of iterations ( number of new test data ), 
		the weighted similarity score will be updated

	Returns
	-------
	generation_history : list
		each element of the list is a namedtuple( "cost", "chromo" ),
		storing each generation's best chromosome (B1, B2 parameter) and 
		its cost (MAE, mean absolute error of the predicted rating on the test data)
	"""
	
	# randomly generate the initial population
	pop = population( pop_size, chromo_len, lower_bound, upper_bound )

	# store the best chromosome and its cost for each generation,
	# so we can get an idea of when the algorithm converged
	generation_history = []
	for i in range(generation):
		pop, generation_best = evolve( pop, retain, mutate, 
									   chromo_len, lower_bound, upper_bound,
									   K, data, columns, test, iterations )
		generation_history.append(generation_best)
		print( "iteration {}'s best generation: {}".format( i + 1, generation_best ) )

	return generation_history


def population( pop_size, chromo_len, lower_bound, upper_bound ):
	"""
	creates a collection of chromosomes (i.e. a population)

	Returns
	-------
	(list) each element is a chromosome
	"""
	def chromosome( chromo_len, lower_bound, upper_bound ):
		return [ random.randint( lower_bound, upper_bound ) for _ in range(chromo_len) ]

	return [ chromosome( chromo_len, lower_bound, upper_bound ) for _ in range(pop_size) ]


def evolve( pop, retain, mutate, chromo_len, lower_bound, upper_bound,
			K, data, columns, test, iterations ):
	"""
	evolution of the genetic algorithm

	Parameters
	----------
	pop : list
		the initial population for this generation

	Returns
	-------
	children : list
		the crossovered and mutated population for the next generation

	generation_best : namedtuple( "cost", "chromo" )
		the current generation's best chromosome and its cost 
		(evaluated by the cost function)
	"""

	# evolution :
	# take the proportion of the best performing chromosomes
	# judged by the calculate_cost function and these high-performers 
	# will be the parents of the next generation
	generation_info = namedtuple( "generation_info", [ "cost", "chromo" ] )

	graded = []
	for p in pop:
		recommendation = BIKNN( K, *p )
		recommendation.fit( data = data, columns = columns )
		mae = recommendation.update( test = test, iterations = iterations )
		graded.append( generation_info( mae, p ) )

	graded  = sorted(graded)
	parents = [ g.chromo for g in graded ]
	retain_len = int( len(parents) * retain )
	parents = parents[:retain_len]
	
	# the children_index set is used to
	# check for duplicate index1, index2. since
	# choosing chromosome ( a, b ) to crossover is the same
	# as choosing chromosome ( b, a )
	children = []
	children_index = set()
	desired_len = len(pop)
	parents_len = len(parents)

	# generate the the children (the parent for the next generation),
	# the children is mated by randomly choosing two parents and
	# mix the first half element of one parent with the later half 
	# element of the other
	while len(children) < desired_len:

		index1, index2 = random.sample( range(parents_len), k = 2 )

		if ( index1, index2 ) not in children_index:
			male   = parents[index1]
			female = parents[index2]
			pivot  = len(male) // 2
			child1 = male[:pivot] + female[pivot:]
			child2 = female[:pivot] + male[pivot:]
			children.append(child1)
			children.append(child2)
			children_index.add( ( index1, index2 ) )
			children_index.add( ( index2, index1 ) )

	# mutation :
	# randomly change one element of the chromosome
	for chromosome in children:
		if mutate > random.random():
			index_to_mutate = random.randint( 0, chromo_len - 1 )
			chromosome[index_to_mutate] = random.randint( lower_bound, upper_bound )

	# evaluate the children chromosome and retain the overall best
	graded_childen = []
	for p in children:
		recommendation = BIKNN( K, *p )
		recommendation.fit( data = data, columns = columns )
		mae = recommendation.update( test = test, iterations = iterations )
		graded_childen.append( generation_info( mae, p ) )	

	graded.extend(graded_childen)
	graded = sorted(graded)
	generation_best = graded[0]
	children = [ g.chromo for g in graded[:desired_len] ]
	return children, generation_best


if __name__ == '__main__':

	ga1 = ga( 
		pop_size = 15, 
		chromo_len = 2, 
		lower_bound = 0, 
		upper_bound = 100,
		retain = 0.5, 
		mutate = 0.2, 
		generation = 2,
		K = 10,
		data = train,
		columns = [ 'user_id', 'item_id', 'ratings' ],
		test = test,
		iterations = 1000
	)
	print(ga1)




