from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import MessageGenerator, StringMessageGenerator

class TGQueueMG(StringMessageGenerator):
    def __init__(self, in_context, idval, tqueueinfo):
        strmsg = COMMAND_RECEIVETGQUEUEINFO
        strmsg += COMMA + str(idval)
        for key in tqueueinfo:
            strmsg += COMMA + str(key) + COMMA + str(tqueueinfo[key])
        StringMessageGenerator.__init__(self, strmsg, in_context)

class RequirementSetMG(StringMessageGenerator):
    def __init__(self, in_context, fromtaskid,totaskid, fnames):
        strmsg = COMMAND_RECEIVEREQSET
        strmsg += COMMA + TASKID
        strmsg += COMMA + fromtaskid
        strmsg += COMMA + totaskid
        strmsg += COMMA + FILENAMES
        for fname in fnames:
            strmsg += COMMA + fname
        StringMessageGenerator.__init__(self, strmsg, in_context) 

class DYNTaskObligMG(StringMessageGenerator):
    def __init__(self, in_context, taskid, fname):
        strmsg = COMMAND_DYNTASKOBLIG
        strmsg = strmsg + COMMA
        strmsg = strmsg + TASKID
        strmsg = strmsg + COMMA
        strmsg = strmsg + taskid
        strmsg = strmsg + COMMA
        strmsg = strmsg + FILENAME
        strmsg = strmsg + COMMA
        strmsg = strmsg + fname
        StringMessageGenerator.__init__(self, strmsg, in_context)

    def OneShot(self):return False

class IHaveObligMG(StringMessageGenerator):
    def __init__(self, in_context, taskid, fname):
        strmsg = COMMAND_IHAVEOBLIG
        strmsg = strmsg + COMMA
        strmsg = strmsg + TASKID
        strmsg = strmsg + COMMA
        strmsg = strmsg + taskid
        StringMessageGenerator.__init__(self, strmsg, in_context)

class INeedObligMG(StringMessageGenerator):
    def __init__(self, in_context, taskid, fname):
        strmsg = COMMAND_INEEDOBLIG
        strmsg = strmsg + COMMA
        strmsg = strmsg + TASKID
        strmsg = strmsg + COMMA
        strmsg = strmsg + taskid
        StringMessageGenerator.__init__(self, strmsg, in_context)

    def OneShot(self):return False


class LocMG(StringMessageGenerator):
    def __init__(self, in_context, aip, aport, ataskid, aindex):
        strmsg = COMMAND_TASKLOCATION
        strmsg += COMMA + STR_IP + COMMA + aip
        strmsg += COMMA + STR_PORT + COMMA + str(aport)
        strmsg += COMMA + TASKID + COMMA + ataskid
        strmsg += COMMA + INDEX + COMMA + str(aindex)
        dbgprint("LocMG:"+strmsg.__class__.__name__)
        StringMessageGenerator.__init__(self, strmsg, in_context)

class LinkMG(StringMessageGenerator):
    def __init__(self, in_context, aip, aport, taskidatloc, taskidthatrefs, reltag, aindex):
        strmsg = COMMAND_TASKLINK
        strmsg += COMMA + STR_IP + COMMA + aip
        strmsg += COMMA + STR_PORT + COMMA + str(aport)
        strmsg += COMMA + TASKID + COMMA + taskidatloc
        strmsg += COMMA + REFTASKID + COMMA + taskidthatrefs
        strmsg += COMMA + INDEX + COMMA + str(aindex)
        strmsg += COMMA + TAG + COMMA + reltag
        dbgprint("LinkMG:"+strmsg.__class__.__name__)
        StringMessageGenerator.__init__(self, strmsg, in_context)
        
    
class RemoveForwarderMG(StringMessageGenerator):
    def __init__(self, in_context, taskid):
        strmsg = COMMAND_REMOVEFORWARDER
        strmsg = strmsg + COMMA
        strmsg = strmsg + taskid
        StringMessageGenerator.__init__(self, strmsg, in_context)

class TaskGraphHeaderMG(StringMessageGenerator):
    def __init__(self, in_context, taskgraphid, taskcount):
        strmsg = COMMAND_TG_HEADER
        strmsg = strmsg + COMMA
        strmsg = strmsg + TASKGRAPHID
        strmsg = strmsg + COMMA
        strmsg = strmsg + taskgraphid
        strmsg = strmsg + COMMA
        strmsg = strmsg + TASKCOUNT
        strmsg = strmsg + COMMA
        strmsg = strmsg + taskcount
        StringMessageGenerator.__init__(self, strmsg, in_context)
        
    def OneShot(self):return False
        
class SendTaskGraphMessageController():
    def __init__(self, in_context, ataskgraph, adestip, adestport):
        self.context = in_context
        self.taskgraph = ataskgraph
        self.destip = adestip
        self.destport = adestport
        self.idval = ataskgraph.idval

    def sendstart(self):
        startmg = self.taskgraph.getstartmg()
        self.context.msgmon.sendGen(startmg, self.destip, self.destport)

    def sendmiddle(self):
        midmgs = self.taskgraph.getmidmgs()
        for mg in midmgs:
            self.context.msgmon.sendGen(mg, self.destip, self.destport)
