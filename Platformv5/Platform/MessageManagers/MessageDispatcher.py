from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.protocols.basic import LineReceiver
from Utilities.Const import *
from CommandReaders.ReaderFactory import ReaderFactory

#This class will handle received messages
#it is extended by MessageSender in SendMessage.py
#for the ability to send a message and
#handle a received response.
class MessageDispatcher(LineReceiver):

    #The factory will parse initial command lines
    #from TCP to determine what kind of handler
    #to construct
    def __init__(self, factory, in_context):
        self.factory = factory
        self.messagehandler = None
        self.ReaderFactory = ReaderFactory(in_context)

    #Not much beyond the default here.
    def connectionMade(self):
        self.factory.numProtocols = self.factory.numProtocols + 1

    #Not much beyond default here.
    def connectionLost(self, reason):
        self.factory.numProtocols = self.factory.numProtocols - 1

    #If we receive a line we check and see if
    #there is an active messagehandler
    #if so then that will handle lines
    #once it handles a line we check and see if 
    #it is done.  If so, it can designate a
    #successor that will handle subsequent lines
    #if it doesn't designate a successor then
    #self.messagehandler will be set to None again
    #and the next message will be parsed by the factory
    #to create a new handler.
    def lineReceived(self, line):
        #from Utilities.Const import *               ##
        #dbgprint("LineReceived:"+str(line))
        if(self.messagehandler == None):
            self.messagehandler = self.ReaderFactory.buildMessageHandler(line)
        if(self.messagehandler == None):
            dbgprint ("ERROR:Unable to build reader for line:"+line)
            return
        self.messagehandler.HandleLine(line)
        if(self.messagehandler.IsFinished()):
            if(self.messagehandler.SetToRaw()):
                self.setRawMode()

            self.messagehandler.WriteResponse(self.transport)
            if(self.messagehandler.LoseConnection()):
                self.transport.loseConnection()
            self.messagehandler = self.messagehandler.GetNextHandler()

    #If a raw message needs to be handled
    #we must first receive and handle a line message
    #defining it, and create a raw handler
    #successor, and switch to raw, in the lineReceived.
    #if we are in raw mode without a handler
    #we are in an error state.
    #I don't support multiple sequential raw
    #handlers atm.
    def rawDataReceived(self, data):
        #dbgprint("Raw Received:"+str(data))
        if(self.messagehandler == None):
            #Error
            dbgprint("Raw data being received by no handler")
        else:
            self.messagehandler.HandleLine(data)
            if(self.messagehandler.IsFinished()):
                if(not self.messagehandler.SetToRaw()):
                    self.setLineMode(self.messagehandler.GetRemainder())
                else:
                    #Error
                    dbgprint("Cannot have two raw handlers in a row")
                self.messagehandler.WriteResponse(self.transport)
                if(self.messagehandler.LoseConnection()):
                    self.transport.loseConnection()
                self.messagehandler = self.messagehandler.GetNextHandler()

class MessageDispatcherFactory(Factory):
    def __init__(self, in_context):
        self.numProtocols = 0
        self.context = in_context
    def buildProtocol(self, addr):
        return MessageDispatcher(self, self.context)    

