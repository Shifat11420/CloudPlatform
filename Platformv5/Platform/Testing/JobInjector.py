from MessageManagers.SendMessage import MessageSenderFactory
from DockerManagers.SubContManager import ContainerManager
from PlatformManager import PlatformManager
from CommandMessageGenerators.ContainerMessageGenerator import ContainerMessageGenerator
from twisted.internet import reactor
from Utilities.Const import *
from Utilities.FileInputTokenize import FIP
from Utilities.FileUtil import OUTFOLDER, SetOutputFolder
import threading
import uuid

class JobInjector():
    def __init__(self):
        self.pm = None
    
    def run(self):
        fopen = FIP('InputFiles/InjectContainer.dat')

        source_ip = str(fopen.read())
        dbgprint(source_ip)
        port = int(fopen.read())
        dbgprint(str(port))
        SetOutputFolder(fopen.read())
        dbgprint(OUTFOLDER)

        cont_args = str(fopen.read())
        cont_files = []
        num_files = int(fopen.read())

        for x in range(0,num_files):
            a_file = str(fopen.read())
            cont_files.append(a_file)

        idstr = str(uuid.uuid4())

        self.pm = PlatformManager(source_ip, port, workInjectorMode=True)
        self.pm.StartAll()

        cont = ContainerManager(cont_args, cont_files, idstr, source_ip, port, self.pm)

        cont_msg_gen = ContainerMessageGenerator(cont, self.pm)

        fact = MessageSenderFactory(cont_msg_gen,self.pm)

        target_ip = str(fopen.read())
        dbgprint(target_ip)
        target_port = int(fopen.read())
        dbgprint(str(target_port))

        reactor.callFromThread(self.inReactorConnect, target_ip, target_port, fact)

    def inReactorConnect(self, target_ip, target_port, fact):
        reactor.connectTCP(target_ip, target_port, fact)

