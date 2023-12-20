from pyautogui import *
from time import sleep
from tackle import Tackle
import keyboard
from timer import Timer
import win32api, win32con
from threading import Thread
from monitor import *
from mouse import hold_left_click, hold_right_click

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
                self.start_spin_fishing()
            elif self.fishing_strategy == 'strong_pirking':
                self.start_strong_pirking()
            elif self.fishing_strategy == 'pirking':
                self.start_pirking()
            elif self.fishing_strategy == 'twitching':
                self.start_special_spin_fishing(0.25, 1)
            elif self.fishing_strategy == 'walking_dog':
                self.start_special_spin_fishing(0.25, 1)
            elif self.fishing_strategy == 'jig_step':
                self.start_jig_step_fishing()
            elif self.fishing_strategy == 'jig_step_1':
                self.start_jig_step_fishing(False, 1, 3)
            elif self.fishing_strategy == 'bottom':
                #todo: improve bottom fishing
                failed_count = 0
                rod_key = 0
                while True:
                    if not tackle.is_fish_hooked():
                        rod_key = 1 if rod_key == 3 else rod_key + 1
                        press(f'{rod_key}')
                        failed_count = 0
                    else:
                        failed_count += 1
                        if failed_count % 1 == 0 and self.trophy_mode:
                            self.drink_coffee()
                    sleep(1)
                    if tackle.is_broked():
                        print('The rod is broken')
                        self.save_screenshot()
                        self.quit_game()
                    if tackle.is_fish_hooked():
                        if self.trophy_mode:
                            tackle.retrieve(duration=16, delay=4)
                        else:
                            tackle.retrieve(duration=4, delay=2)
                        # tackle.tighten_fishline()
                        if tackle.is_fish_hooked():
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
                                if tackle.is_fish_hooked():
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

    def start_spin_fishing(self):
        pull_timeout = 4
        while True:
            if is_tackle_broked(): #todo: use another thread to monitor it
                print('! Tackle is broken')
                self.save_screenshot()
                self.quit_game()

            self.tackle.reset()

            if is_fish_captured():
                print('! Fish caught without pulling')
                self.keep_the_fish()
            elif is_fish_hooked():
                print('! Fish hooked while resetting')
                if self.tackle.pull(i=pull_timeout):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    print('! Back to normal routine')
            
            self.tackle.cast()
            self.tackle.retrieve()

            # retrieval is done
            if is_fish_hooked():
                if self.tackle.pull(i=pull_timeout):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            else:
                self.cast_miss_count += 1

    def start_special_spin_fishing(self, duration, delay):
        rod = self.tackle
        pull_timeout = 4
        while True:
            if is_tackle_broked(): #todo: use another thread to monitor it
                print('! Rod is broken')
                self.save_screenshot()
                self.quit_game()

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
            
            rod.cast()
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

    def start_jig_step_fishing(self, waiting=True, duration=0.52, delay=3):
        rod = self.tackle
        pull_timeout = 6 #todo
        while True:
            if is_tackle_broked(): #todo: use another thread to monitor it
                print('! Rod is broken')
                self.save_screenshot()
                self.quit_game()

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

    def start_strong_pirking(self):
        while True:
            if is_tackle_broked(): #todo: use another thread to monitor it
                print('! Rod is broken')
                self.save_screenshot()
                self.quit_game()

            click()
            sleep(4)

            print('Waiting for lure sinking to bottom layer')
            timeout = 30
            while timeout and not is_moving_in_bottom_layer() and not is_fish_hooked():
                sleep(2)
                timeout -= 2
            print('Lure reached bottom layer, timeout:, ', timeout)
            self.tackle.reel.do_pre_rotation()

            while not is_fish_hooked():
                hold_right_click(1.5)
                sleep(4)

            print('Fish is hooked, start retrieving')
            with hold('shift'):
                self.tackle.retrieve(duration=8)
            click()

            if is_fish_captured():
                print('! Fish caught without pulling')
                self.keep_the_fish()
        
            if is_fish_hooked():
                if self.tackle.pull(i=8):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            else:
                self.cast_miss_count += 1
    
    def start_pirking(self):
        while True:
            if is_tackle_broked(): #todo: use another thread to monitor it
                print('! Rod is broken')
                self.save_screenshot()
                self.quit_game()

            click()
            sleep(4)

            print('Waiting for lure sinking to bottom layer')
            timeout = 30
            while timeout and not is_moving_in_bottom_layer() and not is_fish_hooked():
                sleep(2)
                timeout -= 2
            print('Lure reached bottom layer, timeout:, ', timeout)
            self.tackle.reel.do_pre_rotation()

            while not is_fish_hooked():
                hold_right_click(0.5)
                sleep(2)

            print('Fish is hooked, start retrieving')
            with hold('shift'):
                self.tackle.retrieve(duration=8)
            click()

            if is_fish_captured():
                print('! Fish caught without pulling')
                self.keep_the_fish()
        
            if is_fish_hooked():
                if self.tackle.pull(i=8):
                    self.keep_the_fish()
                else:
                    print('! Failed to capture the fish')
                    #todo
            else:
                self.cast_miss_count += 1

        
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
        if not self.keep_fish_count:
            print('No fish have been caught yet.')
            print('The script has been terminated.')
            return
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