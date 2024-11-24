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
        self.monitor_process = Process(target=monitor_friction_brake, args=(self,))

    def reset(
        self,
        target_friction_brake: int,
    ) -> None:
        """Reset to the target friction brake.

        :param target_friction_brake: target friction brake to reset
        :type target_friction_brake: int
        """
        logger.info("Resetting friction brake")
        for _ in range(MAX_FRICTION_BRAKE):
            pag.scroll(UP)

        diff = MAX_FRICTION_BRAKE - target_friction_brake
        for _ in range(abs(diff)):
            pag.scroll(DOWN)
        self.cur_friction_brake.value = target_friction_brake

    def change(self, increase: bool) -> None:
        """Increae or decrease friction.

        :param increase: increae or decreae the friction brake
        :type increase: bool
        """
        if increase:
            if self.cur_friction_brake.value < self.setting.max_friction_brake:
                pag.scroll(UP, _pause=False)
                self.cur_friction_brake.value += 1
        else:
            if self.cur_friction_brake.value > 0:
                pag.scroll(DOWN, _pause=False)
                self.cur_friction_brake.value -= 1
        sleep(0.04)


def monitor_friction_brake(friction_brake):
    """Monitor friction brake bar and change it accordingly.

    This is used as target function in multiprocess.Process and must be pickable,
    thus it must be declared as a global function instead of a instance method.

    :param friction_brake: friction brake controller
    :type friction_brake: FrictionBrake
    """
    logger.info("Monitoring friction brake")

    pre_time = time()
    fish_hooked = False
    try:
        while True:
            if not friction_brake.monitor.is_fish_hooked_pixel():
                sleep(FRICTION_BRAKE_MONITOR_DELAY)
                fish_hooked = False
                continue
            else:
                if not fish_hooked:
                    sleep(friction_brake.setting.friction_brake_adjust_delay)
                    fish_hooked = True
            with friction_brake.lock:
                if friction_brake.monitor.is_friction_brake_high():
                    friction_brake.change(increase=False)
                else:
                    cur_time = time()
                    if (
                        cur_time - pre_time
                        < friction_brake.setting.friction_brake_increase_delay
                    ):
                        continue
                    pre_time = cur_time
                    friction_brake.change(increase=True)
    except KeyboardInterrupt:
        pass
