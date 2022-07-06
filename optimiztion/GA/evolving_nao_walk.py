
class NaoWalkOptimizer:

    def __init__(self, population_size, ):
        self.population = []
        self.fitness_scores = []

    def _initialize_population(self, population_size):
        for i in range(population_size):
            self.population.append(self.problem.generate_individual())