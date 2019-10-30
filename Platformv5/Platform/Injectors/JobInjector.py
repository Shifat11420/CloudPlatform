from Injectors.Injector import Injector
from Utilities.Const import *
from DockerManagers.SubContManager import ContainerManager
from CommandMessageGenerators.ContainerMessageGenerator import ContainerMessageGenerator
import uuid

class JobInjector(Injector):

    def __init__(self, odict):
        Injector.__init__(self, odict)
        cont_args = str(odict[DICT_CONTAINER_ARGS])
        allfiles = str(odict[DICT_CONTAINER_FILES])
        cont_files = allfiles.split(COMMA)
        
        idstr = str(uuid.uuid4())

        cont = ContainerManager(cont_args, cont_files, idstr, self.source_ip, self.source_port, self.pm)

        cont_msg_gen = ContainerMessageGenerator(cont, self.pm)

        self.SetMsgGen(cont_msg_gen)
