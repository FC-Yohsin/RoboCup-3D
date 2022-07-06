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

w = 0.3 # constant inertia weight (how much to previous velocity)
c1 = 0.1 # cognative const weigh theant
c2 = 0.1  # social constant
num_dimensions = len(joints)
num_particles = 15
num_iterations = 100
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
file = open("PSO_training_logs_2.txt", "a")
file2 = open("Best_avg_logs_2.csv", "a")
initial = get_random_vector()
# initial = [-10.514059504647033, -12.883960943363997, 41.318961739793764, 14.383040347219378, -56.502459184470624, -44.270896990269776, 14.010952437889483, 28.898514258154673, -2.5374780564386024, -0.10131107519380833]
swarm = [[-58.335603140724224, -42.7825308406334, 0.24523211654331992, -19.83825958852398, 30.294899706478173, 38.86155647791799, -69.25474424204917, -49.09150652306993, 28.670264200599284, 3.909123015133371, -13.326545548769902, -5.188858767295522, 66.41813803686689, 75.97123693902932, -20.858450021689116, -1.0, -17.530955162841643, 45.02504755179358, 44.03817626063646, 0.7443884724685544], [-58.39042745542937, -42.56382847780963, 0.26662604985105903, -19.89775993931676, 30.24308122247538, 38.699719116274835, -69.1995369390863, -49.263710661810556, 28.766380539376645, 3.7974662590384707, -13.532108137840073, -5.326402345746307, 66.78242735695206, 76.1952489445045, -20.63541652002554, -0.9565802984248853, -17.324144183858447, 45.15236034195943, 44.14882927972556, 0.8283599073732743], [-58.33562816773252, -42.92143775762341, 0.3030909775561238, -19.828437077087603, 30.397607536501347, 38.63254364054178, -69.45222100180773, -49.042602550646514, 28.828257983868074, 4.0169504771424664, -13.505686280527259, -5.155762822013239, 66.5189211466202, 76.21130460885803, -20.827829123605504, -1.0, -17.271642667790523, 45.26756914951357, 44.03091538648995, 0.791127076453474], [-58.1962111573123, -42.755542184127144, 0.34837841317488055, -19.852285765023787, 30.344159794807425, 38.73140288248877, -69.16976954960695, -49.251669147560776, 28.828938912739176, 3.828463630269035, -13.481735451717558, -5.193119866702538, 66.6819965823131, 76.18213435101265, -20.84436412384727, -1.0, -17.382912866899865, 45.41829659548034, 44.049418572617455, 0.9030352414589724], [-58.324291281598484, -42.99499865797043, 0.40338730518876165, -19.84759824456159, 30.559586969177285, 38.6263804533167, -69.1104451461022, -49.312162929053684, 28.750439367096703, 3.9023583129161916, -13.42486605106053, -5.311501877385449, 66.33738607420545, 76.14166441967708, -20.736559336086437, -0.9127746242693788, -17.440699959718, 45.31663539855393, 44.18055793825459, 0.8321068894433299], [-58.251896745604775, -42.77869367728888, 0.42570330086406927, -19.766207602762492, 30.327938234930286, 38.83702099293669, -69.35547959658965, -49.13327861946154, 28.80428307371313, 3.9301104661985007, -13.45832954993531, -5.2526379939136545, 66.83632717953189, 76.30428242091756, -20.5409120186287, -1.0, -17.306409135862673, 44.90429016933363, 44.13774685307345, 0.7608833716820704], [-58.3249179714274, -42.777828126834265, 0.14339577668391384, -19.852127789176144, 30.261780610384463, 38.728073284735125, -69.04601355541308, -49.33162371007271, 28.599662668469023, 4.004204049606883, -13.524343056038223, -5.232917766316168, 66.66650536029202, 76.22155775754331, -20.78548532859813, -1.0, -17.28473810748571, 44.89019785577408, 44.0519377961618, 0.7835081086044424], [-58.329858151966796, -42.74819352264938, 0.4026178677584695, -19.914440226859618, 30.47398073581446, 38.70161565557227, -69.21840441780067, -49.25256430303419, 28.83694028468755, 3.857494816929832, -13.512705104438592, -5.183483964738835, 66.91009654177063, 76.28292722578075, -20.73039830114366, -0.9593833551247325, -17.463466872160875, 45.04476700160309, 44.10174859280212, 0.7488091303652759], [-58.19998342199342, -42.7146079924557, 0.33148959650543697, -19.893877796068878, 30.20839391504658, 38.822315225483806, -69.26340033317955, -49.236451439611656, 28.84639458085709, 3.9708130076919987, -13.404202583789537, -5.255219905197309, 66.43006108092126, 76.35039756468564, -20.7284651739244, -0.9613983644978439, -17.451348422690142, 45.06872042563318, 44.084741828996926, 0.754664548992573], [-58.397892833477584, -42.81833767164955, 0.24973905839172733, -19.73539231223023, 30.230523817280854, 38.70230272602383, -69.25393668942448, -49.37564418840077, 28.599351664865413, 3.7752648167713088, -13.471353276618654, -5.23977943404691, 66.10076606023706, 76.06991511257426, -20.770754820193606, -1.0, -17.350510632673068, 44.78506222204746, 44.1069773293443, 0.8912520356804192], [-58.31035487189387, -42.64413813721364, 0.40035604142966325, -19.93950336508606, 29.915484055440277, 38.67556540859011, -69.15547025767444, -49.25997149107744, 28.629943248990006, 3.8947190462648997, -13.52518675745533, -5.3792906001124114, 66.61158706453352, 76.17835009084403, -20.80722432346102, -1.0, -17.470500653053453, 45.13273513434162, 44.15280781980975, 0.8198448656094703], [-58.38811045031402, -42.79889495682988, 0.2574959271132906, -19.886660472914585, 30.267161988777506, 38.77686903272282, -69.13658923645427, -49.21262670168466, 28.718153836676205, 3.926755110372194, -13.37119831871111, -5.393436274783375, 66.47895561044179, 76.25439668852354, -20.817087011018373, -0.909430562866639, -17.447830728123606, 44.98758416578053, 43.99703068810735, 0.7652937042345525], [-58.29588136465794, -42.689975913769196, 0.435222904758459, -19.926517731380127, 30.401463927851857, 38.767918915712706, -69.05156234384874, -49.37222235904153, 28.674211091959457, 3.8978038039801692, -13.488277775083395, -5.179998534604297, 66.67661272424645, 76.41856005822623, -20.795426131763058, -1.0, -17.383393314294633, 45.19117855699877, 44.09636164611459, 0.8838269212844502], [-58.34158260343922, -42.743676101094536, 0.23432421669481965, -19.744123933163333, 30.42208595551569, 38.69633417838157, -69.0445848661309, -49.154943316336826, 28.741269732141163, 3.841576270915677, -13.507042509258605, -5.242037417762877, 66.78698854016612, 76.02597863032372, -20.71011605105068, -0.9060499597062802, -17.38996476072299, 45.18927602743801, 44.03353967708711, 0.8172318114864526], [-58.41157056418084, -42.60126304367056, 0.23388959211944368, -19.795072055910797, 30.255883873999707, 38.77424514912513, -69.19444837060212, -49.23904240153833, 28.598217717469712, 3.910334041883221, -13.247323838480403, -5.158963273613652, 66.52717576625052, 76.25471834771463, -20.67732530734689, -1.0, -17.32760493042541, 45.14398987316644, 44.15333536393029, 0.7626218938063217]]
best_vector = [-38.28021915065322, -26.808060878373492, 30.890118547321915, 56.19985473320423, -63.02110166515954, -33.35191408401462, 24.390382553555597, -7.408932742446857, 2.210138237132364, 2.729917082240965, -23.481040976179532, -84.06350129079597, -48.757803577013185, 7.69552103601769, -47.0241387520988, 43.60103859810434, 35.847283671619216, 0.9631031189924801]
best_value = 1000
PSO(fitness,
    initial,
    bounds,
    file,
    file2,
    num_particles=num_particles,
    num_iterations=num_iterations,
    population=swarm,
    # global_best=best_vector,
    # best_value=best_value
    )

#--- END ---------------------------------------------------------------