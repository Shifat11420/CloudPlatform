from Utilities.Const import *
from CommandReaders.AddNeighborReader import AddNeighborReader, DeleteNeighborReader
from CommandReaders.ContainerReader import ContainerReader, ContainerQueueReader, ContainerResponseReader
from CommandReaders.FileIfNeededReader import IHaveFileReader, INeedFileReader, DoYouNeedFileReader
from CommandReaders.HelloReader import HelloReader, HelloResponder, TerminateReader, EndServerReader
from CommandReaders.TCPFileReader import TCPFileReader
from CommandReaders.AskForWorkReader import AskForWorkReader
from CommandReaders.ExperimentControlReader import ReceiveExpNodeReader
from CommandReaders.LatencyReportReader import LatencyReportReader
from CommandReaders.BenchReportReader import BenchReportReader
from CommandReaders.LowperfReader import LowperfReader
from CommandReaders.AsktosleepExpReader import AsktosleepExpReader
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
        dbgprint("RF:"+name.decode('utf-8'))                                      ##
        if(name.startswith(COMMAND_RECEIVEFILE.encode('utf-8'))):
            return TCPFileReader(self.context)
 #       if(name.startswith(COMMAND_STARTCONTAINER)):
 #           return JobReader(self.context)
        if(name.startswith(COMMAND_SAYHELLO.encode('utf-8'))):
            return HelloReader(self.context)
        if(name.startswith(COMMAND_RESPONDHELLO.encode('utf-8'))):
            return HelloResponder(self.context)
        if(name.startswith(COMMAND_LOSECONNECTION.encode('utf-8'))):
            return TerminateReader(self.context)
        if(name.startswith(COMMAND_ADDNEIGHBOR.encode('utf-8'))):
            return AddNeighborReader(self.context)
        if(name.startswith(COMMAND_DELETENEIGHBOR.encode('utf-8'))):
            return DeleteNeighborReader(self.context)
        if(name.startswith(COMMAND_RECEIVECONTAINER.encode('utf-8'))):
            return ContainerReader(self.context)
        if(name.startswith(COMMAND_RECEIVEEXPECTEDCOMPTIME.encode('utf-8'))):
            return RecieveExpectCompTime(self.context)
        if(name.startswith(COMMAND_QUEUECONTAINER.encode('utf-8'))):
            return ContainerQueueReader(self.context)
        if(name.startswith(COMMAND_DOYOUNEEDFILE.encode('utf-8'))):
            return DoYouNeedFileReader(self.context)
        if(name.startswith(COMMAND_INEEDFILE.encode('utf-8'))):
            return INeedFileReader(self.context)
        if(name.startswith(COMMAND_IHAVEFILE.encode('utf-8'))):
            return IHaveFileReader(self.context)
        if(name.startswith(COMMAND_ASKFORWORK.encode('utf-8'))):
            return AskForWorkReader(self.context)
        if(name.startswith(COMMAND_CONTAINERRESPONSE.encode('utf-8'))):
            return ContainerResponseReader(self.context)
        if(name.startswith(COMMAND_ENDSERVER.encode('utf-8'))):
            return EndServerReader(self.context)
        if(name.startswith(COMMAND_RECEIVEEXPNODE.encode('utf-8'))):
	        return ReceiveExpNodeReader(self.context)
        if(name.startswith(COMMAND_GETBENCH.encode('utf-8'))):
            return SendBenchReader(self.context)
        if(name.startswith(COMMAND_RECEIVEBENCH.encode('utf-8'))):
            return ReceiveBenchReader(self.context)
        if(name.startswith(COMMAND_GETQUEUELEN.encode('utf-8'))):
            return SendQueueLenReader(self.context)
        if(name.startswith(COMMAND_RECEIVEQUEUELEN.encode('utf-8'))):
            return ReceiveQueueLenReader(self.context)
        if(name.startswith(COMMAND_SENDLOGS.encode('utf-8'))):
            return SendLogsReader(self.context)
        if(name.startswith(COMMAND_RECEIVELOGS.encode('utf-8'))):
            return ReceiveLogsReader(self.context)
        if(name.startswith(COMMAND_UNPAUSETIME.encode('utf-8'))):
            return TimeUnpauseReader(self.context)
        if(name.startswith(COMMAND_STASISVECTOR.encode('utf-8'))):
            return StasisVectorReader(self.context)
        if(name.startswith(COMMAND_FLOWVECTOR.encode('utf-8'))):
            return FlowVectorReader(self.context)
        if(name.startswith(COMMAND_SWAPTIMES.encode('utf-8'))):
            return SwapTimesReader(self.context)
        if(name.startswith(COMMAND_CONNTEST.encode('utf-8'))):
            return ConnTestReader(self.context)
        if(name.startswith(COMMAND_CONNRESP.encode('utf-8'))):
            return ConnRespReader(self.context)

        if(name.startswith(COMMAND_LATENCYREPORTNODE.encode('utf-8'))):                   ##
    	    return LatencyReportReader(self.context)                                      ##
        if(name.startswith(COMMAND_BENCHREPORTNODE.encode('utf-8'))):                     ##
    	    return BenchReportReader(self.context)                                        ##
        if(name.startswith(COMMAND_ASKTOSLEEP.encode('utf-8'))):                     ##
    	    return LowperfReader(self.context)    
        if(name.startswith(COMMAND_ASKTOSLEEPEXP.encode('utf-8'))):                     ##
    	    return AsktosleepExpReader(self.context)     
     

        
        if(name.startswith(COMMAND_DYNTASKOBLIG.encode('utf-8'))):
            return DYNTaskObligRdr(self.context)
        if(name.startswith(COMMAND_IHAVEOBLIG.encode('utf-8'))):
            return IHaveObligRdr(self.context)
        if(name.startswith(COMMAND_INEEDOBLIG.encode('utf-8'))):
            return INeedObligRdr(self.context)
        if(name.startswith(COMMAND_TASKLOCATION.encode('utf-8'))):
            return LocReader(self.context)
        if(name.startswith(COMMAND_REMOVEFORWARDER.encode('utf-8'))):
            return RemoveForwarderRdr(self.context)
        if(name.startswith(COMMAND_TG_HEADER.encode('utf-8'))):
            return TaskGraphHeaderRdr(self.context)
        if(name.startswith(COMMAND_RECEIVETASKOBLIG.encode('utf-8'))):
            return TCPFileReader(self.context)
        if(name.startswith(COMMAND_RECEIVETGJOB.encode('utf-8'))):
            return TaskContainerReader(self.context)
        if(name.startswith(COMMAND_RECEIVEREQSET.encode('utf-8'))):
            return RequirementSetRdr(self.context)
        if(name.startswith(COMMAND_RECEIVETGQUEUEINFO.encode('utf-8'))):
            return ReceiveTGQueueRdr(self.context)
        if(name.startswith(COMMAND_RECEIVETGQUEUEINFO.encode('utf-8'))):
            return ReceiveTGQueueRdr(self.context)
        if(name.startswith(COMMAND_TASKLINK.encode('utf-8'))):
            return LinkReader(self.context)
        
