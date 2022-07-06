from Agent import *
from Action import *
from Think import *

class Nao3(NaoRobot):                    #longer legs and arms + wider hip Nao
    def __init__(self,agetID,teamname,startCoordinates=[]):
        NaoRobot.__init__(agentID=self.agentID, teamname=self.teamname, host='localhost', port=3100, model='rsg/agent/nao/nao_hetero.rsg 3', debugLevel=0,startCoordinates=self.startCoordinates)
    def Action(self):
        NaoAction = MyNao3Action

class MyNao3Action(Action):
    def __init__(self):
        pass