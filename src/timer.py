"""
Module for Timer class.
"""
import time
import datetime

class Timer():
    """Class for calculating and generatiing timestamps for logs.
    """
    def __init__(self):
        """Constructor method.
        """
        self.start_time = time.time()
        self.start_datetime = time.strftime("%m/%d %H:%M:%S", time.localtime())

    def get_duration(self) -> str:
        """Calculate the execution time of the program.

        :return: formatted execution time (hh:mm:ss)
        :rtype: str
        """
        return str(datetime.timedelta(seconds=int(time.time() - self.start_time))) # truncate to seconds
    
    def get_cur_timestamp(self) -> str:
        """Generate timestamp for images in screenshots/.

        :return: current timestamp
        :rtype: str
        """
        return time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime())
    
    def get_start_datetime(self) -> str:
        """Generate a simplified timestamp for quit message.

        :return: start date and time
        :rtype: str
        """
        return self.start_datetime

    def get_cur_datetime(self) -> str:
        """Generate a simplified timestamp for quit message.

        :return: current date and time
        :rtype: str
        """
        return time.strftime("%m/%d %H:%M:%S", time.localtime())
    