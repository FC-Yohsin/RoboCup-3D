from cgitb import reset
import time, math
import threading
from logger import logger
import numpy as np
from constants import CYCLE_LENGTH
from pns import PNS
from agent.movement_scheduler import MovementScheduler
from game_state import GameState
from agent.sensors import Gyroscope, Accelerometer, Vision, ForceResistanceSensor
from roboviz_drawing import RobovizDrawing
from world import *


class NaoRobot(object):
    """Class that represents the Nao Soccer Robot
    机器人的实现"""

    def __init__(self, agentID, teamname, host='localhost', port=3100, model='', debugLevel=0,
            startCoordinates=[-0.5, 0, 0]): 

        self.agentID       = agentID
        self.teamname      = teamname
        self.host          = host
        self.port          = port
        self.model         = model
        self.debugLevel    = debugLevel
        self.alive         = False
        self.realstarttime = None # starttime of robot
        self.simstarttime  = None 
        self.counter = 0
        # set maximum hinge effector speed
        self.maxhjSpeed = 7.035

        # movement schedule
        # each sublist should contain a function object and
        # a dictionary of keyword arguments
        # e.g. [foo, {'kw1': val1, 'kw2', val2}]
        # the function will be executed until it returns "done"
        self.msched     = MovementScheduler()

        # games state information
        self.gamestate  = GameState()

        # gyroscope and accelerometer
        self.gyr        = Gyroscope    ('torso')
        self.acc        = Accelerometer('torso')

        # self.see        = Vision('F1L')               应该枚举一下，或者字典类型？　　　for flag in itemuarter ,return
        # self.see        =[Vision('F1L'),Vision('F2L'),Vision('F1R'),Vision('F2R'),Vision('G1L'),Vision('G2L'),Vision('G1R'),Vision('G2R'),Vision('B'),Vision('team'),Vision('id')]


        # hinge joint perceptor states
        #对应的三种状态，左右摇摆，上下倾斜，沿轴转动
        self.hj         = {'hj1' : 0.0,         #Neck Yaw   脖子左右摇摆
                           'hj2' : 0.0,         #Neck Pitch    脖子上下倾斜
                           'raj1': 0.0,         #Right Shoulder Pitch
                           'raj2': 0.0,         #Right Shoulder Yaw
                           'raj3': 0.0,         #Right Arm Roll
                           'raj4': 0.0,         #Right Arm Yaw
                           'laj1': 0.0,         #___Left Shoulder Pitch
                           'laj2': 0.0,         #___Left Shoulder Yaw
                           'laj3': 0.0,         #___Left Arm Roll
                           'laj4': 0.0,         #___Left Arm Yaw
                           'rlj1': 0.0,         #Right Hip YawPitch
                           'rlj2': 0.0,         #Right Hip Roll
                           'rlj3': 0.0,         #Right Hip Pitch
                           'rlj4': 0.0,         #Right Knee Pitch
                           'rlj5': 0.0,         #Right Foot Pitch
                           'rlj6': 0.0,         #Right Foot Roll
                           'llj1': 0.0,         #___Left Hip YawPitch
                           'llj2': 0.0,         #___Left Hip Roll
                           'llj3': 0.0,         #___Left Hip Pitch
                           'llj4': 0.0,         #___Left Knee Pitch
                           'llj5': 0.0,         #___Left Foot Pitch
                           'llj6': 0.0,}        #___Left Foot Roll

        # corresponding hinge joint effectors
        #铰链关节感受器与之对应的效应器
        self.hjEffector = {'hj1' : 'he1',
                           'hj2' : 'he2',
                           'raj1': 'rae1',
                           'raj2': 'rae2',
                           'raj3': 'rae3',
                           'raj4': 'rae4',
                           'laj1': 'lae1',
                           'laj2': 'lae2',
                           'laj3': 'lae3',
                           'laj4': 'lae4',
                           'rlj1': 'rle1',
                           'rlj2': 'rle2',
                           'rlj3': 'rle3',
                           'rlj4': 'rle4',
                           'rlj5': 'rle5',
                           'rlj6': 'rle6',
                           'llj1': 'lle1',
                           'llj2': 'lle2',
                           'llj3': 'lle3',
                           'llj4': 'lle4',
                           'llj5': 'lle5',
                           'llj6': 'lle6',} 

        # force resistance perceptors
        self.frp        = {'rf': ForceResistanceSensor('rf'),
                           'lf': ForceResistanceSensor('lf')}


        self.flags_positions = {
            "F1L": [-16,10],
            "F2L": [-16,-10],
            "F1R": [16,10],
            "F2R": [16,-10],
            "G1L": [16,1.05],
            "G2L": [16,-1.05],
            "G1R": [16,1.05],
            "G2R": [16,-1.05],
            "Center": [0,0],
        }


        self.flag_distances = {
            "F1L": float("inf"),
            "F2L": float("inf"),
            "F1R": float("inf"),
            "F2R": float("inf"),
            "G1L": float("inf"),
            "G2L": float("inf"),
            "G1R": float("inf"),
            "G2R": float("inf"),
            "B" : float("inf"),
        }


        self.visible_flags = []

        # =========================================================增加vision
        self.vision     = {
                            'F1L' : Vision('F1L'),
                            'F2L' : Vision('F2L'),
                            'F1R' : Vision('F1R'),
                            'F2R' : Vision('F2R'),
                            'G1L' : Vision('G1L'),
                            'G1R' : Vision('G1R'),
                            'G2L' : Vision('G2L'),
                            'G2R' : Vision('G2R'),
                            'B'   : Vision('B'),
                            'P'   : Vision('P'),
                            'id'  : Vision('id'),
                            'team': Vision('team')
                        }

        # =================================================================2015/8/24

        # hinge joint effector states
        #要明白一个关节转动之后对其他关节的带动及影响
        self.he         = {'he1' : 0.0,
                           'he2' : 0.0,
                           'rae1': 0.0,
                           'rae2': 0.0,
                           'rae3': 0.0,
                           'rae4': 0.0,
                           'lae1': 0.0,
                           'lae2': 0.0,
                           'lae3': 0.0,
                           'lae4': 0.0,
                           'rle1': 0.0,
                           'rle2': 0.0,
                           'rle3': 0.0,
                           'rle4': 0.0,
                           'rle5': 0.0,
                           'rle6': 0.0,
                           'lle1': 0.0,
                           'lle2': 0.0,
                           'lle3': 0.0,
                           'lle4': 0.0,
                           'lle5': 0.0,
                           'lle6': 0.0,} 


        # maxima of hinge joints
        self.hjMax      = {'hj1' :  120.0,
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

        # minima of hinge joints
        self.hjMin      = {'hj1' : -120.0,
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

        # defaults (starting positions) of hinge joints in percent
        self.hjDefault  = {'hj1' : 0.0,
                           'hj2' : 0.0,
                           'raj1': 0.0,
                           'raj2': 0.0,
                           'raj3': 0.0,
                           'raj4': 0.0,
                           'laj1': 0.0,
                           'laj2': 0.0,
                           'laj3': 0.0,
                           'laj4': 0.0,
                           'rlj1': 0.0,
                           'rlj2': 0.0,
                           'rlj3': 0.0,
                           'rlj4': 0.0,
                           'rlj5': 0.0,
                           'rlj6': 0.0,
                           'llj1': 0.0,
                           'llj2': 0.0,
                           'llj3': 0.0,
                           'llj4': 0.0,
                           'llj5': 0.0,
                           'llj6': 0.0,}

        
        self.visible_flags = []
        self.is_fallen = False
        self.penalty = 0
        self.fallen_count = 0
        self.roboviz = RobovizDrawing()

        self.startCoordinates = startCoordinates

        self.pns = PNS(self.agentID, self.teamname,
                host=self.host, port=self.port, model=self.model, debugLevel=self.debugLevel)
        self.perceive()
        self.pns.beam_effector(startCoordinates[0], startCoordinates[1], startCoordinates[2])
        
        for hj in self.hjDefault.keys():
            self.hjDefault[hj] = self.get_hj(hj)

        self.lifeThread = threading.Thread(target=self.live)                #难道要直接在类里面使用？
        self.lifeThread.start()

        self.change_in_gyr = np.zeros((3,3))
        self.orientations_hist = np.array([[0,0,0]])



# ==================================== #

    # tuning walking parameters
    def set_walk_config(self, config):
        self.walk_config = config

# ==================================== #


    def live(self):
        """Start the robot"""

        # only one live thread allowed!
        #只允许有一个活动线程，所以说，如何使用多线程？？
        if self.alive:
            return

        self.alive = True
        startSkippingNumber = 10
        # print(self.perceive())
        iteration         = -1
        skippedIterations =  0
        
        # self.roboviz.addAnnotation(
        #         text="Annotations faaz TEXT!!",
        #         position=(-5.5,0.9,2.0),
        #         color=(200,255,255),
        #         setName="Annotation.8",
        #     )
        
        # self.roboviz.drawCircle(
        #     center=(-5.0,5.0),
        #     radius=10.0,
        #     thickness=1.0,
        #     color=(255,0,0),
        #     setName="Circle.1",
        # )
        
        # self.roboviz.drawCircle(
        #     center=(-5.0,5.0),
        #     radius=6.0,
        #     thickness=7.0,
        #     color=(255,213,10),
        #     setName="Circle.2",
        # )
        
        # self.roboviz.drawLine(
        #     pointA=(-5.0,5.0,1.0),
        #     pointB=(-5.0,10.0,2.0),
        #     thickness=2.0,
        #     color=(255,255,0),
        #     setName="Line.1",
        # )
        
        # self.roboviz.clearAgentAnnotation(agentNum=10)
        self.roboviz.addAgentAnnotation(
            agentNum=10,
            text="This is a agent annotation test",
        )
        
        while self.alive:
            
            iteration += 1
            self.counter += 1
#             if self.check_sync() >= startSkippingNumber:
#                 while self.check_sync() > 2:
# #                    print(self.check_sync())
#                     self.peself.is_fallenfrom another perc: {}".format(self.counter))
#                     iteration         += 1
#                     skippedIterations += 1 

            
            
            self.perceive()
            self.think()

            if iteration * CYCLE_LENGTH % 3.0 == 0:
#                print("Robot {} lags {} cycles behind after {} iterations".format(self.agentID, self.check_sync(), iteration+1))
                logger.info("gametime - realtime: {:.5f}".format(self.gamestate.get_gametime() - time.time()))


        # report statistics
        iterations = iteration + 1
        logger.info("Robot {} lived for {:.1f} seconds,\n\ti.e. {} iterations, {} of which have been skipped ({:.2f}%).".format(self.agentID, time.time()-self.realstarttime, iterations, skippedIterations, 100.0*skippedIterations/iterations))


# ==================================== #

    def calculate_gyr_fitness(self):
        """
        This is a fitness calculation for the measuring the stability of Nao. We use 
        the difference between the current orientation and the previous orientation.
        """
        x = np.mean(self.orientations_hist, axis=0)
        x = np.mean(x, axis=0)
        score_percent = ((1/x) * 100) * (100/6)
        return score_percent

# ==================================== #

    def evaluating(self):
        # maintaing track of gyroscope changes
        self.change_in_gyr = (self.gyr.get_orientation()*100) - self.change_in_gyr
        self.orientations_hist = np.abs(np.concatenate((self.orientations_hist, self.change_in_gyr), axis=0))


# ==================================== #
    def get_position(self):
        """
        Returns the current position of the robot.
        """
        # distance from F1R: K
        # distance from F2R: L
        # if 'F1R' in self.visible_flags and 'F2R' in self.visible_flags:
        K = self.flag_distances['F1R']
        L = self.flag_distances['F2R']
        sqr_dist = (L**2) - (K**2)
        F1R_pos = self.flags_positions['F1R']
        F2R_pos = self.flags_positions['F2R']
        y = (-K**2+L**2) / 40
        # print("y: {}".format(y))
        temp = -(K**4) + (2*K**2*L**2) + (800*K**2) - (L**4) + (800*L**2) - 160000
        x = -(math.sqrt(temp)/40) + 16
    # else:
    #     return [self.startCoordinates[0], self.startCoordinates[1]]
        return [x, y] 

# ==================================== #

    def get_distance_fitness_score(self):
        current_pos = self.get_position()
        score = math.dist(current_pos, [self.startCoordinates[0], self.startCoordinates[1]]) * 30

        if current_pos[0] < self.startCoordinates[0]:
            score = score * -1
        logger.info("Score 01: {}".format(score))
        if self.is_fallen:
            score = score - (100*self.penalty)
        logger.info("Score 02: {}".format(score))
        straight_line_error = abs(self.get_position()[1]-self.startCoordinates[1])

        score = score - (straight_line_error * 10)
        # print(self.visible_flags)
        # if "F1R" not in self.visi ble_flags and "F2R" not in self.visible_flags:
        #     distance_traveled = distance_traveled - 5
        logger.info("Score 03: {}".format(score))
        return score

# ==================================== #

    def think(self):
        if self.counter <= 80:
            self.stand()

# ==================================== #
    def simpleWalk(self):
        gain = self.walk_gain
        if self.counter > 80 and self.counter <= 104:

            self.moveJointByAngle(
                "rlj1",
                self.walk_config["rlj1"][0], 
                gain)
            self.moveJointByAngle(
                "llj1",
                self.walk_config["llj1"][0], 
                gain)
            # self.moveJointByAngle("rlj2", self.walk_config["rlj2"][0], gain)
            # self.moveJointByAngle("llj2", self.walk_config["llj2"][0], gain)
            self.moveJointByAngle(
                "rlj3",
                self.walk_config["rlj3"][0], 
                gain)
            self.moveJointByAngle(
                "rlj4",
                self.walk_config["rlj4"][0], 
                gain)
            self.moveJointByAngle(
                "rlj5",
                self.walk_config["rlj5"][0], 
                gain)

            self.moveJointByAngle(
                "llj3",
                self.walk_config["llj3"][0], 
                gain)
            self.moveJointByAngle(
                "llj4",
                self.walk_config["llj4"][0], 
                gain)
            self.moveJointByAngle(
                "llj5",
                self.walk_config["llj5"][0], 
                gain)

            self.moveJointByAngle(
                "rlj6", 
                self.walk_config["rlj6"][0], 
                gain)
            self.moveJointByAngle(
                "llj6", 
                self.walk_config["llj6"][0], 
                gain)
            # self.moveJointByAngle("raj1", self.walk_config["raj1"][0], gain)
            # self.moveJointByAngle("laj1", self.walk_config["laj1"][0], gain)
            # self.moveJointByAngle("raj2", self.walk_config["raj2"][0], gain)
            # self.moveJointByAngle("laj2", self.walk_config["laj2"][0], gain)
            # self.moveJointByAngle("raj3", self.walk_config["raj3"][0], gain)
            # self.moveJointByAngle("laj3", self.walk_config["laj3"][0], gain)
            # self.moveJointByAngle("raj4", self.walk_config["raj4"][0], gain)
            # self.moveJointByAngle("laj4", self.walk_config["laj4"][0], gain)


        if self.counter > 95 and self.counter <= 120:

            self.moveJointByAngle(
                "rlj1",
                self.walk_config["rlj1"][1], 
                gain)
            self.moveJointByAngle(
                "llj1",
                self.walk_config["llj1"][1], 
                gain)
            # self.moveJointByAngle("rlj2", self.walk_config["rlj2"][0], gain)
            # self.moveJointByAngle("llj2", self.walk_config["llj2"][0], gain)
            self.moveJointByAngle(
                "rlj3",
                self.walk_config["rlj3"][1], 
                gain)
            self.moveJointByAngle(
                "rlj4",
                self.walk_config["rlj4"][1], 
                gain)
            self.moveJointByAngle(
                "rlj5",
                self.walk_config["rlj5"][1], 
                gain)

            self.moveJointByAngle(
                "llj3",
                self.walk_config["llj3"][1], 
                gain)
            self.moveJointByAngle(
                "llj4",
                self.walk_config["llj4"][1], 
                gain)
            self.moveJointByAngle(
                "llj5",
                self.walk_config["llj5"][1], 
                gain)

            self.moveJointByAngle(
                "rlj6", 
                self.walk_config["rlj6"][1], 
                gain)
            self.moveJointByAngle(
                "llj6", 
                self.walk_config["llj6"][1], 
                gain)
            # self.moveJointByAngle("raj1", self.walk_config["raj1"][1], gain)
            # self.moveJointByAngle("laj1", self.walk_config["laj1"][1], gain)
            # self.moveJointByAngle("raj2", self.walk_config["raj2"][1], gain)
            # self.moveJointByAngle("laj2", self.walk_config["laj2"][1], gain)
            # self.moveJointByAngle("raj3", self.walk_config["raj3"][1], gain)
            # self.moveJointByAngle("laj3", self.walk_config["laj3"][1], gain)
            # self.moveJointByAngle("raj4", self.walk_config["raj4"][1], gain)
            # self.moveJointByAngle("laj4", self.walk_config["laj4"][1], gain)

                


    # def simpleWalk(self):
    #     gain = 4
    #     if self.counter > 80 and self.counter <= 104:

    #         self.moveJointByAngle("rlj1",-12, gain)
    #         self.moveJointByAngle("llj1",-11, gain)

    #         self.moveJointByAngle("rlj3",40.4, gain)
    #         self.moveJointByAngle("rlj4",-55, gain)
    #         self.moveJointByAngle("rlj5",13, gain)

    #         self.moveJointByAngle("llj3",15, gain)
    #         self.moveJointByAngle("llj4",-45, gain)
    #         self.moveJointByAngle("llj5",30, gain)

    #         self.moveJointByAngle("rlj6", -4, gain)
    #         self.moveJointByAngle("llj6", -1, gain)


    #     if self.counter > 95 and self.counter <= 120:

    #         self.moveJointByAngle("rlj1",-11, gain)
    #         self.moveJointByAngle("llj1",-12, gain)

    #         self.moveJointByAngle("llj3",40.4, gain)
    #         self.moveJointByAngle("llj4",-55, gain)
    #         self.moveJointByAngle("llj5",13, gain)

    #         self.moveJointByAngle("rlj3",15, gain)
    #         self.moveJointByAngle("rlj4",-45, gain)
    #         self.moveJointByAngle("rlj5",30, gain)

    #         self.moveJointByAngle("rlj6", 1, gain)
    #         self.moveJointByAngle("llj6", 4, gain)



            
# ==================================== #


    def stand(self):
        gain = 3

        self.moveJointByAngle('llj1', angle=0, speed=gain)
        self.moveJointByAngle('rlj1', angle=0, speed=gain)

        self.moveJointByAngle('llj2', angle=5, speed=gain)
        self.moveJointByAngle('rlj2', angle=-5, speed=gain)

        self.moveJointByAngle('llj3', angle=25, speed=gain)
        self.moveJointByAngle('rlj3', angle=25, speed=gain)

        self.moveJointByAngle('llj4', angle=-65, speed=gain)
        self.moveJointByAngle('rlj4', angle=-65, speed=gain)

        self.moveJointByAngle('llj5', angle=36, speed=gain)
        self.moveJointByAngle('rlj5', angle=36, speed=gain)

        self.moveJointByAngle('llj6', angle=-1, speed=gain)
        self.moveJointByAngle('rlj6', angle=1, speed=gain)

        self.moveJointByAngle('laj1', angle=-75, speed=gain)
        self.moveJointByAngle('raj1', angle=-75, speed=gain)
        self.moveJointByAngle('laj2', angle=45, speed=gain)
        self.moveJointByAngle('raj2', angle=-45, speed=gain)
        self.moveJointByAngle('laj4', angle=-68, speed=gain)
        self.moveJointByAngle('raj4', angle=68, speed=gain)
        self.moveJointByAngle('llj1', angle=-11, speed=gain)
        self.moveJointByAngle('rlj1', angle=-11, speed=gain)


# ==================================== #


    def standPosture1(self):

        gain = 4
        self.moveJointByAngle("llj3", angle=100, speed=gain)
        self.moveJointByAngle("rlj3", angle=100, speed=gain) # torso

        self.moveJointByAngle("llj2", angle=30, speed=gain)
        self.moveJointByAngle("rlj2", angle=-30, speed=gain)

        self.moveJointByAngle("llj1", angle=-60, speed=gain)
        self.moveJointByAngle("rlj1", angle=-60, speed=gain)

        self.moveJointByAngle("llj4", angle=-100, speed=gain)
        self.moveJointByAngle("rlj4", angle=-100, speed=gain) # knees

        self.moveJointByAngle("llj6", angle=-45, speed=gain)
        self.moveJointByAngle("rlj6", angle=45, speed=gain)

        self.moveJointByAngle("laj1", angle=20, speed=gain)
        self.moveJointByAngle("raj1", angle=20, speed=gain)

        self.moveJointByAngle("laj2", angle=0, speed=gain)
        self.moveJointByAngle("raj2", angle=0, speed=gain)


# ==================================== #
    """
    If a joint movement does not stop at the requested angle, 
    increase the counter until it does.
    """

    def moveJointByAngle(self, name: str, angle: float, speed: float):
        currentAngle = self.hj[name]
        speed = abs(speed)

        if angle >= self.hjMax[name]:
            angle = self.hjMax[name]
        elif angle <= self.hjMin[name]:
            angle = self.hjMin[name]
        if abs(angle - currentAngle) < 5:
            self.pns.hinge_joint_effector(name=self.hjEffector[name], rate=0)
        elif currentAngle < angle:
            self.pns.hinge_joint_effector(name=self.hjEffector[name], rate= math.radians(abs(angle - currentAngle)) * speed)
        elif currentAngle > angle:
            self.pns.hinge_joint_effector(name=self.hjEffector[name], rate= - math.radians(abs(angle - currentAngle)) * speed)
       

# ==================================== #

    def die(self, timeout=0):
        """Stop robot execution and close socket connection to server
        If timeout is > 0, give the robot some time to finish scheduled movements.
        如果超时，则给机器人一些时间去结束动作调度"""
        start    = time.time()
        timeleft = timeout - time.time() + start
        while timeleft > 0:
            if len(self.msched) == 0:
                self.alive = False
                break
            timeleft = timeout - time.time() + start
        self.alive = False
        self.lifeThread.join()
        self.pns.socket.close()

# ==================================== #

    def perceive(self, skip=False):
        """Receive perceptor information from server and
        update status accordingly
        根据从服务器接收到的感知信息更新自身状态"""

#        start = time.time()
        perceptors = self.pns.receive_perceptors()
#        print("receive_perceptors() took {:.8f} sec.".format(time.time()-start))
        # if self.counter % 3 == 0:
        #     self.visible_flags = []
        # title = [y[0] for y in perceptors]
        # if "See" not in title:
        #     self.visible_flags = []

        for perceptor in perceptors:

            # time
            if perceptor[0] == 'time':
                self.gamestate.set_time(perceptor[1][1])
                if self.realstarttime == None:
                    self.realstarttime = time.time()                #真时的时间
                    self.simstarttime  = self.gamestate.get_time()  #仿真服务器的时间
                if skip:
                    break

            # game state
            elif perceptor[0] == 'GS':
                for field in perceptor[1:]:
                    if field[0] == 'sl':                            #我是左边开球
                        self.gamestate.set_scoreLeft(field[1])      #我是右边开球
                    elif field[0] == 'sr':
                        self.gamestate.set_scoreRight(field[1])
                    elif field[0] == 't':
                        self.gamestate.set_gametime(field[1])
                    elif field[0] == 'pm':
                        self.gamestate.set_playmode(field[1])

            # gyroscope
            elif perceptor[0] == 'GYR':
                self.gyr.set(perceptor[2][1:])
                # print("GYR:")
                # print(perceptor)

            # set accelerometer
            elif perceptor[0] == 'ACC':
                self.acc.set(perceptor[2][1:])

            # vision information
            elif perceptor[0] == 'See':
                # print(perceptor[1:])
                # pass
                # 添加vision,由于前面是使用字典进行解析的，所以不能使用类似这种格式，self.vision['f1l'].setflag(xxx),擦，竟然又可以了，什么鬼
                #在这里指存储一遍，故不必设置成字典相对应
                self.visible_flags = []
                self.visible_flags = [x[0] for x in perceptor[1:]]
                # print(len(perceptor[1:]))
                for field in perceptor[1:]:
                    if field[0] == 'F1L':
                        # print(field)
                        # self.vision[perceptor[1][1]].setFlag(perceptor[2][1:])
                        #上面这种写法竟然是错的，虽然逻辑是相同的，但是提示unhashable list,don't know why
                        # self.flag_distances['F1L'] = field[1]
                        self.visible_flags.append('F1L')
                        self.flag_distances['F1L'] = field[1][1]
                        # self.vision['F1L'].setMyFlag(perceptor[2][1:])
                    elif field[0] == 'F2L':
                        # print(field)
                        self.visible_flags.append('F2L')
                        self.flag_distances['F2L'] = field[1][1]
                        # self.vision['F2L'].setMyFlag(perceptor[2][1:])
                        # self.vision[perceptor[1][1]].setMyFlag(perceptor[2][1:])
                    elif field[0] == 'F1R':
                        self.visible_flags.append('F1R')
                        self.flag_distances['F1R'] = field[1][1]
                        # self.vision['F1R'].setMyFlag(perceptor[2][1:])
                        # self.vision[perceptor[1][1]].setMyFlag(perceptor[2][1:])
                    elif field[0] == 'F2R':
                        self.visible_flags.append('F2R')
                        self.flag_distances['F2R'] = field[1][1]
                        # self.vision['F2R'].setMyFlag(perceptor[2][1:])
                        # self.vision[perceptor[1][1]].setMyFlag(perceptor[2][1:])
                    elif field[0] == 'G1L':
                        self.visible_flags.append('G1L')
                        self.flag_distances['G1L'] = field[1][1]
                        # self.vision['G1L'].setMyFlag(perceptor[2][1:])
                        # self.vision[perceptor[1][1]].setMyFlag(perceptor[2][1:])
                    elif field[0] == 'G2L':
                        self.visible_flags.append('G2L')
                        self.flag_distances['G2L'] = field[1][1]
                        # self.vision['G2L'].setMyFlag(perceptor[2][1:])
                        # self.vision[perceptor[1][1]].setMyFlag(perceptor[2][1:])
                    elif field[0] == 'G1R':
                        # print(field)
                        self.visible_flags.append('G1R')
                        self.flag_distances['G1R'] = field[1][1]
                        # self.vision['G1R'].setMyFlag(perceptor[2][1:])
                        # self.vision[perceptor[1][1]].setMyFlag(perceptor[2][1:])
                    elif field[0] == 'G2R':
                        self.visible_flags.append('G2R')
                        self.flag_distances['G2R'] = field[1][1]
                        # self.vision['G2R'].setMyFlag(perceptor[2][1:])
                        # self.vision[perceptor[1][1]].setMyFlag(perceptor[2][1:])
                    elif field[0] == 'B':
                        self.visible_flags.append('B')
                        self.flag_distances['B'] = field[1][1]
                        # self.vision['B'].setMyFlag(perceptor[2][1:])
                        # self.vision[perceptor[1][1]].setBallLocation(perceptor[2][1:])

                    elif field[0] == 'team':
                        self.vision['team'].setTeamname(perceptor[2][1:])
                    elif field[0] == 'id':
                        self.vision['id'].setPlayerId(perceptor[2][1:])
                    # elif field[0] == 'P':
                    #     # if self.vision['P'].setPlayerLocation(perceptor[3][1:]) == None :
                    #     #     pass
                    #     # else:
                    #     print(self.vision['P'].setPlayerLocation(perceptor[4][1:]))

            #针对player这一块的信息解析来讲，是有问题的，幸好可以使用最后的排除方法。所以vison['p]标签本来是没什么用的及时解析到也没用，但可以用来存储player的位置信息
            #此处有错误，但不知问题出在哪里IndexError: list index out of range, 是不是因为没有player才导致呢？先注释掉试试

        

            # hinge joints
            elif perceptor[0] == 'HJ':
                self.hj[perceptor[1][1]] = perceptor[2][1]

            # force resistance perceptors
            elif perceptor[0] == 'FRP':
                self.frp[perceptor[1][1]].set(perceptor[2][1:], perceptor[3][1:])

            # unknown perceptor
            else:
                if self.debugLevel >= 10:
                    logger.warning("DEBUG: unknown perceptor: {}".format(perceptor[0]))
                    logger.warning(perceptor)


        # title = [y[0] for y in perceptors]
        # if "See" not in title:
        #     self.visible_flags = []    
         
# ==================================== #

    def check_sync(self):
        """Check if perceived time is in sync with real time
        Return True if so, else False
        检查时间是否同步"""

        realruntime = time.time() - self.realstarttime
        simruntime  = self.gamestate.get_time() - self.simstarttime

        cycleDiff = int((realruntime - simruntime) / CYCLE_LENGTH)
        return cycleDiff

# ==================================== #

    def rock_hj(self, hj, speed, minAngle, maxAngle):
        """Rock a hinge joint at the given speed between min and max degrees"""

        he = self.hjEffector[hj]
        speed = abs(speed)

        if abs(self.he[he]) < speed:
            self.pns.hinge_joint_effector(he, speed)
            self.he[he] = speed

        if self.hj[hj] > maxAngle and self.he[he] > 0:
            self.pns.hinge_joint_effector(he, -speed)
            self.he[he] = -speed
        elif self.hj[hj] < minAngle and self.he[he] < 0:
            self.pns.hinge_joint_effector(he,  speed)
            self.he[he] =  speed

        return "not done"

# ==================================== #

#    move_hj_to:移动关节到特殊角
#    move_hj_by:通过特殊角移动关节

# +++++++++++++++++++++++++++++++++++++++ #
    def move_hj_to(self, hj, angle=None, percent=None, speed=25):
        """Move the given hinge joint to the specified angle
        移动铰链关节达到特殊的角度
        The angle can be given in degree (angle=<degree>)
        角度的格式可以是度数angle=<degree>或者是百分比，
        or percent (percent=<percentage>). If both are specified, the angle keyword
        gets priority.
        如果两者都是特殊的，将被指定优先级
        Speed is specified in percent of maximum speed"""

        # get corresponding hinge effector
        he = self.hjEffector[hj]

        if angle == None and percent == None:
            raise Exception("Either angle or percent must be specified in move_hj_to()")
        elif angle != None:
            # just to give angle keyword priority over percent
            pass
        else:
            angle = self.hjMin[hj] + percent/100.0*(self.hjMax[hj]-self.hjMin[hj])
        
        if   angle > self.hjMax[hj]: angle = self.hjMax[hj]
        elif angle < self.hjMin[hj]: angle = self.hjMin[hj]
        if   speed > 100: speed = 100.0                             #即便如此，我发现当每次speed为>100和>>100的时候，机器人的运转还是不一样的
        elif speed < 0:   speed = 0.0

        speed = speed/100.0 * self.maxhjSpeed
        accuracy = 0.1
        diff  = self.hj[hj] - angle

        if abs(diff) <= accuracy:
            self.pns.hinge_joint_effector(he, 0.0)
            self.he[he] = 0.0
            if self.debugLevel > 20:
                print(hj, "done")
            return "done"

        if abs(speed) > abs(diff)/4.0:
            speed = abs(diff)/4.0

        if self.debugLevel > 20:
            print("hj: {}, he: {} target={:.2f}, current={:.2f}, diff={:.2f}, speed={:.2f}".format(hj, he, angle, self.hj[hj], diff, speed))

        if self.hj[hj] < angle:
            self.pns.hinge_joint_effector(he, abs(speed))
            self.he[he] = abs(speed) 
        elif self.hj[hj] > angle:
            self.pns.hinge_joint_effector(he, -abs(speed))
            self.he[he] = -abs(speed)

        return "not done"

# ==================================== #

    def move_hj_by(self, hj, angle=None, percent=None, speed=25):
        """Move the given hinge joint by the specified angle
        移动铰链关节通过给予特定的角度值
        The angle can be given in degree (angle=<degree>)
        or percent (percent=<percentage>). If both are specified, the angle keyword
        gets priority.
        Speed is specified in percent of maximum speed""" 

        if angle == None and percent == None:
            raise Exception("Either angle or percent must be specified in move_hj_by()")

        elif angle != None:
            # just to give angle keyword priority over percent
            pass

        else:
            angle = percent/100.0*(self.hjMax[hj]-self.hjMin[hj]) 

        targetAngle = self.hj[hj] + angle
        kwDict = {'hj': hj, 'angle': targetAngle, 'speed': speed}
        self.msched.append([self.move_hj_to, kwDict])

        return "done"

# ==================================== #

    def get_hj(self, hj):
        """Return hj value in percent
        返回铰链关节的百分比"""

        angle    = self.hj[hj]
        minAngle = self.hjMin[hj]
        maxAngle = self.hjMax[hj]

        percent  = 100.0 * (angle - minAngle) / (maxAngle - minAngle)

        return percent

# ==================================== #

    def step_left(self):
        """Make a step with the left foot
        迈左脚"""
        done = [False]
        print("ACC:", np.linalg.norm(self.acc.get()))
        #numpy.linalg.norm欧氏距离公式可以直接求空间中两点的距离,numpy.linalg.norm(a-b)    a,b分别存储一个三维坐标

        done[0] = False
#        self.msched.append([self.move_hj_to, {'hj': 'rlj3', 'percent': 50}, done])
#        self.msched.append([self.move_hj_to, {'hj': 'rlj4', 'percent': 50}, done])
        self.msched.append([self.move_hj_to, {'hj': 'rlj5', 'percent': 100}, done])
        self.msched.append([self.move_hj_to, {'hj': 'llj5', 'percent': 100}, done])

        self.test_orientation(0.1)              #orientation方向，定位


        # while not done[0]:
        #    print("ACC:", np.linalg.norm(self.acc.get()))
        #    print("GYR:", self.gyr.get())
        #    print(self.gyr.x)
        #    print(self.gyr.y)
        #    print(self.gyr.z)
        #    print("")
        #    time.sleep(0.05)
        #
        # time = time.time()
        # time.sleep(1.0)
        #
        # done[0] = False
        # self.msched.append([self.move_hj_to, {'hj': 'hj1', 'percent': 0}, done])
        # while not done[0]:
        #     pass
        # done[0] = False
        # self.msched.append([self.move_hj_to, {'hj': 'hj1', 'percent': 50}, done])
        # while not done[0]:
        #     pass

# ============================================================================ #