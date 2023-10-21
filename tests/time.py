import time
import datetime
from time import sleep

t = time.localtime()
hour = int(time.strftime("%H", t))
min = int(time.strftime("%M", t))
timestamp = (hour * 60 + min)
print(timestamp)

# print(hours, mins)

t1 = time.time()
sleep(3)
t2 = time.time()
t3 = t2 - t1
print(t3)
print(datetime.timedelta(seconds=t3))
print(datetime.timedelta(seconds=int(t3)))