import imp
import numpy as np
from constants import CYCLE_LENGTH
from helper_function import HelperFunction


class Gyroscope(object):
    """Gyroscope perceptor holding information about the change in
    陀螺仪感受器手机信息关于所有的改变
    orientation of a body with respect to the global coordinate system
    在身体和方向等方面的全局坐标系统
    The rate of change is measured in deg/s
    """

    def __init__(self, name):
        self.name = name
        self.rate = np.zeros(3, dtype=np.float)

        # unit vectors of body with respect to global coordinate system
        self.x = np.array([1.0, 0.0, 0.0])
        self.y = np.array([0.0, 1.0, 0.0])
        self.z = np.array([0.0, 0.0, 1.0])

    def set(self, rate):
        for i in range(3):
            self.rate[i] = rate[i]

        # rotation in degree during the last cycle
        rotationAngle = np.linalg.norm(self.rate) / (1.0/CYCLE_LENGTH) 

        # rotate local coordinate frame
        #使用local坐标系
        self.x = HelperFunction.rotate_arbitrary(self.rate, self.x, angle=rotationAngle)
        self.y = HelperFunction.rotate_arbitrary(self.rate, self.y, angle=rotationAngle)
        self.z = HelperFunction.rotate_arbitrary(self.rate, self.z, angle=rotationAngle)

    def get_rate(self):
        return self.rate

    def get_orientation(self):
        return np.array([self.x, self.y, self.z])
    

# ============================================================================ #


class Accelerometer(object):
    """Accelerometer to measure the acceleration relative to free fall
    Will therefore indica]te 1g = 9.81m/s at rest in positive z direction
    计算相对于自由落体的加速度，因此以9.81m/s 在z轴正方向
    """

    def __init__(self, name):
        self.name = name
        self.acceleration = np.zeros(3, dtype=np.float)

    def set(self, acceleration):
        for i in range(3):
            self.acceleration[i] = acceleration[i]
        self.acceleration[i] -= 9.81

    def get(self):
        return self.acceleration


# ============================================================================ #


class ForceResistanceSensor(object):
    """Sensor state of a Force resistance perceptor
    point is the point of origin of the force
    force is the force vector
    力量抵抗感知器：一个位于原点的力的向量"""

    def __init__(self, name):
        self.name  = name
        self.point = np.zeros(3, dtype=np.float)
        self.force = np.zeros(3, dtype=np.float)

    def set(self, point, force):
        """Set the point of origin and the force
        Any 3 dimensional object that holds data convertible to float is valid
        设置原点和力，任何三维物体将数值转换为浮点型是有效的"""
        for i in range(3):
            self.point[i] = point[i]
            self.force[i] = force[i]

    def get_point(self):
        """get the point of origin coordinates
        得到原点坐标"""
        return self.point

    def get_force(self):
        """get the force vector"""
        return self.force

# ============================================================================ #
# 连个Vision都没有，玩你妹╮（╯＿╰）╭　
#  Soccer Perceptors:
                                    # Vision Perceptor          --need--        √ 2015/8/24
                                    # GameState Perceptor         √
                                    # Hear Perceptor           --need--
                                    # AgentState Perceptor     --need--         server 没有开启充电这一块的功能

# ============================================================================ #
#[name,[x,y,z]]
class Vision(object):
    def __init__(self,name):
        self.name = name
        self.flag= np.zeros(3, dtype=np.float)
        self.ballLocation = np.zeros(3, dtype=np.float)
        self.playerLocation = np.zeros(3, dtype=np.float)
        self.teamname = ''
        self.playerid = ''
        self.playerinfo = {'teamname':self.teamname,
                           'id':self.playerid,
                           'location' :self.playerLocation }

    def setMyFlag(self,hflag):
        for i in range(3):
            # self.flag[i] = flag
            self.flag = hflag
    def setBallLocation(self,ball):
        for i in range(3):
            self.ballLocation = ball

    def setPlayerLocation(self,hplayerLocation):
        for i in range(3):
            self.playerLocation = hplayerLocation

    def setPlayerId(self,unid):
        self.playerid = unid

    def setTeamname(self,unname):
        self.teamname = unname

    def getPlayerInfo(self):
        return self.playerinfo
    def getFlagLocation(self):
        return  self.flag
    def getBallLocation(self):
        return self.ballLocation
    def getPlayerLocation(self):
        return self.playerLocation
# =========================================================================== #

"""Actually the underlying model stems from the 2D Soccer Simulation and has been
integrated in the 3D simulator since server version 0.4."""

# (hear <time> ’self’|<direction> <message>)        ASCII[32-126] 20byter
#每个player每0.4s最多只能传递一条，并且不能对手也能听到
#这属于对未知数据进行划分，猜测和预测，是不是属于高级的机器学习算法呢？想想都和激动呢～～～
#思路：选取特征码，and不会了

class Hear(object):
    def __init__(self):
        pass