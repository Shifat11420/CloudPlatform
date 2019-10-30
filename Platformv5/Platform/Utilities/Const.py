import sys
import os
import time

from Utilities.FileUtil import filedbgprint, GetOutputFolder

DEFAULTJOBTIME = 34.8

LOGTIME = 10
TERMTIME = 700

BNM_BASEINTERVAL = 20
BNM_PUSHDIFF = 0.3

STARTKILLCOUNT = 3
NOWORK_SECONDS = 10
STOPNOWORK = 70

DEBUG = True
COMMA = ","
PORT = 8007
FILECHUNK = 100
LINEDELIM = "\r\n"
FILENAME = "Filename"
FILENAMES = "Filenames"
FILESIZE = "Filesize"
ISDOCKER = "IsDocker"
OUTFILENAME = "OutFileName"
ITYPE_ADDNEIGHBOR = "AddNeighbor"
ITYPE_ADDJOB = "AddJob"
ITYPE_KILLSERVER = "KillServer"

INDEX = "Index"
UFILLREQ = "UFillReq"
PRIORITY = "Priority"
LOCINDEX = "LocIndex"

REFTASKID = "RefTaskID"
DICT_DEBUG = "Debug"
DICT_SOURCE_IP = "Source_IP"
DICT_SOURCE_PORT = "Source_Port"
DICT_EXP_IP = "Exp_IP"
DICT_EXP_PORT = "Exp_Port"
DICT_EXP_FILE = "Exp_File"
DICT_EXP_INDEX = "Exp_Index"
DICT_FOLDER = "Folder"
DICT_TARGET_IP = "Target_IP"
DICT_TARGET_PORT = "Target_Port"
DICT_INJECTOR_TYPE = "Injector_Type"
DICT_CONTAINER_ARGS = "Container_Args"
DICT_CONTAINER_FILES = "Container_Files"
DICT_NEIGHBOR_IP = "Neighbor_IP"
DICT_NEIGHBOR_PORT = "Neighbor_Port"

LOSECONNECTION = "LoseConnection"

COMMAND_SENDLOGS = "SendLogs"
COMMAND_RECEIVELOGS = "ReceiveLogs"
COMMAND_TERMINATE = "Terminate"
COMMAND_RECEIVEEXPECTEDCOMPTIME = "ReceiveExpectedCompTime"
COMMAND_RECEIVETGQUEUEINFO = "ReceiveTGQueueInfo"
COMMAND_RECEIVEREQSET = "ReceiveReqSet"

COMMAND_ENDSERVER = "EndServer"
COMMAND_RECEIVEFILE = "ReceiveFile"
COMMAND_STARTCONTAINER = "StartContainer"
COMMAND_SAYHELLO = "SayHello"
COMMAND_RESPONDHELLO = "HelloBack"
COMMAND_LOSECONNECTION = LOSECONNECTION
COMMAND_ADDNEIGHBOR = "AddNeighbor"
COMMAND_DELETENEIGHBOR = "DeleteNeighbor"
COMMAND_RECEIVECONTAINER = "ReceiveContainer"
COMMAND_QUEUECONTAINER = "QueueContainer"
COMMAND_DOYOUNEEDFILE = "DoYouNeedFile"
COMMAND_IHAVEFILE = "IHaveFile"
COMMAND_INEEDFILE = "INeedFile"

COMMAND_RESPONDPAUSED = "RespondPaused"
COMMAND_PAUSE = "Pause"
COMMAND_UNPAUSETIME = "TimeUnpause"
COMMAND_RECEIVECONTROLLER = "ReceiveController"

COMMAND_ASKFORWORK = "AskForWork"
COMMAND_CONTAINERRESPONSE = "ContainerResponse"

COMMAND_RECEIVEEXPNODE = "ReceiveExpNode"

COMMAND_GETBENCH = "GetBench"
COMMAND_RECEIVEBENCH = "ReceiveBench"

COMMAND_GETQUEUELEN = "GetQueueLen"
COMMAND_RECEIVEQUEUELEN = "ReceiveQueueLen"

COMMAND_CONNTEST = "ConnTest"
COMMAND_CONNRESP = "ConnResp"

COMMAND_STASISVECTOR = "StasisVector"
COMMAND_FLOWVECTOR = "FlowVector"
COMMAND_SWAPTIMES = "SwapTimes"

COMMAND_DYNTASKOBLIG = "DYNTaskOblig"
COMMAND_IHAVEOBLIG = "IHaveOblig"
COMMAND_INEEDOBLIG = "INeedOblig"
COMMAND_TASKLOCATION = "TaskLocation"
COMMAND_REMOVEFORWARDER = "RemoveForwarder"
COMMAND_TG_HEADER = "TG_Header"
COMMAND_RECEIVETASKOBLIG = "ReceiveTaskOblig"
COMMAND_RECEIVETGJOB = "ReceiveTGJob"
COMMAND_TASKLINK = "TaskLink"

TAG = "Tag"
TASKGRAPHID = "TaskGraphID"
TASKCOUNT = "TaskCount"
TASKID = "TaskID"

TIME = "Time"
FILESEP = "/"
IPLOCATION = "localhost"

STR_IP = "IP"
STR_PORT = "PORT"
STR_ID = "ID"

IMAGE = "Image"
COMMAND = "Command"
ARGS = "Args"
ARGSFILE = "ArgsFile"
ID = "ID"
SOURCEIP = "SourceIP"
SOURCEPORT = "SourcePort"
FILECOUNT = "FileCount"

MANAGERCHECKTIME = 1

def setDbg(val):
    global DEBUG
    DEBUG = val

def dbgprint(val):
    if(DEBUG):
        filedbgprint(val)
        sys.stdout.write(val + '\n')
        sys.stdout.write("TIME:"+str(CurrentTimeMillis())+'\n')
        sys.stdout.flush()

def ConcatePath(first, second):
    if(first.endswith(FILESEP)):
        return first + second
    else:
        return first + FILESEP + second

def CurrentTimeMillis():
    return int(round(time.time() * 1000))

def GetFilePath(filename):
    return ConcatePath(GetOutputFolder(), filename)

def GetFileNameFromPath(filepath):
    vals = filepath.split(FILESEP)
    return vals[-1:][0]

def LocalizeFileNames(filelist):
    listret = []
    for x in filelist:
        listret.append(GetFilePath(x))
    return listret

