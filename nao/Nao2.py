from Agent import *
from Action import *
from Think import *

class Nao２(NaoRobot):                    #faster ankle-pitch and slower ankle-roll speed Nao
    def __init__(self,agetID,teamname,startCoordinates=[]):
        NaoRobot.__init__(agentID=self.agentID, teamname=self.teamname, host='localhost', port=3100, model='rsg/agent/nao/nao_hetero.rsg 2', debugLevel=0,startCoordinates=self.startCoordinates)

    def Action(self):
        NaoAction = MyNao2Action

class MyNao2Action(Action):
    def __init__(self):
        pass
