"""
Module for Player class

Todo: docstrings
"""
from pyautogui import *
from time import sleep
from tackle import Tackle
import keyboard
from timer import Timer
import win32api, win32con
from threading import Thread
from monitor import *
from script import *
from datetime import datetime
from userprofile import UserProfile

class Player():
    keepnet_limit = 100
    keep_fish_count = 0
    marked_fish_count = 0
    unmarked_fish_count = 0
    cast_miss_count = 0
    delay = 12 # 8
    trophy_mode = None
    cast_records = []
    keep_records = []

    def __init__(self, profile: UserProfile) -> None:
        """Initialize attributes based on the user profile.

        :param profile: profile
        :type profile: UserProfile
        """
        self.keepnet_limit -= profile.current_fish_count
        self.fishing_strategy = profile.fishing_strategy
        self.release_strategy = profile.release_strategy
        self.tackle = Tackle(profile.reel_name)
        self.timer = Timer()

    # todo: complete this and add docstring
    def record_routine_duration(self, cast_time, keep_time) -> None:
        """Record cast time and keep time."""
        self.cast_records.append(cast_time)
        self.keep_records.append(keep_time)


    def keep_the_fish(self) -> None:
        """Handle the fish and record the fish count."""
        #! a trophy ruffe will break the checking mechanism
        if is_fish_marked():
            self.marked_fish_count += 1
        else:
            self.unmarked_fish_count += 1
            if self.release_strategy == 'unmarked':
                press('backspace')
                print('Release unmarked fish')
                return

        # if the fish is marked or the release strategy is set to none, keep the fish
        press('space')
        print('Keep the fish')
        self.keep_fish_count += 1
        if self.is_keepnet_full():
            self.quit_game()


    def is_keepnet_full(self) -> bool:
        """Check if the keepnet is full

        :return: True if the keepnet limit is reached, False otherwise
        :rtype: bool
        """
        return self.keep_fish_count == self.keepnet_limit

    # todo: revise and add docstring
    def start(self):
        tackle = self.tackle
        try:
            if self.fishing_strategy == 'spin':
                self.do_spin_fishing(time_limit=False)
            elif self.fishing_strategy == 'time_limit_spin':
                self.do_spin_fishing(time_limit=True)
            elif self.fishing_strategy == 'strong_pirking':
                self.do_pirking_fishing(duration=1.75, delay=4)
            elif self.fishing_strategy == 'pirking':
                self.do_pirking_fishing(duration=0.5, delay=2)
            elif self.fishing_strategy == 'twitching':
                self.do_special_spin_fishing(0.25, 1)
            elif self.fishing_strategy == 'walking_dog':
                self.do_special_spin_fishing(0.25, 1)
            elif self.fishing_strategy == 'jig_step':
                self.dp_jig_2step_fishing()
            elif self.fishing_strategy == 'jig_step_1':
                self.do_jig_step_fishing(False, 1, 3)
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
                        if is_fish_hooked():
                            if self.trophy_mode:
                                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(0), int(-200), 0, 0)
                            if tackle.pull():
                                self.keep_the_fish()
                            else:
                                print('! pull failed')
                                if self.trophy_mode:
                                    sleep(6)
                                    if is_fish_captured():
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
                    elif is_fish_captured():
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

    def start_resetting_stage(self):
        while not is_tackle_ready():
            if self.tackle.reset():
                break
            elif is_fish_hooked():
                print('! Fish hooked while resetting')
                # a single pull should do the job
                if self.tackle.pull():
                    self.keep_the_fish()
                break # success or not, back to normal program flow 
            elif is_fish_captured():
                print('! Fish captured without pulling')
                self.keep_the_fish() # keep it to reset the tackle
                break
            else:
                pass # reset again

    def start_retrieving_stage(self, duration=32, delay=4, is_fast=False):
        if is_fast:
            keyDown('shift')
        while True:
            if self.tackle.retrieve(duration=duration, delay=delay):
                break
            elif is_fish_hooked():
                #todo: refill the energy
                if is_fast:
                    keyUp('shift') # large fish, back to slow mode
                self.tackle.retrieve(duration=duration, delay=delay)
            elif is_fish_captured():
                print('! Fish captured without pulling')
                break # defer to pulling stage
            else:
                pass # retrieve again
        if is_fast:
            keyUp('shift')

    def start_sinking_stage(self):
        print('Sinking Lure')
        i = 30
        while i > 0:
            if is_moving_in_bottom_layer():
                break
            elif is_fish_hooked():
                return
            i = sleep_and_decrease(i, 2)
        self.tackle.reel.do_pre_rotation()


    def start_pirking_stage(self, duration, delay):
        while not self.tackle.pirking(duration, delay):
            # adjust the depth of the lure if no fish is hooked
            print('Adjust lure depth')
            press('enter') # open reel
            sleep(2)
            self.tackle.reel.do_pre_rotation()
            self.cast_miss_count += 1 # add a miss count if pirking is failed
            # todo: add miss count dedicated for marine fishing
    
    def start_pulling_stage(self):
        while True:
            if self.tackle.pull():
                self.keep_the_fish()
                break
            elif is_fish_hooked():
                self.tackle.retrieve(duration=16, delay=4) # half retrieval
            else:
                print('! Fish got away while pulling')
                break # leave it for the resetting stage

    def do_spin_fishing(self, time_limit=False):
        while True:
            #todo: revise time_limit spin fishing
            if time_limit and datetime.now().hour == 7 and datetime.now().minute >= 40:
                self.quit_game("! Time is up: 7:40 A.M.")
            #todo: use another thread to monitor it
            if is_tackle_broked():
                self.save_screenshot()
                self.quit_game("! Tackle is broken")

            self.start_resetting_stage()
            self.tackle.cast() # default
            self.start_retrieving_stage() # default
            # skip pulling if there is no fish
            if not is_fish_hooked():
                self.cast_miss_count += 1
                continue
            self.start_pulling_stage()


    def do_special_spin_fishing(self, duration, delay):
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
                if rod.pull():
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
                if rod.pull():
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            else:
                self.cast_miss_count += 1

    def do_jig_step_fishing(self, waiting=True, duration=0.52, delay=3):
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
                if rod.pull():
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
                if rod.pull():
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            else:
                self.cast_miss_count += 1

    def do_pirking_fishing(self, duration, delay):
        while True:
            if is_tackle_broked(): #todo: use another thread to monitor it
                self.save_screenshot()
                self.quit_game("! Tackle is broken")
                
            self.start_resetting_stage()
            self.tackle.cast(power_level=1)
            self.start_sinking_stage()
            self.start_pirking_stage(duration, delay)
            # for small fishes at 34m and 41m, use accelerated retrieval
            self.start_retrieving_stage(duration=8, is_fast=True)
            # there is a high chance that fish get away while retrieving from bottom layer
            if is_fish_hooked():
                self.start_pulling_stage()

        
    def quit_game(self, msg=""):
        print(msg)
        press('esc')
        sleep(1) # wait for the menu to load
        moveTo(get_quit_position(), duration=0.4) 
        click()
        sleep(1)
        moveTo(get_yes_position(), duration=0.4)
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

    # todo
    def relogin(self):
        pass
    
    # todo
    def drink_coffee(self):
        keyDown('t')
        sleep(1)
        moveTo(locateOnScreen('../static/coffee.png', confidence=0.98), duration=0.5)
        click()
        sleep(0.5)
        keyUp('t')