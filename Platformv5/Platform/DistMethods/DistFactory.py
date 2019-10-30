from DistMethods.FlowVector import getRedistDict_Flow, getTGRedistDict_Flow

#the zeroth is the local node in all three arrays
def getRedistDict(VCont, n_keys, n_benches, bench_tot, n_queuelens, queuelen_tot, n_sublvls, n_subtotal):
    return getRedistDict_Flow(VCont, n_keys, n_benches, bench_tot, n_queuelens, queuelen_tot)

def getTGRedistDict(VCont, n_keys, n_benches, bench_tot, n_tgqls):
    return getTGRedistDict_Flow(VCont, n_keys, n_benches, bench_tot, n_tgqls)
