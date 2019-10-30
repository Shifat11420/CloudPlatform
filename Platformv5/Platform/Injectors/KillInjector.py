from Injectors.Injector import Injector
from CommandMessageGenerators.MessageGenerator import EndServerMessageGenerator

class KillInjector(Injector):
    def __init__(self, odict):
        Injector.__init__(self, odict)
        esmg = EndServerMessageGenerator(self.pm)
        self.SetMsgGen(esmg)
