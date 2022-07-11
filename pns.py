import socket, struct
import os

class PNS(object):
    """Peripheral nervous system
    周围神经系统
    Creates socket connections to the simulation server.
    创建套接字连接到仿真服务器
    Sends effector messages.
    发送效应器消息
    Receives perceptor messages.
    接受感知器消息
    Upon creation the agent is registered with the server.
    一旦创建智能体，就向服务器注册
    """
    def __init__(self, agentID, teamname, host='localhost', port=3100,
            model='', debugLevel=10):

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

        # create socket and connect to simulation server
        #创建并连接到仿真服务器
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        # create and initialize agent
        #创建并初始化一个智能体
        self._send_effector('(scene {})'.format(self.model))
        self.receive_perceptors()
        self._send_effector('(init (unum {})(teamname {}))'.format(self.agentID, self.teamname))
        self.receive_perceptors()

# ==================================== #

    def _send_effector(self, message):
        """Each message is prefixed with the length of the payload message.
        每个消息命令都有一个前缀标识
        The length prefix is a 32 bit unsigned integer in network order
        这个在网络命令中的前缀标识是一个32位无符号整形
        """

        # report message
        if (self.debugLevel >= 10):
            print("S:", message)

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
        经由套接字从服务器接收消息"""

        message = b''
        while (len(message) < length):
            nextBytes = self.socket.recv(length - len(message))
            if (nextBytes == ''):
                # raise OSError('Socket to simulation server was closed')
                print("Socket to simulation server was closed")
                print("Starting Server Again...") # code for Optimization
                os.system('rcssserver3d')
            else:
                message += nextBytes

        return message

# ==================================== #

    def _parse_perceptors(self, perceptors):
        """Minimal parsing of perceptor message.
        Convert message to nested python lists, substituting '[' and ']'
        for '(' and ')'
        解析感知器信息，并存储到列表中--->把()内的内容转换为嵌套式的列表
        """

        return self.__str2list(perceptors)

#这个写的是真棒，所有东西最核心基础的地方
# ==================================== #

    def __str2list(self, string):
        """Convert a string to a (nested) python list, substituting '[' and ']'
        for '(' and ')'
        用列表存储接收到的字符串
        """
        
        l     = []
        bra   = '('
        ket   = ')'
        space = ' '
        nbra  = 0 # number of '('       左括号的数量
        nket  = 0 # number of ')'       右括号的数量

        nonword = [space, bra, ket]

        # begin and end indices of new sublist　　开始到结束之间一共有多少子表
        begin = 0
        end   = 0

        prevc = ''
        for i, c in enumerate(string):

            # detect word beginnings    探测开始字符
            if (i == 0 and c != bra):
                begin = i
            elif (nbra == 0 and c not in nonword and (prevc == bra or prevc == space)):
                begin = i

            # detect beginning of new nested list　　探测嵌入列表  (gyr (n torse) (pol x y z))
            elif (c == bra and nbra == nket):
                begin = i+1
            elif (c == ket and nbra == nket+1):
                end = i
                l.append(self.__str2list(string[begin:end]))

            # detect word endings       探测结束字符
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
        铰链关节效应器：通过提供关节名字，发送每周期的角速度的改变
        """
        message = "({} {:.2f})".format(name, rate)
        self._send_effector(message)

# ==================================== #

    def universal_joint_effector(self, name, rate1, rate2):
        """Set the change rate in degree/cycle of axis 1 and 2 of the
        普通关节的改变
        hinge joint with the provided name"""
        message = "({} {:.2f} {:.2f})".format(name, rate1, rate2)
        self._send_effector(message)

# ==================================== #

    def beam_effector(self, x, y, rotation):
        """Position the player on the field before the game starts
        and after a goal was scored.
        在比赛前和一方得分后初始化球员的位置
        Position and orientation of the team playing from right to left is
        point reflected at the center point.
        从右方到左方的球队的位置和方向反射自中心点
        x, y        Coordinates
        rotation旋转    horizontal orientation（水平方向） with respect to x-axis in degree"""
        message = "(beam {:.2f} {:.2f} {:.2f})".format(x, y, rotation)
        self._send_effector(message)

# ==================================== #

    def say_effector(self, message):
        """Broadcast a message to other agents.
        广播一个消息给其他智能体
        At most 20 ASCII characters are allowed
        最多20个字符
        white space and normal brackets are prohibited.
        空格和方括号是被禁止的（防注入?）"""
        if len(message) > 20:
            message = message[:20]
        for c in message:
            if (c == ' ' or c == '(' or c == ')'):
                print("Character not allowed for say effector: '{}'".format(c))
                print("Nothing sent.")
                return
        message = "(say {})".format(message)
        self._send_effector(message)