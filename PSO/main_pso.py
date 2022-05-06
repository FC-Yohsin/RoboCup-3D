import sys
# setting path
import subprocess
sys.path.append('../robocup_3d')

import pickle
from configs import *
import random, math
# import constants
from Agent import *
from Action import *

w = 0.9 # constant inertia weight (how much to previous velocity)
c1 = 0.9  # cognative const weigh theant
c2 = 0.1  # social constant
num_dimensions = len(joints)
num_particles = 15
num_iterations = 20
bounds = [(hjMin[joint], hjMax[joint]) for joint in joints]


# function we are attempting to optimize (minimize)
def fitness(vector):
    subproces = subprocess.Popen(['gnome-terminal', '-e', 'rcssserver3d'], stdout=subprocess.PIPE)
    time.sleep(3)
    print("Starting to Evaluate Individual")
    agent = NaoRobot(8,'Test','localhost',3100,'rsg/agent/nao/nao.rsg',startCoordinates=[-12.0,0.0,0],debugLevel=0)
    agent.set_walk_config(congigure_vector(vector))
    time.sleep(40)
    print("Now Killing")
    score = agent.get_distance_fitness_score() * -1
    print("Distance Travelled: {}".format(score))
    agent.die() 
    time.sleep(3)
    os.system("killall -9 rcssserver3d")
    time.sleep(3)
    return score

class Particle:

    def __init__(self, vector):
        self.position_vector = []  # particle position
        self.velocity_vector = []  # particle velocity
        self.best_position = []  # best position individual
        self.best_value = -1  # best error individual
        self.value = -1  # error individual

        for i in range(num_dimensions):
            self.velocity_vector.append(random.uniform(-1, 1))
            self.position_vector.append(vector[i])

    # evaluate current fitness
    def evaluate(self, fitness_function):
        self.value = fitness_function(self.position_vector)

        # check to see if the current position is an individual best
        if self.value < self.best_value or self.best_value == -1:
            self.best_position = self.position_vector
            self.best_value = self.value

    # update new particle velocity
    def update_velocity(self, global_best):
        for i in range(num_dimensions):
            r1 = random.random()
            r2 = random.random()

            cognitive = c1 * r1 * (self.best_position[i] -
                                   self.position_vector[i])

            social = c2 * r2 * (global_best[i] - self.position_vector[i])
            new_velocity = w * self.velocity_vector[i] + cognitive + social
            self.velocity_vector[i] = new_velocity

    # update the particle position based off new velocity updates
    def update_position(self, bounds):
        for i in range(num_dimensions):

            new_position = self.position_vector[i] + self.velocity_vector[i]
            self.position_vector[i] = new_position

            # adjust maximum position if necessary
            if self.position_vector[i] > bounds[i][1]:
                self.position_vector[i] = bounds[i][1]

            # adjust minimum position if neseccary
            if self.position_vector[i] < bounds[i][0]:
                self.position_vector[i] = bounds[i][0]


class PSO():

    def __init__(self, fitness_function, initial_vector,bounds, file, file2, num_particles,
                 num_iterations, population=None, best_value=1000, global_best=[]):
        
        file.write("------------------------------new run-----------------------------------\n")

        global_best_history = []
        global_average_history = []

        # if best_value and global_best:
        #     best_value = -1  # best error for group
        #     global_best = []  # best position for group

        # establish the swarm
        swarm: list[Particle] = []
        if population:
            assert len(population) == num_particles
            for i in population:
                swarm.append(Particle(i))
        else:
            swarm.append(Particle(initial_vector))
            for i in range(num_particles-1):
                swarm.append(Particle(get_random_vector()))

        # begin optimization loop
        i = 0
        while i < num_iterations:
            print("---------------------------------------NEW ITERATION---------------------------------------")
            if (i+1)%10==0:
                print("Resetting Global Best")
                best_value = 1000
            # cycle through particles in swarm and evaluate fitness
            for j in range(num_particles):
                swarm[j].evaluate(fitness_function)

                # determine if current particle is the best (globally)
                # if swarm[j].value < best_value or best_value == -1:
                if swarm[j].value < best_value:
                    global_best = list(swarm[j].position_vector)
                    best_value = float(swarm[j].value)

            # cycle through swarm and update velocities and position
            for j in range(num_particles):
                swarm[j].update_velocity(global_best)
                swarm[j].update_position(bounds)

            global_best_history.append(best_value)
            average = sum(swarm[j].best_value for j in range(num_particles)) / num_particles
            global_average_history.append(average)

            file2.write("{},{}\n".format(best_value, average))
            
            file.write("Global Best Value:{}\n".format(best_value))
            file.write("Global Best Vector: {}\n".format(global_best))
            file.write("{}\n".format([x.best_position for x in swarm]))
            file.write("\n\n")
            i += 1

            

        position = (global_best)
        value = (best_value)

        solution = (congigure_vector(position))

        print("Fitness: ", value)
        print()
        for joint in solution:
            print(joint, solution[joint])

        for i in range(len(position)):
            if position[i] > bounds[i][1] or position[i] < bounds[i][0]:
                print("Error")


#--- RUN ----------------------------------------------------------------------+
file = open("PSO_training_logs.txt", "a")
file2 = open("Best_avg_logs.csv", "a")
initial = get_random_vector()
# initial = [-10.514059504647033, -12.883960943363997, 41.318961739793764, 14.383040347219378, -56.502459184470624, -44.270896990269776, 14.010952437889483, 28.898514258154673, -2.5374780564386024, -0.10131107519380833]
swarm = [[-60.71685305907364, -53.06367412985607, -45.0, 6.608870195504571, 52.97455875318992, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.36550424985638, -120.0, -120.0, 1.0, -1.0, -64.01058253681495, -120.0, 90.0, 1.0], [-61.25531598440282, -52.60156110555605, -45.0, 7.146100781153519, 52.608479684729446, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.708103346683295, -120.0, -120.0, 1.0, -1.0, -62.101675798682344, -120.0, 90.0, 1.0], [-60.874801159760075, -51.930677451310494, -45.0, 7.452941428264864, 53.02933273981896, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.43802326832277, -120.0, -120.0, 1.0, -1.0, -60.96670259917269, -120.0, 90.0, 1.0], [-56.93016398610012, -52.33071170585668, -45.0, 7.220663594852574, 52.44502049122911, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.51236655036192, -120.0, -120.0, 1.0, -1.0, -35.324668995154454, -120.0, 90.0, 1.0], [-60.88098094198665, -53.202946131191254, -45.0, 7.671598707786609, 51.814443974055465, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.457442734458567, -120.0, -120.0, 1.0, -1.0, -62.948849020233986, -120.0, 90.0, 1.0], [-61.37381152025322, -53.859973602065885, -45.0, 7.2862785507178405, 50.6032589051612, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.13892183630999, -120.0, -120.0, 1.0, -1.0, -64.09208010064955, -120.0, 90.0, 1.0], [-60.02871519507495, -52.69430613652246, -45.0, 8.00990418387316, 53.10714657096904, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.787848059984075, -120.0, -120.0, 1.0, -1.0, -63.21720653870876, -120.0, 90.0, 1.0], [-61.42792051425175, -51.71735063394777, -45.0, 7.0879844349109185, 52.74941657012196, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.573004756510727, -120.0, -120.0, 1.0, -1.0, -63.399905995927114, -120.0, 90.0, 1.0], [-61.582474441496416, -52.96209564110295, -45.0, 7.199149337829423, 53.08558082961253, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.36224865986852, -120.0, -120.0, 1.0, -1.0, -64.11919852096058, -120.0, 90.0, 1.0], [-61.02347556972069, -51.8114611960932, -45.0, 7.302173112970612, 48.79747366651651, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.50464526257873, -120.0, -120.0, 1.0, -1.0, -61.787291257767386, -120.0, 90.0, 1.0], [-59.11514613681256, -53.23877332468478, -45.0, 6.247921071487722, 51.92441526097584, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.220758736691593, -120.0, -120.0, 1.0, -1.0, -57.55181258370382, -120.0, 90.0, 1.0], [-60.60228039826515, -51.70852856236265, -45.0, 8.101900011004801, 52.71066218659766, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 24.198297718595402, -120.0, -120.0, 1.0, -1.0, -58.87476630859468, -120.0, 90.0, 1.0], [-60.411816075763504, -51.82439158737697, -45.0, 6.88471945124816, 52.971297269081994, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.61636340698825, -120.0, -120.0, 1.0, -1.0, -62.701431551166465, -120.0, 90.0, 1.0], [-61.35791419664516, -52.01527162639135, -45.0, 7.577686343226347, 53.84519285420806, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.7322325152612, -120.0, -120.0, 1.0, -1.0, -76.90268641811038, -120.0, 90.0, 1.0], [-61.02079130439082, -50.89002295827996, -45.0, 7.621889787859818, 51.63952296738252, -25.0, 1.0, 1.0, 75.0, 75.0, 45.0, 23.382379036125087, -120.0, -120.0, 1.0, -1.0, -50.536055162629566, -120.0, 90.0, 1.0]]
best_vector = [-38.28021915065322, -26.808060878373492, 30.890118547321915, 56.19985473320423, -63.02110166515954, -33.35191408401462, 24.390382553555597, -7.408932742446857, 2.210138237132364, 2.729917082240965, -23.481040976179532, -84.06350129079597, -48.757803577013185, 7.69552103601769, -47.0241387520988, 43.60103859810434, 35.847283671619216, 0.9631031189924801]
best_value = 1000
PSO(fitness,
    initial,
    bounds,
    file,
    file2,
    num_particles=num_particles,
    num_iterations=num_iterations,
    # population=swarm,
    # global_best=best_vector,
    # best_value=best_value
    )

#--- END ---------------------------------------------------------------