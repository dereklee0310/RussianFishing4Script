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
        self.init_fish_count = fish_count
        self.fish_count = fish_count
        self.release_count = 0
        self.timer = Timer()
        self.miss_count = 0
        self.delay = 8

    def keep_the_fish(self):
        #todo: check if it's a trophy
        #! remove this!!!
        # self.save_screenshot()
        if not locateOnScreen('../static/mark.png', confidence=0.7): # don't modify the confidence! #todo: for ruffe
            if self.release_strategy == 'unmarked':
                press('backspace')
                print('Release unmarked fish')
                self.release_count += 1 #todo
                return
        press('space')
        self.fish_count += 1
        print(f'Fish count: {self.fish_count}')
        if self.is_keepnet_full():
            self.quit_game()

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
                    if rod.is_fish_hooked():
                        if rod.pull(i=2):
                            self.keep_the_fish()
                        else:
                            rod.retrieve()
                            continue
                    rod.cast()
                    rod.retrieve()
                    if rod.is_fish_hooked():
                        rod.tighten_fishline()
                        if rod.pull():
                            self.keep_the_fish()
                    else:
                        self.miss_count += 1
            except KeyboardInterrupt:
                self.show_quit_msg()
        else:
            # print('Feeder strategy, todo...')
            # exit()
            try:
                rod_key = 0
                while True:
                    rod_key = 1 if rod_key == 3 else rod_key + 1
                    press(f'{rod_key}')
                    sleep(1)
                    if rod.is_broked():
                        print('The rod is broken')
                        self.save_screenshot()
                        self.quit_game()
                    if rod.is_fish_hooked():
                        rod.retrieve(duration=4, delay=2)
                        # rod.tighten_fishline()
                        if rod.is_fish_hooked():
                            if rod.pull():
                                self.keep_the_fish()
                        self.delay = 4 if self.delay == 4 else self.delay - 1
                    else:
                        self.miss_count += 1
                        if self.miss_count % 4 == 0:
                            self.delay += 1
                        if self.miss_count % 32 == 0:
                            #todo: package this
                            for rod_key in range(1, 4):
                                press(f'{rod_key}')
                                rod.reset()
                                if rod.is_fish_hooked():
                                    if rod.pull():
                                        self.keep_the_fish()
                                sleep(1)
                                keyDown('shift')
                                mouseDown()
                                sleep(1)
                                keyUp('shift')
                                mouseUp()
                                click()
                                sleep(1)
                                click()
                            self.delay = 8 # reset delay
                        sleep(self.delay)
                        continue
                    
                    sleep(1)
                    keyDown('shift')
                    mouseDown()
                    sleep(1)
                    keyUp('shift')
                    mouseUp()
                    click()
                    sleep(1)
                    click()
                    sleep(self.delay)
            except KeyboardInterrupt:
                self.show_quit_msg()

    def quit_game(self):
        press('esc')
        sleep(1) # wait for the menu to load
        moveTo(locateOnScreen('../static/quit.png', confidence=0.8), duration=0.4) 
        click()
        moveTo(locateOnScreen('../static/yes.png', confidence=0.8), duration=0.4)
        click()
        self.show_quit_msg()

    def show_quit_msg(self):
        caught_fish = self.fish_count - self.init_fish_count 
        total = caught_fish + self.release_count
        total_cast = total + self.miss_count
        print(f'The script has been terminated')
        print('--------------------Result--------------------')
        if total:
            print(f'marked  : {caught_fish}') #todo mark checker
            print(f'total   : {total}')
            print(f'ratio   : {caught_fish / (total)}')
            print(f'hit rate: {total}/{total_cast} {int((total / total_cast) * 100)}%')
        else:
            print('No fish have been caught yet')
        print(f'start time    : {self.timer.get_start_datetime()}')
        print(f'finish time   : {self.timer.get_cur_datetime()}')
        print(f'execution time: {self.timer.get_duration()}')
        sys.exit()

    def save_screenshot(self):
        # datetime.now().strftime("%H:%M:%S")
        with open(fr'../screenshots/{self.timer.get_cur_timestamp()}.png', 'wb') as file: 
            screenshot().save(file, 'png')

    def relogin(self):
        pass