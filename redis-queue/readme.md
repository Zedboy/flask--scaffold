

### 任务异步化

打开浏览器，输入地址，按下回车，打开了页面。于是一个`HTTP`请求（`request`）就由客户端发送到服务器，服务器处理请求，返回响应（`response`）内容。

我们每天都在浏览网页，发送大大小小的请求给服务器。有时候，服务器接到了请求，会发现他也需要给另外的服务器发送请求，或者服务器也需要做另外一些事情，于是最初们发送的请求就被阻塞了，也就是要等待服务器完成其他的事情。

更多的时候，服务器做的额外事情，并不需要客户端等待，这时候就可以把这些额外的事情异步去做。从事异步任务的工具有很多。主要原理还是处理通知消息，针对通知消息通常采取是队列结构。生产和消费消息进行通信和业务实现。

### 生产消费与队列

上述异步任务的实现，可以抽象为生产者消费模型。如同一个餐馆，厨师在做饭，吃货在吃饭。如果厨师做了很多，暂时卖不完，厨师就会休息；如果客户很多，厨师马不停蹄的忙碌，客户则需要慢慢等待。实现生产者和消费者的方式用很多，下面使用`Python`标准库`Queue`写个小例子：

```python

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
            print "厨师 {} 做了 {} 饭 --- 还剩 {} 饭没卖完".format(self.name, elem, queue.qsize())
            time.sleep(random.random())

class Consumer(Thread):
    def run(self):
        while True:
            elem = queue.get()
            print "吃货{} 吃了 {} 饭 --- 还有 {} 饭可以吃".format(self.name, elem, queue.qsize())
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

```

大概输出如下：

```
厨师 Thread-1 做了 1 饭 --- 还剩 1 饭没卖完
厨师 Thread-2 做了 8 饭 --- 还剩 2 饭没卖完
厨师 Thread-3 做了 3 饭 --- 还剩 3 饭没卖完
吃货Thread-4 吃了 1 饭 --- 还有 2 饭可以吃
吃货Thread-5 吃了 8 饭 --- 还有 1 饭可以吃
吃货Thread-4 吃了 3 饭 --- 还有 0 饭可以吃
厨师 Thread-1 做了 0 饭 --- 还剩 1 饭没卖完
厨师 Thread-2 做了 0 饭 --- 还剩 2 饭没卖完
厨师 Thread-1 做了 1 饭 --- 还剩 3 饭没卖完
厨师 Thread-1 做了 1 饭 --- 还剩 4 饭没卖完
吃货Thread-4 吃了 0 饭 --- 还有 3 饭可以吃
厨师 Thread-3 做了 3 饭 --- 还剩 4 饭没卖完
吃货Thread-5 吃了 0 饭 --- 还有 3 饭可以吃
吃货Thread-5 吃了 1 饭 --- 还有 2 饭可以吃
厨师 Thread-2 做了 8 饭 --- 还剩 3 饭没卖完
厨师 Thread-2 做了 8 饭 --- 还剩 4 饭没卖完
```

### Redis 队列

Python内置了一个好用的队列结构。我们也可以是用redis实现类似的操作。并做一个简单的异步任务。

Redis提供了两种方式来作消息队列。一个是使用`生产者消费模式`模式，另外一个方法就是`发布订阅者模式`。前者会让一个或者多个客户端监听消息队列，一旦消息到达，消费者马上消费，谁先抢到算谁的，如果队列里没有消息，则消费者继续监听。后者也是一个或多个客户端订阅消息频道，只要发布者发布消息，所有订阅者都能收到消息，订阅者都是品等的。

### 生产消费模式

主要使用了redis提供的blpop获取队列数据，如果队列没有数据则阻塞等待，也就是监听。

```python

import redis

class Task(object):
    def __init__(self):
        self.rcon = redis.StrictRedis(host='localhost', db=5)
        self.queue = 'task:prodcons:queue'

    def listen_task(self):
        while True:
            task = self.rcon.blpop(self.queue, 0)[1]
            print "Task get", task

if __name__ == '__main__':
    print 'listen task queue'
    Task().listen_task()

```

### 发布订阅模式

使用redis的pubsub功能，订阅者订阅频道，发布者发布消息到频道了，频道就是一个消息队列。

```python
import redis


class Task(object):

    def __init__(self):
        self.rcon = redis.StrictRedis(host='localhost', db=5)
        self.ps = self.rcon.pubsub()
        self.ps.subscribe('task:pubsub:channel')

    def listen_task(self):
        for i in self.ps.listen():
            if i['type'] == 'message':
                print "Task get", i['data']

if __name__ == '__main__':
    print 'listen task channel'
    Task().listen_task()

```

### Flask 入口

我们分别实现了两种异步任务的后端服务，直接启动他们，就能监听redis队列或频道的消息了。简单的测试如下：

```python


import redis
import random
import logging
from flask import Flask, redirect

app = Flask(__name__)

rcon = redis.StrictRedis(host='localhost', db=5)
prodcons_queue = 'task:prodcons:queue'
pubsub_channel = 'task:pubsub:channel'

@app.route('/')
def index():

    html = """
<br>
<center><h3>Redis Message Queue</h3>
<br>
<a href="/prodcons">生产消费者模式</a>
<br>
<br>
<a href="/pubsub">发布订阅者模式</a>
</center>
"""
    return html


@app.route('/prodcons')
def prodcons():
    elem = random.randrange(10)
    rcon.lpush(prodcons_queue, elem)
    logging.info("lpush {} -- {}".format(prodcons_queue, elem))
    return redirect('/')

@app.route('/pubsub')
def pubsub():
    ps = rcon.pubsub()
    ps.subscribe(pubsub_channel)
    elem = random.randrange(10)
    rcon.publish(pubsub_channel, elem)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

```

启动脚本，使用

    siege -c10 -r 5 http://127.0.0.1:5000/prodcons
    siege -c10 -r 5 http://127.0.0.1:5000/pubsub
     
可以分别在监听的脚本输入中看到异步消息。在异步的任务中，可以执行一些耗时间的操作，当然目前这些做法并不知道异步的执行结果，如果需要知道异步的执行结果，可以考虑设计协程任务或者使用一些工具如`RQ`或者`celery`等。