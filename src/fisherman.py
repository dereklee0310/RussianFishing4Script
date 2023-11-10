from pyautogui import *
from time import sleep
from rod import Rod
import keyboard
import sys
from timer import Timer
import time
import win32api, win32con


class Fisherman():
    KEEPNET_LIMIT = 100

    def __init__(self, fishing_strategy, release_strategy, fish_count, trophy_mode):
        self.rod = Rod()
        self.fishing_strategy = fishing_strategy
        self.release_strategy = release_strategy
        self.init_fish_count = fish_count
        self.fish_count = fish_count
        self.trophy_mode = trophy_mode
        self.release_count = 0
        self.timer = Timer()
        self.miss_count = 0
        self.delay = 12 # 8
        self.debug_count = 0

    def keep_the_fish(self):
        #todo: check if it's a trophy
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
            self.start_spin_fishing()
            # try:
            #     while True:
            #         if rod.is_broked():
            #             print('The rod is broken')
            #             self.save_screenshot()
            #             self.quit_game()
            #         rod.reset()
            #         if locateOnScreen('../static/keep.png', confidence=0.9):
            #             self.keep_the_fish()
            #         elif rod.is_fish_hooked():
            #             if rod.pull(i=4):
            #                 self.keep_the_fish()
            #             else:
            #                 rod.retrieve()
            #                 continue
            #         rod.cast()
            #         rod.retrieve()
            #         if rod.is_fish_hooked():
            #             rod.tighten_fishline()
            #             if rod.pull():
            #                 self.keep_the_fish()
            #         else:
            #             self.miss_count += 1
            # except KeyboardInterrupt:
            #     self.show_quit_msg()
        else:
            # print('Feeder strategy, todo...')
            # exit()
            try:
                failed_count = 0
                rod_key = 0
                while True:
                    if not rod.is_fish_hooked():
                        rod_key = 1 if rod_key == 3 else rod_key + 1
                        press(f'{rod_key}')
                        failed_count = 0
                    else:
                        failed_count += 1
                        if failed_count % 1 == 0:
                            self.drink_coffee()
                    sleep(1)
                    if rod.is_broked():
                        print('The rod is broken')
                        self.save_screenshot()
                        self.quit_game()
                    if rod.is_fish_hooked():
                        if self.trophy_mode:
                            rod.retrieve(duration=16, delay=4)
                        else:
                            rod.retrieve(duration=4, delay=2)
                        # rod.tighten_fishline()
                        if rod.is_fish_hooked():
                            if self.trophy_mode:
                                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(0), int(-200), 0, 0)
                            if rod.pull(i=8):
                                self.keep_the_fish()
                            else:
                                print('! pull failed')
                                if self.trophy_mode:
                                    sleep(6)
                                    if locateOnScreen('../static/keep.png', confidence=0.9):
                                        self.keep_the_fish()
                                    else:
                                        print('! second check failed')
                                else:
                                    rod.reset(self.trophy_mode)
                            if self.trophy_mode:
                                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(0), int(200), 0, 0)
                        if not self.trophy_mode:
                            self.delay = 4 if self.delay == 4 else self.delay - 1
                        else:
                            self.delay = 8 if self.delay == 8 else self.delay - 1
                            #todo: reset tackle
                    elif locateOnScreen('../static/keep.png', confidence=0.9):
                        self.keep_the_fish()
                    else:
                        press('0')
                        sleep(1)
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
                                if self.trophy_mode:
                                    sleep(3)
                                else:
                                    sleep(1)
                                # click()
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
                    print(self.trophy_mode)
                    if self.trophy_mode:
                        sleep(3)
                    else:
                        sleep(1)
                    # click()
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
        sleep(1)
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
        print(f'debug count (a fish is caught without pulling): {self.debug_count}')

        sys.exit()

    def save_screenshot(self):
        # datetime.now().strftime("%H:%M:%S")
        with open(fr'../screenshots/{self.timer.get_cur_timestamp()}.png', 'wb') as file: 
            screenshot().save(file, 'png')

    def relogin(self):
        pass

    def start_spin_fishing(self):
        rod = self.rod
        pull_timeout = 4
        try:
            while True:
                if rod.is_broked():
                    print('The rod is broken')
                    self.save_screenshot()
                    self.quit_game()
                
                rod.reset()

                if locateOnScreen('../static/keep.png', confidence=0.9):
                    print('! a fish is caught without pulling')
                    self.debug_count += 1 #! DEBUG
                    self.keep_the_fish()
                elif rod.is_fish_hooked():
                    print('! a fish is hooked while resetting')
                    self.pull_and_keep(rod=rod, pull_timeout=pull_timeout)
                rod.cast()
                rod.retrieve()
                if rod.is_fish_hooked():
                    # rod.tighten_fishline() #todo: read this?
                    self.pull_and_keep(rod=rod, pull_timeout=pull_timeout)
                else:
                    self.miss_count += 1
        except KeyboardInterrupt:
            self.show_quit_msg()
    
    def drink_coffee(self):
        keyDown('t')
        sleep(1)
        moveTo(locateOnScreen('../static/coffee.png', confidence=0.98), duration=0.5)
        click()
        sleep(0.5)
        keyUp('t')

    def pull_and_keep(self, rod, pull_timeout):
        if rod.pull(i=pull_timeout):
            self.keep_the_fish()
        else:
            print('! failed to get the fish after pulling')