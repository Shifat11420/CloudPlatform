from CommandMessageGenerators.MessageGenerator import MessageGenerator

class ComboGen(MessageGenerator):
    def __init__(self, in_context, msggens):
        MessageGenerator.__init__(self, in_context)
        self.msggens = msggens
        self.index = 0

    def read(self):
        val = None
        while (val == None) and (self.index < len(self.msggens)) :
            val = self.msggens[self.index].read()
            if(val == None):
                self.index = self.index + 1
        return val

    def reset(self):
        MessageGenerator.reset(self)
        for agen in self.msggens:
            agen.reset()
        self.index = 0
