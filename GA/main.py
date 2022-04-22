from EA import *

naoWalkOptimizer = EA_NaoWalkOptimizer()
naoWalkOptimizer.initialize_population()

for i in range(15):
    naoWalkOptimizer.update_fitness_scores()
    naoWalkOptimizer.generate_offspring(selection=Selection.BinaryTournament)
    naoWalkOptimizer.evaluate_population(selection=Selection.Truncation)

