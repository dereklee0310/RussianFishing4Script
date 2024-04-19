"""
Module for Timer class.
"""
import time
import datetime

class Timer():
    """Class for calculating and generatiing timestamps for logs.
    """
    cast_rhour = None
    cast_ghour = None
    cast_rhour_list = []
    cast_ghour_list = []


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
    
    def update_cast_hour(self) -> None:
        """Update latest real and in-game hour of casting.
        """
        dt = datetime.datetime.now()
        self.cast_rhour = int((time.time() - self.start_time) // 3600)
        self.cast_ghour = int((dt.minute / 60 + dt.second / 3600) * 24 % 24)
    
    def add_cast_hour(self) -> None:
        """Record latest real and in-game hour
        """
        self.cast_rhour_list.append(self.cast_rhour)
        self.cast_ghour_list.append(self.cast_ghour)

    def get_cast_hour_list(self) -> tuple[list[int]]:
        """Getter.

        :return: lists of real and in-game hours 
        :rtype: tuple[list[int]]
        """
        return self.cast_rhour_list, self.cast_ghour_list