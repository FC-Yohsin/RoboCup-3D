class GameState(object):
    """Store game state information"""

    def __init__(self, time=0.0, gametime=0.0, scoreLeft=0, scoreRight=0,
            playmode='BeforeKickOff'):
        self.time       = time
        self.gametime   = gametime
        self.scoreLeft  = scoreLeft
        self.scoreRight = scoreRight
        self.playmode   = playmode

# ==================================== #

    def set_time(self, time):
        self.time       = time
    def set_gametime(self, gametime):
        self.gametime   = gametime
    def set_scoreLeft(self, scoreLeft):
        self.scoreLeft  = scoreLeft
    def set_scoreRight(self, scoreRight):
        self.scoreRight = scoreRight
    def set_playmode(self, playmode):
        self.playmode   = playmode 

    def get_time(self):
        return self.time
    def get_gametime(self):
        return self.gametime
    def get_scoreLeft(self):
        return self.scoreLeft
    def get_scoreRight(self):
        return self.scoreRight
    def get_playmode(self):
        return self.playmode

# ==================================== #
    
    def __str__(self):
        string = ""
        string += "time       = {}\n".format(self.time      )
        string += "gametime   = {}\n".format(self.gametime  )
        string += "scoreLeft  = {}\n".format(self.scoreLeft )
        string += "scoreRight = {}\n".format(self.scoreRight)
        string += "playmode   = {}"  .format(self.playmode  )
        return string