#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import threading
import Queue
import time


class Worker(threading.Thread):
    request_id = 0

    def __init__(self, request_queue, result_queue, **kwargs):
        super(Worker, self).__init__(**kwargs)
        self.setDaemon(True)
        self.request_queue = request_queue
        self.result_queue = result_queue
        self.start()

    def perform_work(self, func, *args, **kwargs):
        Worker.request_id += 1
        self.request_queue.put((Worker.request_id, func, args, kwargs))
        return self.result_queue.get()

    def run(self):
        while True:
            request_id, func, args, kwargs = self.request_queue.get()
            self.result_queue.put((request_id, func(*args, **kwargs)))


def hello(name):
    time.sleep(1)
    return "hello {}".format(name)


request_queue = Queue.Queue()
result_queue = Queue.Queue()

for i in range(1, 10):
    worker = Worker(request_queue, result_queue)
    print worker.perform_work(hello, i)


