import logging
from time import sleep
import pyautogui as pag
from typing import Callable

from multiprocessing.sharedctypes import Synchronized
from multiprocessing.synchronize import Lock
from multiprocessing import Process, Value

MAX_FRICTION_BRAKE = 30
UP = 1
DOWN = -1
FRICTION_BRAKE_MONITOR_DELAY = 2

logger = logging.getLogger(__name__)

class FrictionBrake:
    def __init__(self, setting, monitor, friction_brake_lock) -> None:
        self.cur_friction_brake = Value("i", setting.initial_friction_brake)
        self.initialized = False
        self.monitor_process = Process(
            target=monitor_friction_brake,
            args=(
                self.cur_friction_brake,
                self.change_friction_brake,
                monitor.is_fish_hooked_pixel,
                monitor.is_friction_brake_high,
                setting.friction_brake_check_delay,
                setting.friction_brake_increase_delay,
                setting.max_friction_brake,
                friction_brake_lock
                )
            )

    def reset_friction_brake(self, cur_friction_brake: Synchronized, target_friction_brake: int , initialized: bool) -> None:
        """Reset to the target friction brake.

        :param cur_friction_brake: current friction brake
        :type cur_friction_brake: Synchronized
        :param target_friction_brake: target friction brake to reset
        :type target_friction_brake: int
        :param initialized: whether it's the fisrt time to reset the friction brake
        :type initialized: bool
        """
        logger.info("Resetting friction brake")
        if not initialized:
            for _ in range(MAX_FRICTION_BRAKE):
                pag.scroll(UP)
            cur_friction_brake.value = MAX_FRICTION_BRAKE

        diff = cur_friction_brake.value - target_friction_brake
        direction = DOWN if diff > 0 else UP
        for _ in range(abs(diff)):
            pag.scroll(direction)
        cur_friction_brake.value = target_friction_brake

    def change_friction_brake(self, cur_friction_brake: Synchronized, max_friction_brake: int, increase) -> None:
        """Increae or decrease friction.

        :param cur_friction_brake: current friction brake
        :type cur_friction_brake: Synchronized
        :param max_friction_brake: maximum friction brake
        :type max_friction_brake: int
        :param increase: increae or decreae the friction brake
        :type increase: bool
        """
        if increase:
            if cur_friction_brake.value < max_friction_brake:
                pag.scroll(UP)
                cur_friction_brake.value += 1
        else:
            if cur_friction_brake.value > 0:
                pag.scroll(DOWN)
                cur_friction_brake.value -= 1

# this be used as target in multiprocess.Process and must be pickable
# thus it must be declared as a global function instead of a instance method

def monitor_friction_brake(
        cur_friction_brake: Synchronized,
        change_friction_brake: Callable,
        is_fish_hooked: Callable,
        is_friction_brake_high: Callable,
        check_delay: int,
        increase_delay: int,
        max_friction_brake: int,
        friction_brake_lock: Lock):
    """Monitor friction brake bar and change it accordingly.

    :param cur_friction_brake: current friction brake
    :type cur_friction_brake: Synchronized
    :param change_friction_brake: FrictionBrake.change_friction_brake()
    :type change_friction_brake: Callable
    :param is_fish_hooked: Monitor.is_fish_hooked_pixel()
    :type is_fish_hooked: Callable
    :param is_friction_brake_high: Monitor.is_friction_brake_high
    :type is_friction_brake_high: Callable
    :param check_delay: main loop delay
    :type check_delay: int
    :param increase_delay: delay before increasing friction brake
    :type increase_delay: int
    :param max_friction_brake: maximum friction brake
    :type max_friction_brake: int
    :param friction_brake_lock: mutex lock for cur_friction_brake
    :type friction_brake_lock: Lock
    """
    logger.info("Monitoring friction brake")
    try:
        while True:
            if not is_fish_hooked():
                sleep(FRICTION_BRAKE_MONITOR_DELAY)
                continue
            with friction_brake_lock:
                if is_friction_brake_high():
                    change_friction_brake(cur_friction_brake, max_friction_brake, False)
                else:
                    sleep(increase_delay)
                    change_friction_brake(cur_friction_brake, max_friction_brake, True)
            sleep(check_delay)
    except KeyboardInterrupt:
        pass