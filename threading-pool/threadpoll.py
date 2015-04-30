#!/usr/bin/env python
# -*- coding:utf-8 -*-


import Queue
import time
import threading
import sys


class Worker(threading.Thread):
    def __init__(self, work_queue, result_queue, **kwargs):
        super(Worker, self).__init__(**kwargs)
        self.setDaemon(True)
        self.work_queue = work_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            try:
                func, args, kwargs = self.work_queue.get(block=False)
                res = func(*args, **kwargs)
                self.result_queue.put(res)
            except Queue.Empty:
                break


class WorkerManger(object):
    def __init__(self, num_of_workers=10):
        self.work_queue = Queue.Queue()
        self.result_queue = Queue.Queue()
        self.workers = []
        self._result_threads(num_of_workers)

    def _result_threads(self, num_of_workers):
        for i in range(num_of_workers):
            worker = Worker(self.work_queue, self.result_queue)
            self.workers.append(worker)

    def start(self):
        for w in self.workers:
            w.start()

    def wait_for_complete(self):
        while len(self.workers):
            worker = self.workers.pop()
            worker.join()

            if worker.isAlive() and not self.work_queue.empty():
                self.workers.append(worker)
        print "All jobs were completed."

    def add_job(self, func, *args, **kwargs):
        self.work_queue.put((func, args, kwargs))

    def get_result(self, *args, **kwargs):
        return self.result_queue.get(*args, **kwargs)


def task(num):
    print "do tasking {}".format(num)
    print threading.current_thread()


worker_manger = WorkerManger(5)

for i in range(100):
    worker_manger.add_job(task, i)

worker_manger.start()
worker_manger.wait_for_complete()





