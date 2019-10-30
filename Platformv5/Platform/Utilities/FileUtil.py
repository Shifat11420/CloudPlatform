import os
import datetime

OUTFOLDER = "Sandbox"
dbgerrata = ""
errata = ""
filename = None

def getDFilePath():
    return OUTFOLDER+filename+"dbg"

def getPFilePath():
    return OUTFOLDER+filename

def GetOutputFolder():
    global OUTFOLDER
    return OUTFOLDER

def SetOutputFolder(val):
    global OUTFOLDER
    OUTFOLDER = val.strip()
    if not os.path.exists(OUTFOLDER):
        os.makedirs(OUTFOLDER)

def setFileName(strfilename):
    global errata
    global filename
    filename = strfilename
    filedbgprint(dbgerrata)
    filedbgprint("setfilename:"+strfilename)
    expprint(errata)

def expprint(line):
    global filename
    global errata
    line = line + str(datetime.datetime.now())
    if(filename is None):
        errata = errata + line
    else:
        vals = line.replace("\t", "\n")
        vals = vals + "\n"
        print(filename+vals)
        with open(OUTFOLDER + filename, "a") as efile:
            efile.write(str(vals))

def filedbgprint(line):
    global filename
    global dbgerrata
    if(filename is None):
        dbgerrata = dbgerrata + line
    else:
        vals = line.replace("\t", "\n")
        vals = vals + "\n"
        with open(OUTFOLDER+filename+"dbg", "a") as dfile:
            dfile.write(str(vals))
