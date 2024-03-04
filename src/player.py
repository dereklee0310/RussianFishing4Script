"""
Module for Player class

Todo: docstrings
"""
import os
from time import sleep, time
from datetime import datetime
from threading import Thread
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from pyautogui import *
import win32api, win32con
from configparser import ConfigParser
import keyboard
from prettytable import PrettyTable
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

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

    total_coffee_count = 0 
    cur_coffee_count = 0
    tea_count = 0
    pre_refill_time = 0 # for tea drinking
    carrot_count = 0
    harvest_count = 0

    def __init__(self, profile: UserProfile, config: ConfigParser) -> None:
        """Configure static game settings.

        :param profile: consists of user profile and command line arguments
        :type profile: UserProfile
        :param config: parsed configuration
        :type config: ConfigParser
        """
        self.profile = profile
        self.timer = Timer()
        self.tackle = Tackle(self.timer)

        # general settings
        self.keepnet_limit = config['game'].getint('keepnet_limit')
        self.fishes_to_catch = self.keepnet_limit - profile.fishes_in_keepnet
        self.harvest_baits_threshold = config['game'].getfloat('harvest_baits_threshold')
        self.coffee_limit = config['game'].getint('coffee_limit')

        # shortcuts
        self.coffee_shortcut = config['shortcut']['coffee']
        self.shovel_spoon_shortcut = config['shortcut']['shovel_spoon']

    def start_fishing(self) -> None:
        """Start main fishing loop with specified fishing strategt.
        """
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
                case 'wakey_rig':
                    self.wakey_rig_fishing()
                # default: already checked in app.show_user_settings()
        except KeyboardInterrupt:
                # avoid shift key stuck
                if self.profile.enable_acceleration:
                    keyUp('shift')
                print(self.gen_result('Terminated by user'))
                if self.profile.enable_plotting:
                    self.plot_and_save()
                exit()

    # ---------------------------------------------------------------------------- #
    #                              main fishing loops                              #
    # ---------------------------------------------------------------------------- #
    def spin_fishing(self) -> None:
        """Main spin fishing loop.
        """
        while True:
            self.refilling_stage()
            self.resetting_stage()
            self.tackle.cast(self.profile.cast_power_level)
            self.retrieving_stage()
            if not is_fish_hooked():
                self.cast_miss_count += 1
                continue
            self.pulling_stage()

    # todo: combine this with spin_fishing()
    def spin_fishing_with_pause(self) -> None:
        """Spin fishing with a "retrieve_with_pause" stage before normal retrieving stage.
        """
        while True:
            self.refilling_stage()
            self.resetting_stage()
            self.tackle.cast(self.profile.cast_power_level)
            self.tackle.retrieve_with_pause(self.profile.retrieval_duration, 
                                            self.profile.retrieval_delay, 
                                            self.profile.base_iteration,
                                            self.profile.enable_acceleration)
            self.retrieving_stage(duration=4, delay=2)
            if not is_fish_hooked():
                self.cast_miss_count += 1
                continue
            self.pulling_stage()

    def bottom_fishing(self) -> None:
        """Main bottom fishing loop.
        """
        # todo: add retrieval duration and delay
        check_counts = [-1, 0, 0, 0]
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
                check_counts[rod_key] += 1
                self.cast_miss_count += 1
                # recast if check failed more than 16 times
                if check_counts[rod_key] > 16:
                    check_counts[rod_key] = 0
                    self.resetting_stage()
                    self.tackle.cast(self.profile.cast_power_level, cast_delay=4)
                    click()
                
                press('0')
                sleep(self.profile.check_delay)
                continue

            check_counts[rod_key] = 0
            self.retrieving_stage(duration=4, delay=2)
            if is_fish_hooked():
                self.pulling_stage()
            self.resetting_stage()
            self.tackle.cast(self.profile.cast_power_level, cast_delay=4)
            click()

    def marine_fishing(self) -> None:
        """Main marine fishing loop.
        """
        while True:    
            self.refilling_stage()
            self.resetting_stage()
            self.tackle.cast(self.profile.cast_power_level)
            self.marine_sinking_stage()
            self.pirking_stage()
            # for small fishes at 34m and 41m, use accelerated retrieval
            self.retrieving_stage(duration=8, accelerated=True)
            if is_fish_hooked():
                self.pulling_stage()

    def wakey_rig_fishing(self) -> None:
        """Main wakey rig fishing loop.
        """
        while True:    
            self.refilling_stage()
            self.resetting_stage()
            self.tackle.cast(self.profile.cast_power_level)
            self.wakey_sinking_stage()
            # self.pirking_stage()
            self.retrieving_stage(duration=4, delay=2)
            if is_fish_hooked():
                self.pulling_stage()

    def trolling_fishing(self) -> None:
        # temp
        rods = range(1, 4)
        base_waiting_time = 30

        while True:
            sleep(base_waiting_time)
            self.retrieving_stage()
            if is_fish_hooked():
                self.pulling_stage()
            else:
                # reset thrid rod to check other rods
                self.resetting_stage()

            for rod in [1, 3]:
                press(str(rod))
                if is_fish_hooked():
                    self.retrieving_stage()
                    if is_fish_hooked():
                        self.pulling_stage()
                        self.tackle.cast(self.profile.cast_power_level)
                    else:
                        self.cast_miss_count += 1
            self.tackle.cast(self.profile.cast_power_level)


    # ---------------------------------------------------------------------------- #
    #            stages and their helper functions in main fishing loops           #
    # ---------------------------------------------------------------------------- #
    def harvesting_stage(self) -> None:
        """If enable_baits_harvesting is True and the energy level 
            is greater than the threshold, harvest baits. 
        """
        if not self.profile.enable_baits_harvesting:
            return
        elif is_energy_high(self.harvest_baits_threshold):
            print('Harvest baits')
            self.harvest_baits()
            self.harvest_count += 1

    def harvest_baits(self) -> None:
        """Use shortcut defined in config.ini to use shovel/spoon, 
            then hide the tool after the harvest success or the timeout is reached.
        """
        # pull out the shovel/spoon and harvest baits
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

    def refilling_stage(self) -> None:
        """If enable_food_comfort_refill is enabled, 
            consume tea or carrot to refill comfort and food level.
        """
        if not self.profile.enable_food_comfort_refill:
            return

        # refill comfort
        # comfort is affected by weather, add a time threshold to prevent over drinking
        if is_comfort_low() and time.time() - self.pre_refill_time > 300:
            self.pre_refill_time = time.time()
            self.consume_food('tea')
            self.tea_count += 1
        sleep(0.25)

        # refill food level
        if is_food_level_low():
            self.consume_food('carrot')
            self.carrot_count += 1
        sleep(0.25)

    def consume_food(self, food: str) -> None:
        """Open food menu, then click on food icon to consume it.

        :param food: food's name
        :type food: str
        """
        print(f'Consume {food}')
        with hold('t'):
            sleep(0.25)
            moveTo(getattr(monitor, f'get_{food}_icon_position')())
            click()

    def resetting_stage(self) -> None:
        """Reset the tackle until the it's ready or an exceptional event occurs.
        """
        while not self.tackle.reset():
            if is_fish_hooked():
                if self.tackle.pull(): # a single pull should do the job
                    self.handle_fish()
                break # whether success or not, back to main fishing loop
            elif is_fish_captured():
                self.handle_fish()
                break
            elif is_tackle_broke():
                self.save_screenshot()
                self.general_quit('Tackle is broken')
            elif is_disconnected():
                self.disconnected_quit()
            # reset again if no fish is hoooked or captured

    def retrieving_stage(self, duration=16, delay=4, accelerated=False):
        """Retrieve the fishing line until it's fully retrieved or an exceptional event occurs.

        :param duration: base retrieval time, defaults to 16
        :type duration: int, optional
        :param delay: delay after retrieval, defaults to 4
        :type delay: int, optional
        :param accelerated: option for accelerated retrieval, defaults to False
        :type accelerated: bool, optional
        """
        if accelerated:
            keyDown('shift')

        while not self.tackle.retrieve(duration, delay):
            # no fish, return to main loop
            # captured, defer to pulling stage
            if is_line_at_end():
                self.general_quit('Fishing line is at its end')

            if not is_fish_hooked() or is_fish_captured():
                break

            # toggle accelerated retrieval and refill energy
            if accelerated:
                keyUp('shift')

            # drink coffee if energy is low
            if not is_energy_high(threshold=0.9) and self.profile.enable_coffee_drinking:
                self.cur_coffee_count += 1
                if self.cur_coffee_count > self.coffee_limit:
                    press('esc') # back to control panel to reduce power usage
                    print(self.gen_result('Coffee limit reached'))
                    exit()
                print('Consume coffee')
                press(self.coffee_shortcut)
                self.total_coffee_count += 1

        if accelerated:
            keyUp('shift')
        self.cur_coffee_count = 0

    def marine_sinking_stage(self) -> None:
        """Sink the lure until it reaches the bottom layer, 
            a fish is hooked, or timeout reached.
        """
        print('Sinking Lure')
        i = self.profile.sink_timeout
        while i > 0:
            if is_moving_in_bottom_layer():
                print('Lure reached bottom layer')
                break
            elif is_fish_hooked():
                print('Fish is hooked')
                return
            i = sleep_and_decrease(i, 2)
        self.tackle.reel.tighten_line(self.profile.tighten_duration)

    def wakey_sinking_stage(self) -> None:
        """Sink the lure until a fish is hooked or timeout reached.
        """
        print('Sinking Lure')
        # todo: dynamic timeout
        i = 60
        while i > 0:
            if is_fish_hooked():
                print('Fish is hooked')
                break
            i = sleep_and_decrease(i, 2)


    def pirking_stage(self) -> None:
        """Perform pirking until a fish is hooked, adjust the lure if timeout is reached.
        """
        while not self.tackle.pirking(self.profile.pirk_duration, self.profile.pirk_delay):
            # adjust the depth of the lure if no fish is hooked
            print('Adjust lure depth')
            press('enter') # open reel
            sleep(4)
            self.tackle.reel.tighten_line(self.profile.tighten_duration)
            self.cast_miss_count += 1
            # todo: improve dedicated miss count for marine fishing

    def pulling_stage(self) -> None:
        """Pull the fish up, then handle it.
        """
        while True:
            if self.tackle.pull():
                self.handle_fish()
                break
            elif not is_fish_hooked():
                break
            self.tackle.retrieve(duration=8, delay=4) # half retrieval
    
    def handle_fish(self) -> None:
        """Keep or release the fish and record the fish count.
        """
        #! a trophy ruffe will break the checking mechanism            
        if not is_fish_marked():
            self.unmarked_fish_count += 1
            if self.profile.enable_unmarked_release:
                print('Release unmarked fish')
                press('backspace')
                return
        else:
            self.marked_fish_count += 1

        # fish is marked or enable_unmarked_release is set to False
        print('Keep the fish')
        press('space')

        # avoid wrong cast hour
        if self.profile.fishing_strategy == 'bottom':
            self.timer.update_cast_hour()
        
        self.timer.add_cast_hour()

        self.keep_fish_count += 1
        if self.keep_fish_count == self.fishes_to_catch:
            self.general_quit('Keepnet limit reached')

    # ---------------------------------------------------------------------------- #
    #                                     misc                                     #
    # ---------------------------------------------------------------------------- #
    def general_quit(self, termination_cause: str) -> None:
        """Show the running result with cause of termination, 
            then quit the game through control panel.

        :param termination_cause: the cause of the termination
        :type termination_cause: str
        """
        press('esc')
        sleep(0.25)
        moveTo(get_quit_position()) 
        click()
        sleep(0.25)
        moveTo(get_yes_position())
        click()

        result = self.gen_result(termination_cause)
        print(result)
        if self.profile.enable_email_sending:
            self.send_email(result)
        if self.profile.enable_plotting:
            self.plot_and_save()
        exit()

    def disconnected_quit(self) -> None:
        """show the running result with disconnected status,
            then quit the game through main menu.
        """
        press('space')
        sleep(0.25)

        # sleep to bypass the black screen (experimental)
        sleep(10)

        press('space')
        sleep(0.25)
  
        moveTo(get_exit_icon_position())
        click()
        sleep(0.25)
        moveTo(get_confirm_exit_icon_position())
        click()

        result = self.gen_result('Disconnection')
        print(result)
        if self.profile.enable_email_sending:
            self.send_email(result)
        exit()

    def gen_result(self, termination_cause: str) -> PrettyTable:
        """Generate a PrettyTable object for logging and email based on running results.

        :param termination_cause: cause of termination
        :type termination_cause: str
        :return: table consisting cause of termination and run-time records
        :rtype: PrettyTable
        """
        total_fish_count = self.marked_fish_count + self.unmarked_fish_count
        total_cast_count = self.cast_miss_count + total_fish_count

        table = PrettyTable(header=False, align='l')
        table.title = 'Running Results'
        # table.field_names = ['Record', 'Value']

        table.add_rows(
            [   
                ['Cause of termination', termination_cause],
                ['Start time', self.timer.get_start_datetime()], 
                ['Finish time', self.timer.get_cur_datetime()], 
                ['Running time', self.timer.get_duration()], 
                ['Fish caught', self.keep_fish_count]
            ])
        
        if total_fish_count > 0:
            marked_rate = int((self.marked_fish_count) / total_fish_count * 100)
            table.add_row(['Marked ratio', f'{self.marked_fish_count}/{total_fish_count} {marked_rate}%'])
        if total_cast_count > 0:
            bite_rate = int(total_fish_count / total_cast_count * 100)
            table.add_row(['Bite rate', f'{total_fish_count}/{total_cast_count} {bite_rate}%'])
        if self.profile.enable_coffee_drinking:
            table.add_row(['Coffee consumed', self.total_coffee_count])
        if self.profile.enable_food_comfort_refill:
            table.add_rows(
                [
                    ['Tea consumed', self.tea_count],
                    ['Carrot consumed', self.carrot_count]
                ])
            
        if self.profile.enable_baits_harvesting:
            table.add_row(['Harvest baits count', self.harvest_count])
        return table

    def send_email(self, table: PrettyTable) -> None:
        """Send an notification email to the user's email address that specified in ".env".

        :param table: table consisting cause of termination and run-time records
        :type table: PrettyTable
        """
        # get environment variables
        load_dotenv()
        sender = os.getenv('GMAIL')
        password = os.getenv('APP_PASSWORD')
        
        # configure mail info
        msg = MIMEMultipart()
        msg['Subject'] = "RussianFishing4Script: Notice of Program Termination"
        msg['From'] = sender
        recipients = [sender]
        msg['To'] = ', '.join(recipients)

        # content
        html = MIMEText(table.get_html_string(), 'html')
        msg.attach(html)

        # send email with SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            # smtp_server.ehlo()
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())
        print('An email containing the running results has been sent to your email address')

    def save_screenshot(self) -> None:
        """Save screenshot to screenshot/, only be invoked when the tackle is broke.
        """
        # datetime.now().strftime("%H:%M:%S")
        press('q')
        with open(fr'../screenshots/{self.timer.get_cur_timestamp()}.png', 'wb') as file: 
            screenshot().save(file, 'png')
        press('esc')

    def plot_and_save(self):
        cast_rhour_list, cast_ghour_list = self.timer.get_cast_hour_list()

        fig, ax = plt.subplots(nrows=1, ncols=2)
        # fig.canvas.manager.set_window_title('Record')
        ax[0].set_ylabel('Fish')
        
        fish_per_rhour = [0] * 12
        for hour in cast_rhour_list:
            fish_per_rhour[hour] += 1
        ax[0].plot(range(12), fish_per_rhour)
        ax[0].set_title('Fish Caughted per Real Hour')
        ax[0].set_xticks(range(12))
        ax[0].set_xlabel('Hour (real running time)')
        ax[0].yaxis.set_major_locator(MaxNLocator(integer=True))

        fish_per_ghour = [0] * 12
        for hour in cast_ghour_list:
            fish_per_ghour[hour] += 1
        ax[1].bar(range(12), fish_per_ghour)
        ax[1].set_title('Fish Caughted per Game Hour')
        ax[1].set_xticks(range(12))
        ax[1].set_xlabel('Hour (game time)')
        ax[1].yaxis.set_major_locator(MaxNLocator(integer=True))

        # plt.tight_layout()
        plt.savefig(f'../logs/{self.timer.get_cur_timestamp()}.png')
        print('The Plot has been saved under logs/')

# head up backup
# win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(0), int(-200), 0, 0)