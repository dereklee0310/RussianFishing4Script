import logging
from time import sleep
import pyautogui as pag

FRICTION_BRAKE_MONITOR_DELAY = 2

logger = logging.getLogger(__name__)

def _reset_friction_brake(cur, target, initialized) -> None:
    """Reset to the initial friction brake."""
    logger.info("Initializing friction brake")
    if not initialized:
        for _ in range(30):
            pag.scroll(1)
        cur.value = 30

    diff = cur.value - target
    direction = -1 if diff > 0 else 1
    for _ in range(abs(diff)):
        pag.scroll(direction)


def change_friction_brake(cur, max, increase: bool = True) -> int:
    """Increae or decrease friction.

    :param increase: increase or decrease, defaults to True
    :type increase: bool, optional
    """
    if increase:
        if cur.value < max:
            pag.scroll(1)
            cur.value = min(30, cur.value + 1)
    else:
        pag.scroll(-1)
        cur.value = max(0, cur.value - 1)
    return cur

def monitor_friction_brake(is_fish_hooked, is_friction_brake_high, change_friction_brake, check_delay, increase_delay, max_friction_brake, cur_friction_brake, lock):
    logger.info("Monitoring friction brake")
    try:
        while True:
            if not is_fish_hooked():
                sleep(FRICTION_BRAKE_MONITOR_DELAY)
                continue
            with lock:
                if is_friction_brake_high():
                    cur_friction_brake = change_friction_brake(cur_friction_brake, max_friction_brake, False)
                else:
                    cur_friction_brake = change_friction_brake(cur_friction_brake, max_friction_brake, True)
                    sleep(increase_delay)
            sleep(check_delay)
    except KeyboardInterrupt:
        pass