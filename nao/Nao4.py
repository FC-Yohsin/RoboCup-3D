from Agent import *
from Action import *
from Think import *

class Nao4(NaoRobot):                    # Nao toe
    def __init__(self,agetID,teamname,startCoordinates=[]):
        NaoRobot.__init__(agentID=self.agentID, teamname=self.teamname, host='localhost', port=3100, model='rsg/agent/nao/nao_hetero.rsg 4', debugLevel=0,startCoordinates=self.startCoordinates)

    def Action(self):
        NaoAction = MyNao4Action

class MyNao4Action(Action):                                                     #针对kick和walk的不同角度
    def __init__(self):
        pass