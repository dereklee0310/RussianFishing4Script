"""
Module for Player class

Todo: docstrings
"""
from time import sleep
from datetime import datetime
from threading import Thread

from pyautogui import *
import win32api, win32con
import keyboard

from tackle import Tackle
from timer import Timer
from monitor import *
from script import *
from userprofile import UserProfile

class Player():
    keepnet_limit = 100
    keep_fish_count = 0
    marked_fish_count = 0
    unmarked_fish_count = 0
    cast_miss_count = 0
    # delay = 8
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
        self.keep_strategy = profile.keep_strategy
        self.tackle = Tackle(profile.reel_name)
        self.timer = Timer()

        self.duration = profile.duration
        self.delay = profile.delay
        self.check_delay_second = profile.check_delay_second
        self.cast_power_level = profile.cast_power_level

    # todo: complete this and add docstring
    def record_routine_duration(self, cast_time, keep_time) -> None:
        """Record cast time and keep time.
        """
        self.cast_records.append(cast_time)
        self.keep_records.append(keep_time)

    def keep_fish(self) -> None:
        """Keep or release the fish and record the fish count.
        """
        #! a trophy ruffe will break the checking mechanism
        if is_fish_marked():
            self.marked_fish_count += 1
        else:
            self.unmarked_fish_count += 1
            if self.keep_strategy == 'marked':
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
    def start_fishing(self):
        try:
            match self.fishing_strategy:
                case 'spin':
                    self.spin_fishing()
                case 'bottom':
                    self.bottom_fishing()
                case 'strong_pirking':
                    self.pirking_fishing(duration=1.75, delay=4)
                case 'pirking':
                    self.pirking_fishing(duration=0.5, delay=2)
                case 'spin_with_pause':
                    self.spin_fishing_with_pause(duration=self.duration, delay=self.delay)
                #todo: default
        except KeyboardInterrupt:
                self.show_quit_msg()

    def resetting_stage(self):
        while not is_tackle_ready():
            if self.tackle.reset():
                break
            elif is_fish_hooked():
                print('! Fish hooked while resetting')
                # a single pull should do the job
                if self.tackle.pull():
                    self.keep_fish()
                break # whether success or not, back to normal program flow 
            elif is_fish_captured():
                print('! Fish captured without pulling')
                self.keep_fish()
                break
            # reset again if no fish is hoooked or captured

    def retrieving_stage(self, duration=16, delay=4, is_fast=False):
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

    def sinking_stage(self):
        print('Sinking Lure')
        i = 30
        while i > 0:
            if is_moving_in_bottom_layer():
                break
            elif is_fish_hooked():
                return # start retrieving immediately
            i = sleep_and_decrease(i, 2)
        self.tackle.reel.do_pre_rotation()


    def pirking_stage(self, duration, delay):
        while not self.tackle.pirking(duration, delay):
            # adjust the depth of the lure if no fish is hooked
            print('Adjust lure depth')
            press('enter') # open reel
            sleep(4)
            self.tackle.reel.do_pre_rotation()
            self.cast_miss_count += 1 # add a miss count if pirking is failed
            # todo: improve dedicated miss count for marine fishing

    def pulling_stage(self):
        while True:
            if self.tackle.pull():
                self.keep_fish()
                break
            elif is_fish_hooked():
                press('space') # use landing net
                sleep(6)
                if is_fish_captured():
                    self.keep_fish()
                    break
                else:
                    press('space') # hide landing net if failed
                self.tackle.retrieve(duration=8, delay=4) # half retrieval
            else:
                print('! Fish got away while pulling')
                break # leave it for the resetting stage

    def spin_fishing(self):
        while True:
            #todo: use another thread to monitor it
            if is_tackle_broked():
                self.save_screenshot()
                self.quit_game('! Tackle is broken')

            self.resetting_stage()
            self.tackle.cast()
            self.retrieving_stage()
            # skip pulling if there is no fish
            if not is_fish_hooked():
                self.cast_miss_count += 1
                continue
            self.pulling_stage()

    def spin_fishing_with_pause(self, duration, delay):
        while True:
            #todo: use another thread to monitor it
            if is_tackle_broked():
                self.save_screenshot()
                self.quit_game('! Tackle is broken')

            self.resetting_stage()
            self.tackle.cast() # default
            self.tackle.retrieve_with_pause(duration, delay)
            self.retrieving_stage(duration=8) # default
            # skip pulling if there is no fish
            if not is_fish_hooked():
                self.cast_miss_count += 1
                continue
            self.pulling_stage()

    def bottom_fishing(self, retrieval_duration=4, retrieval_delay=2):
        check_counts = [0, 0, 0, 0]
        rod_key = 0
        while True:
            if is_tackle_broked():
                print('! Tackle is broken')
                self.save_screenshot()
                self.quit_game()
            
            rod_key = 1 if rod_key == 3 else rod_key + 1
            print(f'Checking rod {rod_key}')
            press(f'{rod_key}')
            sleep(1) # wait for pick up animation

            # check the next rod if no fish is hooked
            if not is_fish_hooked():
                self.cast_miss_count += 1
                check_counts[rod_key] += 1
                if check_counts[rod_key] > 16:
                    check_counts[rod_key] = 0
                    self.resetting_stage()
                    self.tackle.cast(power_level=self.cast_power_level, cast_delay=4)
                press('0')
                sleep(self.check_delay_second)
                continue

            check_counts[rod_key] = 0

            self.retrieving_stage(duration=retrieval_duration, delay=retrieval_delay)
            if is_fish_hooked():
                self.pulling_stage()
            self.resetting_stage()
            self.tackle.cast(power_level=self.cast_power_level, cast_delay=4)

    def pirking_fishing(self, duration, delay):
        while True:
            if is_tackle_broked(): #todo: use another thread to monitor it
                self.save_screenshot()
                self.quit_game('! Tackle is broken')
                
            self.resetting_stage()
            self.tackle.cast(power_level=1)
            self.sinking_stage()
            self.pirking_stage(duration, delay)
            # for small fishes at 34m and 41m, use accelerated retrieval
            self.retrieving_stage(duration=8, is_fast=True)
            # there is a high chance that fish get away while retrieving from bottom layer
            if is_fish_hooked():
                self.pulling_stage()
        
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
        print('The script has been terminated')
        if not self.keep_fish_count:
            print('No fish have been caught yet')
            exit()
        total_fish_count = self.marked_fish_count + self.unmarked_fish_count
        total_cast_count = self.cast_miss_count + total_fish_count
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


# bottom backup
# failed_count = 0
# rod_key = 0
# while True:
#     if not is_fish_hooked():
#         rod_key = 1 if rod_key == 3 else rod_key + 1
#         press(f'{rod_key}')
#         failed_count = 0
#     else:
#         failed_count += 1
#         if failed_count % 1 == 0 and self.trophy_mode:
#             self.drink_coffee()
#     sleep(1)
#     if is_tackle_broked():
#         print('The rod is broken')
#         self.save_screenshot()
#         self.quit_game()
#     if is_fish_hooked():
#         if self.trophy_mode:
#             tackle.retrieve(duration=16, delay=4)
#         else:
#             tackle.retrieve(duration=4, delay=2)
#         if is_fish_hooked():
#             if self.trophy_mode:
#                 win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(0), int(-200), 0, 0)
#             if tackle.pull():
#                 self.keep_the_fish()
#             else:
#                 print('! pull failed')
#                 if self.trophy_mode:
#                     sleep(6)
#                     if is_fish_captured():
#                         self.keep_the_fish()
#                     else:
#                         print('! second check failed')
#                 else:
#                     tackle.reset(self.trophy_mode)
#             if self.trophy_mode:
#                 win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(0), int(200), 0, 0)
#         if not self.trophy_mode:
#             self.delay = 4 if self.delay == 4 else self.delay - 1
#         else:
#             self.delay = 8 if self.delay == 8 else self.delay - 1
#             #todo: reset tackle
#     elif is_fish_captured():
#         self.keep_the_fish()
#     else:
#         press('0')
#         sleep(1)
#         self.cast_miss_count += 1
#         if self.cast_miss_count % 4 == 0:
#             self.delay += 1
#         if self.cast_miss_count % 32 == 0:
#             #todo: package this
#             for rod_key in range(1, 4):
#                 press(f'{rod_key}')
#                 tackle.reset()
#                 if is_fish_hooked():
#                     if tackle.pull():
#                         self.keep_the_fish()
#                 sleep(1)
#                 keyDown('shift')
#                 mouseDown()
#                 sleep(1)
#                 keyUp('shift')
#                 mouseUp()
#                 if self.trophy_mode:
#                     sleep(3)
#                 else:
#                     sleep(1)
#                 # click()
#                 sleep(1)
#                 click()
#             self.delay = 8 # reset delay
#         sleep(self.delay)
#         continue
    
#     sleep(1)
#     keyDown('shift')
#     mouseDown()
#     sleep(1)
#     keyUp('shift')
#     mouseUp()
#     print(self.trophy_mode)
#     if self.trophy_mode:
#         sleep(3)
#     else:
#         sleep(1)
#     # click()
#     sleep(1)
#     click()
#     sleep(self.delay)