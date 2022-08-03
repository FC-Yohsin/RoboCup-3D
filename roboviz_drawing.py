from cmath import log
from distutils.command.build import build
from pns import PNS
from enum import Enum
from logger import logger
import socket


class HeaderType(Enum):
    """
    Enum for the buffer header types
    """
    ANNOTATION = (2,0)
    DRAW_CIRCLE = (1,0)
    DRAW_LINE = (1,1)
    AGENT_ANNOTATION = (2,1)
    CLEAR_ANNOTATION = (2,2)
    

class RobovizDrawing:
    
    def __init__(self) -> None:
        self.PORT = 3300
        self.HOST = 'localhost'
        self.defaultColor = (255, 255, 255)
        self.defaultThickness = 2.0
        
    
    def __sendMessage(self, message, size) -> None:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            bytesSent = 0
            while (bytesSent < size):
                bytesSent += sock.sendto(message[bytesSent:], (self.HOST, self.PORT))
            logger.info("Command sent to Roboviz Drawing Server")
        except socket.error as err:
            logger.error("Cannot connect to Roboviz Drawing Server:" + str(err))
    
    
    def __swapBuffer(self, buffer: bytearray, setName: str) -> None:
        buffer.append(0)
        buffer.append(0)
        buffer.extend(list(map(ord, setName)))
        buffer.append(0)
        
    
    def __floatToBuffer(self, buffer: bytearray, value: float) -> None:
        buffer.extend((str(value).ljust(6, '0')).encode('ASCII'))
        
    
    def __colorToBuffer(self, buffer: bytearray, color: tuple) -> None:
        buffer.append(color[0])
        buffer.append(color[1])
        buffer.append(color[2])


    def __strToBuffer(self, buffer: bytearray, text: str) -> None:
        buffer.extend(list(map(ord, text)))
        buffer.append(0)
    
    
    def __headerToBuffer(self, buffer: bytearray, header: HeaderType) -> None:
        buffer.append(header.value[0])
        buffer.append(header.value[1])
    
            
    def addAnnotation(self, text: str, position: tuple, setName: str, color: tuple=(255,255,255)) -> None:
        buffer = bytearray(0)
        
        self.__headerToBuffer(buffer, HeaderType.ANNOTATION)
        self.__floatToBuffer(buffer, position[0])
        self.__floatToBuffer(buffer, position[1])
        self.__floatToBuffer(buffer, position[2])
        self.__colorToBuffer(buffer, color)
        self.__strToBuffer(buffer, text)
        self.__strToBuffer(buffer, setName)
        
        # swapping buffer
        self.__swapBuffer(buffer, setName)
        
        self.__sendMessage(bytes(buffer), len(buffer))
        
        
    def drawCircle(self, center: tuple, radius: float, setName: str, color: tuple=(255,255,255), thickness: float=2.0) -> None:
        buffer = bytearray(0)
        
        self.__headerToBuffer(buffer, HeaderType.DRAW_CIRCLE)
        self.__floatToBuffer(buffer, center[0])
        self.__floatToBuffer(buffer, center[1])
        self.__floatToBuffer(buffer, radius)
        self.__floatToBuffer(buffer, thickness)
        self.__colorToBuffer(buffer, color)
        buffer.extend(list(map(ord, setName)))
        buffer.append(0)
        
        # swap buffers
        self.__swapBuffer(buffer, setName)
        
        self.__sendMessage(bytes(buffer), len(buffer))
        
    
    def drawLine(self, pointA: tuple, pointB: tuple, setName: str, color: tuple=(255,255,255), thickness: float=2.0)-> None:
        buffer = bytearray(0)
        
        self.__headerToBuffer(buffer, HeaderType.DRAW_LINE)
        self.__floatToBuffer(buffer, pointA[0])
        self.__floatToBuffer(buffer, pointA[1])
        self.__floatToBuffer(buffer, pointA[2])
        self.__floatToBuffer(buffer, pointB[0])
        self.__floatToBuffer(buffer, pointB[1])
        self.__floatToBuffer(buffer, pointB[2])
        self.__floatToBuffer(buffer, thickness)
        self.__colorToBuffer(buffer, color)
        self.__strToBuffer(buffer, setName)
        
        # swap buffers
        self.__swapBuffer(buffer, setName)
        
        self.__sendMessage(bytes(buffer), len(buffer))
        
    
    def addAgentAnnotation(self, text: str, agentNum: int, opponent: bool=False, color: tuple=(255,255,255))->None:
        buffer = bytearray(0)
        
        self.__headerToBuffer(buffer, HeaderType.AGENT_ANNOTATION)
        
        # if not opponent:
        buffer.append(agentNum - 1)
        # else:
        #     buffer.append(agentNum + 127)
        
        self.__colorToBuffer(buffer, color)
        self.__strToBuffer(buffer, text)
        
        self.__sendMessage(bytes(buffer), len(buffer))
        
    
    def clearAgentAnnotation(self, agentNum: int):
        buffer = bytearray(0)
        
        self.__headerToBuffer(buffer, HeaderType.CLEAR_ANNOTATION)
        buffer.append(agentNum - 1)
        
        self.__sendMessage(bytes(buffer), len(buffer))