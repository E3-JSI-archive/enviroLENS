from eurlex_crawler import get_celex_numbers
import threading
import time
from collections import deque

class Consumer(threading.Thread):

    def __init__(self, queue, number):
        threading.Thread.__init__(self)
        self.queue = queue
        self.number = number
    
    def run(self):

        while True:

            #: We give thread a task
            task = self.queue.popleft()

            #: If all the tasks are done, we can go home.
            if task == 'work_day_over':
                break

            #: Workers starts collecting celex numbers for particular task (year)
            get_celex_numbers(task)
            print('Worker {} has completed task {}.'.format(self.number, task))

        print("Worker {} going home. Bye!".format(self.number))

def build_work_force(queue, number_of_workers):

    workers = []
    for i in range(number_of_workers):
        worker = Consumer(queue, i)
        worker.start()
        workers.append(worker)

    return workers


class Producer():

    queue = deque()

    for y in range(1950, 1970):
        queue.append(y)

    workers = build_work_force(queue, 10)

    for worker in workers:
        queue.append('work_day_over')
    
    production_time = time.time()

    for worker in workers:
        worker.join()
    
    print('Job is done. Time needed : {}.'.format(round(time.time() - production_time, 6)))

if __name__=='__main__':
    Producer()

    # Job is done. Time needed : 2539.416711. 4 workers
    # Job is done. Time needed : 1627.934864. 10 workers (many finished early and were waiting for
    # the last one to finish.)

