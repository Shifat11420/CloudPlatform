from Graph.GraphGen import GraphGen


g = GraphGen(145)

mat = g.ErdosRenyiConnected(20, 0.2)

print (mat)
