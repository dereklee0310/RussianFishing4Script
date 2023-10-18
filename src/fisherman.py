from pyautogui import *
from time import sleep
from rod import Rod
import keyboard
import sys
from timer import Timer
import time

class Fisherman():
    KEEPNET_LIMIT = 100

    def __init__(self, fishing_strategy, release_strategy, fish_count):
        self.rod = Rod()
        self.fishing_strategy = fishing_strategy
        self.release_strategy = release_strategy
        self.fish_count = fish_count
        self.timer = Timer()

    def keep_the_fish(self):
        #todo: check if it's a trophy
        if self.release_strategy == 'unmarked' and not locateOnScreen('../static/beleya_marked.png', confidence=0.8):
            press('backspace')
            print('Release unmarked fish')
            return
        press('space')
        self.fish_count += 1
        print(f'Fish count: {self.fish_count}')
        if self.is_keepnet_full():
            self.quit_game()
            print(f'execution time: {self.timer.get_duration()}')
            sys.exit()

    def is_keepnet_full(self):
        return self.fish_count == self.KEEPNET_LIMIT

    def start_fishing(self):
        rod = self.rod
        if self.fishing_strategy == 'spinning':
            try:
                while True:
                    if rod.is_broked():
                        print('The rod is broken')
                        self.save_screenshot()
                        self.quit_game()
                    rod.reset()
                    if locateOnScreen('../static/keep.png', confidence=0.9):
                        self.keep_the_fish()
                    rod.cast()
                    rod.retrieve()
                    if rod.is_fish_hooked():
                        rod.tighten_fishline()
                        if rod.pull():
                            self.keep_the_fish()
            except KeyboardInterrupt:
                print(f'The script has been terminated, execution time: {self.timer.get_duration()}')
                sys.exit()
        else:
            print('Feeder strategy, todo...')
            exit()

    def quit_game(self):
        press('esc')
        sleep(1) # wait for the menu to load
        moveTo(locateOnScreen('../static/quit.png', confidence=0.8), duration=0.4) 
        click()
        moveTo(locateOnScreen('../static/yes.png', confidence=0.8), duration=0.4)
        click()
        print(f'The script has been terminated, execution time: {self.timer.get_duration()}')
        sys.exit()

    def save_screenshot(self):
        # datetime.now().strftime("%H:%M:%S")
        with open(f'screenshots\\{time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime())}.png', 'wb') as file: 
            screenshot().save(file, 'png')

    def relogin(self):
        pass