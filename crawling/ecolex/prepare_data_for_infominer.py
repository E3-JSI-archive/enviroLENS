import json
import os

path = os.getcwd()

folder = '/legislation/'

with open('legislation_infominer.txt', 'w', encoding='utf-8') as outfile:

    params = ['name', 'keyword', 'subject', 'geographicalArea', 'country/Territory', 'abstract']

    outfile.write('|'.join(params) + '\n')

    counter = 0

    for doc in os.listdir(path + folder):

        try:

            with open(path+folder+doc, 'r', encoding='utf-8') as f:

                info = json.load(f)

            line = ''
            
            for param in params:
                if info[param] is not None:
                    line += str(info[param])
                line += '|'
            
            line = line[:-1]

            outfile.write(line + '\n')

            counter += 1
        
        except:
            print('FAIL', counter)
            pass
    

        if counter % 1000 == 0:
            print(counter)

            