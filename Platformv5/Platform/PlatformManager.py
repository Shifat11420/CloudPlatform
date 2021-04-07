from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from MessageManagers.MessageDispatcher import MessageDispatcherFactory
from MessageManagers.SendMessage import MessageSenderFactory
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from CommandMessageGenerators.MessageRepeat import MsgMonitor
from CommandMessageGenerators.ExpMessageGenerator import ReceiveExpNode
from Utilities.Const import *
from Utilities.FileInputTokenize import ArgFIP
from Utilities.FileUtil import expprint, setFileName, OUTFOLDER, getDFilePath, getPFilePath
import threading
import time
import sys
import uuid

class outgoer():
    def __init__(self, ip, port, fact):
        self.ip = ip
        self.port = port
        self.fact = fact

    def call(self):
        reactor.connectTCP(self.ip, self.port, self.fact)

class PlatformManager():
    def __init__(self, in_my_IP, in_my_Port, location):
        self.IP = in_my_IP
        self.Port = in_my_Port
        self.reactorFileConfirmers = []
        self.msgmon = MsgMonitor()
        self.idval = str(uuid.uuid4())
        setFileName(self.idval)
        self.templogfilenames = []
        self.location = location

    def ManagerThreadRun(self):
        dbgprint("bad way")
        raise NotImplementedError("Abstract method")

    def StartAll(self):
        self.StartServer()
        self.StartManager()
    def StartServer(self):
        #from Utilities.Const import *                          ##
        self.serverThread = threading.Thread(target=self.ServerThreadRun)
        self.serverThread.start()
    def StartManager(self):
        #from Utilities.Const import *                            ##
        dbgprint("starting mngr")
        self.managerThread = threading.Thread(target=self.ManagerThreadRun)
        self.managerThread.start()

    def SafeStopServer(self):
        dbgprint("SafeStopCalled")
        reactor.callFromThread(reactor.stop)
        self.msgmon.terminate()

    def ServerThreadRun(self):

        endpoint = TCP4ServerEndpoint(reactor, self.Port)
        endpoint.listen(MessageDispatcherFactory(self))
        dbgprint("server starting...")
        reactor.run(installSignalHandlers=0)

    def ReactorReceiverAdd(self, filerec):
        dbgprint("added filerec")
        self.reactorFileConfirmers.append(filerec)

    def ReactorFileSent(self, filename, transp):
        dbgprint("Reactor File Sent")
        self.reactorFileConfirmers[:] = [x for x in self.reactorFileConfirmers if x.FileResponded(filename, transp)]

    def storeLog(self, vals):
        afilename = str(uuid.uuid4())
        v = vals.replace("\t", "\n")    
        if(afilename in self.templogfilenames):
            expprint("BADFILENAME!!")
        self.templogfilenames.append(afilename)
        with open(afilename, 'w') as afile:
            afile.write(v)

    def compilelogs(self):
        expprint("Compiling " + str(len(self.templogfilenames)) + " logs\n")
        for filename in self.templogfilenames:
            if(self.templogfilenames.count(filename) > 1):
                expprint("found dup\n");
        for filename in self.templogfilenames:
            with open(filename, 'r') as afile:
                for line in afile:
                    expprint(line +"\n")
            os.remove(filename)
        dbgprint("Logs Compiled To "+OUTFOLDER+str(self.idval))

    def dumpLogToStdOut(self):
        filename = OUTFOLDER+"/"+str(self.idval)
        with open(filename, 'r') as afile:
            for line in afile:
                print (line + "\n")                           ##

    def getPFileName(self):
        return getPFilePath()

    def getDFileName(self):
        return getDFilePath()
