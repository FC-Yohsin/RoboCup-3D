import sys
# setting path
sys.path.append('../robocup_3d')


from problem import Problem
from selection_functions import SelectionFunctions
from enum import Enum
import random
import constants
from Agent import *
from Action import *
import time
import random

# Global Parameters
# BEST PARAMETERS SO FAR FOR TSP!!!
# POPULATION_SIZE = 110
# OFFSPRING_SIZE = 94  # offspring size must be a multiple of 2 (even)
# GENERATIONS = 10000
# MUTATION_RATE = 0.70                                                                                          
# ITERATIONS = 10


POPULATION_SIZE = 20
OFFSPRING_SIZE = 6 # offspring size must be a multiple of 2 (even)
GENERATIONS = 10
MUTATION_RATE = 0.45                                                                                     
ITERATIONS = 10



class Selection(Enum):
    """
    This class will contain the different selection functions
    """
    Random = 1
    Truncation = 2
    ProportionalSelection = 3
    RankBasedSelection = 4
    BinaryTournament = 5


class EA_NaoWalkOptimizer:
    """
    This class will be a generic one. This will contain the evolutionary process
    """
    def __init__(self):
        self.population = []
        self.fitness_scores = []
        self.generation = 1
        self.hjMin = hjMin
        self.hjMax = hjMax
        

    def _generate_random_individual(self):
        """
        This method will generate a random individual
        """
        lj1 = (random.uniform(hjMin['rlj1'], hjMax['rlj1']), random.uniform(hjMin['rlj1'], hjMax['rlj1']))
        lj3 = (random.uniform(hjMin['rlj3'], hjMax['rlj3']), random.uniform(hjMin['rlj3'], hjMax['rlj3']))
        lj4 = (random.uniform(hjMin['rlj4'], hjMax['rlj4']), random.uniform(hjMin['rlj4'], hjMax['rlj4']))
        lj5 = (random.uniform(hjMin['rlj5'], hjMax['rlj5']), random.uniform(hjMin['rlj5'], hjMax['rlj5']))
        lj6 =  (random.uniform(hjMin['rlj6'], hjMax['rlj6']), random.uniform(hjMin['rlj6'], hjMax['rlj6']))

        return {
                "rlj1":[lj1[0], lj1[1]],
                "llj1":[lj1[1], lj1[0]],
                "rlj3":[lj3[0], lj3[1]],
                "rlj4":[lj4[0], lj4[1]],
                "rlj5":[lj5[0], lj5[1]],
                "llj3":[lj3[1], lj3[0]],
                "llj4":[lj4[1], lj4[0]],
                "llj5":[lj5[1], lj5[0]],
                "rlj6":[lj6[0], lj6[1]],
                "llj6":[lj6[1], lj6[0]],
                }

    def initialize_population(self):
        """
        This method will initialize the population
        """
        for i in range(POPULATION_SIZE):
            self.population.append(self._generate_random_individual())
            self.fitness_scores.append(0.0)

    def add_custom_population(self, population):
        """
        This method will add a population to the current population
        """
        if len(population) == POPULATION_SIZE:
            self.population = population
            self.fitness_scores = [0.0] * POPULATION_SIZE
        else:
            print("Population size is not correct")
    
    def add_custom_child(self, child):
        """
        This method will add a child to the population
        """
        if len(self.population) < POPULATION_SIZE:
            self.population.append(child)
        else:
            self.population[0] = child

    def _crossover(self, p1: dict, p2: dict)-> dict:
        """
        This method will perform crossover between two parents. Both parents are dictionaries
        """
        child = {}
        for key in p1.keys():
            if random.random() < 0.5:
                child[key] = p1[key]
            else:
                child[key] = p2[key]
        return child

    def _mutation(self, child: dict, mutation_rate: float)-> dict:
        """
        This method will perform mutation on the child
        """
        for key in child.keys():
            if random.random() < mutation_rate:
                child[key] = self._generate_random_individual()[key]
        return child

    def generate_offspring(self, selection: Selection):
        """
        This method will generate offspring from the population
        """
        print("Generating Offspring Now")
        # Selecting the fittest chromosomes
        if selection == Selection.Random:
            parents = SelectionFunctions.random(self.population, self.fitness_scores, OFFSPRING_SIZE)
        elif selection == Selection.Truncation:
            parents = SelectionFunctions.truncation(self.population, self.fitness_scores, OFFSPRING_SIZE)
        elif selection == Selection.ProportionalSelection:
            parents = SelectionFunctions.proportional_selection(self.population, self.fitness_scores, OFFSPRING_SIZE)
        elif selection == Selection.RankBasedSelection:
            parents = SelectionFunctions.rank_based_selection(self.population, self.fitness_scores, OFFSPRING_SIZE)
        elif selection == Selection.BinaryTournament:
            parents = SelectionFunctions.binary_tournament(self.population, self.fitness_scores, OFFSPRING_SIZE)
        
        for i in range(0,OFFSPRING_SIZE,2):
            child1 = self._crossover(self.population[parents[i]],self.population[parents[i+1]])
            child2 = self._crossover(self.population[parents[i]],self.population[parents[i+1]])

            child1 = self._mutation(child1, MUTATION_RATE)
            child2 = self._mutation(child2, MUTATION_RATE)

            self.population.append(child1)
            self.population.append(child2)
            self.fitness_scores.append(0.0)
            self.fitness_scores.append(0.0)


    def update_fitness_scores(self, only_zero=False):
        """
        This method will update the fitness scores of the current population
        """
        for i in range(len(self.population)):
            if only_zero:
                if self.fitness_scores[i] == 0.0:
                    print("Starting to Evaluate Individual {}".format(i))
                    agent = NaoRobot(8,'Test','localhost',3100,'rsg/agent/nao/nao.rsg',startCoordinates=[-5.5,0.9,0],debugLevel=0)
                    agent.set_walk_config(self.population[i])
                    time.sleep(20)
                    print("Now Killing")
                    score = agent.get_distance_fitness_score()
                    self.fitness_scores[i] = score
                    print("Distance Travelled: {}".format(score))
                    agent.die()
                    time.sleep(2)
            elif not only_zero:
                print("Starting to Evaluate Individual {}".format(i))
                agent = NaoRobot(8,'Test','localhost',3100,'rsg/agent/nao/nao.rsg',startCoordinates=[-5.5,0.9,0],debugLevel=0)
                agent.set_walk_config(self.population[i])
                time.sleep(20)
                print("Now Killing")
                score = agent.get_distance_fitness_score()
                self.fitness_scores[i] = score
                print("Distance Travelled: {}".format(score))
                agent.die()
                time.sleep(2)

        print("Done Updating Fitness Scores")

    def evaluate_population(self, selection: Selection):
        """
        This method will evaluate the existing population and select the fittest chromosomes
        """
        # updating the fitness scores
        print('Starting to Evaluate Population')
        # Selecting the unfit chromosomes
        if selection == Selection.Random:
            survivors_indices = SelectionFunctions.random(self.population, self.fitness_scores, POPULATION_SIZE)
        elif selection == Selection.Truncation:
            survivors_indices = SelectionFunctions.truncation(self.population, self.fitness_scores, POPULATION_SIZE)
        elif selection == Selection.ProportionalSelection:
            survivors_indices = SelectionFunctions.proportional_selection(self.population, self.fitness_scores, POPULATION_SIZE)
        elif selection == Selection.RankBasedSelection:
            survivors_indices = SelectionFunctions.rank_based_selection(self.population, self.fitness_scores, POPULATION_SIZE)
        elif selection == Selection.BinaryTournament:
            survivors_indices = SelectionFunctions.binary_tournament(self.population, self.fitness_scores, POPULATION_SIZE)

        # updating the population with survivorsi 
        temp_pop = []
        temp_fitness = []
        for i in survivors_indices:
            temp_pop.append(self.population[i])
            temp_fitness.append(self.fitness_scores[i])

        self.population = temp_pop
        self.fitness_scores = temp_fitness

        del temp_pop
        del temp_fitness
        

        # incrementing the generation
        self.generation += 1
        print("Done Evaluating Population")
        print("Population Size: {}".format(len(self.population)))
        print("Fitness Scores Length: {}".format(len(self.fitness_scores)))

    
    def best_fitness_score(self):
        """
        This method will return the best fitness score of the current population
        """
        return max(self.fitness_scores)

    
    def worst_fitness_score(self):
        """
        This method will return the worst fitness score of the current population
        """
        return min(self.fitness_scores)

    def averaga_fitness_score(self):
        """
        This method will return the average fitness score of the current population
        """
        return sum(self.fitness_scores) / len(self.fitness_scores)