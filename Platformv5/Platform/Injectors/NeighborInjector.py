from Injectors.Injector import Injector
from CommandMessageGenerators.NeighborMessageGenerator import AddNeighborMessageGenerator
from Utilities.Const import *

class NeighborInjector(Injector):
    def __init__(self, odict):
        Injector.__init__(self, odict)
        n_ip = odict[DICT_NEIGHBOR_IP]
        n_port = odict[DICT_NEIGHBOR_PORT]
        anmg = AddNeighborMessageGenerator(self.pm, n_ip, n_port)
        self.SetMsgGen(anmg)
