from Agent import *
from Action import *
from Think import *

class Nao1(NaoRobot):                    #Long legs and arms Nao
    def __init__(self,agetID,teamname,startCoordinates=[]):
        NaoRobot.__init__(agentID=self.agentID, teamname=self.teamname, host='localhost', port=3100, model='rsg/agent/nao/nao_hetero.rsg 1', debugLevel=0,startCoordinates=self.startCoordinates)
    def Action(self):
        NaoAction = MyNao1Action

class MyNao1Action(Action):
    def __init__(self):
        pass
