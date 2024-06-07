"""
Module for Timer class.
"""

import time
import datetime

TEA_DRINK_DELAY = 300


class Timer:
    """Class for calculating and generatiing timestamps for logs."""

    # pylint: disable=too-many-instance-attributes
    # there are too many counters...

    def __init__(self):
        """Constructor method."""
        self.start_time = time.time()
        self.start_datetime = time.strftime("%m/%d %H:%M:%S", time.localtime())

        self.cast_rhour = None
        self.cast_ghour = None
        self.cast_rhour_list = []
        self.cast_ghour_list = []

        self.pre_tea_drink_time = 0
        self.pre_alcohol_drink_time = 0

    def get_duration(self) -> str:
        """Calculate the execution time of the program.

        :return: formatted execution time (hh:mm:ss)
        :rtype: str
        """
        return str(
            datetime.timedelta(seconds=int(time.time() - self.start_time))
        )  # truncate to seconds

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
        """Update latest real and in-game hour of casting."""
        dt = datetime.datetime.now()
        self.cast_rhour = int((time.time() - self.start_time) // 3600)
        self.cast_ghour = int((dt.minute / 60 + dt.second / 3600) * 24 % 24)

    def add_cast_hour(self) -> None:
        """Record latest real and in-game hour"""
        self.cast_rhour_list.append(self.cast_rhour)
        self.cast_ghour_list.append(self.cast_ghour)

    def get_cast_hour_list(self) -> tuple[list[int]]:
        """Getter.

        :return: lists of real and in-game hours
        :rtype: tuple[list[int]]
        """
        return self.cast_rhour_list, self.cast_ghour_list

    def is_tea_drinkable(self) -> bool:
        """Check if it has been a long time since the last tea consumption.

        :return: True if long enough, False otherwise
        :rtype: bool
        """
        cur_time = time.time()
        if cur_time - self.pre_tea_drink_time > TEA_DRINK_DELAY:
            self.pre_tea_drink_time = cur_time
            return True
        return False

    def is_alcohol_drinkable(self, alcohol_drink_delay) -> bool:
        """Check if it has been a long time since the last alcohol consumption.

        :return: True if long enough, False otherwise
        :rtype: bool
        """
        if time.time() - self.pre_alcohol_drink_time > alcohol_drink_delay:
            self.pre_alcohol_drink_time = time.time()
            self.pre_tea_drink_time = time.time()  # no need to drink tea so fast
            return True
        return False
