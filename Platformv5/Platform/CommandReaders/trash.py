
from Utilities.Const import *    
from CommandMessageGenerators.MessageGenerator import StringMessageGenerator

class NewLeaderAcceptReader(TCPReader):
    def HandleLine(self, data):
        
        vals = data.split(COMMA.encode('utf-8'))
        fid = vals[1].decode('utf-8')

        self.context.SetFollower(fid)

class NewLeaderRejectReader(TCPReader):
    def HandleLine(self, data):
        vals = data.split(COMMA.encode('utf-8'))
        fid = vals[1].decode('utf-8')
        self.context.RejectFollower(fid)
class TaskGraphLinksMG(StringMessageGenerator):
    def __init__(self, in_context, taskgraphid, taskgraphasstr):
        strmsg = COMMAND_TG_LINKS
        strmsg = strmsg + COMMA
        strmsg = strmsg + TASKGRAPHID
        strmsg = strmsg + COMMA
        strmsg = strmsg + taskgraphid
        strmsg = strmsg + COMMA
        strmsg = strmsg + TASKLINKS
        strmsg = strmsg + COMMA
        strmsg = strmsg + taskgraphasstr
        StringMessageGenerator.__init__(self, in_context, strmsg)
        
    def OneShot(self):return False

class RequirementsMG(StringMessageGenerator):
    def __init__(self, in_context, filenames):
        strmsg = COMMAND_TGREQUIREMENTS
        for fname in filenames:
            strmsg = strmsg + COMMA
            strmsg = strmsg + FILENAME
            strmsg = strmsg + COMMA
            strmsg = strmsg + fname
        StringMessageGenerator.__init__(self, in_context, strmsg)
        
