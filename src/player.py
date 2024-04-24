"""
Module for Player class

Todo: docstrings
"""
import os
import smtplib
import sys
from time import sleep, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

import logging
import pyautogui as pag
from playsound import playsound
from argparse import Namespace
from configparser import ConfigParser
from prettytable import PrettyTable
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from dotenv import load_dotenv
from pyscreeze import Box

import monitor
from tackle import Tackle
from timer import Timer
from script import sleep_and_decrease, hold_left_click

logger = logging.getLogger(__name__)

class Player():
    keep_fish_count = 0
    marked_fish_count = 0
    unmarked_fish_count = 0
    cast_miss_count = 0

    total_coffee_count = 0 
    cur_coffee_count = 0
    alcohol_count = 0
    tea_count = 0
    pre_tea_drink_time = 0
    pre_alcohol_drink_time = 0
    carrot_count = 0
    harvest_count = 0

    def __init__(self, args: Namespace, config: ConfigParser, profile_name: str) -> None:
        """Configure game settings, Variables are already validated in app.py.

        :param args: parsed command line arguments
        :type args: Namespace
        :param config: parsed config file
        :type config: ConfigParser
        :param profile_name: title of profile with respect to pid
        :type profile_name: str
        """
        self.timer = Timer()
        self.tackle = Tackle(self.timer)
        self.shortcut_dict = dict(config['shortcut'])
        self._build_args(args)
        self._build_game_config(config)
        self._build_profile_config(config, profile_name)

        #todo: revise this shit
        if self.rainbow_line_enabled:
            monitor.set_rainbow_line_retrieval()

    def _build_args(self, args: Namespace) -> None:
        """Generate attributes from command line arguments

        :param args: dict-like parsed arguments
        :type args: Namespace
        """
        self.unmarked_release_enabled = args.marked
        self.coffee_drinking_enabled = args.coffee
        self.alcohol_drinking_enabled = args.alcohol
        self.hunger_and_comfort_refill_enabled = args.refill
        self.baits_harvesting_enabled = args.harvest
        self.email_sending_enabled = args.email
        self.plotting_enabled = args.plot
        self.shutdown_enabled = args.shutdown
        self.rainbow_line_enabled = args.rainbow_line
        self.lift_enabled = args.lift
        self.gear_ratio_switching_enabled = args.gear_ratio_switching
        self.fishes_in_keepnet = args.fishes_in_keepnet
        self.boat_ticket_duration = args.boat_ticket_duration

    def _build_game_config(self, config: ConfigParser) -> None:
        """Generate attributes from "game" section in config.ini

        :param config: parser for config.ini
        :type config: ConfigParser
        """
        game_section = config['game']
        self.keepnet_limit = game_section.getint('keepnet_limit')
        self.fishes_to_catch = self.keepnet_limit - self.fishes_in_keepnet
        self.harvest_baits_threshold = game_section.getfloat('harvest_baits_threshold')
        self.coffee_limit = game_section.getint('coffee_limit')
        self.keep_fish_delay = game_section.getint('keep_fish_delay')
        self.alcohol_drinking_delay = game_section.getint('alcohol_drinking_delay')
        self.alcohol_quantity = game_section.getint('alcohol_quantity')
        self.lure_broken_action = game_section.get('lure_broken_action')
        self.keepnet_full_action = game_section.get('keepnet_full_action')
        self.alarm_sound_file_path = game_section.get('alarm_sound_file_path')
        self.unmarked_release_whitelist = [key.strip() for key in game_section.get('unmarked_release_whitelist').split(',')]

    def _build_profile_config(self, config: ConfigParser, profile_name: str) -> None:
        """Generate attributes from chosen user profile section

        :param config: parser for config.ini
        :type config: ConfigParser
        :param profile_name: section name of user profile
        :type profile_name: str
        """
        profile_section = config[profile_name]
        self.fishing_strategy = profile_section.get('fishing_strategy')
        self.cast_power_level = profile_section.getfloat('cast_power_level')
        match self.fishing_strategy:
            case 'spin':
                pass
            case 'spin_with_pause':
                self.retrieval_duration = profile_section.getfloat('retrieval_duration')
                self.retrieval_delay = profile_section.getfloat('retrieval_delay')
                self.base_iteration = profile_section.getint('base_iteration')
                self.acceleration_enabled = profile_section.getboolean('acceleration_enabled')
            case 'bottom':
                self.check_delay = profile_section.getfloat('check_delay')
            case 'marine':
                self.sink_timeout = profile_section.getfloat('sink_timeout')
                self.pirk_duration = profile_section.getfloat('pirk_duration')
                self.pirk_delay = profile_section.getfloat('pirk_delay')
                self.pirk_timeout = profile_section.getfloat('pirk_timeout')
                self.tighten_duration = profile_section.getfloat('tighten_duration')
                self.fish_hooked_check_delay = profile_section.getfloat('fish_hooked_check_delay')
            case 'wakey_rig':
                pass
            case _:
                logger.error('Invalid fishing strategy')
                sys.exit()

    def start_fishing(self) -> None:
        """Start main fishing loop with specified fishing strategt.
        """
        try:
            match self.fishing_strategy:
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
                # already checked in self._build_profile_config()
        except KeyboardInterrupt:
            # avoid shift key stuck
            if self.fishing_strategy == 'spin_with_pause' and self.acceleration_enabled:
                pag.keyUp('shift')
            print(self.gen_result('Terminated by user'))
            if self.plotting_enabled:
                self.plot_and_save()
            sys.exit()

    # ---------------------------------------------------------------------------- #
    #                              main fishing loops                              #
    # ---------------------------------------------------------------------------- #
    def spin_fishing(self) -> None:
        """Main spin fishing loop.
        """
        while True:
            self.refilling_stage()
            self.resetting_stage()
            self.tackle.cast(self.cast_power_level)
            self.retrieving_stage()
            if not monitor.is_fish_hooked():
                self.cast_miss_count += 1
                continue
            self.drinking_stage()
            self.pulling_stage()

    # todo: combine this with spin_fishing()
    def spin_fishing_with_pause(self) -> None:
        """Spin fishing with a "retrieve_with_pause" stage before normal retrieving stage.
        """
        while True:
            self.refilling_stage()
            self.resetting_stage()
            self.tackle.cast(self.cast_power_level)
            self.tackle.retrieve_with_pause(self.retrieval_duration,
                                            self.retrieval_delay,
                                            self.base_iteration,
                                            self.acceleration_enabled)
            self.retrieving_stage(duration=4, delay=2)
            if not monitor.is_fish_hooked():
                self.cast_miss_count += 1
                continue
            self.drinking_stage()
            self.pulling_stage()

    def bottom_fishing(self) -> None:
        """Main bottom fishing loop.
        """
        # todo: add retrieval duration and delay
        check_counts = [-1, 0, 0, 0]
        rod_idx = -1
        bottom_rods = [key.strip() for key in self.shortcut_dict['bottom_rods'].split(',')]
        rod_count = len(bottom_rods)

        while True:
            self.refilling_stage()
            self.harvesting_stage()
            rod_idx = 0 if rod_idx == rod_count - 1 else rod_idx + 1
            rod_key = bottom_rods[rod_idx]
            logger.info(f'Checking rod {rod_idx + 1}')
            pag.press(f'{rod_key}')
            sleep(1) # wait for pick up animation

            # check the next rod if no fish is hooked
            if not monitor.is_fish_hooked():
                check_counts[rod_idx] += 1
                self.cast_miss_count += 1
                # recast if check failed more than 16 times
                if check_counts[rod_idx] > 16:
                    check_counts[rod_idx] = 0
                    self.resetting_stage()
                    self.tackle.cast(self.cast_power_level, cast_delay=4)
                    pag.click()
                
                pag.press('0')
                sleep(self.check_delay)
                continue

            check_counts[rod_idx] = 0
            self.retrieving_stage(duration=4, delay=2)
            if monitor.is_fish_hooked():
                self.drinking_stage()
                self.pulling_stage()
            self.resetting_stage()
            self.tackle.cast(self.cast_power_level, cast_delay=4)
            pag.click()

    def marine_fishing(self) -> None:
        """Main marine fishing loop.
        """
        while True:    
            self.refilling_stage()
            self.resetting_stage()
            if monitor.is_fish_captured():
                self.handle_fish()
            self.tackle.cast(self.cast_power_level)
            self.marine_sinking_stage()
            self.pirking_stage()
            # for small fishes at 34m and 41m, use accelerated retrieval
            # self.retrieving_stage(duration=8, accelerated=True)
            # todo, temp fix for Atalantic saury
            self.retrieving_stage(duration=2.2, delay=0, accelerated=True) # at least 2.2
            if monitor.is_fish_hooked():
                self.drinking_stage()
                self.pulling_stage()

    def wakey_rig_fishing(self) -> None:
        """Main wakey rig fishing loop.
        """
        while True:    
            self.refilling_stage()
            self.resetting_stage()
            self.tackle.cast(self.cast_power_level)
            self.wakey_sinking_stage()
            # self.pirking_stage()
            self.retrieving_stage(duration=4, delay=2)
            if monitor.is_fish_hooked():
                self.drinking_stage()
                self.pulling_stage()

    # this is not done yet :(
    # def trolling_fishing(self) -> None:
    #     # temp
    #     rod_idx = -1
    #     rod_count = len(self.bottom_rods_shortcuts) #! todo
    #     base_waiting_time = 16

    #     while True:
    #         self.refilling_stage()
    #         self.harvesting_stage()
    #         # if there is a rod on hand
    #         if rod_count == 3:
    #             sleep(base_waiting_time)
    #             logger.info(f'Checking rod {3}')
    #             self.retrieving_stage()
    #             if monitor.is_fish_hooked():
    #                 self.pulling_stage()
    #             else:
    #                 self.resetting_stage()

    #         for rod_key in self.bottom_rods_shortcuts[:-1]:
    #             pag.press(rod_key)
    #             if monitor.is_fish_hooked():
    #                 self.retrieving_stage()
    #                 if monitor.is_fish_hooked():
    #                     self.pulling_stage()
    #                     self.tackle.cast(self.cast_power_level)
    #                 else:
    #                     self.cast_miss_count += 1

    #         # if both missed, recast the third rod
    #         self.tackle.cast(self.cast_power_level)


    # ---------------------------------------------------------------------------- #
    #            stages and their helper functions in main fishing loops           #
    # ---------------------------------------------------------------------------- #
    def harvesting_stage(self) -> None:
        """If enable_baits_harvesting is True and the energy level 
            is greater than the threshold, harvest baits. 
        """
        if not self.baits_harvesting_enabled:
            return
        elif monitor.is_energy_high(self.harvest_baits_threshold):
            self.harvest_baits()
            self.harvest_count += 1

    def harvest_baits(self) -> None:
        """Use shortcut defined in config.ini to use shovel/spoon, 
            then hide the tool after the harvest success or the timeout is reached.
        """
        logger.info('Harvesting baits')
        # pull out the shovel/spoon and harvest baits
        self.access_item('shovel_spoon')
        sleep(3)
        pag.click()

        # wait for result
        sleep(5) # 4 is enough, + 1 for inspection
        i = 64
        while i > 0 and not monitor.is_harvest_success():
            i = sleep_and_decrease(i, 4)

        # accept result and hide the tool
        pag.press('space')
        sleep(0.25)
        pag.press('backspace')
        sleep(0.5) # wait for hide animation

    def refilling_stage(self) -> None:
        """If enable_food_comfort_refill is enabled, 
            consume tea or carrot to refill comfort and food level.
        """
        if not self.hunger_and_comfort_refill_enabled:
            return

        # refill comfort
        # comfort is affected by weather, add a time threshold to prevent over drinking
        cur_time = time()
        if monitor.is_comfort_low() and cur_time - self.pre_tea_drink_time > 300:
            self.pre_tea_drink_time = cur_time
            self.access_item('tea')
            self.tea_count += 1
        sleep(0.25)

        # refill food level
        if monitor.is_hunger_low():
            self.access_item('carrot')
            self.carrot_count += 1
        sleep(0.25)
    
    def drinking_stage(self) -> None:
        """Drink alcohol and update drinking time.
        """
        cur_time = time()
        if (not self.alcohol_drinking_enabled or 
            cur_time - self.pre_alcohol_drink_time < self.alcohol_drinking_delay):
            return

        self.pre_alcohol_drink_time = cur_time
        self.pre_tea_drink_time = cur_time
        for _ in range(self.alcohol_quantity):
            self.access_item('alcohol')
            self.alcohol_count += 1
            sleep(0.25)

    def access_item(self, item: str) -> None:
        """Access item by name using quick selection shortcut or menu.

        :param item: the name of the item
        :type item: str
        """
        key = self.shortcut_dict[item]
        if int(key) < -1 or int(key) > 7:
            logger.error(f'Invalid {item} key: {key}')
            sys.exit()
        elif int(key) != -1:
            pag.press(key)
            return
        
        # key = 'u' if item == 'shovel_spoon' else 't'
        with pag.hold('t'):
            sleep(0.25)
            pag.moveTo(getattr(monitor, f'get_{item}_icon_position')())
            pag.click()

    def consume_food_deprecated(self, food: str) -> None:
        """Open food menu, then pag.click on food icon to consume it.

        :param food: food's name
        :type food: str
        """
        print(f'Consume {food}')
        with pag.hold('t'):
            sleep(0.25)
            pag.moveTo(getattr(monitor, f'get_{food}_icon_position')())
            pag.click()

    def resetting_stage(self) -> None:
        """Reset the tackle until the it's ready or an exceptional event occurs.
        """
        sleep(0.25) # wait for rendering

        if monitor.is_tackle_ready():
            return
        
        if monitor.is_lure_broken():
            msg = 'Lure is broken'
            match self.lure_broken_action:
                case 'alarm':
                    logger.warning(msg)
                    playsound(str(Path(self.alarm_sound_file_path).resolve()))

                    # todo: fix this coffee-limit like handling strategy
                    result = self.gen_result(msg)
                    print(result)
                    if self.email_sending_enabled:
                        self.send_email(result)
                    if self.plotting_enabled:
                        self.plot_and_save()
                    sys.exit()
                case 'replace':
                    self.replace_broken_lures()
                    sleep(0.25)
                    return
                case 'quit':
                    self.general_quit(msg)           
        elif monitor.is_ticket_expired():
            if self.boat_ticket_duration is None:
                pag.press('esc')
                sleep(2)
                self.general_quit('Boat ticket expired')
            self.renew_boat_ticket()
            sleep(0.25)
            return
        
        # also deals with scenarios that may occur during resetting
        while not self.tackle.reset():
            if monitor.is_fish_hooked():
                if self.tackle.pull(): # a single pull should do the job
                    self.handle_fish()
                break # whether success or not, back to main fishing loop
            elif monitor.is_fish_captured():
                self.handle_fish()
                break
            elif monitor.is_tackle_broken():
                self.save_screenshot()
                self.general_quit('Tackle is broken')
            elif monitor.is_disconnected():
                self.disconnected_quit()
        sleep(0.25)
            # reset again if no special event occured

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
            pag.keyDown('shift')

        gear_ratio_switched = False

        while not self.tackle.retrieve(duration, delay, lift_enabled=self.lift_enabled):
            # no fish, return to main loop
            # captured, defer to pulling stage
            if monitor.is_line_at_end():
                self.general_quit('Fishing line is at its end')
            elif not monitor.is_fish_hooked() or monitor.is_fish_captured():
                break
            elif monitor.is_ticket_expired():
                if self.boat_ticket_duration is None:
                    pag.press('esc')
                    sleep(2)
                    self.general_quit('Boat ticket expired')
                else:
                    self.renew_boat_ticket()

            if self.gear_ratio_switching_enabled and not gear_ratio_switched:
                self.tackle.switch_gear_ratio()
                gear_ratio_switched = True

            # toggle accelerated retrieval
            if accelerated:
                pag.keyUp('shift')

            # drink coffee if energy is low
            if not monitor.is_energy_high(threshold=0.9) and self.coffee_drinking_enabled:
                self.cur_coffee_count += 1
                if self.cur_coffee_count > self.coffee_limit:
                    pag.press('esc') # back to control panel to reduce power usage
                    result = self.gen_result('Coffee limit reached')
                    print(result)
                    if self.email_sending_enabled:
                        self.send_email(result)
                    if self.plotting_enabled:
                        self.plot_and_save()
                    sys.exit()
                logger.info('Consume coffee')
                self.access_item('coffee')
                self.total_coffee_count += 1

        if accelerated:
            pag.keyUp('shift')

        if gear_ratio_switched:
            self.tackle.switch_gear_ratio()
        self.cur_coffee_count = 0

    def marine_sinking_stage(self) -> None:
        """Sink the lure until it reaches the bottom layer, 
            a fish is hooked, or timeout reached.
        """
        logger.info('Sinking Lure')
        i = self.sink_timeout
        while i > 0:
            if monitor.is_moving_in_bottom_layer():
                logger.info('Lure reached bottom layer')
                break
            elif monitor.is_fish_hooked():
                if self.fish_hooked_check_delay == 0:
                    pag.click()
                    return
                
                # check if the fish got away after biting
                sleep(self.fish_hooked_check_delay)
                if monitor.is_fish_hooked():
                    logger.info('Fish is hooked')
                    pag.click() #todo: tmp fix
                    return
            i = sleep_and_decrease(i, 2)
        hold_left_click(self.tighten_duration)

    def wakey_sinking_stage(self) -> None:
        """Sink the lure until a fish is hooked or timeout reached.
        """
        logger.info('Sinking Lure')
        # todo: dynamic timeout
        i = 60
        while i > 0:
            if monitor.is_fish_hooked():
                logger.info('Fish is hooked')
                break
            i = sleep_and_decrease(i, 2)


    def pirking_stage(self) -> None:
        """Perform pirking until a fish is hooked, adjust the lure if timeout is reached.
        """
        if monitor.is_ticket_expired():
            if self.boat_ticket_duration is None:
                pag.press('esc')
                sleep(2)
                self.general_quit('Boat ticket expired')
            else:
                self.renew_boat_ticket()

        while not self.tackle.pirk(self.pirk_duration,
                                   self.pirk_delay,
                                   self.pirk_timeout,
                                   self.fish_hooked_check_delay):
            
            if monitor.is_ticket_expired():
                pag.press('esc')
                sleep(2)
                if self.boat_ticket_duration is None:
                    self.general_quit('Boat ticket expired')
                else:
                    self.renew_boat_ticket()

            # adjust the depth of the lure if no fish is hooked
            logger.info('Adjusting lure depth')
            pag.press('enter') # open reel
            sleep(4)
            hold_left_click(self.tighten_duration)
            self.cast_miss_count += 1
            # todo: improve dedicated miss count for marine fishing

    def pulling_stage(self) -> None:
        """Pull the fish up, then handle it.
        """
        while True:
            if self.tackle.pull():
                self.handle_fish()
                break
            elif not monitor.is_fish_hooked():
                break
            elif not monitor.is_retrieve_finished():
                self.tackle.retrieve(duration=8, delay=4, lift_enabled=self.lift_enabled) # half retrieval
    
    def handle_fish(self) -> None:
        """Keep or release the fish and record the fish count.
        """

        #! a trophy ruffe will break the checking mechanism            
        if monitor.is_fish_green_marked():
            self.marked_fish_count += 1
        else:
            self.unmarked_fish_count += 1
            if self.unmarked_release_enabled:
                if self.unmarked_release_whitelist[0] != 'None':           
                    for fish_name in self.unmarked_release_whitelist:
                        if getattr(monitor, f'is_fish_{fish_name}')():
                            sleep(self.keep_fish_delay)
                            logger.info('Keep whitelisted fish')
                            pag.press('space')
                            return
                        
                # no whitelisted fish or fish not in whitelist
                logger.info('Release unmarked fish')
                pag.press('backspace')
                return

        # fish is marked or enable_unmarked_release is set to False
        sleep(self.keep_fish_delay)
        logger.info('Keep the fish')
        pag.press('space')

        # avoid wrong cast hour
        if (self.fishing_strategy == 'bottom' or
            self.fishing_strategy == 'marine'):
            self.timer.update_cast_hour()
        
        self.timer.add_cast_hour()

        self.keep_fish_count += 1
        if self.keep_fish_count == self.fishes_to_catch:
            msg = 'Keepnet is full'
            if self.keepnet_full_action == 'alarm':
                logger.warning(msg)
                playsound(str(Path(self.alarm_sound_file_path).resolve()))
            elif self.keepnet_full_action == 'quit':
                self.general_quit(msg)

    # ---------------------------------------------------------------------------- #
    #                                     misc                                     #
    # ---------------------------------------------------------------------------- #

    def general_quit(self, termination_cause: str) -> None:
        """Show the running result with cause of termination, 
            then quit the game through control panel.

        :param termination_cause: the cause of the termination
        :type termination_cause: str
        """
        sleep(2) # pre-delay
        pag.press('esc')
        sleep(4)
        pag.moveTo(monitor.get_quit_position()) 
        pag.click()
        sleep(4)
        pag.moveTo(monitor.get_yes_position())
        pag.click()

        result = self.gen_result(termination_cause)
        if self.email_sending_enabled:
            self.send_email(result)
        if self.plotting_enabled:
            self.plot_and_save()

        if self.shutdown_enabled:
            os.system('shutdown /s /t 5')
        print(result)
        sys.exit()

    def disconnected_quit(self) -> None:
        """show the running result with disconnected status,
            then quit the game through main menu.
        """
        pag.press('space')
        sleep(2)

        # sleep to bypass the black screen (experimental)
        sleep(10)

        pag.press('space')
        sleep(2)
  
        pag.moveTo(monitor.get_exit_icon_position())
        pag.click()
        sleep(2)
        pag.moveTo(monitor.get_confirm_exit_icon_position())
        pag.click()

        result = self.gen_result('Disconnection')
        if self.email_sending_enabled:
            self.send_email(result)

        if self.shutdown_enabled:
            os.system('shutdown /s /t 5')
        print(result)
        sys.exit()

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
        if self.coffee_drinking_enabled:
            table.add_row(['Coffee consumed', self.total_coffee_count])
        if self.alcohol_drinking_enabled:
            table.add_row(['Alcohol consumed', self.alcohol_count])
        if self.hunger_and_comfort_refill_enabled:
            table.add_rows(
                [
                    ['Tea consumed', self.tea_count],
                    ['Carrot consumed', self.carrot_count]
                ])
            
        if self.baits_harvesting_enabled:
            table.add_row(['Harvest baits count', self.harvest_count])
        return table

    def send_email(self, table: PrettyTable) -> None:
        """Send an notification email to the user's email address that specified in ".env".

        :param table: table consisting cause of termination and run-time records
        :type table: PrettyTable
        """
        # get environment variables
        load_dotenv()
        sender = os.getenv('EMAIL')
        password = os.getenv('PASSWORD')
        smtp_server_name = os.getenv('SMTP_SERVER')
        
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
        with smtplib.SMTP_SSL(smtp_server_name, 465) as smtp_server:
            # smtp_server.ehlo()
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())
        print('An email containing the running results has been sent to your email address')

    def save_screenshot(self) -> None:
        """Save screenshot to screenshot/, only be invoked when the tackle is broke.
        """
        # datetime.now().strftime("%H:%M:%S")
        pag.press('q')
        with open(fr'../screenshots/{self.timer.get_cur_timestamp()}.png', 'wb') as file: 
            pag.screenshot().save(file, 'png')
        pag.press('esc')

    def plot_and_save(self) -> None:
        """Plot and save an image using rhour and ghour list from timer object.
        """
        if self.marked_fish_count + self.unmarked_fish_count == 0:
            return

        cast_rhour_list, cast_ghour_list = self.timer.get_cast_hour_list()
        fig, ax = plt.subplots(nrows=1, ncols=2)
        # fig.canvas.manager.set_window_title('Record')
        ax[0].set_ylabel('Fish')
        
        last_rhour = cast_rhour_list[-1] # hour: 0, 1, 2, 3, 4, "5"
        fish_per_rhour = [0] * (last_rhour + 1) # idx: #(0, 1, 2, 3, 4, 5) = 6
        for hour in cast_rhour_list:
            fish_per_rhour[hour] += 1
        ax[0].plot(range(last_rhour + 1), fish_per_rhour)
        ax[0].set_title('Fish Caughted per Real Hour')
        ax[0].set_xticks(range(last_rhour + 2))
        ax[0].set_xlabel('Hour (real running time)')
        ax[0].yaxis.set_major_locator(MaxNLocator(integer=True))

        fish_per_ghour = [0] * 24
        for hour in cast_ghour_list:
            fish_per_ghour[hour] += 1
        ax[1].bar(range(0, 24), fish_per_ghour)
        ax[1].set_title('Fish Caughted per Game Hour')
        ax[1].set_xticks(range(0, 24, 2))
        ax[1].set_xlabel('Hour (game time)')
        ax[1].yaxis.set_major_locator(MaxNLocator(integer=True))

        # plt.tight_layout()
        plt.savefig(f'../logs/{self.timer.get_cur_timestamp()}.png')
        print('The Plot has been saved under logs/')

    def renew_boat_ticket(self):
        """Select and use the ticket according to boat_ticket_duration argument.
        """
        logger.info('Renewing boat ticket')
        ticket_loc = monitor.get_boat_ticket_position(self.boat_ticket_duration)
        if ticket_loc is None:
            pag.press('esc') # quit ticket menu
            sleep(2)
            self.general_quit('Boat ticket not found')
        pag.moveTo(ticket_loc)
        pag.click(clicks=2, interval=0.1) # interval is required, doubleClick() not implemented
        sleep(4) # wait for animation
        
    def replace_broken_lures(self):
        """Replace multiple broken items (lures).
        """
        logger.info('Replacing broken lures')
        # open tackle menu
        pag.press('v')
        sleep(0.25)

        scrollbar_position = monitor.get_scrollbar_position()
        if scrollbar_position is None:
            logger.info('Scroll bar not found, changing lures for normal rig')
            while self.open_broken_lure_menu():
                self.replace_selected_item()
            pag.press('v')
            return
        
        logger.info('Scroll bar found, changing lures for dropshot rig')
        pag.moveTo(scrollbar_position)
        for _ in range(5):
            sleep(1)
            pag.drag(xOffset=0, yOffset=125, duration=0.5, button='left')

            replaced = False
            while self.open_broken_lure_menu():
                self.replace_selected_item()
                replaced = True

            if replaced:
                pag.moveTo(monitor.get_scrollbar_position())
        pag.press('v')

    def open_broken_lure_menu(self) -> bool:
        """Search for text of broken item, open selection menu if found.

        :return: True if broken item is found, False otherwise
        :rtype: bool
        """
        logger.info('Searching for broken lure')
        broken_item_position = monitor.get_100wear_position()
        if broken_item_position is None:
            logger.warning('Broken lure not found')
            return False
        
        # click item to open selection menu
        logger.info('Broken lure found')
        pag.moveTo(broken_item_position)
        sleep(0.25)
        pag.click()
        sleep(0.25)
        return True

    def replace_selected_item(self) -> None:
        """Search for favorite items for replacement and skip the broken ones.
        """
        # iterate through favorite items for replacement
        favorite_item_positions = monitor.get_favorite_item_positions()

        logger.info('Search for favorite items')
        while True:
            favorite_item_position = next(favorite_item_positions, None)
            if favorite_item_position is None:
                msg = 'Lure for replacement not found'
                logger.warning(msg)
                pag.press('esc')
                sleep(0.25)
                pag.press('esc')    
                sleep(0.25)
                self.general_quit(msg)

            # box -> x, y, np.int64 -> int
            get_box_center = lambda box: (int(box.left + box.width // 2), int(box.top + box.height // 2))
            x, y = get_box_center(favorite_item_position)
            # check if the lure for replacement is already broken
            if pag.pixel(x - 75, y + 190) != (178, 59, 30): # magic value
                logger.info('The broken lure has been replaced')
                # pag.moveTo(x - 75, y + 200) # ?
                pag.moveTo(x - 75, y + 190)
                pag.click(clicks=2, interval=0.1)
                sleep(2) # wait for wear text to update
                break
            logger.warning('Lure for replacement found but already broken')

# head up backup
# win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(0), int(-200), 0, 0)