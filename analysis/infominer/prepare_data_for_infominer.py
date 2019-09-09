import json
import os
import traceback
import random

path = os.getcwd()
path = r'C:/Users/Samo/Desktop/EnviroLENS/enviroLENS/Data grabber'

folder = '/legislation/'

with open('legislation_sample_full.txt', 'w', encoding='utf-8') as outfile:

    params = ['name', 'keyword', 'subject', 'geographicalArea', 'country/Territory', 'abstract']

    outfile.write('|'.join(params) + '\n')

    counter = 0

    samples = random.sample(list(os.listdir(path + folder)), len(list(os.listdir(path + folder))))

    for doc in samples:

        try:

            with open(path+folder+doc, 'r', encoding='utf-8') as f:

                info = json.load(f)

            line = ''
            
            for param in params:
                if info[param] is not None:
                    if type(info[param]) is list or type(info[param]) is tuple:
                        line += ','.join(info[param])
                    else:
                        line += str(info[param])
                line += '|'
            
            line = line[:-1]

            outfile.write(line + '\n')

            counter += 1
        
        except Exception:
            print('FAIL', counter)
            traceback.print_exc()
            pass
    

        if counter % 1000 == 0:
            print(counter)

            
