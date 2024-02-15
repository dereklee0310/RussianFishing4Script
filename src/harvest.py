from pyautogui import *
from monitor import *
import monitor
from script import *
from configparser import ConfigParser
from windowcontroller import WindowController
import time
from prettytable import PrettyTable

def harvest_baits(shovel_spoon_shortcut):
    """An modified version of player.harvest_baits().

    :param shovel_spoon_shortcut: _description_
    :type shovel_spoon_shortcut: _type_
    """
    # digging
    click()

    # wait for result
    sleep(5) # 4 is enough, + 1 for inspection
    i = 64
    while i > 0 and not is_harvest_success():
        i = sleep_and_decrease(i, 4)

    # accept result
    press('space')
    sleep(0.25)

def consume_food(food: str) -> None:
    """Open food menu, then click on food icon to consume it.

    :param food: food's name
    :type food: str
    """
    print(f'Consume {food}')
    with hold('t'):
        sleep(0.25)
        moveTo(getattr(monitor, f'get_{food}_icon_position')())
        click()

if __name__ == '__main__':
    config = ConfigParser()
    config.read('../config.ini')
    threshold = config['game'].getfloat('harvest_baits_threshold')
    shovel_spoon_shortcut = config['shortcut']['shovel_spoon']

    tea_count = 0
    pre_refill_time = 0
    carrot_count = 0
    harvest_count = 0
    
    controller = WindowController()
    controller.activate_game_window()

    print('The script has been started')
    press(shovel_spoon_shortcut)
    sleep(3)
    try:
        while True:
            if is_comfort_low() and time.time() - pre_refill_time > 300:
                pre_refill_time = time.time()
                consume_food('tea')
                tea_count += 1
            sleep(0.25)

            if is_food_level_low():
                consume_food('carrot')
                carrot_count += 1
            sleep(0.25)

            if is_energy_high(threshold):
                print('Harvest baits')
                harvest_baits(shovel_spoon_shortcut)
                harvest_count += 1
            else:
                print('Low energy level')
            press('esc')
            sleep(30)
            press('esc')
            sleep(0.25)
    except KeyboardInterrupt:
        print('Terminated by user')
        table = PrettyTable(header=False, align='l')
        table.title = 'Running Results'
        table.add_rows(
            [   
                ['Harvest baits count', harvest_count],
                ['Tea consumed', tea_count],
                ['Carrot consumed', carrot_count]
            ])
        print(table)
        exit()