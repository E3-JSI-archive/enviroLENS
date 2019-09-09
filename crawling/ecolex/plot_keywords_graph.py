import matplotlib.pyplot as plt
import networkx as nx
import json

with open('keywords_graph.json', 'r') as infile:
    graph = json.load(infile)

G = nx.Graph()

visibleEdge = 1500
visibleNode = 100000

# G.add_nodes_from(list(graph.keys()))
for node in graph:
    if sum(list(graph[node].values())) > visibleNode:
        print(sum(list(graph[node].values())))
        G.add_node(node)

for node in graph:
    for edge,weight in graph[node].items():
        if weight > visibleEdge:
            G.add_edge(node, edge)

print(G.number_of_edges())
print(G.number_of_nodes())
#print(G.edges())

nx.draw(G, with_labels=False, font_weight='bold', node_size = 45)
plt.show()
