import time
import datetime

class Timer():
    def __init__(self):
        self.start_time = time.time()
        self.start_datetime = time.strftime("%m/%d %H:%M:%S", time.localtime())

    def get_duration(self):
        return str(datetime.timedelta(seconds=int(time.time() - self.start_time))) # truncate to seconds
    
    def get_cur_timestamp(self):
        return time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime())
    
    def get_cur_datetime(self):
        return time.strftime("%m/%d %H:%M:%S", time.localtime())
    
    def get_start_datetime(self):
        return self.start_datetime