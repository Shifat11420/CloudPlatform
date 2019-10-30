from Injectors.NeighborInjector import NeighborInjector
from Injectors.JobInjector import JobInjector
from Injectors.KillInjector import KillInjector
from Utilities.FileInputTokenize import KeyedFIP
from Utilities.Const import *

def BuildInjector(afile):
    kfip = KeyedFIP(afile)
    ijtp = kfip[DICT_INJECTOR_TYPE]
    if(ijtp == ITYPE_ADDNEIGHBOR):
        return NeighborInjector(kfip)
    elif(ijtp == ITYPE_ADDJOB):
        return JobInjector(kfip)
    elif(ijtp == ITYPE_KILLSERVER):
        return KillInjector(kfip)
    else:
        return None

