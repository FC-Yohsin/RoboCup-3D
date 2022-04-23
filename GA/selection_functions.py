from enum import Enum
from EA import *
import random
import numpy as np

class SelectionFunctions:
    """
    This class contains static methods of different fitness functions
    These functions takes list of tuples as population and
    returns their fitness scores as list of integers

    These functions are used in the EA class for both Parent Selection and Evaluating the fitness of the population
    """

    @staticmethod
    def random(population: list, fitness_scores: list, select_count: int) -> list:
        """
        This method will select randomly two chromosomes from the population as selected_chromosome
        """
        assert len(population) == len(fitness_scores)
        assert select_count <= len(population)

        selected_chromosomes_indices = random.sample([x for x in range(len(population))],k=select_count)
        print("Selected Chromosomes Indices: ", selected_chromosomes_indices)
        return selected_chromosomes_indices

    
    @staticmethod
    def truncation(population: list, fitness_scores: list, select_count: int) -> list:
        """
        This method will select chromosomes with the highest fitness values from the population as selected_chromosome
        """
        # print(len(population), len(fitness_scores))
        # assert len(population) == len(fitness_scores)
        assert select_count <= len(population)

        fitness_scores_copy = fitness_scores.copy()
        fitness_scores_copy.sort(reverse=True)
        selected_chromosome_index = [fitness_scores.index(value) for value in fitness_scores_copy[:select_count]]
        # selected_chromosome = [population[index] for index in selected_chromosome_index]
        print("Selected Chromosomes Indices: ", selected_chromosome_index)
        return selected_chromosome_index

    @staticmethod
    def proportional_selection(population: list, fitness_scores: list, select_count: int) -> list:
        """
        This method will select chromosomes by following the proportional selection approach
        """
        assert len(population) == len(fitness_scores)
        assert select_count <= len(population)

        normalized_values = [x/sum(fitness_scores) for x in fitness_scores]
        selected_chromosome = []
        
        # creating ranges for each chromosome using their normalized fitness scores
        # ranges = [(0, normalized_values[0])]
        # for i in range(len(normalized_values)-1):
        #     ranges.append((ranges[i][1], ranges[i][1]+normalized_values[i+1],))

        # generating random numbers between 0 and 1 and making sure that they doesn't lie in the same range
        # and selecting those who are in the range
        # while len(selected_chromosome) < select_count:
        #     random_val = random.random()
        #     for i in range(len(ranges)):
        #         # print(ranges[i][0], ranges[i][1], random_val)
        #         if random_val > ranges[i][0] and random_val <= ranges[i][1]:
        #             # print("inside if", select_count, random_val)
        #             selected_chromosome.append(population[i])
        
        # assert len(selected_chromosome) == select_count
        selected_chromosome_indices = random.choices([x for x in range(len(population))], weights=normalized_values, k=select_count)
        print("Selected Chromosomes Indices: ", selected_chromosome_indices)
        return selected_chromosome_indices

    @staticmethod
    def rank_based_selection(population: list, fitness_scores: list, select_count: int) -> list:
        """
        In rank-based selection we will assign ranks and then normalize those ranks for creating 
        ranges.
        """
        assert len(population) == len(fitness_scores)
        assert select_count <= len(population)

        # assigning ranks to chromosomes
        fitness_scores_copy = fitness_scores.copy()
        fitness_scores_copy.sort(reverse=False)
        ranks = [fitness_scores_copy.index(x)+1 for x in fitness_scores]
        selected_chromosome = []

        # normalizing ranks
        ranks = [(x/sum(ranks)) for x in ranks]

        # creating ranges for each chromosome using their normalized fitness scores
        # ranges = [(0, ranks[0])]
        # for i in range(len(ranks)-1):
        #     ranges.append((ranges[i][1], ranges[i][1]+ranks[i+1],))
        
        # generating random numbers between 0 and 1 and making sure that they doesn't lie in the same range
        # and selecting those who are in the range
        # selected_chromosome = []
        # while len(selected_chromosome) < select_count:
        #     random_val = random.random()
        #     for i in range(len(ranges)):
        #         if random_val > ranges[i][0] and random_val <= ranges[i][1]:
        #             selected_chromosome.append(population[i])
        
        # assert len(selected_chromosome) == select_count
        selected_chromosome_indices = random.choices([x for x in range(len(population))], weights=ranks, k=select_count)
        print("Selected Chromosomes Indices: ", selected_chromosome_indices)
        return selected_chromosome_indices


    @staticmethod
    def binary_tournament(population: list, fitness_scores: list, select_count: int) -> list:
        """
        This method will select two chromosomes from the population as selected_chromosome using binary tournament approach
        """
        assert len(population) == len(fitness_scores)
        assert select_count <= len(population)

        selected_chromosome = []
        while len(selected_chromosome) < select_count:
            val_1 = random.randint(0, len(population)-1)
            val_2 = random.randint(0, len(population)-1)

            candidate = max(fitness_scores[val_1], fitness_scores[val_2])
            if candidate == fitness_scores[val_1]:
                candidate = val_1
            else:
                candidate = val_2
            selected_chromosome.append(candidate)

        assert len(selected_chromosome) == select_count
        print("Selected Chromosomes Indices: ", selected_chromosome)
        return selected_chromosome