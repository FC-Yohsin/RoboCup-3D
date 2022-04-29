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

w = 0.5 # constant inertia weight (how much to previous velocity)
c1 = 0.8  # cognative const weigh theant
c2 = 0.65  # social constant
num_dimensions = len(joints)
num_particles = 10
num_iterations = 100
bounds = [(hjMin[joint], hjMax[joint]) for joint in joints]


# function we are attempting to optimize (minimize)
def fitness(vector):
    subproces = subprocess.Popen(['gnome-terminal', '-e', 'rcssserver3d'], stdout=subprocess.PIPE)
    time.sleep(3)
    print("Starting to Evaluate Individual")
    agent = NaoRobot(8,'Test','localhost',3100,'rsg/agent/nao/nao.rsg',startCoordinates=[-5.5,0.9,0],debugLevel=0)
    agent.set_walk_config(congigure_vector(vector))
    time.sleep(30)
    print("Now Killing")
    score = agent.get_distance_fitness_score() * -1
    print("Distance Travelled: {}".format(score))
    agent.die() 
    time.sleep(2)
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

    def __init__(self, fitness_function, initial_vector,bounds, file, num_particles,
                 num_iterations, population=None, best_value=-1, global_best=[]):
        
        if best_value and global_best:
            best_value = -1  # best error for group
            global_best = []  # best position for group

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

        checkpoint = [best_value, global_best, swarm]
        with open('PSO_checkpoint.pickle', 'wb') as f:
            pickle.dump(checkpoint, f)
        print("done")
        # begin optimization loop
        i = 0
        while i < num_iterations:
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
initial = get_random_vector()
# initial = [-10.514059504647033, -12.883960943363997, 41.318961739793764, 14.383040347219378, -56.502459184470624, -44.270896990269776, 14.010952437889483, 28.898514258154673, -2.5374780564386024, -0.10131107519380833]
swarm = [[-44.62747738294922, -38.570800467092596, 67.32232365098501, 38.43067857316945, -83.18436607226528, -72.62263670514156, 32.355757260562385, 24.683632435376044, 6.188509531970289, -13.399312663321435], [-44.895512280141084, -38.224364213418795, 65.88724228044379, 38.136892315787684, -82.15983847056056, -72.85038230902059, 32.36377739574939, 25.33905627077553, 5.724259501945166, -13.2988109143459], [-44.732273347704556, -38.233844591597624, 66.82385514204195, 38.271940492344655, -83.65254095266494, -72.63001364186248, 32.246339212572245, 24.500885299930093, 6.227067470870109, -13.366544291302496], [-44.8865600505636, -38.34221337175412, 67.56075766295677, 38.30100210039696, -82.64438236497996, -72.93406978702292, 31.978347062193624, 25.09109593628762, 5.511633746224695, -13.639039360707054], [-44.85657448548145, -38.52867408346527, 66.73789189200743, 38.20007945395163, -82.89724922415918, -72.80944111745035, 32.18173714983987, 24.488008653039245, 5.963095349447624, -13.550226354781168], [-44.744477956209664, -38.12875411310339, 66.83107731125651, 38.14649522536163, -82.1175217549918, -73.05306397447559, 32.40271750980213, 25.258988728170486, 5.795090405759699, -13.765017576043155], [-43.90731837477242, -38.154669697895564, 66.97346744217569, 38.09831054840438, -82.59116507976759, -72.96784734896585, 32.09490387202975, 25.136418385524237, 5.639467673649502, -13.256932227632149], [-44.94546636228561, -38.328997785219755, 66.59300195216511, 38.695945061935745, -82.64156016570001, -72.45858762283044, 32.45573002961277, 24.97159032621146, 6.03919127987842, -13.171899564675563], [-44.78719457051124, -38.09150092238276, 66.7177479978043, 38.20632444105912, -82.7801961578152, -73.27950021818137, 32.327532848134446, 24.759556647048864, 5.906828848120219, -13.144180631201714], [-44.723490461538894, -38.390401534629454, 66.97298135731289, 38.42338800809232, -82.96935933741366, -73.13242118694762, 32.382598213363295, 25.40368164567866, 6.003121793538581, -13.91169479699383]]
best_vector = [-43.7602439172008, -37.4813363442764, 65.91450103725698, 38.59104831352813, -83.02061887752699, -72.41660458725907, 30.294326337697477, 24.711953775252333, 6.452935730411978, -15.126119552173499]
best_value = -99.25807134899803
PSO(fitness,
    initial,
    bounds,
    file,
    num_particles=num_particles,
    num_iterations=num_iterations,
    population=swarm,
    # global_best=best_vector,
    # best_value=best_value
    )

#--- END ---------------------------------------------------------------