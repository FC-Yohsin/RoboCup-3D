from Agent import *
from Action import *
import time
import random
import matplotlib



hjMax  = {
            'hj1' :  120.0,
            'hj2' :   45.0,
            'raj1':  120.0,
            'raj2':    1.0,
            'raj3':  120.0,
            'raj4':   90.0,
            'laj1':  120.0,
            'laj2':   95.0,
            'laj3':  120.0,
            'laj4':    1.0,
            'rlj1':    1.0,
            'rlj2':   25.0,
            'rlj3':  100.0,
            'rlj4':    1.0,
            'rlj5':   75.0,
            'rlj6':   45.0,
            'llj1':    1.0,
            'llj2':   45.0,
            'llj3':  100.0,
            'llj4':    1.0,
            'llj5':   75.0,
            'llj6':   25.0,} 


hjMin      = {
                'hj1' : -120.0,
                'hj2' :  -45.0,
                'raj1': -120.0,
                'raj2':  -95.0,
                'raj3': -120.0,
                'raj4':   -1.0,
                'laj1': -120.0,
                'laj2':   -1.0,
                'laj3': -120.0,
                'laj4':  -90.0,
                'rlj1':  -90.0,
                'rlj2':  -45.0,
                'rlj3':  -25.0,
                'rlj4': -130.0,
                'rlj5':  -45.0,
                'rlj6':  -25.0,
                'llj1':  -90.0,
                'llj2':  -25.0,
                'llj3':  -25.0,
                'llj4': -130.0,
                'llj5':  -45.0,
                'llj6':  -45.0,}




def get_random_config():
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

def get_random_gain():
    return random.uniform(0.1, 6.0)



if __name__ == '__main__':
    count = 1
    # while True:
    print("Agent {}".format(count))
    agent = NaoRobot(8,'Test','localhost',3100,'rsg/agent/nao/nao.rsg',startCoordinates=[-5.5,0.9,0],debugLevel=0)
    # agent.set_walk_config(get_random_config())
    # time.sleep(20)
    # print("Now Killing")
    # print(agent.calculate_gyr_fitness())
    # agent.die()
    # time.sleep(2)
    # count += 1