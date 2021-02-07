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
            transp.write(val.encode('utf-8'))
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
        #if(not isinstance(self.msg, basestring)):                          ##added self with basestring
        #    dbgprint("DANGER:"+str(self.msg))                              ##

        if(not isinstance(self.msg, bytes) and not isinstance(self.msg, str)):                          ##added basestring alternatives for python 3. Python 3 does not support basestring,
            print("DANGER:"+str(self.msg))                                                              ## it's either bytes or str 

        if(isinstance(self.msg, bytes)):                                                                ## if it's a byte, decode it to str
            msg=msg.decode('utf-8')                                                                     ##
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
