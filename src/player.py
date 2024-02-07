"""
Module for Player class

Todo: docstrings
"""
from time import sleep, time
from datetime import datetime
from threading import Thread

from pyautogui import *
import win32api, win32con
import keyboard

from tackle import Tackle
from timer import Timer
import monitor
from monitor import *
from script import *
from userprofile import UserProfile

class Player():
    keep_fish_count = 0
    marked_fish_count = 0
    unmarked_fish_count = 0
    cast_miss_count = 0
    coffee_count = 0
    trophy_mode = None
    cast_records = []
    keep_records = []

    def __init__(self, profile: UserProfile, config: configparser.ConfigParser) -> None:
        """Initialize attributes based on the user profile.

        :param profile: profile
        :type profile: UserProfile
        # todo
        """
        self.timer = Timer()

        # general settings
        self.keepnet_limit = config['game'].getint('keepnet_limit')
        self.harvest_baits_threshold = config['game'].getfloat('harvest_baits_threshold')

        # shortcuts
        self.coffee_shortcut = config['shortcut']['coffee']
        self.shovel_spoon_shortcut = config['shortcut']['shovel_spoon']

        # user profile and command line arguments
        self.profile = profile

        self.fishes_to_catch = self.keepnet_limit - profile.fishes_in_keepnet
        self.tackle = Tackle()
        self.pre_refill_time = 0
        

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
            if self.profile.enable_release_unmarked:
                press('backspace')
                print('Release unmarked fish')
                return

        # if the fish is marked or the release strategy is set to none, keep the fish
        press('space')
        print('Keep the fish')
        self.keep_fish_count += 1
        if self.is_keepnet_full():
            self.normal_quit('Keepnet limit reached')

    def is_keepnet_full(self) -> bool:
        """Check if the keepnet is full

        :return: True if the keepnet limit is reached, False otherwise
        :rtype: bool
        """
        return self.keep_fish_count == self.fishes_to_catch

    # todo: revise and add docstring
    def start_fishing(self):
        try:
            match self.profile.fishing_strategy:
                case 'spin':
                    self.spin_fishing()
                case 'spin_with_pause':
                    self.spin_fishing_with_pause()
                case 'bottom':
                    self.bottom_fishing()
                case 'marine':
                    self.marine_fishing()
                case _:
                    raise ValueError('Invalid fishing strategy')

        except KeyboardInterrupt:
                self.show_quit_msg()

    def refilling_stage(self):
        if not self.profile.enable_food_comfort_refill:
            return

        # affected by weather, need a threshold
        if self.is_comfort_low() and time.time() - self.pre_refill_time > 300:
            self.pre_refill_time = time.time()
            self.consume_food('tea')
        sleep(0.25)
        if self.is_hunger_low():
            self.consume_food('carrot')
        sleep(0.25)

    def consume_food(self, food):
        with hold('t'):
            sleep(0.25)
            moveTo(getattr(monitor, f'get_{food}_icon_position')())
            click()

    def resetting_stage(self):
        while not is_tackle_ready():
            if self.tackle.reset():
                break
            elif is_fish_hooked():
                print('! Fish hooked while resetting')
                if self.tackle.pull(): # a single pull should do the job
                    self.keep_fish()
                break # whether success or not, back to main fishing loop
            elif is_fish_captured():
                print('! Fish captured without pulling')
                self.keep_fish()
                break
            elif is_tackle_broke():
                self.save_screenshot()
                self.normal_quit('! Tackle is broken')
            elif is_disconnected():
                self.disconnected_quit()
            # reset again if no fish is hoooked or captured

    def retrieving_stage(self, duration=16, delay=4, is_fast=False):
        if is_fast:
            keyDown('shift')

        while True:
            if self.tackle.retrieve(duration, delay):
                break
            elif is_fish_hooked():
                # if fish is still hoooked, refill energy and toggle accelerated retrieval
                if is_fast:
                    keyUp('shift')
                if self.profile.enable_coffee_drinking:
                    press(self.coffee_shortcut)
                    self.coffee_count += 1
                continue # retrive again
            elif is_fish_captured():
                print('! Fish captured without pulling')
                break # defer to pulling stage
            else:
                break # unexpected failure, return to main fishing loop

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
        self.tackle.reel.tighten_line()


    def pirking_stage(self):
        pirk_duration = self.profile.pirk_duration
        pirk_delay = self.profile.pirk_delay
        tighten_duration = self.profile.tighten_duration

        while not self.tackle.pirking(pirk_duration, pirk_delay):
            # adjust the depth of the lure if no fish is hooked
            print('Adjust lure depth')
            press('enter') # open reel
            sleep(4)
            self.tackle.reel.tighten_line(tighten_duration)
            self.cast_miss_count += 1 # add a miss count if pirking is failed
            # todo: improve dedicated miss count for marine fishing

    def pulling_stage(self):
        while True:
            if self.tackle.pull():
                self.keep_fish()
                break
            elif is_fish_hooked():
                self.tackle.retrieve(duration=8, delay=4) # half retrieval
            else:
                print('! Fish got away while pulling')
                break # leave it for the resetting stage

    def spin_fishing(self):
        while True:
            self.refilling_stage()
            self.resetting_stage()
            self.tackle.cast(power_level=5)
            self.retrieving_stage()
            # skip pulling if there is no fish
            if not is_fish_hooked():
                self.cast_miss_count += 1
                continue
            self.pulling_stage()

    def spin_fishing_with_pause(self):
        duration = self.profile.retrieval_duration
        delay = self.profile.retrieval_delay
        base_iteration = self.profile.base_iteration
        while True:
            self.refilling_stage()
            self.resetting_stage()
            self.tackle.cast(power_level=5)
            self.tackle.retrieve_with_pause(duration, delay, base_iteration)
            self.retrieving_stage(duration=4, delay=2)
            # skip pulling if there is no fish
            if not is_fish_hooked():
                self.cast_miss_count += 1
                continue
            self.pulling_stage()

    def bottom_fishing(self):
        #? add retrieval duration and delay
        check_delay = self.profile.check_delay
        cast_power_level = self.profile.cast_power_level
        check_counts = [0, 0, 0, 0]
        rod_key = 0

        while True:
            self.refilling_stage()
            self.harvesting_stage()

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
                    self.tackle.cast(cast_power_level, cast_delay=4)
                    click() # close the reel
                press('0')
                sleep(check_delay)
                continue

            check_counts[rod_key] = 0

            self.retrieving_stage(duration=4, delay=2)
            if is_fish_hooked():
                self.pulling_stage()
            self.resetting_stage()
            self.tackle.cast(cast_power_level, cast_delay=4)
            click() # close the reel

    def marine_fishing(self):
        while True:    
            self.refilling_stage()
            self.resetting_stage()
            self.tackle.cast(power_level=1)
            self.sinking_stage()
            self.pirking_stage()
            # for small fishes at 34m and 41m, use accelerated retrieval
            self.retrieving_stage(duration=8, is_fast=True)
            # there is a high chance that fish get away while retrieving from bottom layer
            if is_fish_hooked():
                self.pulling_stage()
        
    def normal_quit(self, msg=""):
        print(msg)

        # add sleep() to wait for the menu to load
        press('esc')
        sleep(0.25)
        moveTo(get_quit_position()) 
        click()
        sleep(0.25)
        moveTo(get_yes_position())
        click()
        self.show_quit_msg()

    def disconnected_quit(self):
        print('! No connection with the game server')

        # add sleep() to wait for the menu to load
        press('space')
        sleep(0.25)
        press('space')
        sleep(0.25)
  
        # another space might be required when server down
        press('space')
        sleep(0.25)

        moveTo(get_exit_icon_position())
        click()
        sleep(0.25)
        moveTo(get_confirm_exit_icon_position())
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
        print(f'Marked ratio   : {self.marked_fish_count}/{total_fish_count} {int((self.marked_fish_count) / total_fish_count * 100)}%')
        print(f'Bite rate      : {total_fish_count}/{total_cast_count} {int(total_fish_count / total_cast_count * 100)}%')   
        print(f'Start time     : {self.timer.get_start_datetime()}')
        print(f'Finish time    : {self.timer.get_cur_datetime()}')
        print(f'Execution time : {self.timer.get_duration()}')
        if self.profile.enable_coffee_drinking:
            print(f'Coffee Drank   : {self.coffee_count}')
        exit()

    def save_screenshot(self):
        # datetime.now().strftime("%H:%M:%S")
        press('q')
        with open(fr'../screenshots/{self.timer.get_cur_timestamp()}.png', 'wb') as file: 
            screenshot().save(file, 'png')
        press('esc')

    def is_energy_high(self):
        pos = get_energy_icon_position()
        if not pos:
            return False
        x, y = int(pos.x), int(pos.y)
        # default threshold: 0.74,  well done FishSoft
        last_point = int(19 + 152 * self.harvest_baits_threshold) - 1
        return pixel(x + 19, y) == pixel(x + last_point, y)
    
    def is_hunger_low(self):
        # 17 pre end 18 start
        pos = get_food_icon_position()
        if not pos:
            return False
        x, y = int(pos.x), int(pos.y)
        last_point = int(18 + 152 * 0.5) - 1
        return not pixel(x + 18, y) == pixel(x + last_point, y)

    def is_comfort_low(self):
        pos = get_comfort_icon_position()
        if not pos:
            return False
        x, y = int(pos.x), int(pos.y)
        last_point = int(18 + 152 * 0.51) - 1
        return not pixel(x + 18, y) == pixel(x + last_point, y)
    
    def harvesting_stage(self):
        if not self.profile.enable_baits_harvesting:
            return
        elif self.is_energy_high():
            self.harvest_baits()

    def harvest_baits(self):
        # digging
        press(self.shovel_spoon_shortcut)
        sleep(3)
        click()

        # wait for result
        sleep(5) # 4 is enough, + 1 for inspection
        i = 64
        while i > 0 and not is_harvest_success():
            i = sleep_and_decrease(i, 4)

        # accept result and hide the tool
        press('space')
        sleep(0.25)
        press('backspace')
        sleep(0.5) # wait for hide animation

    # todo
    def relogin(self):
        pass

# bottom fishing backup
    
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