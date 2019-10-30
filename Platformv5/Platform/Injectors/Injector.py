from PlatformManager import PlatformManager
from MessageManagers.SendMessage import MessageSenderFactory
from twisted.internet import reactor
from Utilities.Const import *
from Utilities.FileUtil import SetOutputFolder

class Injector():
    def __init__(self, odict):

        self.source_ip = str(odict[DICT_SOURCE_IP])
        self.source_port = int(odict[DICT_SOURCE_PORT])
        self.target_ip = str(odict[DICT_TARGET_IP])
        self.target_port = int(odict[DICT_TARGET_PORT])
        SetOutputFolder(odict[DICT_FOLDER])

        self.pm = PlatformManager(self.source_ip, self.source_port, ManagerOn=False)

    def SetMsgGen(self, a_msg_gen):
        self.msggen = a_msg_gen

    def run(self):
        self.pm.StartAll()

        fact = MessageSenderFactory(self.msggen, self.pm)
        reactor.callFromThread(self.InReactorConnect, fact)

    def InReactorConnect(self, fact):
        reactor.connectTCP(self.target_ip, self.target_port, fact)
    
