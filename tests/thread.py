from threading import Thread
from time import sleep

def count(thread_id):
    for i in range(10):
        print(f'{thread_id}_{i}')
        sleep(1)

thread1 = Thread(target=count, args=('thread1', ))
thread2 = Thread(target=count, args=('thread2', ))

thread1.start()
thread2.start()

thread1.join()
thread2.join()