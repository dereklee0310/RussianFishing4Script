"""Module for Timer class.

This module provides functionality for managing timers and generating timestamps
for logging and automation purposes in Russian Fishing 4.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import datetime
import logging
import sys
import time
from pathlib import Path

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

from rf4s.utils import is_compiled

logger = logging.getLogger("rich")


if is_compiled():
    ROOT = Path(sys.executable).parent  # Running as .exe (Nuitka/PyInstaller)
else:
    ROOT = Path(__file__).resolve().parents[2]


class Timer:
    """Class for calculating and generating timestamps for logs.

    This class manages various timers and counters for tracking in-game events,
    such as casting times, consumable cooldowns, and script pauses.

    Attributes:
        cfg (CfgNode): Configuration node for timer settings.
        start_time (float): Timestamp when the timer was initialized.
        start_datetime (str): Formatted start date and time.
        cast_rhour (int | None): Real-time hour of the last cast.
        cast_ghour (int | None): In-game hour of the last cast.
        cast_rhour_list (list[int]): List of real-time hours for casts.
        cast_ghour_list (list[int]): List of in-game hours for casts.
        last_tea_drink (float): Timestamp of the last tea consumption.
        last_alcohol_drink (float): Timestamp of the last alcohol consumption.
        last_lure_change (float): Timestamp of the last lure change.
        last_spod_rod_recast (float): Timestamp of the last spod rod recast.
        last_pause (float): Timestamp of the last script pause.
    """

    def __init__(self, cfg):
        """Initialize the Timer class with configuration settings.

        :param cfg: Configuration node for timer settings.
        :type cfg: CfgNode
        """
        self.cfg = cfg
        self.start_time = time.time()
        self.start_datetime = time.strftime("%m/%d %H:%M:%S", time.localtime())

        self.cast_rhour = None
        self.cast_ghour = None
        self.cast_rhour_list = []
        self.cast_ghour_list = []

        self.last_tea_drink = 0
        self.last_alcohol_drink = 0
        self.last_lure_change = self.start_time
        self.last_spod_rod_recast = self.start_time
        self.last_pause = self.start_time

    def get_running_time(self) -> str:
        """Calculate the execution time of the program.

        :return: Formatted execution time (hh:mm:ss).
        :rtype: str
        """
        return time.time() - self.start_time

    def get_running_time_str(self) -> str:
        """Calculate the execution time of the program.

        :return: Formatted execution time (hh:mm:ss).
        :rtype: str
        """
        return str(
            datetime.timedelta(seconds=int(time.time() - self.start_time))
        )  # truncate to seconds

    def get_cur_timestamp(self) -> str:
        """Generate timestamp for images in screenshots/.

        :return: Current timestamp.
        :rtype: str
        """
        return time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime())

    def get_start_datetime(self) -> str:
        """Generate a simplified timestamp for quit message.

        :return: Start date and time.
        :rtype: str
        """
        return self.start_datetime

    def get_cur_datetime(self) -> str:
        """Generate a simplified timestamp for quit message.

        :return: Current date and time.
        :rtype: str
        """
        return time.strftime("%m/%d %H:%M:%S", time.localtime())

    def update_cast_time(self) -> None:
        """Update the latest real and in-game hour of casting."""
        dt = datetime.datetime.now()
        self.cast_rhour = int((time.time() - self.start_time) // 3600)
        self.cast_ghour = int((dt.minute / 60 + dt.second / 3600) * 24 % 24)

    def add_cast_time(self) -> None:
        """Record the latest real and in-game hour of casting."""
        self.cast_rhour_list.append(self.cast_rhour)
        self.cast_ghour_list.append(self.cast_ghour)

    def get_cast_time_list(self) -> tuple[list[int]]:
        """Get lists of real and in-game hours for casts.

        :return: Lists of real and in-game hours.
        :rtype: tuple[list[int]]
        """
        return self.cast_rhour_list, self.cast_ghour_list

    def is_tea_drinkable(self) -> bool:
        """Check if it has been a long time since the last tea consumption.

        :return: True if long enough, False otherwise.
        :rtype: bool
        """
        cur_time = time.time()
        if cur_time - self.last_tea_drink > self.cfg.STAT.TEA_DELAY:
            self.last_tea_drink = cur_time
            return True
        return False

    def is_alcohol_drinkable(self) -> bool:
        """Check if it has been a long time since the last alcohol consumption.

        :return: True if long enough, False otherwise.
        :rtype: bool
        """
        cur_time = time.time()
        if cur_time - self.last_alcohol_drink > self.cfg.STAT.ALCOHOL_DELAY:
            self.last_alcohol_drink = cur_time
            self.last_tea_drink = cur_time  # Alcohol also refill comfort
            return True
        return False

    def is_lure_changeable(self):
        """Check if it has been a long time since the last lure change.

        :return: True if long enough, False otherwise.
        :rtype: bool
        """
        cur_time = time.time()
        if cur_time - self.last_lure_change > self.cfg.SCRIPT.LURE_CHANGE_DELAY:
            self.last_lure_change = cur_time
            return True
        return False

    def is_spod_rod_castable(self):
        """Check if it has been a long time since the last spod rod recast.

        :return: True if long enough, False otherwise.
        :rtype: bool
        """
        cur_time = time.time()
        if cur_time - self.last_spod_rod_recast > self.cfg.SCRIPT.SPOD_ROD_RECAST_DELAY:
            self.last_spod_rod_recast = cur_time
            return True
        return False

    def is_script_pausable(self):
        """Check if it has been a long time since the last script pause.

        :return: True if long enough, False otherwise.
        :rtype: bool
        """
        cur_time = time.time()
        if cur_time - self.last_pause > self.cfg.PAUSE.DELAY:
            self.last_pause = cur_time
            return True
        return False

    def save_data(self) -> None:
        """Plot and save an image using rhour and ghour lists from the timer object."""
        cast_rhour_list, cast_ghour_list = self.get_cast_time_list()
        if not cast_rhour_list:
            logger.warning("No cast record, skip plotting")
            return

        logger.info("Plotting line chart")

        _, ax = plt.subplots(nrows=1, ncols=2)
        # _.canvas.manager.set_window_title('Record')
        ax[0].set_ylabel("Fish")

        last_rhour = cast_rhour_list[-1]  # Hour: 0, 1, 2, 3, 4, "5"
        fish_per_rhour = [0] * (last_rhour + 1)  # Idx: (0, 1, 2, 3, 4, 5) = 6
        for hour in cast_rhour_list:
            fish_per_rhour[hour] += 1
        ax[0].plot(range(last_rhour + 1), fish_per_rhour, marker=".")
        ax[0].set_title("Fish Caughted per Real Hour")
        ax[0].set_xticks(range(last_rhour + 2))
        ax[0].set_xlabel("Hour (real running time)")
        ax[0].yaxis.set_major_locator(MaxNLocator(integer=True))

        fish_per_ghour = [0] * 24
        for hour in cast_ghour_list:
            fish_per_ghour[hour] += 1
        ax[1].bar(range(0, 24), fish_per_ghour)
        ax[1].set_title("Fish Caughted per Game Hour")
        ax[1].set_xticks(range(0, 24, 2))
        ax[1].set_xlabel("Hour (game time)")
        ax[1].yaxis.set_major_locator(MaxNLocator(integer=True))

        # plt.tight_layout()
        plt.savefig(str(ROOT / f"logs/{self.get_cur_timestamp()}.png"))
        logger.info("Chart has been saved under logs/")
