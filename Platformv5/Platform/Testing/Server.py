import threading
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from MessageManagers.MessageDispatcher import MessageDispatcher, MessageDispatcherFactory
from Utilities.Const import *


def ServerListen():
    from Utilities.Const import *
    # 8007 is the port, choo >1024
    endpoint = TCP4ServerEndpoint(reactor, PORT)
    endpoint.listen(MessageDispatcherFactory(None))
    reactor.run(installSignalHandlers=0)

t = threading.Thread(target=ServerListen)
t.start()
print "Server Running"
