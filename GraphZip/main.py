from Class.edge_graph import Edge_Graph
from Class.Clique_Graph import Clique_Graph
#simple main program to initialise and work the programs

EG=Edge_Graph()
EG.edge_append(1,2)
EG.edge_append(1,3)
EG.edge_append(2,1)
EG.edge_append(2,4)
EG.edge_append(2,6)
EG.edge_append(3,1)
EG.edge_append(3,4)
EG.edge_append(3,5)
EG.edge_append(4,2)
EG.edge_append(4,3)
EG.edge_append(4,5)
EG.edge_append(5,3)
EG.edge_append(5,4)
EG.edge_append(5,7)
EG.edge_append(6,2)
EG.edge_append(6,7)
EG.edge_append(7,5)
EG.edge_append(7,6)
EG.edge_append(7,8)
EG.edge_append(8,7)
EG.encode()
CG=Clique_Graph()
CG.decode(EG)
print(CG.view_cliques())
CG.encode()