#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import random
import time
from Queue import Queue
from threading import Thread


queue = Queue(10)


class Producer(Thread):
    def run(self):
        while True:
            elem = random.randrange(9)
            queue.put(elem)
            print "Producer --- {} Size --- {}".format(elem, queue.qsize())
            time.sleep(random.random())


class Consumer(Thread):
    def run(self):
        while True:
            elem = queue.get()
            print "Consumer --- {} Size --- {}".format(elem, queue.qsize())
            time.sleep(random.random())


def main():
    for i in range(3):
        p = Producer()
        p.start()
    for i in range(2):
        c = Consumer()
        c.start()


if __name__ == '__main__':
    main()

