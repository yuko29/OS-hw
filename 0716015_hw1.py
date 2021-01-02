import itertools
import hashlib
import requests
from bs4 import BeautifulSoup
import threading
import time
import queue
import multiprocessing
import asyncio

# task data queue
shareQueue = queue.Queue()

# lock
lock = threading.Lock()
m = multiprocessing.Manager()
#lock = m.Lock()
# execute time
executionTime = []

def task1(s):
    S = s.encode()
    for item in itertools.product(range(0x21, 0x7E), repeat=5):
        C = bytes(item)
        if hashlib.sha256(C+S).hexdigest()[0:5] == "00000":
            print((C+S).decode())
            return 0

def task2(url):
    headers = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    print(soup.title.text)
    return 0

async def task1_async(s):
    S = s.encode()
    for item in itertools.product(range(0x21, 0x7E), repeat=5):
        C = bytes(item)
        if hashlib.sha256(C+S).hexdigest()[0:5] == "00000":
            print((C+S).decode())
            return 0

async def task2_async(url):
    r = await loop.run_in_executor(None, requests.get, url)
    soup = BeautifulSoup(r.text, "html.parser")
    print(soup.title.text)
    end = time.time()
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

method, line = input().split(" ")
method = int(method)
line = int(line)

taskNumber = int(input())

for i in range(taskNumber):
    shareQueue.put(input())

# main
if method == 1:
    threads = []
    start = time.time()
    for i in range(line):
        threads.append(threading.Thread(target=distribute, args=(task,)))
        threads[i].start()
    for i in range(line):
        threads[i].join()
    end = time.time()
    executionTime.append(end-start)
elif method == 2:
    pool = multiprocessing.Pool(processes=line)
    start = time.time()
    if task == 1:
        for i in range(taskNumber):
            s = shareQueue.get()
            pool.apply_async(task1, (s,))
        pool.close()
        pool.join()
    else:
        for i in range(taskNumber):
            s = shareQueue.get()
            pool.apply_async(task2, (s,))
        pool.close()
        pool.join()
    end = time.time()
    executionTime.append(end-start)
elif method == 3:
    tasks = []
    loop = asyncio.get_event_loop()
    start = time.time()
    if task == 1:
        for i in range(taskNumber):
            s = shareQueue.get()
            task = loop.create_task(task1_async(s))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))
    else:
        for i in range(taskNumber):
            s = shareQueue.get()
            task = loop.create_task(task2_async(s))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))
    end = time.time()
    executionTime.append(end-start)



print(sum(executionTime))
print("Done.")

