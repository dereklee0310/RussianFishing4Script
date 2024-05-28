"""
Module for Player class.
"""

import os
import sys
import logging
import smtplib
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from email.mime.image import MIMEImage
from pathlib import Path

import pyautogui as pag
from playsound import playsound
from prettytable import PrettyTable
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from dotenv import load_dotenv

import script
import exceptions
from timer import Timer
from tackle import Tackle
from setting import Setting
from monitor import Monitor

logger = logging.getLogger(__name__)

CHECK_MISS_LIMIT = 16
PRE_RETRIEVAL_DURATION = 1
PULL_OUT_DELAY = 3
DIG_DELAY = 5
DIG_TIMEOUT = 32
LOOP_DELAY = 2
ANIMATION_DELAY = 0.5
LURE_ADJUST_DELAY = 4

class Player:
    """Main interface of fishing loops and stages."""
    # pylint: disable=too-many-instance-attributes, disable=no-member
    # there are too many counters...
    # setting node's attributes will be merged on the fly

    def __init__(self, setting: Setting):
        """Initialize monitor, timer, timer and some trivial counters.

        :param setting: universal setting node, initialized in App()
        :type setting: Setting
        """
        self.setting = setting
        self.monitor = Monitor(setting)
        if setting.rainbow_line_enabled:
            self.monitor.is_retrieval_finished = self.monitor._is_rainbow_line_0or5m
        else:
            self.monitor.is_retrieval_finished = self.monitor._is_spool_full
        self.timer = Timer()
        self.tackle = Tackle(self.setting, self.monitor, self.timer)

        self.telescopic = self.setting.fishing_strategy # for acceleration
        if self.telescopic == 'float':
            self.puller = self.tackle.telescopic_pull
        else:
            self.puller = self.tackle.general_pull

        # fish count and bite rate
        self.cast_miss_count = 0
        self.keep_fish_count = 0
        self.marked_fish_count = 0
        self.unmarked_fish_count = 0

        # item use count
        self.tea_count = 0
        self.carrot_count = 0
        self.alcohol_count = 0
        self.cur_coffee_count = 0
        self.total_coffee_count = 0
        self.harvest_count = 0

    def start_fishing(self) -> None:
        """Start main fishing loop with specified fishing strategt."""
        match self.setting.fishing_strategy:
            case "spin" | "spin_with_pause":
                self.general_spin_fishing()
            case "bottom":
                self.bottom_fishing()
            case "marine":
                self.marine_fishing()
            case "float":
                self.float_fishing()
            case "wakey_rig":
                self.wakey_rig_fishing()

    # ---------------------------------------------------------------------------- #
    #                              main fishing loops                              #
    # ---------------------------------------------------------------------------- #
    def general_spin_fishing(self) -> None:
        """Main spin fishing loop for "spin" and "spin_with_pause"."""
        retrieval_with_pause = self.setting.fishing_strategy == "spin_with_pause"
        while True:
            self._refill_user_stats()
            self._resetting_stage()
            self.tackle.cast()
            if retrieval_with_pause:
                self.tackle.retrieve_with_pause()
            self.retrieving_stage()
            if not self.monitor.is_fish_hooked():
                self.cast_miss_count += 1
                continue
            self._drink_alcohol()
            self.pulling_stage()

    def bottom_fishing(self) -> None:
        """Main bottom fishing loop."""
        rod_idx = -1
        rod_count = len(self.setting.bottom_rods)
        check_miss_counts = [0] * rod_count

        while True:
            self._refill_user_stats()
            self._harvesting_stage()
            rod_idx = (rod_idx + 1) % rod_count
            rod_key = self.setting.bottom_rods[rod_idx]
            logger.info("Checking rod %s", rod_idx + 1)
            pag.press(f"{rod_key}")
            sleep(1)  # wait for pick up animation

            if not self.monitor.is_fish_hooked():
                self.put_tackle_back(check_miss_counts, rod_idx)
                continue

            check_miss_counts[rod_idx] = 0
            self.retrieving_stage()
            if self.monitor.is_fish_hooked():
                self._drink_alcohol()
                self.pulling_stage()
            self._resetting_stage()
            self.tackle.cast()
            pag.click()

    def marine_fishing(self) -> None:
        """Main marine fishing loop."""
        while True:
            self._refill_user_stats()
            self._resetting_stage()
            self.tackle.cast()
            self.sinking_stage()
            self.pirking_stage()
            # todo: for small fishes at 34m and 41m, accelerated retrieval is adopted
            self.retrieving_stage(accelerated=True)
            if self.monitor.is_fish_hooked():
                self._drink_alcohol()
                self.pulling_stage()

    def float_fishing(self) -> None:
        """Main float fishing loop."""
        float_region = self.monitor.get_float_camera_region()
        while True:
            self._refill_user_stats()
            self._resetting_stage()
            self.tackle.cast()
            try:
                self.monitor_float_state(float_region)
            except TimeoutError:
                self.cast_miss_count += 1
                continue
            sleep(self.setting.pull_delay)
            script.hold_left_click(PRE_RETRIEVAL_DURATION)
            if self.setting.is_fish_hooked():
                self._drink_alcohol()
                self.pulling_stage()

    # def wakey_rig_fishing(self) -> None:
    #     """Main wakey rig fishing loop."""
    #     while True:
    #         self._refilling_stage()
    #         self._resetting_stage()
    #         self.tackle.cast()
    #         self.wakey_sinking_stage()
    #         # self.pirking_stage()
    #         self.retrieving_stage()
    #         if self.monitor.is_fish_hooked():
    #             self._drinking_stage()
    #             self.pulling_stage()

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
    def _harvesting_stage(self) -> None:
        """Harvest the bait."""
        if not self.setting.baits_harvesting_enabled:
            return

        if not self.monitor.is_energy_high():
            return

        logger.info("Harvesting baits")
        self._access_item("shovel_spoon")
        sleep(PULL_OUT_DELAY)
        pag.click()

        i = DIG_TIMEOUT
        while i > 0:
            i = script.sleep_and_decrease(i, DIG_DELAY)
            if self.monitor.is_harvest_success():
                 # accept result and hide the tool
                pag.press("space")
                # sleep(ANIMATION_DELAY) #TODO: is this necessary?
                pag.press("backspace")
                sleep(ANIMATION_DELAY)
                self.harvest_count += 1
                return

        # when timeouted, do nott raise a TimeoutError but defer it to resetting stage

    def _refill_user_stats(self) -> None:
        """Refill player stats using tea and carrot."""
        if not self.setting.player_stat_refill_enabled:
            return

        logger.info("Refilling player stats")
        # comfort is affected by weather, add a check to avoid over drink
        if self.monitor.is_comfort_low() and self.timer.is_tea_drinkable():
            self._access_item("tea")
            self.tea_count += 1
            sleep(ANIMATION_DELAY)

        # refill food level
        if self.monitor.is_hunger_low():
            self._access_item("carrot")
            self.carrot_count += 1
            sleep(ANIMATION_DELAY)

    def _drink_alcohol(self) -> None:
        """Drink alcohol with given quantity."""
        if not self.alcohol_drinking_enabled:
            return

        if not self.timer.is_alcohol_drinkable(self.setting.alcohol_drinking_delay):
            return

        for _ in range(self.alcohol_drinking_quantity):
            self._access_item("alcohol")
            self.alcohol_count += 1
            sleep(ANIMATION_DELAY)

    def _drink_coffee(self) -> None:
        """Drink coffee."""
        if not self.coffee_drinking_enabled:
            return

        if not self.monitor.is_energy_high():
            return

        if self.cur_coffee_count > self.setting.coffee_limit:
            pag.press("esc")  # back to control panel to reduce power usage
            self.handle_termination("Coffee limit reached")

        logger.info("Consume coffee")
        self._access_item("coffee")
        self.cur_coffee_count += 1
        self.total_coffee_count += 1


    def _access_item(self, item: str) -> None:
        """Access item by name using quick selection shortcut or menu.

        :param item: the name of the item
        :type item: str
        """
        key = getattr(self.setting, f"{item}_shortcut")
        if key != "-1":
            pag.press(key)
            return

        # key = 1, item is a food
        with pag.hold("t"):
            sleep(ANIMATION_DELAY)
            food_position = getattr(self.monitor, "get_food_position")(item)
            pag.moveTo(food_position)
            pag.click()

    def _resetting_stage(self) -> None:
        """Reset the tackle till it's ready."""
        sleep(ANIMATION_DELAY)
        if self.monitor.is_tackle_ready():
            return

        if self.monitor.is_lure_broken():
            self.handle_broken_lure()
            return

        while True:
            try:
                self.tackle.reset()
                return
            except exceptions.FishHookedError:
                try:
                    self.puller()
                    self.handle_fish()
                except TimeoutError:
                    pass
                return # whether success or not, back to main fishing loop
            except exceptions.FishCapturedError:
                self.handle_fish()
                return
            except TimeoutError:  # rare events
                self.handle_timeout()

    def handle_timeout(self) -> None:
        """Handle common timeout events."""
        if self.monitor.is_tackle_broken():
            self.save_screenshot()
            self.general_quit("Tackle is broken")

        if self.monitor.is_disconnected():
            self.disconnected_quit()

        if self.monitor.is_ticket_expired():
            self.handle_expired_ticket()

    def handle_broken_lure(self):
        """Handle the broken lure event according to the settings."""
        msg = "Lure is broken"
        logger.warning(msg)
        match self.setting.lure_broken_action:
            case "alarm":
                self.handle_termination(msg)
            case "replace":
                self.replace_broken_lures()
                return
            case "quit":
                self.general_quit(msg) #todo: merge with handle_termination

    def handle_termination(self, msg: str) -> None:
        """Send email and plot diagram, quit the game if necessary

        :param msg: quit message
        :type msg: str
        """
        #todo: quit game?
        result = self.gen_result(msg)
        print(result)
        if self.setting.email_sending_enabled:
            self.send_email(result)
        if self.setting.plotting_enabled:
            self.plot_and_save()
        sys.exit()


    def retrieving_stage(self, accelerated=False) -> None:
        """Retrieve the fishing line till it's fully retrieved.

        :param accelerated: option for accelerated retrieval, defaults to False
        :type accelerated: bool, optional
        """
        if self.monitor.is_retrieval_finished():
            return

        if accelerated:
            pag.keyDown("shift")
        gear_ratio_switched = False

        self.cur_coffee_count = 0
        while True:
            try:
                self.tackle.retrieve()
                break
            except exceptions.FishCapturedError:
                self.handle_fish()
                break
            except exceptions.LineAtEndError:
                self.general_quit("Fishing line is at its end")
            except TimeoutError:
                self.handle_timeout()
                if self.setting.gr_switching_enabled and not gear_ratio_switched:
                    self.tackle.switch_gear_ratio()
                    gear_ratio_switched = True
                #todo: improve this? toggle accelerated retrieval after first retrieval
                if accelerated:
                    pag.keyUp("shift")
                self._drink_coffee()

        if accelerated:
            pag.keyUp("shift")
        if gear_ratio_switched:
            self.tackle.switch_gear_ratio()

    def sinking_stage(self, marine: bool=True) -> None:
        """Sink the lure until an event happend, designed for marine and wakey rig.

        :param marine: whether to check is lure moving in bottom layer, defaults to True
        :type marine: bool, optional
        """
        logger.info("Sinking Lure")
        i = self.setting.sink_timeout
        while i > 0:
            i = script.sleep_and_decrease(i, LOOP_DELAY)
            if marine and self.monitor.is_moving_in_bottom_layer():
                logger.info("Lure reached bottom layer")
                break

            if not self.monitor.is_fish_hooked():
                continue

            # check if the fish got away after biting
            sleep(self.setting.fish_hooked_check_delay)
            if self.monitor.is_fish_hooked():
                logger.info("Fish is hooked")
                pag.click()
                return

        script.hold_left_click(self.setting.tighten_duration)

    def pirking_stage(self) -> None:
        """Perform pirking till a fish hooked, adjust the lure if timeout is reached."""
        while True:
            try:
                self.tackle.pirk()
                break
            except TimeoutError:
                self.handle_timeout()
                # adjust lure depth if no fish is hooked
                logger.info("Adjusting lure depth")
                pag.press("enter")  # open reel
                sleep(LURE_ADJUST_DELAY)
                script.hold_left_click(self.setting.tighten_duration)
                # todo: improve dedicated miss count for marine fishing
                self.cast_miss_count += 1

    def monitor_float_state(self, float_region: tuple[int, int, int, int]) -> None:
        """Monitor the state of the float.

        :param float_region: a PyScreeze.Box-like coordinate tuple
        :type float_region: tuple[int, int, int, int]
        """
        reference_img = pag.screenshot(region=float_region)
        i = self.setting.drifting_timeout
        while i > 0:
            i = script.sleep_and_decrease(i, self.setting.check_delay)
            logger.info("Checking float status")
            current_img = pag.screenshot(region=float_region)
            if not pag.locate(
                current_img,
                reference_img,
                grayscale=True,
                confidence=self.setting.float_confidence,
            ):
                logger.info("Float status changed")
                return

        raise TimeoutError

    def pulling_stage(self) -> None:
        """Pull the fish up, then handle it."""
        while True:
            try:
                self.puller()
                self.handle_fish()
                return
            except exceptions.FishGotAwayError:
                return
            except TimeoutError:
                self.handle_timeout()
                if self.telescopic:
                    continue
                self.tackle.retrieve()

    def handle_fish(self) -> None:
        """Keep or release the fish and record the fish count."""

        #! a trophy ruffe will break the checking mechanism
        if self.monitor.is_fish_green_marked():
            self.marked_fish_count += 1
        else:
            self.unmarked_fish_count += 1
            if self.unmarked_release_enabled:
                if not self._is_fish_in_whitelist():
                    logger.info("Release unmarked fish")
                    pag.press("backspace")
                    return

        # fish is marked or enable_unmarked_release is set to False
        sleep(self.keep_fish_delay)
        logger.info("Keep the fish")
        pag.press("space")

        # avoid wrong cast hour
        if self.fishing_strategy in ["bottom", "marine"]:
            self.timer.update_cast_hour()
        self.timer.add_cast_hour()

        self.keep_fish_count += 1
        if self.keep_fish_count == self.fishes_to_catch:
            msg = "Keepnet is full"
            if self.keepnet_full_action == "alarm":
                logger.warning(msg)
                playsound(str(Path(self.alarm_sound_file_path).resolve()))
            elif self.keepnet_full_action == "quit":
                self.general_quit(msg)

    def _is_fish_in_whitelist(self):
        if self.unmarked_release_whitelist[0] == "None":
            return False

        for fish_name in self.unmarked_release_whitelist:
            if getattr(monitor, f"is_fish_{fish_name}")():
                return True
        return False

    # ---------------------------------------------------------------------------- #
    #                                     misc                                     #
    # ---------------------------------------------------------------------------- #

    def general_quit(self, termination_cause: str) -> None:
        """Show the running result with cause of termination,
            then quit the game through control panel.

        :param termination_cause: the cause of the termination
        :type termination_cause: str
        """
        sleep(2)  # pre-delay
        pag.press("esc")
        pag.click()  # prevent possible stuck
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
            os.system("shutdown /s /t 5")
        print(result)
        sys.exit()

    def disconnected_quit(self) -> None:
        """show the running result with disconnected status,
        then quit the game through main menu.
        """
        pag.press("space")
        sleep(2)

        # sleep to bypass the black screen (experimental)
        sleep(10)

        pag.press("space")
        sleep(2)

        pag.moveTo(monitor.get_exit_icon_position())
        pag.click()
        sleep(2)
        pag.moveTo(monitor.get_confirm_exit_icon_position())
        pag.click()

        result = self.gen_result("Disconnection")
        if self.email_sending_enabled:
            self.send_email(result)

        if self.shutdown_enabled:
            os.system("shutdown /s /t 5")
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

        table = PrettyTable(header=False, align="l")
        table.title = "Running Results"
        # table.field_names = ['Record', 'Value']

        table.add_rows(
            [
                ["Cause of termination", termination_cause],
                ["Start time", self.timer.get_start_datetime()],
                ["Finish time", self.timer.get_cur_datetime()],
                ["Running time", self.timer.get_duration()],
                ["Fish caught", self.keep_fish_count],
            ]
        )

        if total_fish_count > 0:
            marked_rate = int((self.marked_fish_count) / total_fish_count * 100)
            table.add_row(
                [
                    "Marked ratio",
                    f"{self.marked_fish_count}/{total_fish_count} {marked_rate}%",
                ]
            )
        if total_cast_count > 0:
            bite_rate = int(total_fish_count / total_cast_count * 100)
            table.add_row(
                ["Bite rate", f"{total_fish_count}/{total_cast_count} {bite_rate}%"]
            )
        if self.coffee_drinking_enabled:
            table.add_row(["Coffee consumed", self.total_coffee_count])
        if self.alcohol_drinking_enabled:
            table.add_row(["Alcohol consumed", self.alcohol_count])
        if self.hunger_and_comfort_refill_enabled:
            table.add_rows(
                [
                    ["Tea consumed", self.tea_count],
                    ["Carrot consumed", self.carrot_count],
                ]
            )

        if self.baits_harvesting_enabled:
            table.add_row(["Harvest baits count", self.harvest_count])
        return table

    def send_email(self, table: PrettyTable) -> None:
        """Send an notification email to the user's email address that specified in ".env".

        :param table: table consisting cause of termination and run-time records
        :type table: PrettyTable
        """
        # get environment variables
        load_dotenv()
        sender = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")
        smtp_server_name = os.getenv("SMTP_SERVER")

        # configure mail info
        msg = MIMEMultipart()
        msg["Subject"] = "RussianFishing4Script: Notice of Program Termination"
        msg["From"] = sender
        recipients = [sender]
        msg["To"] = ", ".join(recipients)

        # content
        html = MIMEText(table.get_html_string(), "html")
        msg.attach(html)

        # send email with SMTP
        with smtplib.SMTP_SSL(smtp_server_name, 465) as smtp_server:
            # smtp_server.ehlo()
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())
        print(
            "An email containing the running results has been sent to your email address"
        )

    def save_screenshot(self) -> None:
        """Save screenshot to screenshot/, only be invoked when the tackle is broke."""
        # datetime.now().strftime("%H:%M:%S")
        pag.press("q")
        with open(
            rf"../screenshots/{self.timer.get_cur_timestamp()}.png", "wb"
        ) as file:
            pag.screenshot().save(file, "png")
        pag.press("esc")

    def plot_and_save(self) -> None:
        """Plot and save an image using rhour and ghour list from timer object."""
        if self.marked_fish_count + self.unmarked_fish_count == 0:
            return

        cast_rhour_list, cast_ghour_list = self.timer.get_cast_hour_list()
        fig, ax = plt.subplots(nrows=1, ncols=2)
        # fig.canvas.manager.set_window_title('Record')
        ax[0].set_ylabel("Fish")

        last_rhour = cast_rhour_list[-1]  # hour: 0, 1, 2, 3, 4, "5"
        fish_per_rhour = [0] * (last_rhour + 1)  # idx: #(0, 1, 2, 3, 4, 5) = 6
        for hour in cast_rhour_list:
            fish_per_rhour[hour] += 1
        ax[0].plot(range(last_rhour + 1), fish_per_rhour)
        ax[0].set_title("Fish Caughted per Real Hour")
        ax[0].set_xticks(range(last_rhour + 2))
        ax[0].set_xlabel("Hour (real running time)")
        ax[0].yaxis.set_major_locator(MaxNLocator(integer=True))

        fish_per_ghour = [0] * 24
        for hour in cast_ghour_list:
            fish_per_ghour[hour] += 1
        ax[1].bar(range(0, 24), fish_per_ghour)
        ax[1].set_title("Fish Caughted per Game Hour")
        ax[1].set_xticks(range(0, 24, 2))
        ax[1].set_xlabel("Hour (game time)")
        ax[1].yaxis.set_major_locator(MaxNLocator(integer=True))

        # plt.tight_layout()
        plt.savefig(f"../logs/{self.timer.get_cur_timestamp()}.png")
        print("The Plot has been saved under logs/")

    def handle_expired_ticket(self):
        """Select and use the ticket according to boat_ticket_duration argument."""
        if self.setting.boat_ticket_duration is None:
            #todo: refactor this
            pag.press("esc")
            sleep(ANIMATION_DELAY)
            self.general_quit("Boat ticket expired")

        logger.info("Renewing boat ticket")
        ticket_loc = monitor.get_boat_ticket_position(self.boat_ticket_duration)
        if ticket_loc is None:
            pag.press("esc")  # quit ticket menu
            sleep(2)
            self.general_quit("Boat ticket not found")
        pag.moveTo(ticket_loc)
        pag.click(
            clicks=2, interval=0.1
        )  # interval is required, doubleClick() not implemented
        sleep(4)  # wait for animation
        sleep(ANIMATION_DELAY)

    def replace_broken_lures(self):
        """Replace multiple broken items (lures)."""
        logger.info("Replacing broken lures")
        # open tackle menu
        pag.press("v")
        sleep(0.25)

        scrollbar_position = monitor.get_scrollbar_position()
        if scrollbar_position is None:
            logger.info("Scroll bar not found, changing lures for normal rig")
            while self.open_broken_lure_menu():
                self.replace_selected_item()
            pag.press("v")
            return

        logger.info("Scroll bar found, changing lures for dropshot rig")
        pag.moveTo(scrollbar_position)
        for _ in range(5):
            sleep(1)
            pag.drag(xOffset=0, yOffset=125, duration=0.5, button="left")

            replaced = False
            while self.open_broken_lure_menu():
                self.replace_selected_item()
                replaced = True

            if replaced:
                pag.moveTo(monitor.get_scrollbar_position())
        pag.press("v")
        sleep(ANIMATION_DELAY)

    def open_broken_lure_menu(self) -> bool:
        """Search for text of broken item, open selection menu if found.

        :return: True if broken item is found, False otherwise
        :rtype: bool
        """
        logger.info("Searching for broken lure")
        broken_item_position = monitor.get_100wear_position()
        if broken_item_position is None:
            logger.warning("Broken lure not found")
            return False

        # click item to open selection menu
        logger.info("Broken lure found")
        pag.moveTo(broken_item_position)
        sleep(0.25)
        pag.click()
        sleep(0.25)
        return True

    def replace_selected_item(self) -> None:
        """Search for favorite items for replacement and skip the broken ones."""
        # iterate through favorite items for replacement
        favorite_item_positions = monitor.get_favorite_item_positions()

        logger.info("Search for favorite items")
        while True:
            favorite_item_position = next(favorite_item_positions, None)
            if favorite_item_position is None:
                msg = "Lure for replacement not found"
                logger.warning(msg)
                pag.press("esc")
                sleep(0.25)
                pag.press("esc")
                sleep(0.25)
                self.general_quit(msg)

            # box -> x, y, np.int64 -> int
            get_box_center = lambda box: (
                int(box.left + box.width // 2),
                int(box.top + box.height // 2),
            )
            x, y = get_box_center(favorite_item_position)
            # check if the lure for replacement is already broken
            if pag.pixel(x - 75, y + 190) != (178, 59, 30):  # magic value
                logger.info("The broken lure has been replaced")
                # pag.moveTo(x - 75, y + 200) # ?
                pag.moveTo(x - 75, y + 190)
                pag.click(clicks=2, interval=0.1)
                sleep(2)  # wait for wear text to update
                break
            logger.warning("Lure for replacement found but already broken")

    def put_tackle_back(self, check_miss_counts: list[int], rod_idx: int) -> None:
        """Update counters, put down the tackle and wait for a while.

        :param check_miss_counts: miss counts of all rods
        :type check_miss_counts: list[int]
        :param rod_idx: current index of the rod
        :type rod_idx: int
        """
        self.cast_miss_count += 1
        check_miss_counts[rod_idx] += 1
        if check_miss_counts[rod_idx] > CHECK_MISS_LIMIT:
            check_miss_counts[rod_idx] = 0
            self._resetting_stage()
            self.tackle.cast()
            pag.click()

        pag.press("0")
        sleep(self.setting.check_delay)


# head up backup
# win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(0), int(-200), 0, 0)
