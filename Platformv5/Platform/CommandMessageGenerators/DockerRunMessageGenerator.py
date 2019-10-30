from Utilities.Const import *
from CommandMessageGenerators.MessageGenerator import MessageGenerator
import os

class DockerRunMessageGenerator(StringMessageGenerator):
    def __init__(self, in_command, in_image, in_args, in_context):
        self.command = in_command
        self.image = in_image
        self.args = in_args
        strval = COMMAND_STARTCONTAINER
        strval += COMMA + IMAGE
        strval += COMMA + self.image
        strval += COMMA + COMMAND
        strval += COMMA + self.command
        strval += COMMA + ARGS
        strval += COMMA + self.args
        strval += COMMA + LINEDELIM
        StringMessageGenerator.__init__(self, strval, in_context)
        
