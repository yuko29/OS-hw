import itertools
import hashlib
import requests
from bs4 import BeautifulSoup
import threading
import time
import queue
import multiprocessing
import asyncio
import os

# task data queue
shareQueue = queue.Queue()

# lock
lock = threading.Lock()
#m = multiprocessing.Manager()
#lock = m.Lock()
# execute time
executionTime = []

def task1(q):
    while q.empty()!=True:
        s = q.get()
        S = s.encode()
        for item in itertools.product(range(0x21, 0x7E), repeat=5):
            C = bytes(item)
            if hashlib.sha256(C+S).hexdigest()[0:5] == "00000":
                print((C+S).decode())
                break
        #print("current alive: " , threading.active_count())
        q.task_done()
    return 0

def task2(q):
    while q.empty()!=True:
        url = q.get()
        headers = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
        }
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        print(soup.title.text)
        #print("current alive: " , threading.active_count())
        #print("pid: ", os.getpid())
        q.task_done()
    return 0

async def task1_async(s):
    S = s.encode()
    for item in itertools.product(range(0x21, 0x7E), repeat=5):
        C = bytes(item)
        if hashlib.sha256(C+S).hexdigest()[0:5] == "00000":
            print((C+S).decode())
            print("pid: ", os.getpid())
            return 0

async def task2_async(url):
    r = await loop.run_in_executor(None, requests.get, url)
    soup = BeautifulSoup(r.text, "html.parser")
    print(soup.title.text)
    return 0


def distribute(task):
    s = ""
    lock.acquire()
    while shareQueue.empty() != True:
        s = shareQueue.get()
        lock.release()
        if task == 1:
            start = time.time()
            task1(s)
            end = time.time()
            executionTime.append(end-start)
        else:
            start = time.time()
            task2(s)
            end = time.time()
            executionTime.append(end-start)
        lock.acquire()
    lock.release()

# input
task = int(input())

#method, line = input().split(" ")

method = 0
line = 0

methodRow = input().split(" ")
if len(methodRow)==2:
    method = int(methodRow[0])
    line = int(methodRow[1])
else:
    method = int(methodRow[0])


taskNumber = int(input())

# main
if method == 1:
    threads = []
    shareQueue = queue.Queue()
    for i in range(taskNumber):
        shareQueue.put(input())
    start = time.time()
    if task == 1:
        for i in range(line):
            threads.append(threading.Thread(target=task1, args=(shareQueue,)))
            threads[i].start()
        for i in range(line):
            threads[i].join()
        end = time.time()
        executionTime.append(end-start)
    elif task == 2:
        for i in range(line):
            threads.append(threading.Thread(target=task2, args=(shareQueue,)))
            threads[i].start()
        for i in range(line):
            threads[i].join()
        end = time.time()
        executionTime.append(end-start)
elif method == 2:
    m = multiprocessing.Manager()
    q = m.Queue()
    for i in range(taskNumber):
        q.put(input())
    processess = []
    start = time.time()
    if task == 1:
        for i in range(line):
            processess.append(multiprocessing.Process(target=task1, args=(q,)))
            processess[i].start()
        for i in range(line):
            processess[i].join()
    elif task == 2:
        for i in range(line):
            processess.append(multiprocessing.Process(target=task2, args=(q,)))
            processess[i].start()
        for i in range(line):
            processess[i].join()
    end = time.time()
    executionTime.append(end-start)
elif method == 3:
    for i in range(taskNumber):
        shareQueue.put(input())
    tasks = []
    loop = asyncio.get_event_loop()
    start = 0
    if task == 1:
        for i in range(taskNumber):
            s = shareQueue.get()
            task = loop.create_task(task1_async(s))
            tasks.append(task)
        start = time.time()
        loop.run_until_complete(asyncio.wait(tasks))
    else:
        for i in range(taskNumber):
            s = shareQueue.get()
            task = loop.create_task(task2_async(s))
            tasks.append(task)
        start = time.time()
        loop.run_until_complete(asyncio.wait(tasks))
    end = time.time()
    executionTime.append(end-start)


print("execute time: ", sum(executionTime))

