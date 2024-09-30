"""
Module for friction brake related methods.
"""

import logging
from multiprocessing import Process, Value
from time import sleep, time

import pyautogui as pag

MAX_FRICTION_BRAKE = 30
UP = 1
DOWN = -1
FRICTION_BRAKE_MONITOR_DELAY = 2

logger = logging.getLogger(__name__)


class FrictionBrake:
    """Friction brake controller."""

    def __init__(self, setting, monitor, lock) -> None:
        self.setting = setting
        self.monitor = monitor
        self.cur_friction_brake = Value("i", setting.initial_friction_brake)
        self.lock = lock
        self.initialized = False
        self.monitor_process = Process(target=monitor_friction_brake, args=(self,))

    def reset(
        self,
        target_friction_brake: int,
        initialized: bool,
    ) -> None:
        """Reset to the target friction brake.

        :param target_friction_brake: target friction brake to reset
        :type target_friction_brake: int
        :param initialized: whether it's the fisrt time to reset the friction brake
        :type initialized: bool
        """
        logger.info("Resetting friction brake")
        if not initialized:
            for _ in range(MAX_FRICTION_BRAKE):
                pag.scroll(UP, _pause=False)
            self.cur_friction_brake.value = MAX_FRICTION_BRAKE

        diff = self.cur_friction_brake.value - target_friction_brake
        direction = DOWN if diff > 0 else UP
        for _ in range(abs(diff)):
            pag.scroll(direction, _pause=False)
        self.cur_friction_brake.value = target_friction_brake

    def change(self, max_friction_brake: int, increase) -> None:
        """Increae or decrease friction.

        :param max_friction_brake: maximum friction brake
        :type max_friction_brake: int
        :param increase: increae or decreae the friction brake
        :type increase: bool
        """
        if increase:
            if self.cur_friction_brake.value < max_friction_brake:
                pag.scroll(UP, _pause=False)
                self.cur_friction_brake.value += 1
        else:
            if self.cur_friction_brake.value > 0:
                pag.scroll(DOWN, _pause=False)
                self.cur_friction_brake.value -= 1


def monitor_friction_brake(friction_brake):
    """Monitor friction brake bar and change it accordingly.

    This is used as target function in multiprocess.Process and must be pickable,
    thus it must be declared as a global function instead of a instance method.

    :param friction_brake: friction brake controller
    :type friction_brake: FrictionBrake
    """
    logger.info("Monitoring friction brake")

    pre_time = time()
    try:
        while True:
            if not friction_brake.monitor.is_fish_hooked_pixel():
                sleep(FRICTION_BRAKE_MONITOR_DELAY)
                continue
            with friction_brake.lock:
                if friction_brake.monitor.is_friction_brake_high():
                    friction_brake.change(
                        friction_brake.setting.max_friction_brake,
                        False,
                    )
                else:
                    cur_time = time()
                    if (
                        cur_time - pre_time
                        < friction_brake.setting.friction_brake_increase_delay
                    ):
                        continue
                    pre_time = cur_time
                    friction_brake.change(
                        friction_brake.setting.max_friction_brake,
                        True,
                    )
            sleep(friction_brake.setting.friction_brake_check_delay)
    except KeyboardInterrupt:
        pass
