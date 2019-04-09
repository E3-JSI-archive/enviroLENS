import json
import threading
from collections import deque
from get_content import collect_data
import os
import time

class Worker(threading.Thread):

    def __init__(self, queue, name):
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue
    
    def run(self):

        while True:

            # Get a job

            task = self.queue.popleft()

            if task != 'Workday is over!':
                collect_data(task)
                print('Worker {} did task {}.'.format(self.name, task))
            else:
                print('Worker {} going home. Bye!'.format(self.name))
                break

def build_work_force(queue, number_of_workers):

    workers = []

    for i in range(number_of_workers):
        worker = Worker(queue, i)
        worker.start()
        workers.append(worker)
    
    return workers

class Producer():

    start_time = time.time()

    # We create a working queue.
    q = deque()

    # Collect all the available celex numbers
    celex_numbers_collection = set()

    # Navigating into celex nums directory
    current_path = os.getcwd()
    celex_nums_path = os.path.join(current_path, 'celex_nums')

    for f in os.listdir(celex_nums_path):
        # For testing purposes only, we currently only download
        # documents with year tag after 2000.
        if int(f[:4]) > 2000:
            with open(os.path.join(celex_nums_path, f), 'r') as infile:
                celex_by_year = json.load(infile)
                celex_numbers_collection = celex_numbers_collection.union(set(celex_by_year))
        
    # We will keep a track of documents that were already collected
    already_done = set()
    # Now we navigate into celex directory and check all the documents
    # that we have already collected
    
    celex_path = os.path.join(current_path, 'eurlex_docs')

    for f in os.listdir(celex_path):
        # The filed ends with '.json', we need to extract everything
        # that comes before that part.
        number = f[:-5]
        already_done.add(number)

    # We create a work queue. We add all the celex numbers that 
    # are not yet collected!
    cnt = 0
    for number in celex_numbers_collection:
        if number not in already_done:
            # For testing purposes only, we only assign 20 docs
            # to work queue.
            cnt += 1
            if cnt > 100:
                break
            q.append(number)
    
    workers = build_work_force(q, 10)

    for worker in workers:
        q.append('Workday is over!')

    for worker in workers:
        worker.join()

    print('Job is done. Time needed : {}'.format(round(time.time() - start_time)))

if __name__ == '__main__':
    Producer()



