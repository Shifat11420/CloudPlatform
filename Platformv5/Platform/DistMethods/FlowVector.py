from Utilities.Const import *
from Utilities.FileUtil import expprint
import math
from twisted.python.compat import xrange                       ##added import

def getTGRedistDict_Flow(VCont, n_keys, n_benches, bench_tot, n_tgsets):
    sv = VCont.getStasisVector()
    fv = VCont.getFlowVector()

    dbgprint("TGRD:sv:"+str(sv))
    dbgprint("TGRD:fv:"+str(fv))
    dbgprint("TGRD:n_tgsets:"+str(n_tgsets))

    max_bench = max(n_benches)
    min_bench = min(n_benches)

    rvals = []
    rvaltotal = 0
    bt2 = bench_tot / 2
    if(bt2 == 0):
        bt2 = 1

    max_ql_bp = {}
    min_ql_bp = {}
    pkeyset = []
    qltot = {}

    
    for i in range(len(n_keys)):
        for p_key in n_tgsets[i]:
            if(not p_key in pkeyset):
                pkeyset.append(p_key)
                qltot[p_key] = 0
                
    for i in range(len(n_keys)):
        for pkey in pkeyset:
            if(not pkey in n_tgsets[i]):
                n_tgsets[i][pkey] = 0
                
    for i in range(len(n_keys)):
        for p_key in n_tgsets[i]:
            qltot[p_key] += n_tgsets[i][p_key]
            if(p_key in max_ql_bp):
                if(n_tgsets[i][p_key] > max_ql_bp[p_key]):
                    max_ql_bp[p_key] = n_tgsets[i][p_key]
            else:
                max_ql_bp[p_key] = n_tgsets[i][p_key]
            if(p_key in min_ql_bp):
                if(n_tgsets[i][p_key] < min_ql_bp[p_key]):
                    min_ql_bp[p_key] = n_tgsets[i][p_key]
            else:
                min_ql_bp[p_key] = n_tgsets[i][p_key]

    dbgprint("TGRD:max_ql_bp:"+str(max_ql_bp))
    dbgprint("TGRD:min_ql_bp:"+str(min_ql_bp))
    dbgprint("TGRD:n_keys:"+str(n_keys))
    

    dbgprint("TGRD:n_tgsets:"+str(n_tgsets))

    rvals_bpkey = {}
    rvaltots = {}
    for pkey in pkeyset:
    
        rvals_bpkey[pkey] = []
        rvaltots[pkey] = 0
        bt2 = bench_tot / 2
        if(bt2 == 0):
            bt2 = 1    

        for i in xrange(0, len(n_keys)):
            dbgprint("nqtg+"+str(i)+":"+str(n_tgsets[i][pkey]))
            #dbgprint("nq_"+str(i)+":"+str(n_queuelens[i]))
            dbgprint("nb_"+str(i)+":"+str(n_benches[i]))
            nqlv = 0
            nbv = 0
            if(min_ql_bp[pkey] != max_ql_bp[pkey]):
                nqlv = (n_tgsets[i][pkey] - min_ql_bp[pkey])*2.0 / float(max_ql_bp[pkey]-min_ql_bp[pkey]) - 1
            if(min_bench != max_bench):
                nbv = (n_benches[i] - min_bench)*2.0 / float(max_bench-min_bench) -1

            if(i == 0):
                nqlv = nqlv + sv[0]
                nbv = nbv + sv[1]

            dbgprint("nqlv:"+str(nqlv))
            dbgprint("nbv:"+str(nbv))
            rval = nqlv * fv[0]
            rval = rval + nbv * fv[1]
            dbgprint("rval:"+str(rval))
            if(rval < 0):
                rval = 0
            rvals_bpkey[pkey].append(rval)
            rvaltots[pkey] += rval






    dbgprint("TGRD:rvals_bpkey:"+str(rvals_bpkey))

    dict_to_r_bpkey = {}
    for pkey in pkeyset:
        dict_to_r_bpkey[pkey] = {}
        dict_of_fract = {}
        totaljobs = n_tgsets[0][p_key]
        extra = 0
        if(rvaltots[pkey] == 0):
            dbgprint("rvaltotal == 0")
            for i in xrange(0, len(n_keys)):
                dict_to_r_bpkey[pkey][i] = 0
        else:
            dbgprint("rvaltots:"+str(rvaltots[pkey]))
            for i in xrange(0, len(n_keys)):
                val = totaljobs * (rvals_bpkey[pkey][i] / rvaltots[pkey])
                dbgprint("TJVal:"+str(val))
                dict_to_r_bpkey[pkey][n_keys[i]] = int(math.floor(val))
                dbgprint("redist-added to dict["+str(n_keys[i])+"] = "+str(math.floor(val)))
                dict_of_fract[n_keys[i]] = val - math.floor(val)
                extra = extra + val - math.floor(val)
            ind = 0

            #ds = sorted(dict_of_fract.items(), reverse=True, key=lambda (key,value):value)            ##python2
            ds = sorted(dict_of_fract.items(), reverse=True, key=lambda key_value: key_value[1])       ##python3
            dbgprint("DS:"+str(ds))
            for val in ds:
                if(extra < 1):
                    break
                dict_to_r_bpkey[pkey][val[0]] += 1
                extra = extra - 1
            expprint("flow redist dict="+str(dict_to_r_bpkey[pkey]))
        
    dbgprint("Before dict return")
    dbgprint("TGRD:dict_to_r_bpkey:"+str(dict_to_r_bpkey))
    return dict_to_r_bpkey



#DEAL WITH RETURNS NOW?  DIFFERENT B/C PRIORITY

            


            
def getRedistDict_Flow(
        VCont, n_keys, n_benches, bench_tot, n_queuelens, queuelen_tot):

    dbgprint("grdf")

    max_bench = max(n_benches)
    min_bench = min(n_benches)

    max_ql = max(n_queuelens)
    min_ql = min(n_queuelens)

    

    expprint("flow redist args1="+str(n_keys))
    expprint("flow redist args2="+str(n_benches))
    expprint("flow redist args3="+str(bench_tot))
    expprint("flow redist args4="+str(n_queuelens))
    expprint("flow redist args5="+str(queuelen_tot))
    sv = VCont.getStasisVector()
    fv = VCont.getFlowVector()
    expprint("flow flow="+str(fv))
    expprint("flow stasis="+str(sv))
    
    rvals = []
    rvaltotal = 0
    bt2 = bench_tot / 2
    if(bt2 == 0):
        bt2 = 1
    qlt2 = queuelen_tot / 2
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
        nqlv = 0
        nbv = 0
        if(min_ql != max_ql):
            nqlv = (n_queuelens[i] - min_ql)*2.0 / float(max_ql-min_ql) - 1
        if(min_bench != max_bench):
            nbv = (n_benches[i] - min_bench)*2.0 / float(max_bench-min_bench) -1

        if(i == 0):
            nqlv = nqlv + sv[0]
            nbv = nbv + sv[1]

        dbgprint("nqlv:"+str(nqlv))
        dbgprint("nbv:"+str(nbv))
        rval = nqlv * fv[0]
        rval = rval + nbv * fv[1]
        dbgprint("rval:"+str(rval))
        if(rval < 0):
            rval = 0
        rvals.append(rval)
        rvaltotal = rvaltotal + rval

    dbgprint("rvals:"+str(rvals))

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
        dbgprint("TJVal:"+str(val))
        dict_to_return[n_keys[i]] = int(math.floor(val))
        dbgprint("redist-added to dict["+str(n_keys[i])+"] = "+str(math.floor(val)))
        dict_of_fract[n_keys[i]] = val - math.floor(val)
        extra = extra + val - math.floor(val)
    ind = 0

    #ds = sorted(dict_of_fract.items(), reverse=True, key=lambda (key,value):value)                      ##python2
    ds = sorted(dict_of_fract.items(), reverse=True, key=lambda key_value: key_value[1])                ##python3
    dbgprint("DS:"+str(ds))
    for val in ds:
        if(extra < 1):
            break
        dict_to_return[val[0]] = dict_to_return[val[0]] + 1
        extra = extra - 1
    expprint("flow redist dict="+str(dict_to_return))
        
    dbgprint("Before dict return")
    return dict_to_return
