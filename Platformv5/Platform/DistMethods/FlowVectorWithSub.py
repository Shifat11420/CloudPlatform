from Utilities.Const import *
from Utilities.FileUtil import expprint
import math

def getRedistDict_Flow(VCont, n_keys, n_benches, bench_tot, n_queuelens, queuelen_tot, n_subqvals, subqval_tot):

    dbgprint("grdf")

    expprint("flow redist args1="+str(n_keys))
    expprint("flow redist args2="+str(n_benches))
    expprint("flow redist args3="+str(bench_tot))
    expprint("flow redist args4="+str(n_queuelens))
    expprint("flow redist args5="+str(queuelen_tot))
    expprint("flow redist args6="+str(n_subqvals))
    expprint("flow redist args7="+str(subqval_tot))
    expprint("flow flow="+str(VCont.flowvector))
    expprint("flow stasis="+str(VCont.stasisvector))
    
    rvals = []
    rvaltotal = 0
    bt2 = bench_tot / 2
    if(bt2 == 0):
        bt2 = 1
    qlt2 = queuelen_tot / 2
    sqlt2 = subqval_tot / 2
    if(sqlt2 == 0):
        sqlt2 = 1
        
    if(qlt2 == 0):
        dbgprint("queuelentot == 0")
        return {}

    if(n_benches[0] > 0):
        dbgprint("FV:Interesting")
    dbgprint("bt2:"+str(bt2))
    dbgprint("qlt2:"+str(qlt2))

    for i in xrange(0, len(n_keys)):
        dbgprint("nq_"+str(i)+":"+str(n_queuelens[i]))
        dbgprint("nb_"+str(i)+":"+str(n_benches[i]))

        dbgprint("nqcount:"+str(len(n_queuelens)))
        dbgprint("nbcount:"+str(len(n_benches)))
        dbgprint("SUBCOUNT:"+str(len(n_subqvals)))
        
        nqlv = ((n_queuelens[i]/qlt2)-1)
        nbv = ((n_benches[i]/bt2)-1)
        nsq = ((n_subqvals[i]/sqlt2)-1)

        if(i == 0):
            nqlv = nqlv + VCont.stasisvector[0]
            nbv = nbv + VCont.stasisvector[1]
            nsq = nsq + VCont.stasisvector[2]

        dbgprint("nqlv:"+str(nqlv))
        dbgprint("nbv:"+str(nbv))
        rval = nqlv * VCont.flowvector[0]
        rval = rval + nbv * VCont.flowvector[1]
        rval = rval + nsq * VCont.flowvector[2]
        dbgprint("rval:"+str(rval))
        #if(rval < 0):
        #    rval = 0
        rvals.append(rval)
        rvaltotal = rvaltotal + rval

    dict_to_return = {}
    dict_of_fract = {}
    totaljobs = n_queuelens[0]
    extra = 0
    if(rvaltotal == 0):
        dbgprint("rvaltotal == 0")
        return {}
    dbgprint("rvaltotal:"+str(rvaltotal))
    for i in xrange(0, len(n_keys)):
        val = totaljobs * (rvals[i] / rvaltotal)
        dict_to_return[n_keys[i]] = int(math.floor(val))
        dbgprint("redist-added to dict["+str(n_keys[i])+"] = "+str(math.floor(val)))
        dict_of_fract[n_keys[i]] = val - math.floor(val)
        extra = extra + val - math.floor(val)
    ind = 0
    
    for val in sorted(dict_of_fract.items(), key=lambda (key,value): value):
        if(extra < 1):
            break
        dict_to_return[val[0]] = dict_to_return[val[0]] + 1
        extra = extra - 1
    expprint("flow redist dict="+str(dict_to_return))
        
    dbgprint("Before dict return")
    return dict_to_return

    
