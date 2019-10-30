
# first idea
# total ncount
# total jcount
# judgeval = -2*ncount + jcount

#this function should take

# a dictionary with
# keys as nodeids
# values as dictionarys such that
#    keys as subnodeids
#    values as subnodeqlens
#and return a dictionary with
# keys as nodeides
# values as subnode ranking in some way

def CalcSubLevel(dbldict_subqlens):
    rdict = {}
    for key in dbldict_subqlens:
        ncount = 0
        jcount = 0
        subdict = dbldict_subqlens[key]
        for skey in subdict:
            ncount = ncount + 1
            jcount = jcount + subdict[skey]
        rdict[key] = -2*ncount + jcount
    return rdict
