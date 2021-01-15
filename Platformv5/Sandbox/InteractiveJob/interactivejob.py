from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
import time

from CommandMessageGenerators.MessageRepeat import MsgMonitor
from MessageManagers.MessageDispatcher import MessageDispatcherFactory
from JobLock import JobLock
from simplematmul import runmatmul
from Utilities.Const import dbgprint
from twisted.python.compat import xrange

class ijob():

    def __init__(self):
        self.msgmon = MsgMonitor()
        self.thelock = JobLock()
        self.ready = False
        self.jobdef = None
        self.remaining_reqs = []
        self.remaining_obls = []
        self.idval = ""

    def define(self, in_jobdef):
        self.jobdef = in_jobdef
        self.remaining_reqs = self.jobdef.req_ids[:]
        self.remainings_obls = self.jobdef.oblig_ids[:]
        
    def ServerThreadRun(self):
        endpoint = TCP4ServerEndpoint(reactor, self.Port)
        endpoint.listen(MessageDispatcherFactory(self))
        dbgprint("server starting...")
        reactor.run(installSignalHandlers=0)

    def JobThreadRun(self):
        
        self.blockReqsDone()
    
        runmatmul()

        self.blockSendObligations()

    def blockSendObligations(self):
        while(len(self.remaining_obls) > 0):
            for i in reversed(xrange(len(self.remaining_obls))):
                self.sendObligation(self.remaining_obls[i])
            
            time.sleep(5)

    def blockAreReqsDone(self):
        while(len(self.remaining_reqs) > 0):
            time.sleep(5)

    #so what I need to do is
    #.  1.  take my own lock, if this fails exit
    #.  2.  request target's lock
    #     a.if this fails, release own lock exit
    #   3.  send message
    #   seperately, reader that recieves ack
    #   should release the lock.
    def sendObligation(self, oid):
        lockkey = oid + "sendoblig"
        if(self.thelock.is_there_a_lock(lockkey)):
            return
        else:
            self.thelock.incllock(lockkey)
        obligmg = SendObligMG(self, self.idval)
        oip = self.jobdef.oblig_map[oid].ip
        oport = self.jobdef.oblig_map[oid].port
        self.msgmon.sendGen(obligmg, oip, oport)
