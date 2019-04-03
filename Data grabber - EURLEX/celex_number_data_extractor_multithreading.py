from multiprocessing.dummy import Pool as ThreadPool
from get_content import collect_data
from time import time
import json
import os

start_time = time()

def wrapper_celex(celex):

    process_time = time()

    collect_data(celex)

    print('Celex number : {} is done. Time needed : {}'.format(celex, round(time() - process_time, 4)))

pool = ThreadPool(11)

with open('celex_numbers.json') as infile:
    celex_nums = json.load(infile)

CURRENT_PATH = os.getcwd()
already_collected_celex_nums = set(os.listdir(os.path.join(CURRENT_PATH, 'eurlex_docs')))

celex_nums_todo = [num for num in celex_nums if str(num)+'.json' not in already_collected_celex_nums]

# celex_nums = [
#     '32018D0051',
#     '32018R0644',
#     '62018CC0095'
# ]


results = pool.map(wrapper_celex, celex_nums_todo)

print('Total time spent:', round(time() - start_time, 6))