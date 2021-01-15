from Utilities.Const import *
import os.path
import shutil
import datetime

class LogStream():
    
    def __init__(self, p_fname, d_fname, prefix):
        self.pfn = p_fname
        self.dfn = d_fname
        self.prefix = prefix
        self.pstr = None
        self.dstr = None
        self.pend = False
        self.dend = False
        dtstart = datetime.datetime.now()
        self.ldbgprint("LOGSTARTTIME!!:"+str(dtstart))

    def ldbgprint(self, val):
        if(True):
            print (val)                           ##

    def reset(self):
        self.pend = False
        self.dend = False
        if(not (self.pstr is None)):
            self.pstr.close()
            self.pstr = None
        if(not(self.dstr is None)):
            self.dstr.close()
            self.dstr = None

    def read(self):
        val = self.innerread()
        self.ldbgprint(val)
        return val

    def innerread(self):

        NL = "\r\n"
        if(not self.pend):
            if(self.pstr is None):
                if((not(self.pfn is None)) and os.path.isfile(self.pfn)):
                    dbgprint("LS:A")
                    xfn = "temp1234.txt"
                    shutil.copy2(self.pfn, xfn)
                    self.pstr = open(xfn, 'r')
                else:
                    dbgprint("LS:B")
                    self.pend = True
                    return self.prefix + "--NO PERF FILE--"+NL
            rval = self.pstr.readline()
            dbgprint("LS:C:"+rval)
            if(len(rval) == 0):
                self.pend = True
                self.pstr.close()
                self.pstr = None
            else:
                return self.prefix + "--PERF--" + rval + NL
        if(not self.dend):
            if(self.dstr is None):
                if((not(self.dfn is None)) and os.path.isfile(self.dfn)):
                    xfn = "temp9876.txt"
                    shutil.copy2(self.dfn, xfn)
                    self.dstr = open(xfn, 'r')
                else:
                    self.dend = True
                    return self.prefix + "--NO DBG FILE--"+NL
            rval = self.dstr.readline()
            if(len(rval) == 0):
                self.dend = True
                self.dstr.close()
                self.dstr = None
            else:
                return self.prefix + "--DEBUG--" + rval + NL
        return None
