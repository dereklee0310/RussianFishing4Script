from pyautogui import *
from pyautogui import getWindowsWithTitle
from time import sleep
from rod import Rod
import keyboard
import sys
from inputimeout import inputimeout, TimeoutOccurred
import datetime
from timer import Timer
import time

class Fisherman():
    KEEPNET_LIMIT = 100

    def __init__(self):
        self.fish_count = 0
        self.rod = Rod()
        self.strategy = "spinning"
        self.timer = Timer()

    def keep_the_fish(self):
        #todo: check if it's a trophy
        press('space')
        self.fish_count += 1
        print(f'Fish count: {self.fish_count}')
        if self.is_keepnet_full():
            self.quit_game()
            print(f'execution time: {self.timer.get_duration()}')
            sys.exit()

    def show_welcome_msg(self):
        try:
            self.fish_count = int(inputimeout(prompt='Please enter the number of fish you have caught or wait for 5 seconds: ', timeout=5))
        except TimeoutOccurred:
            pass
        print(f'The fish count has been set to {self.fish_count}')
        sleep(1)
        
        try:
            self.strategy = inputimeout(prompt='Please enter the fishing strategy or wait for 10 seconds: ', timeout=10)
        except TimeoutOccurred:
            print(f'The strategy has been set to "{self.strategy}"')
            sleep(1)


        for i in range(5, 0, -1):
            print(f'The script will start in: {i} seconds', end='\r')
            sleep(1)
        print('')

    def is_keepnet_full(self):
        return self.fish_count == self.KEEPNET_LIMIT

    def start_fishing(self):
        rod = self.rod
        if self.strategy == 'spinning':
            try:
                while True:
                    if rod.is_broked():
                        print('The rod is broken')
                        self.save_screenshot()
                        self.quit_game()
                    rod.reset()
                    if locateOnScreen('keep.png', confidence=0.9):
                        print('! keep exception occured')
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
            print('feeder strategy, todo...')
            exit()

    def quit_game(self):
        press('esc')
        sleep(1) # wait for the menu to load
        moveTo(locateOnScreen('quit.png', confidence=0.8), duration=0.4) 
        click()
        moveTo(locateOnScreen('yes.png', confidence=0.8), duration=0.4)
        click()
        print(f'The script has been terminated, execution time: {self.timer.get_duration()}')
        sys.exit()

    def save_screenshot(self):
        # datetime.now().strftime("%H:%M:%S")
        with open(f'screenshots\\{time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime())}.png', 'wb') as file: 
            screenshot().save(file, 'png')

    def relogin(self):
        pass

fisherman = Fisherman()
fisherman.show_welcome_msg()
window = getWindowsWithTitle("Russian Fishing 4")[0]
window.activate()
fisherman.start_fishing()
# fisherman.save_screenshot()