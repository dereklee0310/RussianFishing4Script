import logging
import configparser
import argparse
from time import time, sleep

import pyautogui as pag
from prettytable import PrettyTable

import monitor
from windowcontroller import WindowController
from script import sleep_and_decrease, ask_for_confirmation

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def harvest_baits() -> None:
    """Harvest baits and accept the result.
    """
    logger.info("Harvesting baits")
    pag.click()

    # wait for result
    sleep(5) # 4 is enough, + 1 for inspection
    i = 64
    while i > 0 and not monitor.is_harvest_success():
        i = sleep_and_decrease(i, 4)

    # accept result
    pag.press('space')
    sleep(0.25)

def consume_food(food: str) -> None:
    """Open food menu, then click on the food icon to consume it.

    :param food: food's name
    :type food: str
    """
    logger.info(f'Consume {food}')
    with pag.hold('t'):
        sleep(0.25)
        pag.moveTo(getattr(monitor, f'get_{food}_icon_position')())
        pag.click()
        sleep(0.25)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='harvest.py',
                        description='Harvest baits automatically, refill food and comfort if needed',
                        epilog='')
    parser.add_argument('-s', '--power-saving', action='store_true',
                        help='Open control panel between each checks to save power consumption')
    parser.add_argument('-n', '--check-delay-second', type=int, default=32,
                        help='The time interval between each checks, default to 32 seconds')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(r'../config.ini')
    threshold = config['game'].getfloat('harvest_baits_threshold')
    shovel_spoon_shortcut = config['shortcut'].get('shovel_spoon')

    tea_count = 0
    carrot_count = 0
    harvest_count = 0

    ask_for_confirmation('Are you ready to start harvesting baits')
    WindowController().activate_game_window()

    # pull out shovel/spoon
    pag.press(shovel_spoon_shortcut)
    sleep(3)

    try:
        pre_refill_time = 0
        while True:
            if monitor.is_comfort_low() and time() - pre_refill_time > 300:
                logger.info('Low comfort level')
                pre_refill_time = time()
                consume_food('tea')
                tea_count += 1

            if monitor.is_hunger_low():
                logger.info('Low hunger level')
                consume_food('carrot')
                carrot_count += 1

            if monitor.is_energy_high(threshold):
                logger.info('High energy level')
                harvest_baits()
                harvest_count += 1

            logger.info('Waiting for energy regeneration')
            if args.power_saving:
                pag.press('esc')
            sleep(args.check_delay_second)
            if args.power_saving:
                pag.press('esc')
            sleep(0.25)
    except KeyboardInterrupt:
        pass
    table = PrettyTable(header=False, align='l')
    table.title = 'Running Results'
    table.add_rows([
        ['Harvest baits count', harvest_count],
        ['Tea consumed', tea_count],
        ['Carrot consumed', carrot_count]
    ])
    print(table)