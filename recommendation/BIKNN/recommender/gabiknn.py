import random
import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple
from recommender.biknn import BIKNN


class GABIKNN:
    """
    Genetic Algorithm for tuning the B1, B2 hyperparameter
    for BIKNN

    Parameters
    ----------
    generation : int
        number of iteration to train the algorithm

    pop_size : int
        number of chromosomes in the population

    low, high : int
        lower_bound and upper_bound possible value of the randomly generated chromosome

    retain_rate : float 0 ~ 1
        the fraction of the best chromosome to retain. used to mate
        the children for the next generation

    mutate_rate : float 0 ~ 1
        the probability that each chromosome will mutate

    BIKNN : class BIKNN
        a fitted BIKNN model

    verbose : boolean
        whether to print the best chromo (B1, B2) during each generation

    Example
    -------
    import pandas as pd
    from recommender import BIKNN, GABIKNN

    train, test = read_file( FILENAME, TESTSIZE, SEED )
    biknn1 = BIKNN( K = 20, B1 = 25, B2 = 25, iterations = 100000 )
    biknn1.fit( data = train, column_names = [ 'user_ids', 'item_ids', 'ratings' ] )
    
    ga1 = GABIKNN( 
        generation = 2, 
        pop_size = 5,
        low = 0, 
        high = 100, 
        retain_rate = 0.5, 
        mutate_rate = 0.2,
        BIKNN = biknn1
    )
    ga1.predict(test)
    ga1.convergence_plot()
    """
    def __init__(self, BIKNN, generation, pop_size, low, high, 
                 retain_rate, mutate_rate, verbose):       

        self.low  = low
        self.high = high        
        if not BIKNN.is_fitted:
            raise ValueError('BIKNN model is not fitted, call .fit() first')
        
        self.BIKNN = BIKNN
        self.verbose  = verbose
        self.pop_size = pop_size
        self.generation  = generation
        self.retain_len  = int(pop_size * retain_rate)
        self.mutate_rate = mutate_rate

        # only tunes two hyperpameter, thus the chromo size is fixed
        self.chromo_size = 2 
        self.info = namedtuple( 'info', ['cost', 'chromo'] )
    
    
    def predict(self, data):
        """
        Pass in the data and obtain the prediction

        Parameters
        ----------
        data : DataFrame
            base training data

        column_names : list of strings
            specifying the column names of the DataFrame,
            has to be the combination of [ 'user_id', 'item_id', 'ratings' ]
        """
        
        # randomly generate the initial population, and evaluate its cost
        array_size = self.pop_size, self.chromo_size
        pop = np.random.randint(self.low, self.high + 1, array_size)      
        graded_pop = self._compute_cost(pop, data)

        # store the best chromosome and its cost for each generation,
        # so we can get an idea of when the algorithm converged
        self.generation_history = []
        for i in range(self.generation):
            graded_pop, generation_best = self._evolve(data, graded_pop)
            self.generation_history.append(generation_best)
            if self.verbose:
                print( "generation {}'s best chromo: {}".format(i + 1, generation_best) )

        self.best = self.generation_history[self.generation - 1]
        return self


    def _compute_cost(self, pop, data):
        """
        compute the cost (mae) for different B1, B2 hyperparameter
        combine the cost and chromosome into one list and sort them
        in ascending order
        """
        graded = []
        for p in pop:
            p_B1, p_B2 = p
            self.BIKNN.B1 = p_B1
            self.BIKNN.B2 = p_B2
            pred = self.BIKNN.predict(data)
            cost = self.BIKNN.evaluate( pred, data['ratings'] )
            graded.append( self.info( cost, list(p) ) )
        
        graded = sorted(graded)
        return graded

    
    def _evolve(self, data, graded_pop):
        """
        core method that does the crossover, mutation to generate
        the possibly best children for the next generation
        """
        
        # retain the best chromos (number determined by the retain_len)
        graded_pop = graded_pop[:self.retain_len]
        parent = [p.chromo for p in graded_pop]

        # generate the children for the next generation 
        children = []
        while len(children) < self.pop_size:
            child = self._crossover(parent)
            child = self._mutate(child)
            children.append(child)

        # evaluate the children chromosome and retain the overall best,
        # overall simply means the best from the parent and the children, where
        # the size retained is determined by the population size
        graded_children = self._compute_cost(children, data)
        graded_pop.extend(graded_children)
        graded_pop = sorted(graded_pop)
        graded_pop = graded_pop[:self.pop_size]
        
        # also return the current generation's best chromosome and its cost
        generation_best = graded_pop[0]
        return graded_pop, generation_best 


    def _crossover(self, parent):
        """
        mate the children by randomly choosing two parents and mix 
        the first half element of one parent with the later half 
        element of the other
        """
        index1, index2 = random.sample( range(self.retain_len), k = 2 )
        male, female = parent[index1], parent[index2]
        pivot = len(male) // 2
        child = male[:pivot] + female[pivot:]
        return child


    def _mutate(self, child):
        """
        randomly change one element of the chromosome if it
        exceeds the user-specified threshold (mutate_rate)
        """
        if self.mutate_rate > random.random():
            idx_to_mutate = random.randrange(self.chromo_size)
            child[idx_to_mutate] = random.randint(self.low, self.high)

        return child


    def convergence_plot(self):
        gh = self.generation_history
        costs = [g.cost for g in gh]
        plt.plot( range( 1, len(gh) + 1 ), costs, '-o' )
        plt.title('Cost Convergence Plot')
        plt.xlabel('Iteration')
        plt.ylabel('Cost')
        plt.ylim(0, costs[0] + 0.5)
        plt.tight_layout()
        plt.show()

