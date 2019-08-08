import os
import time
import json
import threading
from collections import deque
from get_content import get_available_languages

class Worker(threading.Thread):

    def __init__(self, queue, name, language_pack):
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue
        self.language_pack = language_pack
    
    def run(self):

        while True:

            # Get a job

            task = self.queue.popleft()

            if task != 'Workday is over!':
                try:
                    self.language_pack[task] = get_available_languages(task)
                except:
                    self.language_pack[task] = []
                # print('Worker {} did task {}.'.format(self.name, task))
            else:
                print('Worker {} going home. Bye!'.format(self.name))
                break

def build_work_force(queue, number_of_workers, language_pack):

    workers = []

    for i in range(number_of_workers):
        worker = Worker(queue, i, language_pack)
        worker.start()
        workers.append(worker)
    
    return workers

class Producer():

    start_time = time.time()

    language_pack = dict()

    # Collect all the available celex numbers
    celex_numbers_collection = set()

    # Navigating into celex nums directory
    current_path = os.getcwd()
    celex_nums_path = os.path.join(current_path, 'celex_nums')

    for f in os.listdir(celex_nums_path):
        with open(os.path.join(celex_nums_path, f), 'r') as infile:
            celex_by_year = json.load(infile)
            celex_numbers_collection = celex_numbers_collection.union(set(celex_by_year))
    
    # we open our existing language json file
    with open('document_languages.json', 'r') as infile:
        language_pack = json.load(infile)
    
    # We will work in rounds of 10000 documents.
    while len(celex_numbers_collection) > 0:

        # We create a working queue.
        q = deque()

        for _ in range(200):
            number_candidate = celex_numbers_collection.pop()
            if number_candidate not in language_pack:
                q.append(number_candidate)
            
            if len(celex_numbers_collection) == 0:
                break
        
        workers = build_work_force(q, 10, language_pack)

        for worker in workers:
            q.append('Workday is over!')

        for worker in workers:
            worker.join()

        print('One Batch is done. Time needed : {} - documents left : {}'.format(round(time.time() - start_time), len(celex_numbers_collection)))

        with open('document_languages.json', 'w') as outfile:
            json.dump(language_pack, outfile, indent=1)

if __name__ == '__main__':
    p = Producer()

    with open('document_languages.json', 'w') as outfile:
        json.dump(p.language_pack, outfile)

