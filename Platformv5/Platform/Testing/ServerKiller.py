from MessageManagers.SendMessage import MessageSenderFactory
from DockerManagers.SubContManager import ContainerManager
from PlatformManager import PlatformManager
from CommandMessageGenerators.ContainerMessageGenerator import ContainerMessageGenerator
from CommandMessageGenerators.MessageGenerator import EndServerMessageGenerator
from twisted.internet import reactor
from Utilities.Const import *
from Utilities.FileUtil import OUTFOLDER, SetOutputFolder
from Utilities.FileInputTokenize import FIP
import threading
import uuid

class ServerKiller():
    def __init__(self, target_ip, target_port):
        self.pm = None
        self.target_ip = target_ip
        self.target_port = int(target_port)
    
    def run(self):
        fopen = FIP('InputFiles/InjectContainer.dat')

        source_ip = str(fopen.read())
        dbgprint(source_ip)
        port = int(fopen.read())
        dbgprint(str(port))
        SetOutputFolder(fopen.read())
        dbgprint(OUTFOLDER)

        self.pm = PlatformManager(source_ip, port, workInjectorMode=True)
        self.pm.StartAll()

        es_msggen = EndServerMessageGenerator(self.pm)

        fact = MessageSenderFactory(es_msggen,self.pm)

        reactor.callFromThread(self.inReactorConnect, self.target_ip, self.target_port, fact)

    def inReactorConnect(self, target_ip, target_port, fact):
        reactor.connectTCP(target_ip, target_port, fact)

