import socket, struct
from logger import logger
import os

class PNS(object):
    
    """Peripheral nervous system
    Creates socket connections to the simulation server.
    Sends effector messages.
    Receives perceptor messages.
    Upon creation the agent is registered with the server.
    """
    
    def __init__(self, agentID, teamname, host='localhost', port=3100,
            model='', debugLevel=10, syncMode=False):

        """='rsg/agent/nao/nao.rsg'
        other model:(scene rsg/agent/nao/nao_hetero.rsg 0)
        (scene rsg/agent/nao/nao_hetero.rsg 1)
        (scene rsg/agent/nao/nao_hetero.rsg 2)
        (scene rsg/agent/nao/nao_hetero.rsg 3)
        (scene rsg/agent/nao/nao_hetero.rsg 4)
        :rtype : object
        """
        self.agentID    = agentID
        self.teamname   = teamname
        self.host       = host
        self.port       = port
        self.model      = model
        self.debugLevel = debugLevel
        self.syncMode = syncMode
        
        # create socket and connect to simulation server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        # create and initialize agent
        self._send_effector('(scene {})'.format(self.model))
        self.receive_perceptors()
        self._send_effector('(init (unum {})(teamname {}))'.format(self.agentID, self.teamname))
        self.receive_perceptors()

# ==================================== #

    def _send_effector(self, message):
        """Each message is prefixed with the length of the payload message.
        每个消息命令都有一个前缀标识
        The length prefix is a 32 bit unsigned integer in network order
        """

        # if syncMode is ON, append (sync) to the end
        if self.syncMode:
            message += "(syn)"
        
        # report message
        if (self.debugLevel >= 10):
            logger.info("S:", message)

        # convert message to ASCII encoded byte string
        length   = len(message)
        bmessage = bytes(message, 'ASCII')
        

        # send length of message
        lengthMessage = struct.pack("!I", length)
        bytesSent = 0
        while (bytesSent < 4):
            bytesSent += self.socket.send(lengthMessage[bytesSent:])

        # send actual message
        bytesSent = 0
        while (bytesSent < length):
            bytesSent += self.socket.send(bmessage[bytesSent:])

# ==================================== #

    def receive_perceptors(self):

        # receive length of the message (4 bytes)
        length = self._receive_message(4)
        length = struct.unpack("!I", length)[0]

        # receive actual message
        perceptors = self._receive_message(length)
        perceptors = str(perceptors, 'ASCII')

        return self._parse_perceptors(perceptors)
    
# ==================================== #

    def _receive_message(self, length):
        """Receive a message from server communication socket of given length
        """

        message = b''
        while (len(message) < length):
            nextBytes = self.socket.recv(length - len(message))
            if (nextBytes == ''):
                # raise OSError('Socket to simulation server was closed')
                logger.info("Socket to simulation server was closed")
                logger.info("Starting Server Again...") # code for Optimization
                os.system('rcssserver3d')
            else:
                message += nextBytes

        return message

# ==================================== #

    def _parse_perceptors(self, perceptors):
        """Minimal parsing of perceptor message.
        Convert message to nested python lists, substituting '[' and ']'
        for '(' and ')'
        """

        return self.__str2list(perceptors)

# ==================================== #

    def __str2list(self, string):
        """Convert a string to a (nested) python list, substituting '[' and ']'
        for '(' and ')'
        """
        
        l     = []
        bra   = '('
        ket   = ')'
        space = ' '
        nbra  = 0 # number of '('       
        nket  = 0 # number of ')'       
        nonword = [space, bra, ket]

        # begin and end indices of new sublist　　        begin = 0
        end   = 0

        prevc = ''
        for i, c in enumerate(string):

            # detect word beginnings    
            if (i == 0 and c != bra):
                begin = i
            elif (nbra == 0 and c not in nonword and (prevc == bra or prevc == space)):
                begin = i

            # detect beginning of new nested list　　 (gyr (n torse) (pol x y z))
            elif (c == bra and nbra == nket):
                begin = i+1
            elif (c == ket and nbra == nket+1):
                end = i
                l.append(self.__str2list(string[begin:end]))

            # detect word endings       
            if (i == len(string)-1 and c != ket):
                word = string[begin:]
                try: word = int(word)
                except:
                    try: word = float(word)
                    except: pass
                l.append(word)
            if (c == space and nbra == 0 and prevc not in nonword):
                end = i
                word = string[begin:end]
                try: word = int(word)
                except:
                    try: word = float(word)
                    except: pass 
                l.append(word)
 

            if (c == bra): nbra += 1
            if (c == ket): nket += 1

            prevc = c
                
        # return
        if len(l) == 1:
            return l[0]
        else:
            return l

# ==================================== #

    def hinge_joint_effector(self, name, rate):
        """Set the change rate in degree/cycle of the
        hinge joint with the provided name
        """
        message = "({} {:.2f})".format(name, rate)
        self._send_effector(message)

# ==================================== #

    def universal_joint_effector(self, name, rate1, rate2):
        """Set the change rate in degree/cycle of axis 1 and 2 of the
        hinge joint with the provided name"""
        message = "({} {:.2f} {:.2f})".format(name, rate1, rate2)
        self._send_effector(message)

# ==================================== #

    def beam_effector(self, x, y, rotation):
        """Position the player on the field before the game starts
        and after a goal was scored.
        Position and orientation of the team playing from right to left is
        point reflected at the center point.
        x, y        Coordinates
        rotation    horizontal orientation with respect to x-axis in degree"""
        message = "(beam {:.2f} {:.2f} {:.2f})".format(x, y, rotation)
        self._send_effector(message)

# ==================================== #

    def say_effector(self, message):
        """Broadcast a message to other agents.
        At most 20 ASCII characters are allowed
        white space and normal brackets are prohibited.
        """
        if len(message) > 20:
            message = message[:20]
        for c in message:
            if (c == ' ' or c == '(' or c == ')'):
                logger.warning("Character not allowed for say effector: '{}'".format(c))
                logger.warning("Nothing sent.")
                return
        message = "(say {})".format(message)
        self._send_effector(message)