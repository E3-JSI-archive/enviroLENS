import os
import json

folders = ['jurisprudence', 'legislation', 'treaty', 'treaty decisions', 'literature']

possible_keys = set()

for folder in folders:
    for filename in os.listdir(folder):
        
        with open(os.path.join(folder, filename), 'r') as infile:
            data = json.load(infile)
        
        for key in data:
            possible_keys.add((key, type(data[key])))
        
        with open(os.path.join(folder, filename), 'w') as outfile:
            json.dump(data, outfile, indent=1)

for v in sorted(possible_keys, key=lambda x: x[0]):
    print(v)




