from Utilities.Const import *
from CommandReaders.AddNeighborReader import AddNeighborReader, DeleteNeighborReader
from CommandReaders.ContainerReader import ContainerReader, ContainerQueueReader, ContainerResponseReader
from CommandReaders.FileIfNeededReader import IHaveFileReader, INeedFileReader, DoYouNeedFileReader
from CommandReaders.HelloReader import HelloReader, HelloResponder, TerminateReader, EndServerReader
from CommandReaders.TCPFileReader import TCPFileReader
from CommandReaders.AskForWorkReader import AskForWorkReader
from CommandReaders.ExperimentControlReader import ReceiveExpNodeReader
from CommandReaders.BenchReader import SendBenchReader, ReceiveBenchReader
from CommandReaders.QueueLenReader import SendQueueLenReader, ReceiveQueueLenReader, RecieveExpectCompTime
from CommandReaders.SendLogsReader import SendLogsReader, ReceiveLogsReader
from CommandReaders.PauseUnpauseReader import TimeUnpauseReader
from CommandReaders.VectorReader import StasisVectorReader, FlowVectorReader, SwapTimesReader
from CommandReaders.ConnTestReader import ConnTestReader, ConnRespReader
from CommandReaders.TaskGraphReaders import DYNTaskObligRdr, IHaveObligRdr, INeedObligRdr, LocReader, RemoveForwarderRdr, TaskGraphHeaderRdr, TaskContainerReader, RequirementSetRdr, ReceiveTGQueueRdr, LinkReader

#basic factory checking
#what a command line starts with and
#building a reader based on that
#note that the start of the line is checked
#not consumed and will still be parsed by the handler's
#handle method.
class ReaderFactory():
    def __init__(self, in_context):
        self.context = in_context
    def buildMessageHandler(self, name):
        dbgprint("RF:"+name)
        if(name.startswith(COMMAND_RECEIVEFILE)):
            return TCPFileReader(self.context)
 #       if(name.startswith(COMMAND_STARTCONTAINER)):
 #           return JobReader(self.context)
        if(name.startswith(COMMAND_SAYHELLO)):
            return HelloReader(self.context)
        if(name.startswith(COMMAND_RESPONDHELLO)):
            return HelloResponder(self.context)
        if(name.startswith(COMMAND_LOSECONNECTION)):
            return TerminateReader(self.context)
        if(name.startswith(COMMAND_ADDNEIGHBOR)):
            return AddNeighborReader(self.context)
        if(name.startswith(COMMAND_DELETENEIGHBOR)):
            return DeleteNeighborReader(self.context)
        if(name.startswith(COMMAND_RECEIVECONTAINER)):
            return ContainerReader(self.context)
        if(name.startswith(COMMAND_RECEIVEEXPECTEDCOMPTIME)):
            return RecieveExpectCompTime(self.context)
        if(name.startswith(COMMAND_QUEUECONTAINER)):
            return ContainerQueueReader(self.context)
        if(name.startswith(COMMAND_DOYOUNEEDFILE)):
            return DoYouNeedFileReader(self.context)
        if(name.startswith(COMMAND_INEEDFILE)):
            return INeedFileReader(self.context)
        if(name.startswith(COMMAND_IHAVEFILE)):
            return IHaveFileReader(self.context)
        if(name.startswith(COMMAND_ASKFORWORK)):
            return AskForWorkReader(self.context)
        if(name.startswith(COMMAND_CONTAINERRESPONSE)):
            return ContainerResponseReader(self.context)
        if(name.startswith(COMMAND_ENDSERVER)):
            return EndServerReader(self.context)
        if(name.startswith(COMMAND_RECEIVEEXPNODE)):
	    return ReceiveExpNodeReader(self.context)
        if(name.startswith(COMMAND_GETBENCH)):
            return SendBenchReader(self.context)
        if(name.startswith(COMMAND_RECEIVEBENCH)):
            return ReceiveBenchReader(self.context)
        if(name.startswith(COMMAND_GETQUEUELEN)):
            return SendQueueLenReader(self.context)
        if(name.startswith(COMMAND_RECEIVEQUEUELEN)):
            return ReceiveQueueLenReader(self.context)
        if(name.startswith(COMMAND_SENDLOGS)):
            return SendLogsReader(self.context)
        if(name.startswith(COMMAND_RECEIVELOGS)):
            return ReceiveLogsReader(self.context)
        if(name.startswith(COMMAND_UNPAUSETIME)):
            return TimeUnpauseReader(self.context)
        if(name.startswith(COMMAND_STASISVECTOR)):
            return StasisVectorReader(self.context)
        if(name.startswith(COMMAND_FLOWVECTOR)):
            return FlowVectorReader(self.context)
        if(name.startswith(COMMAND_SWAPTIMES)):
            return SwapTimesReader(self.context)
        if(name.startswith(COMMAND_CONNTEST)):
            return ConnTestReader(self.context)
        if(name.startswith(COMMAND_CONNRESP)):
            return ConnRespReader(self.context)

        
        if(name.startswith(COMMAND_DYNTASKOBLIG)):
            return DYNTaskObligRdr(self.context)
        if(name.startswith(COMMAND_IHAVEOBLIG)):
            return IHaveObligRdr(self.context)
        if(name.startswith(COMMAND_INEEDOBLIG)):
            return INeedObligRdr(self.context)
        if(name.startswith(COMMAND_TASKLOCATION)):
            return LocReader(self.context)
        if(name.startswith(COMMAND_REMOVEFORWARDER)):
            return RemoveForwarderRdr(self.context)
        if(name.startswith(COMMAND_TG_HEADER)):
            return TaskGraphHeaderRdr(self.context)
        if(name.startswith(COMMAND_RECEIVETASKOBLIG)):
            return TCPFileReader(self.context)
        if(name.startswith(COMMAND_RECEIVETGJOB)):
            return TaskContainerReader(self.context)
        if(name.startswith(COMMAND_RECEIVEREQSET)):
            return RequirementSetRdr(self.context)
        if(name.startswith(COMMAND_RECEIVETGQUEUEINFO)):
            return ReceiveTGQueueRdr(self.context)
        if(name.startswith(COMMAND_RECEIVETGQUEUEINFO)):
            return ReceiveTGQueueRdr(self.context)
        if(name.startswith(COMMAND_TASKLINK)):
            return LinkReader(self.context)
        
