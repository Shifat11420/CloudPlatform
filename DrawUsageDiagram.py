import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import string
from datetime import timedelta

def numberNames(setnames):
    returnvals = []
    i = 0
    for val in setnames:
        if(not "exp" in val):
            subv = val[6:-4]
            returnvals.append(subv)
    return returnvals

def drawOnePlot(starttime,data,filenames):
    bar = []
    sizeofbar = []
    barstart = []
    jobcount = 0
    for i in range(len(data)):
        starts = data[i][0]
        ends = data[i][1]


        for key in starts:
            if(key in ends):
                jobcount = jobcount + 1
                bar.append(i) 
                sdelta = starts[key] - starttime
                barstart.append(sdelta.total_seconds())
                edelta = ends[key] -starts[key]
                sizeofbar.append(edelta.total_seconds())
            else:
                #bar.append(i)
                #sdelta = starts[key] - starttime
                #barstart.append(sdelta.total_seconds())
                #edelta = timedelta(seconds=100)
                #sizeofbar.append(edelta.total_seconds())
                pass
    
    labels = np.array(numberNames(filenames))
    nbar = np.array(bar)

    # so y is the set of which bar we're working with
    #z is the size of the bar
    #x is the bar's start point.

    #extra = Rectangle((0,0),1,1,fc="w", fill =False, edgecolor='none', linewidth=0)
    
    #plt.legend([extra], (str(starttime)))
    print(str(starttime))
    print(str(jobcount))
    plt.ylabel("Node Port Number")
    plt.xlabel("Time From Start in Seconds")
    plt.barh(nbar, sizeofbar, left=barstart, color='white', edgecolor='black', align='center')
    plt.ylim(max(nbar)+0.5, min(nbar)-0.5)
    plt.yticks(np.arange(nbar.max()+1), labels)
    plt.show()

