from pyautogui import *
from time import sleep
from tackle import Tackle
import keyboard
from timer import Timer
import win32api, win32con
from threading import Thread
from monitor import *
from mouse import hold_left_click, hold_right_click
from datetime import datetime

class Fisherman():
    keepnet_limit = 100
    keep_fish_count = 0
    marked_fish_count = 0
    unmarked_fish_count = 0
    cast_miss_count = 0
    delay = 12 # 8
    trophy_mode = None

    def __init__(self, profile):
        self.keepnet_limit -= profile.current_fish_count
        self.fishing_strategy = profile.fishing_strategy
        self.release_strategy = profile.release_strategy
        self.tackle = Tackle(profile)
        self.timer = Timer()

    def keep_the_fish(self):
        #! the trophy ruffe will break the checking mechanism
        if is_fish_marked():
            self.marked_fish_count += 1
        else:
            self.unmarked_fish_count += 1
            if self.release_strategy == 'unmarked':
                press('backspace')
                print('Release unmarked fish')
                return
        
        # if the fish is marked or the release strategy is set to none, keep the fish
        print('Keep the fish')
        press('space')
        self.keep_fish_count += 1
        if self.is_keepnet_full():
            self.quit_game()

    def is_keepnet_full(self):
        return self.keep_fish_count == self.keepnet_limit

    def start_fishing(self):
        tackle = self.tackle
        try:
            if self.fishing_strategy == 'spin':
                self.spin_fishing(time_limit=False)
            elif self.fishing_strategy == 'time_limit_spin':
                self.spin_fishing(time_limit=True)
            elif self.fishing_strategy == 'strong_pirking':
                self.pirking(duration=1.75, delay=4)
            elif self.fishing_strategy == 'pirking':
                self.pirking(duration=0.5, delay=2)
            elif self.fishing_strategy == 'twitching':
                self.special_spin_fishing(0.25, 1)
            elif self.fishing_strategy == 'walking_dog':
                self.special_spin_fishing(0.25, 1)
            elif self.fishing_strategy == 'jig_step':
                self.jig_step_fishing()
            elif self.fishing_strategy == 'jig_step_1':
                self.jig_step_fishing(False, 1, 3)
            elif self.fishing_strategy == 'bottom':
                #todo: improve bottom fishing
                failed_count = 0
                rod_key = 0
                while True:
                    if not is_fish_hooked():
                        rod_key = 1 if rod_key == 3 else rod_key + 1
                        press(f'{rod_key}')
                        failed_count = 0
                    else:
                        failed_count += 1
                        if failed_count % 1 == 0 and self.trophy_mode:
                            self.drink_coffee()
                    sleep(1)
                    if is_tackle_broked():
                        print('The rod is broken')
                        self.save_screenshot()
                        self.quit_game()
                    if is_fish_hooked():
                        if self.trophy_mode:
                            tackle.retrieve(duration=16, delay=4)
                        else:
                            tackle.retrieve(duration=4, delay=2)
                        # tackle.tighten_fishline()
                        if is_fish_hooked():
                            if self.trophy_mode:
                                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(0), int(-200), 0, 0)
                            if tackle.pull(i=8):
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
                                    tackle.reset(self.trophy_mode)
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
                                tackle.reset()
                                if is_fish_hooked():
                                    if tackle.pull():
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

    def spin_fishing(self, time_limit=False):
        while True:
            if time_limit and datetime.now().hour == 7:
                self.quit_game("it's 7 A.M.!")

            if is_tackle_broked(): #todo: use another thread to monitor it
                self.save_screenshot()
                self.quit_game("! Tackle is broken")

            self.tackle.reset()

            if is_fish_captured():
                print('! Fish captured without pulling')
                self.keep_the_fish()
            elif is_fish_hooked():
                print('! Fish hooked while resetting')
                if self.tackle.pull(i=8):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
            
            if not is_fish_hooked():
                self.tackle.cast()
            self.tackle.retrieve()

            # retrieval is done
            if is_fish_hooked():
                if self.tackle.pull(i=4):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish') #todo
            else:
                self.cast_miss_count += 1

    def special_spin_fishing(self, duration, delay):
        rod = self.tackle
        pull_timeout = 4
        while True:
            if is_tackle_broked(): #todo: use another thread to monitor it
                self.save_screenshot()
                self.quit_game("! Tackle is broken")

            rod.reset()

            if is_fish_captured():
                print('! Fish caught without pulling')
                self.keep_the_fish()
            elif is_fish_hooked():
                print('! Fish hooked while resetting')
                if rod.pull(i=pull_timeout):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            
            if not is_fish_hooked():
                self.tackle.cast()
            self.tackle.retrieve()
            rod.special_retrieve(duration, delay)

            # now, the retrieval is done
            if is_fish_hooked():
                if rod.pull(i=pull_timeout):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            else:
                self.cast_miss_count += 1

    def jig_step_fishing(self, waiting=True, duration=0.52, delay=3):
        rod = self.tackle
        pull_timeout = 6 #todo
        while True:
            if is_tackle_broked(): #todo: use another thread to monitor it
                self.save_screenshot()
                self.quit_game("! Tackle is broken")

            rod.reset()

            if is_fish_captured():
                print('! Fish caught without pulling')
                self.keep_the_fish()
            elif is_fish_hooked():
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
            if is_fish_hooked():
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

    def pirking(self, duration, delay):
        while True:
            if is_tackle_broked(): #todo: use another thread to monitor it
                self.save_screenshot()
                self.quit_game("! Tackle is broken")

            if is_fish_captured():
                print('! Fish captured after pulling stage')
                self.keep_the_fish()
            elif is_fish_hooked():
                print('! Failed to capture the fish after pulling stage')
                if self.tackle.pull(i=4):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish_2')
            if not is_fish_hooked():
                # cast and wait
                click()
                sleep(4)

            print('Sinking Lure')
            timeout = 30
            while timeout and not is_moving_in_bottom_layer() and not is_fish_hooked():
                sleep(2)
                timeout -= 2
            print('Lure reached bottom layer or a fish was hooked, timeout:', timeout)
            self.tackle.reel.do_pre_rotation()

            pirking_limit = 10
            while not is_fish_hooked():

                # adjust the depth of the lure if no fish is hooked
                pirking_limit -= 1
                print("Pirking limit:", pirking_limit)
                if pirking_limit < 0:
                    press('enter')
                    sleep(2)
                    press('enter')
                    self.tackle.reel.do_pre_rotation()
                    pirking_limit = 10

                hold_right_click(duration=duration)
                sleep(delay)

            print('Fish is hooked, start retrieving')
            with hold('shift'):
                self.tackle.retrieve(duration=8)
            click()

            if is_fish_captured():
                print('! Fish caught without pulling')
                self.keep_the_fish()
            elif is_fish_hooked():
                #todo5
                while not self.tackle.pull(i = 8):
                    print('! Failed to capture the fish')
                self.keep_the_fish()
            else:
                self.cast_miss_count += 1

        
    def quit_game(self, msg=""):
        print(msg)
        press('esc')
        sleep(1) # wait for the menu to load
        moveTo(locateOnScreen('../static/quit.png', confidence=0.8), duration=0.4) 
        click()
        sleep(1)
        moveTo(locateOnScreen('../static/yes.png', confidence=0.8), duration=0.4)
        click()
        self.show_quit_msg()


    def show_quit_msg(self):
        if not self.keep_fish_count:
            print('No fish have been caught yet.')
            print('The script has been terminated.')
            exit()
        total_fish_count = self.marked_fish_count + self.unmarked_fish_count
        total_cast_count = self.cast_miss_count + total_fish_count
        print('The script has been terminated.')
        print('--------------------Result--------------------')
        print(f'Caught fishes  : {self.keep_fish_count}')
        print(f'Marked rate    : {self.marked_fish_count}/{total_fish_count} {int((self.marked_fish_count) / total_fish_count * 100)}%')
        print(f'Bite rate      : {total_fish_count}/{total_cast_count} {int(total_fish_count / total_cast_count * 100)}%')
            
        print(f'Start time     : {self.timer.get_start_datetime()}')
        print(f'Finish time    : {self.timer.get_cur_datetime()}')
        print(f'Execution time : {self.timer.get_duration()}')
        exit()


    def save_screenshot(self):
        # datetime.now().strftime("%H:%M:%S")
        press('q')
        with open(fr'../screenshots/{self.timer.get_cur_timestamp()}.png', 'wb') as file: 
            screenshot().save(file, 'png')
        press('esc')


    def relogin(self):
        pass
    
    def drink_coffee(self):
        keyDown('t')
        sleep(1)
        moveTo(locateOnScreen('../static/coffee.png', confidence=0.98), duration=0.5)
        click()
        sleep(0.5)
        keyUp('t')