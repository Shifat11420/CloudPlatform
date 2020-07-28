from CommandMessageGenerators.GeneratorFactory import MakeGen
from MessageManagers.SendMessage import MessageSenderFactory
import threading
from twisted.internet import reactor
from time import sleep
from Utilities.Const import *

class MsgMonitor():
    def __init__(self):
        from Utilities.Const import *   
        self.msgs = []
        self.monlock = threading.Lock()
        self.done = False
        self.monthread = threading.Thread(target=self.monitor)
        self.monthread.start()

    def terminate(self):
        self.done = True

    def sendCommand(self, command, context, ip, port):
	gen = MakeGen(command, context)
	self.sendGen(gen, ip, port)

    def sendGen(self, msg, ip, port):
        #msgprint("CHECK2"+str(msg.__class__.__name__))
        #msgprint("MON-sendGen")
        msg.ip = ip
        msg.port = port
        reactor.callFromThread(self.resendMsg, msg)
        with self.monlock:
            self.msgs.append(msg)

    def resendMsg(self, msg):
        msf = MessageSenderFactory(msg, msg.context)
        dbgprint("resendMsg:"+str(msg.ip)+":"+str(msg.port))
        
        reactor.connectTCP(msg.ip, int(msg.port), msf)

    def monitor(self):
        while not self.done:
            sleep(10)
            with self.monlock:
                lone = len(self.msgs)
                self.msgs = [x for x in self.msgs if not (x.state == 1)]
                if(lone != len(self.msgs)):
                    pass
                    #msgprint("MON-succeeded at " + str(lone - len(self.msgs)))
                for msg in self.msgs:
                    if msg.state == 2:
                        #msgprint("MON-reset")
                        msg.reset()
                        reactor.callFromThread(self.resendMsg, msg)
