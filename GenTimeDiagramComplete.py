import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
import sys
#import math

def PlotData(data, outfile, gkey=None, datakeys=None):
    tvals = range(0,399)  # original range(0,400) caused exception in ax1.fill_between(), since low and high are of range(399)
    tmarks = [0,100,200,300,400]
    fig, ax1 = plt.subplots(1,1)
    #axall = [ax1, ax2, ax3, ax4]
    ax1.set_ylabel("Time Delta (sec)")
    ax1.set_xlabel("Jobs Complete")
    ax1.set_xticks(tmarks)
    ax1.set_xticklabels(tmarks)
    colors = ['blue', 'red', 'green', 'yellow']
    i = 0
    ldata = []
    if datakeys is None:
        datakeys = data.keys()
    for key in datakeys:
        print ("KEY:"+key)
        print ("COLOR:"+colors[i])
        low = data[key][1]
        high = data[key][2]
        mid = data[key][0]
        #if(not (math.isnan(low[0]) or math.isnan(high[0]))):
        ax1.fill_between(tvals, low, high, facecolor = colors[i], alpha=0.25)
        ax1.plot(tvals, mid, color=colors[i])

        if(not gkey is None):
            ldata.append(mpatches.Patch(
                color=colors[i],
                label=gkey[i]))
        i = i + 1

    if(not gkey is None):
        plt.legend(handles=ldata)
    if(os.path.isfile(outfile)):
        os.remove(outfile)
    fig.savefig(outfile)

def GetData(indir):
    datasets = {}
    for f in os.listdir(indir):
        print("FILE:"+f)
        fullfile = indir + f
        with open(fullfile, 'r') as ifile:
            firstl = ""
            secondl= ""
            thirdl = ""
            
            for line in ifile:
                firstl = secondl
                secondl = thirdl
                thirdl = line
            print("------start " + f + "------")
            print(firstl)
            print(secondl)
            print(thirdl)
            print("------finish-----")
            fvals = firstl.strip()[:-1].split(",")
            del fvals[0]
            fvals = [float(x) for x in fvals]
            svals = secondl.strip()[:-1].split(",")
            del svals[0]
            svals = [float(x) for x in svals]
            tvals = thirdl.strip()[:-1].split(",")
            del tvals[0]
            tvals = [float(x) for x in tvals]
            datasets[f] = [fvals, svals, tvals]
    return datasets

def GenDir(indir, outfile, gkey=None, datakeys=None):
    data = GetData(indir)
    PlotData(data, outfile, gkey, datakeys)

if __name__ == "__main__":
    GenDir(sys.argv[1], sys.argv[2])
