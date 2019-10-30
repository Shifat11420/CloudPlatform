from ExpDefinitions.BenchDefinition import benchBuildFromFile
from ExpDefinitions.BenchDefFactory import BenchDefFactory, BFFromFile
from ExpDefinitions.TaskGraphDefFactory import TGFFromFile

def BuildExpDef(filename, expindex):
    bdf = TGFFromFile(filename, expindex)
    return bdf.build()
