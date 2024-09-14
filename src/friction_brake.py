
import logging
from time import sleep
import pyautogui as pag

FRICTION_BRAKE_MONITOR_DELAY = 2

logger = logging.getLogger(__name__)

def reset_friction_brake(cur, target) -> int:
    """Reset to the initial friction brake."""
    logger.info("Initializing friction brake")

    # if not self.friction_brake_initialized:
    #     for _ in range(30):
    #         pag.scroll(1)
    #     diff = 30 - self.setting.initial_friction
    #     for _ in range(diff):
    #         pag.scroll(-1)
    # else:
    diff = cur - target
    direction = -1 if diff > 0 else 1
    for _ in range(abs(diff)):
        pag.scroll(direction)
    return target

def change_friction_brake(cur, max, increase: bool = True) -> int:
    """Increae or decrease friction.

    :param increase: increase or decrease, defaults to True
    :type increase: bool, optional
    """
    if increase:
        if cur < max:
            pag.scroll(1)
            cur = min(30, cur + 1)
    else:
        pag.scroll(-1)
        cur = max(0, cur - 1)
    return cur

def monitor_friction(is_fish_hooked, is_friction_brake_high, change_friction, check_delay, increase_delay, max_friction, friction_queue):

    cur_friction = friction_queue.get() # block until non empty

    logger.info("Monitoring friction brake")
    try:
        while True:
            # update only if non empty
            if not friction_queue.empty():
                cur_friction = friction_queue.get()

            if not is_fish_hooked():
                sleep(FRICTION_BRAKE_MONITOR_DELAY)
                continue

            if is_friction_brake_high():
                cur_friction = change_friction(cur_friction, max_friction, False)
            else:
                cur_friction = change_friction(cur_friction, max_friction, True)
                sleep(increase_delay)
            sleep(check_delay)
    except KeyboardInterrupt:
        pass