from pyautogui import *
from time import sleep
from rod import Rod
import keyboard
import sys
from timer import Timer
import time
import win32api, win32con
from threading import Thread
from monitor import Monitor

class Fisherman():
    KEEPNET_LIMIT = 100

    def __init__(self, fishing_strategy, release_strategy, fish_count, trophy_mode):
        self.monitor = Monitor()
        self.rod = Rod(self.monitor)
        self.fishing_strategy = fishing_strategy
        self.release_strategy = release_strategy
        self.init_fish_count = fish_count
        self.total_fish_count = fish_count
        self.marked_fish_count = 0
        self.unmarked_fish_count = 0
        self.cast_miss_count = 0
        self.trophy_mode = trophy_mode
        self.timer = Timer()
        self.delay = 12 # 8

    def keep_the_fish(self):
        #todo: check if it's a trophy
        #todo: for ruffe

        if self.monitor.is_fish_marked():
            self.marked_fish_count += 1
        else:
            self.unmarked_fish_count += 1
            if self.release_strategy == 'unmarked':
                press('backspace')
                print('Release unmarked fish')
                return
        
        # if the fish is marked or the release strategy is set to none, keep the fish
        press('space')
        self.total_fish_count += 1
        if self.is_keepnet_full():
            self.quit_game()

    def is_keepnet_full(self):
        return self.total_fish_count == self.KEEPNET_LIMIT

    def start_fishing(self):
        rod = self.rod
        if self.fishing_strategy == 'spin':
            try:
                self.start_spin_fishing()
            except KeyboardInterrupt:
                self.show_quit_msg()
        elif self.fishing_strategy == 'twitching' or self.fishing_strategy == 'walking_dog':
            try:
                self.start_special_spin_fishing(0.25, 1)
            except KeyboardInterrupt:
                self.show_quit_msg()
        elif self.fishing_strategy == 'jig_step':
            try:
                self.start_jig_step_fishing()
            except KeyboardInterrupt:
                self.show_quit_msg()
        elif self.fishing_strategy == 'jig_step_1':
            try:
                self.start_jig_step_fishing(False, 1, 3)
            except KeyboardInterrupt:
                self.show_quit_msg()
        elif self.fishing_strategy == 'bottom':
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
                        if failed_count % 1 == 0 and self.trophy_mode:
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
                        self.cast_miss_count += 1
                        if self.cast_miss_count % 4 == 0:
                            self.delay += 1
                        if self.cast_miss_count % 32 == 0:
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

    def start_spin_fishing(self):
        rod = self.rod
        monitor = self.monitor
        pull_timeout = 4
        while True:
            if monitor.is_rod_broked(): #todo: use another thread to monitor it
                print('! Rod is broken')
                self.save_screenshot()
                self.quit_game()

            rod.reset()

            if monitor.is_fish_captured():
                print('! Fish caught without pulling')
                self.keep_the_fish()
            elif monitor.is_fish_hooked():
                print('! Fish hooked while resetting')
                if rod.pull(i=pull_timeout):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            
            rod.cast()
            rod.retrieve()

            # now, the retrieval is done
            if monitor.is_fish_hooked():
                if rod.pull(i=pull_timeout):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            else:
                self.cast_miss_count += 1

    def start_special_spin_fishing(self, duration, delay):
        rod = self.rod
        monitor = self.monitor
        pull_timeout = 4
        while True:
            if monitor.is_rod_broked(): #todo: use another thread to monitor it
                print('! Rod is broken')
                self.save_screenshot()
                self.quit_game()

            rod.reset()

            if monitor.is_fish_captured():
                print('! Fish caught without pulling')
                self.keep_the_fish()
            elif monitor.is_fish_hooked():
                print('! Fish hooked while resetting')
                if rod.pull(i=pull_timeout):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            
            rod.cast()
            # rod.retrieve()
            rod.special_retrieve(duration, delay)

            # now, the retrieval is done
            if monitor.is_fish_hooked():
                if rod.pull(i=pull_timeout):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            else:
                self.cast_miss_count += 1

    def start_jig_step_fishing(self, waiting=True, duration=0.52, delay=3):
        rod = self.rod
        monitor = self.monitor
        pull_timeout = 6 #todo
        while True:
            if monitor.is_rod_broked(): #todo: use another thread to monitor it
                print('! Rod is broken')
                self.save_screenshot()
                self.quit_game()

            rod.reset()

            if monitor.is_fish_captured():
                print('! Fish caught without pulling')
                self.keep_the_fish()
            elif monitor.is_fish_hooked():
                print('! Fish hooked while resetting')
                if rod.pull(i=pull_timeout):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            if waiting:
                rod.cast(delay=18)
            else:
                rod.cast()
            # rod.retrieve()
            rod.jig_step(duration=duration, delay=delay) #todo

            # now, the retrieval is done
            if monitor.is_fish_hooked():
                if rod.pull(i=pull_timeout):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            else:
                self.cast_miss_count += 1

    # def pull_and_keep(self, rod, pull_timeout):
    #     if rod.pull(i=pull_timeout):
    #         self.keep_the_fish()
    #     else:
    #         print('! failed to get the fish after pulling')

    def start_strong_pirking(self):
        click()
        

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
        if not self.total_fish_count - self.init_fish_count:
            print('No fish have been caught yet.')
            print('The script has been terminated.')
            return
        caught_fish_count = self.total_fish_count - self.init_fish_count + self.unmarked_fish_count
        total_cast_count = self.cast_miss_count + caught_fish_count
        print('The script has been terminated.')
        print('--------------------Result--------------------')
        print(f'Caught fishes  : {caught_fish_count}')
        print(f'Marked rate    : {self.marked_fish_count}/{caught_fish_count} {int((self.marked_fish_count) / caught_fish_count * 100)}%')
        print(f'Bite rate      : {caught_fish_count}/{total_cast_count} {int(caught_fish_count / total_cast_count * 100)}%')
            
        print(f'Start time     : {self.timer.get_start_datetime()}')
        print(f'Finish time    : {self.timer.get_cur_datetime()}')
        print(f'Execution time : {self.timer.get_duration()}')
        exit()

    def save_screenshot(self):
        # datetime.now().strftime("%H:%M:%S")
        press('q')
        with open(fr'../screenshots/{self.timer.get_cur_timestamp()}.png', 'wb') as file: 
            screenshot().save(file, 'png')

    def relogin(self):
        pass
    
    def drink_coffee(self):
        keyDown('t')
        sleep(1)
        moveTo(locateOnScreen('../static/coffee.png', confidence=0.98), duration=0.5)
        click()
        sleep(0.5)
        keyUp('t')