from MessageManagers.SendMessage import MessageSenderFactory
from CommandMessageGenerators.FileMessageGenerator import FileMessageGenerator
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator
from CommandMessageGenerators.DockerRunMessageGenerator import DockerRunMessageGenerator
from twisted.internet import reactor
from Utilities.Const import *

fact = MessageSenderFactory(StringMessageGenerator(COMMAND_SAYHELLO + LINEDELIM+COMMAND_SAYHELLO+LINEDELIM+COMMAND_LOSECONNECTION+LINEDELIM, None),None)

reactor.connectTCP(IPLOCATION, PORT, fact)
reactor.run()
