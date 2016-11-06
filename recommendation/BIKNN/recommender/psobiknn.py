import random
import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple
from recommender.biknn import BIKNN


class PSOBIKNN:

    def __init__(self, generation, swarm_size, low, high,
                 w, c1, c2, vmin, vmax, K, iterations, column_names, verbose):

        self.w  = w
        self.c1 = c1
        self.c2 = c2
        self.vmin = vmin
        self.vmax = vmax
        self.low  = low
        self.high = high
        self.swarm_size = swarm_size
        self.generation = generation

        # BIKNN parameters
        self.K = K
        self.iterations = iterations
        self.column_names = column_names
        self.verbose = verbose

        # only tunes two hyperpameter, thus the position size is fixed
        self.position_size = 2 
        self.info = namedtuple( 'info', ['cost', 'position'] )


    def predict(self, train, test):

        # generate a random initial swarm (between low, high) 
        # and velocity (between 0 and 1)
        array_size = self.swarm_size, self.position_size
        velocity = np.random.random(array_size)
        swarm = np.random.randint( self.low, self.high + 1, array_size )
        graded_swarm = self._compute_cost(swarm, train, test)
        pbest = graded_swarm.copy()
        gbest = graded_swarm[0]
        
        # store the best position and its cost for each generation,
        # so we can get an idea of when the algorithm converged
        self.generation_history = []
        for i in range(self.generation):
            graded_swarm, velocity, pbest, gbest = self._evolve(
                train, test, 
                graded_swarm, 
                velocity, 
                pbest, 
                gbest
            )
            self.generation_history.append(gbest)
            if self.verbose:
                print( "generation {}'s best chromo: {}".format(i + 1, gbest) )

        self.best = self.generation_history[self.generation - 1]
        return self

    
    def _compute_cost(self, pop, train, test):
        """
        compute the cost (mae) for different B1, B2 hyperparameter
        combine the cost and chromosome into one list and sort them
        in ascending order
        """
        graded = []
        for p in pop:
            p_B1, p_B2 = p
            biknn = BIKNN( K = self.K, B1 = p_B1, B2 = p_B2, 
                           iterations = self.iterations,
                           column_names = self.column_names )
            biknn.fit(train)
            pred = biknn.predict(test)
            cost = biknn.evaluate( pred, test['ratings'] )
            graded.append( self.info( cost, list(p) ) )
        
        graded = sorted(graded)
        return graded


    def _evolve(self, train, test, graded_swarm, velocity, pbest, gbest):

        swarm = np.array([ gs.position for gs in graded_swarm ])
        pbest_position = np.array([ p.position for p in pbest ])
        gbest_position = np.array(gbest.position)
        velocity = self._update_velocity(velocity, swarm, pbest_position, gbest_position)
        swarm = self._update_position(swarm, velocity)
        graded_swarm_new = self._compute_cost(swarm, train, test)

        # recompute the individual and global best
        for index, (p, gs_new) in enumerate( zip(pbest, graded_swarm_new) ):
            if gs_new.cost < p.cost:
                pbest[index] = gs_new
        
        gbest_new = graded_swarm[0]
        if gbest_new.cost < gbest.cost:
            gbest = gbest_new

        return graded_swarm_new, velocity, pbest, gbest


    def _update_velocity(self, velocity, swarm, pbest_position, gbest_position):
        # update velocity
        r1, r2 = np.random.random_sample(size = 2)
        cognitive = self.c1 * r1 * (pbest_position - swarm)
        social = self.c2 * r2 * (gbest_position - swarm)
        velocity = self.w * velocity + cognitive + social

        # constraint on velocity, must not exceed upper and lower bound
        velocity[velocity > self.vmax] = self.vmax
        velocity[velocity < self.vmin] = self.vmin
        return velocity

    
    def _update_position(self, swarm, velocity):
        # update position (round all positions)
        swarm = np.round(swarm + velocity)

        # constraint on position
        # if there's any element that exceeds the upper and lower bound
        # by a certain amount, ricochet back from the border by that amount
        exceed = swarm > self.high
        if np.sum(exceed):
            exceed_amount = swarm[exceed] - self.high
            swarm[exceed] = self.high - exceed_amount
            
        exceed = swarm < self.low
        if np.sum(exceed):
            exceed_amount = self.low - swarm[exceed]
            swarm[exceed] = self.low + exceed_amount

        return swarm


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

