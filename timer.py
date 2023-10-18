import time
import datetime

class Timer():
        def __init__(self):
            self.start_time = time.time()

        def get_duration(self):
            return str(datetime.timedelta(seconds=time.time() - self.start_time))