from Utilities.Const import *

class MessageGenerator():
    def __init__(self, in_context):
        self.context = in_context
        self.ip = ""
        self.port = 0
        self.state = 0

    def setGoodFinish(self):
        if(self.state == 2):
            pass
        else:
            self.state = 1

    def setBadFinish(self):
        self.state = 2

    def reset(self):
        self.state = 0

    def read(self):return None

    def OneShot(self):
        dbgprint("OneShot:"+str(self.__class__))
        return True

    def clone(self):return None

    def WriteResponse(self, transp):
        val = self.read()
        while(val != None):
            transp.write(val)
            val = self.read()

class ComboMessageGenerator(MessageGenerator):
    def __init__(self, subgens, in_context):
        MessageGenerator.__init__(self, in_context)
        self.subgens = subgens
        self.genindex = 0

    def read(self):
        if(self.genindex >= len(self.subgens)):
            return None
        cgen = self.subgens[self.genindex]
        val = cgen.read()
        if(val == None):
            self.genindex = self.genindex + 1
            return self.read()
        return val
   
    def reset(self):
	MessageGenerator.reset(self)
	for agen in self.subgens:
	    agen.reset()
	self.genindex = 0

class StringMessageGenerator(MessageGenerator):
    def __init__(self, msgstr, in_context):
        MessageGenerator.__init__(self, in_context)
        self.msg = msgstr
	self.initmsg = msgstr

    def clone(self):
        return StringMessageGenerator(self.initmsg, self.context)

    def read(self):
        if(self.msg == None):return None
        if(not isinstance(self.msg, basestring)):
            dbgprint("DANGER:"+str(self.msg))
        dbgprint("Sending Msg: " + self.msg)
        tosend = self.msg
        if(not tosend.endswith(LINEDELIM)):
            tosend = tosend + LINEDELIM
        self.msg = None
        return tosend

    def reset(self):
	MessageGenerator.reset(self)
	self.msg = self.initmsg

class TerminateMessageGenerator(StringMessageGenerator):
    def __init__(self, in_context):
        StringMessageGenerator.__init__(self, COMMAND_LOSECONNECTION, in_context)

class EndServerMessageGenerator(StringMessageGenerator):
    def __init__(self, in_context):
        StringMessageGenerator.__init__(self, COMMAND_ENDSERVER, in_context)
