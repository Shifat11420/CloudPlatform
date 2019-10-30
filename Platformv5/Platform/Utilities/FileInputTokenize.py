from collections import OrderedDict
from Utilities.Const import *

def setDefaults(odict):
    odict[DICT_SOURCE_IP] = "localhost"
    odict[DICT_SOURCE_PORT] = 8007
    odict[DICT_FOLDER] = "Sandbox/"

class FIP():
    def __init__(self, filepath):
        self.fhandle = open(filepath, 'r')

    def read(self):
        return self.fhandle.readline().rstrip('\n')

    def close(self):
        self.fhandle.close()

class ArgFIP(OrderedDict):
    def __init__(self, argsl, *args, **kwargs):
        OrderedDict.__init__(self, *args, **kwargs)
        setDefaults(self)
        arglist = argsl[1:]
        for val in arglist:
            eq_ind = val.find("=")
            
            akey = val[:eq_ind]
            avalue = val[eq_ind+1:]
            self[akey] = avalue

class KeyedFIP(OrderedDict):
    def __init__(self, filepath, *args, **kwargs):
        OrderedDict.__init__(self, *args, **kwargs)
        setDefaults(self)
        filestr = open(filepath, 'r')
        line = filestr.readline()
        while line:
            line = line.rstrip('\n')
            eq_ind = line.find('=')

            akey = line[:eq_ind]
            avalue = line[eq_ind+1:]
            self[akey] = avalue
            line = filestr.readline()
        filestr.close()
