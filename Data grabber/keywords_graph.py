import json
import os
from collections import defaultdict

folders = ["/jurisprudence/", "/legislation/", "/literature/", "/treaty/", "/treaty decisions/"]
# folders = ["/literature/"]
cwd = os.getcwd()

# We will create a complete weighted graph which will have keywords as vertices
# For each document, for each pair of keywords that appear together we will add 1 to the 
# weight of that edge. 
# In the end we will have a weighted graph, which will have heavy edges between keywords
# that are closely connected to eachother. 

graph_weights = {}

for folder in folders:
    for file in os.listdir(cwd+folder):
        with open(cwd + folder + file, 'r') as f:
            info = json.load(f)

            if 'keyword' in info and info['keyword'] is not None:
                for keyword_1 in info['keyword']:
                    if keyword_1 not in graph_weights:
                        graph_weights[keyword_1] = defaultdict(int)
                    for keyword_2 in info['keyword']:
                        if keyword_1 != keyword_2:
                            graph_weights[keyword_1][keyword_2] += 1
            
            
            if 'keywords' in info and info['keywords'] is not None:
                for keyword_1 in info['keywords']:
                    if keyword_1 not in graph_weights:
                        graph_weights[keyword_1] = defaultdict(int)
                    for keyword_2 in info['keywords']:
                        if keyword_1 != keyword_2:
                            graph_weights[keyword_1][keyword_2] += 1
            
    print('Folder completed!', folder)

with open('keywords_graph.json', 'w') as outfile:
    json.dump(graph_weights, outfile)

print(len(graph_weights))

print(max(max(list(graph_weights[k].values())) for k in graph_weights))
            
