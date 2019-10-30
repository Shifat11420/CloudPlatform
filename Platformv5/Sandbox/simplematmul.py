import random
import sys
from datetime import datetime
random.seed(datetime.now())

dim = int(sys.argv[1])

m1 = []
m2 = []

for i in range(0, dim):
    m1.append([])
    m2.append([])
    for j in range(0,dim):
        m1[i].append(random.random())
        m2[i].append(random.random())

for i in range(0,dim):
    r = []
    for j in range(0,dim):
        val = 0
        for k in range(0,dim):
            for m in range(0,dim):
                val = val + m1[i][k] * m2[m][j]
        r.append(val)
    print(r)
print("Finished matmul")
