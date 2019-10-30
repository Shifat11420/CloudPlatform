from twisted.internet import reactor, protocol
from CommandMessageGenerators.AskForWork import AskForWork
from CommandMessageGenerators.ExpMessageGenerator import ReceiveExpNode
from CommandMessageGenerators.LogMsgGen import SendLogMsgGen
from CommandMessageGenerators.MessageGenerator import TerminateMessageGenerator, EndServerMessageGenerator
from MessageManagers.SendMessage import MessageSender
from Utilities.Const import *

def MakeGen(cmd, context):
    gen = None
    if(cmd == COMMAND_ASKFORWORK):
        gen = AskForWork(context)
    if(cmd == COMMAND_SENDLOGS):
        gen = SendLogMsgGen(context)
    if(cmd == COMMAND_TERMINATE):
        gen = TerminateMessageGenerator(context)
    if(cmd == COMMAND_ENDSERVER):
        gen = EndServerMessageGenerator(context)
    if(gen != None):
        return gen
    return None


