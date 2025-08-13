"""Module for friction brake related methods.

This module provides functionality for managing the friction brake in Russian Fishing 4,
including resetting, adjusting, and monitoring the friction brake.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

from multiprocessing import Process, Value
from time import sleep, time

import pyautogui as pag

from rf4s.controller import logger
from rf4s.controller.detection import Detection

MAX_FRICTION_BRAKE = 30
MIN_FRICTION_BRAKE = 0
UP = 1
DOWN = -1
FRICTION_BRAKE_MONITOR_DELAY = 2
FRICTION_BRAKE_CHANGE_DELAY = 0.04


class FrictionBrake:
    """Friction brake controller.

    This class handles the adjustment and monitoring of the friction brake during gameplay.

    Attributes:
        cfg (CfgNode): Configuration node for friction brake settings.
        detection (Detection): Detection instance for in-game state checks.
        cur (Value): Current value of the friction brake.
        lock (Lock): Lock for thread synchronization.
        monitor_process (Process): Process for monitoring the friction brake.
    """

    def __init__(self, cfg, lock, detection: Detection) -> None:
        """Initialize the FrictionBrake class with configuration, lock, and detection.

        :param cfg: Configuration node for friction brake settings.
        :type cfg: CfgNode
        :param lock: Lock for thread synchronization.
        :type lock: Lock
        :param detection: Detection instance for in-game state checks.
        :type detection: Detection
        """
        self.cfg = cfg
        self.lock = lock
        self.detection = detection

        if self.cfg.ARGS.FEATURE == "bot":
            self.fb_cfg = self.cfg.BOT.FRICTION_BRAKE
        else:
            self.fb_cfg = self.cfg.FRICTION_BRAKE

        self.cur = Value("i", self.fb_cfg.INITIAL)
        self.monitor_process = Process(target=monitor_friction_brake, args=(self,))

    def reset(self, target: int, to_max: bool=False) -> None:
        """Reset the friction brake to the target value.

        :param target: Target friction brake value.
        :type target: int
        :param to_max: Increase to 30 before setting it to target, defaults to False.
        :type to_max: bool, optional
        """
        logger.info("Resetting friction brake")
        with self.lock:
            sleep(FRICTION_BRAKE_CHANGE_DELAY) # might be called after change()
            if to_max:
                for _ in range(MAX_FRICTION_BRAKE):
                    pag.scroll(UP, _pause=False)
                    sleep(FRICTION_BRAKE_CHANGE_DELAY)
                cur = MAX_FRICTION_BRAKE
            else:
                cur = self.cur.value
            diff = cur - target
            for _ in range(abs(diff)):
                pag.scroll(DOWN, _pause=False)
                sleep(FRICTION_BRAKE_CHANGE_DELAY)
            self.cur.value = target

    def change(self, increase: bool) -> None:
        """Increase or decrease the friction brake.

        :param increase: Whether to increase the friction brake.
        :type increase: bool
        """
        if increase:
            if self.cur.value < self.fb_cfg.MAX:
                pag.scroll(UP, _pause=False)
                self.cur.value = min(self.cur.value + 1, MAX_FRICTION_BRAKE)
        else:
            if self.cur.value > 0:
                pag.scroll(DOWN, _pause=False)
                self.cur.value = max(self.cur.value - 1, MIN_FRICTION_BRAKE)


def monitor_friction_brake(friction_brake: FrictionBrake) -> None:
    """Monitor friction brake bar and change it accordingly.

    This is used as the target function in multiprocess.Process and must be pickable,
    thus it must be declared as a global function instead of an instance method.

    :param friction_brake: Friction brake controller.
    :type friction_brake: FrictionBrake
    """
    logger.info("Monitoring friction brake")
    pre_time = time()
    fish_hooked = False

    try:
        while True:
            if not friction_brake.detection.is_fish_hooked_pixel():
                sleep(FRICTION_BRAKE_MONITOR_DELAY)
                fish_hooked = False
                continue
            if not fish_hooked:
                sleep(friction_brake.fb_cfg.START_DELAY)
                fish_hooked = True

            with friction_brake.lock:
                if (
                    friction_brake.detection.is_friction_brake_high()
                    or friction_brake.detection.is_reel_burning()
                ):
                    friction_brake.change(increase=False)
                    sleep(friction_brake.fb_cfg.DECREASE_DELAY)
                else:
                    cur_time = time()
                    if cur_time - pre_time >= friction_brake.fb_cfg.INCREASE_DELAY:
                        pre_time = cur_time
                        friction_brake.change(increase=True)
    except KeyboardInterrupt:
        pass
