from agent import *
from agent.action import *
import time
import random
import matplotlib

if __name__ == '__main__':
    agent = NaoRobot(10,'Test','localhost',3100,'rsg/agent/nao/nao.rsg',startCoordinates=[-5.5,0.9,0],debugLevel=0, syncMode=False)