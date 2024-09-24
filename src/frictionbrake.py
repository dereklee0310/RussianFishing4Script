import logging
from time import sleep
import pyautogui as pag

FRICTION_BRAKE_MONITOR_DELAY = 2

logger = logging.getLogger(__name__)

def _reset_friction_brake(cur_friction_brake, target_friction_brake, initialized) -> None:
    """Reset to the initial friction brake."""
    logger.info("Initializing friction brake")
    if not initialized:
        for _ in range(30):
            pag.scroll(1)
        cur_friction_brake.value = 30

    diff = cur_friction_brake.value - target_friction_brake
    direction = -1 if diff > 0 else 1
    for _ in range(abs(diff)):
        pag.scroll(direction)
    cur_friction_brake.value = target_friction_brake


def change_friction_brake(cur_friction_brake, max_friction_brake, increase: bool=True) -> None:
    """Increae or decrease friction.

    :param increase: increase or decrease, defaults to True
    :type increase: bool, optional
    """
    if increase:
        if cur_friction_brake.value < max_friction_brake:
            pag.scroll(1)
            cur_friction_brake.value += 1
    else:
        if cur_friction_brake.value > 0:
            pag.scroll(-1)
            cur_friction_brake.value -= 1

def monitor_friction_brake(is_fish_hooked, is_friction_brake_high, change_friction_brake, check_delay, increase_delay, max_friction_brake, cur_friction_brake, lock):
    logger.info("Monitoring friction brake")
    try:
        while True:
            if not is_fish_hooked():
                sleep(FRICTION_BRAKE_MONITOR_DELAY)
                continue
            with lock:
                if is_friction_brake_high():
                    change_friction_brake(cur_friction_brake, max_friction_brake, False)
                else:
                    sleep(increase_delay)
                    change_friction_brake(cur_friction_brake, max_friction_brake, True)
            sleep(check_delay)
    except KeyboardInterrupt:
        pass