from twisted.internet import reactor, protocol

from MessageManagers.MessageDispatcher import MessageDispatcher
from Utilities.Const import *
from Utilities.FileUtil import expprint
import time

#this class will start a connection and send a message
#on top of the factory needed to let the super class
#handle the response to the message
#we also need a thing to generate the message we want
#to send.
class MessageSender(MessageDispatcher):

    def __init__(self, factory, messageGenerator, in_context):
        MessageDispatcher.__init__(self, factory, in_context)
        self.messagegen = messageGenerator

    #when a connection is made we 
    #read from the message generator and
    #write the message to send into the transport
    #until the generator is exhausted.
    def connectionMade(self):
        val = self.messagegen.read()
        firstmsg = val
        while(val != None):           
            print("type of val 1 ",type(val))
            expprint("SendMessage:"+str(val))
            dbgprint("SendMessage:Started sending msg:"+str(val))
            if val.find("ReceiveContainer") != -1:
                print("Found!")
                # print("before delay")
                # time.sleep(0.05)
            else:
                print ("Not found!")
            self.transport.write(val.encode('utf-8'))
            print("type of val 2 ",type(val))
            val = self.messagegen.read()
            print("type of val 3 ",type(val))
        
            
        dbgprint("SendMessage: Val is none")
        if(self.messagegen.OneShot()):
            dbgprint("SendMessage: Lose Conn! first send:"+str(firstmsg))
            self.transport.loseConnection()
 
class MessageSenderFactory(protocol.ClientFactory):

    def __init__(self, generator, in_context):
        self.generator = generator
        self.context = in_context
        self.numProtocols = 0

    def startedConnecting(self, connector):
        dbgprint("Started to connect.")

    def buildProtocol(self, addr):
        dbgprint("Connected")
        return MessageSender(self, self.generator, self.context)
    
    def clientConnectionFailed(self, connector, reason):
        dbgprint("Connection failed - goodbye!" + str(reason))
        self.generator.setBadFinish()
    
    def clientConnectionLost(self, connector, reason):
        dbgprint("Connection lost - goodbye!" + str(reason))
        #self.generator.setGoodFinish()

