from collections import deque
import socket

class MovementScheduler(deque):
    """A queue for scheduling robot movements.
    动作调度： 用一个队列储存调度机器人的动作参数
    It guarantees that each function is scheduled only once at a time
    这确保它的每个功能都只能被调度一次
    to prevent conflicts with the potential of deadlocking the bot
    这阻止了潜在的死锁可能（为什么呢？参照事务～）"""

    def append(self, newitem):
        """The first element（元素） in the newitem list must be a function that gets called
        repeatedly until it returns 'done'.
        新指令(list)中的第一个元素是一个函数，可重复调用直到它返回‘done'
        The second element is a dictionary that contains the keyword arguments passed to the function.
         第二个元素是一个字典（包含了动作的关键参数），传递参数给函数
         The third item is optional and should contain a list (as the  simplest mutable datatype)
        whose zeroth element is set to true once the function contains 'done'
        to signal completion.
        第三部分是的参数是可选择的，它应该包含一个列表（简单易变的数据类型），包含一个确认指令（done）
        """
        # check proper format of item first 检查格式是否正确
        if not type(newitem) == list:
            raise QueueItemError("MovementQueue items must be lists.")
        elif not (len(newitem) == 2 or len(newitem) == 3):
            raise QueueItemError("MovementQueue items must be of format: [<function>, <kwargs dict>, <list>].")
        elif len(newitem) == 3 and type(newitem[2]) != list:
            raise QueueItemError("Third (optional) item to MovementQueue entries must be a list.")
        elif not callable(newitem[0]):
            raise QueueItemError("First item in list must be a function.")
        elif not type(newitem[1]) == dict:
            raise QueueItemError("MovementQueue items must be of format: [<function>, <kwargs dict>, <list>].")

        for item in self:
            function      = item[0]
            dictionary    = item[1]
            newFunction   = newitem[0]
            newDictionary = newitem[1]
            if function == newFunction and dictionary == newDictionary:
                try:
                    if dictionary['hj'] == newDictionary['hj']:
                        # two functions operating on the same hj not allowed
                        #两个函数都是操控同一个铰链关节是不允许的。（假如在多线程的情况下是不是可以？，难道非要把一整套的关节弄好输入到新的字典中？
                        raise SchedulerConflict('The function "{}" is already in the queue.'.format(item[0]))
                except KeyError:
                    SchedulerConflict.resue_socket_addr(host=3100)
                    #pass这并不是同用一个端口造成的，所有这个异常写的没有用



        super().append(newitem)

# ==================================== #

    def run(self):
        """Execute all functions currently in msched
        Reschedule if they are not done"""

        for i in range(len(self)):

            item     = self.popleft()
            function = item[0]
            argDict  = item[1]

            returnVal = function(**argDict)

            if returnVal != "done":
                self.append(item)
            elif len(item) == 3:
                item[2][0] = True


# ============================================================================ #
# General Perceptors :
                        # GyroRate Perceptor                  √
                        # HingeJoint Perceptor                √
                        # UniversalJoint Perceptor          --need--
                        # Touch Perceptor                   --need--
                        # ForceResistance Perceptor           √
                        # Accelerometer                       √
    
    

class QueueItemError(Exception):
    """Raised if an item to be schedule with the MovementScheduler
    has the wrong format"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    

class SchedulerConflict(Exception):
    """Raised upon trying to schedule a function that
    is already in the MovementScheduler
    调度冲突；"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

    def resue_socket_addr(self,port):
        resue_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        old_state = resue_socket.getsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR)
        print("Old State:%s" %old_state)

        resue_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        new_state = resue_socket.getsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR)
        print("New State: %s" %new_state)

        self.port = port

        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        srv.bind('',self.port)
        srv.listen(1)
        print("Listening On Port :%s " %self.port)

        while(True):
            try:
                connection,addr = srv.accept()
                print( "Connect by %s:%s" % (addr[0],addr[1]))
            except KeyboardInterrupt:
                break
           # except socket.error,msg:
           #      print("%s" %msg)