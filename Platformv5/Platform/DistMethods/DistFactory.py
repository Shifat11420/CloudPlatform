from DistMethods.FlowVector import getRedistDict_Flow, getTGRedistDict_Flow
from DistMethods.FlowVector import getRedistDict_Flow_3D                  #*

#the zeroth is the local node in all three arrays
def getRedistDict(VCont, n_keys, n_benches, bench_tot, n_queuelens, queuelen_tot, n_sublvls, n_subtotal):
    return getRedistDict_Flow(VCont, n_keys, n_benches, bench_tot, n_queuelens, queuelen_tot)

def getRedistDict_3D(VCont, n_keys, n_benches, bench_tot, n_queuelens, queuelen_tot, n_sublvls, n_subtotal, n_latencies, latency_tot):  #* for 3D scheduling
    return getRedistDict_Flow_3D(VCont, n_keys, n_benches, bench_tot, n_queuelens, queuelen_tot, n_latencies, latency_tot)           #* for 3D scheduling

def getTGRedistDict(VCont, n_keys, n_benches, bench_tot, n_tgqls):
    return getTGRedistDict_Flow(VCont, n_keys, n_benches, bench_tot, n_tgqls)
