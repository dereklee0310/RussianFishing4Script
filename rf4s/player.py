"""
Module for Player class.
"""

import json
import logging
import os
import random
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Lock

# from email.mime.image import MIMEImage
from pathlib import Path
from time import sleep, time
from urllib import parse, request

import pyautogui as pag
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from playsound import playsound
from prettytable import PrettyTable

from rf4s import exceptions
from rf4s import utils
from rf4s.component.friction_brake import FrictionBrake
from rf4s.component.tackle import Tackle
from rf4s.controller.detection import Detection
from rf4s.controller.timer import Timer

logger = logging.getLogger(__name__)
random.seed(datetime.now().timestamp())

PRE_RETRIEVAL_DURATION = 1
PULL_OUT_DELAY = 3
DIG_DELAY = 5
DIG_TIMEOUT = 32
LOOP_DELAY = 2
ANIMATION_DELAY = 0.5
TICKET_EXPIRE_DELAY = 16
LURE_ADJUST_DELAY = 4
DISCONNECTED_DELAY = 8
WEAR_TEXT_UPDATE_DELAY = 2
BOUND = 2

SCREENSHOT_DELAY = 2

TROLLING_KEY = "j"

FORWARD = "w"
LEFT_KEY = "a"
RIGHT_KEY = "d"


class Player:
    """Main interface of fishing loops and stages."""

    # pylint: disable=too-many-instance-attributes, disable=no-member
    # there are too many counters...
    # setting node's attributes will be merged on the fly

    def __init__(self, cfg, window):
        """Initialize monitor, timer, timer and some trivial counters.

        :param setting: universal setting node, initialized in App()
        :type setting: Setting
        """
        self.cfg = cfg
        self.window = window
        self.detection = Detection(cfg)
        self.timer = Timer()
        self.tackle = Tackle(cfg, self.timer)
        self.special_cast_miss = self.cfg.SELECTED.MODE in ["bottom", "marine"]
        self.friction_brake_lock = Lock()
        self.friction_brake = FrictionBrake(cfg, self.friction_brake_lock)

        # fish count and bite rate
        self.cast_miss_count = 0
        self.keep_fish_count = 0
        self.marked_count = 0
        self.unmarked_count = 0

        # item use count
        self.tea_count = 0
        self.carrot_count = 0
        self.alcohol_count = 0
        self.cur_coffee_count = 0
        self.total_coffee_count = 0
        self.harvest_count = 0

    @utils.release_keys_after
    def start_fishing(self) -> None:
        """Start main fishing loop with specified fishing strategt."""
        if self.cfg.ARGS.FRICTION_BRAKE:
            logger.info("Spawing new process, do not quit the utils")
            self.friction_brake.monitor_process.start()
        getattr(self, f"start_{self.cfg.SELECTED.MODE}_mode")()

    # ---------------------------------------------------------------------------- #
    #                              main fishing loops                              #
    # ---------------------------------------------------------------------------- #
    def start_spin_mode(self) -> None:
        """Main spin fishing loop for "spin" and "spin_with_pause"."""
        lure_changing_delay = self.cfg.SCRIPT.LURE_CHANGE_DELAY
        skip_cast = self.cfg.ARGS.SKIP_CAST
        while True:
            if not skip_cast:
                self._refill_user_stats()
                self._harvesting_stage(pickup=True)
                self._resetting_stage()
                if (
                    self.cfg.ARGS.LURE
                    and time() - self.timer.start_time > lure_changing_delay
                ):
                    self._change_lure_randomly()
                    lure_changing_delay += self.cfg.SCRIPT.LURE_CHANGE_DELAY
                self.tackle.cast()
            skip_cast = False

            if self.cfg.SELECTED.RETRIEVE_DURATION > 0:
                utils.hold_mouse_button(self.cfg.SELECTED.TIGHTEN_DURATION)
                self.tackle.retrieve_with_pause()
            self._retrieving_stage()

            if not self.detection.is_fish_hooked():
                self.cast_miss_count += 1
                continue
            self._drink_alcohol()
            self._pulling_stage()

    def start_bottom_mode(self) -> None:
        """Main bottom fishing loop."""
        rod_count = len(self.cfg.KEY.RODS)
        rod_idx = 0
        check_miss_counts = [0] * rod_count

        spod_rod_recast_delay = self.cfg.SCRIPT.SPOD_ROD_RECAST_DELAY
        while True:
            if (
                self.cfg.ARGS.SPOD_ROD
                and time() - self.timer.start_time > spod_rod_recast_delay
            ):
                logger.info("Recasting spod rod")
                spod_rod_recast_delay += self.cfg.SCRIPT.SPOD_ROD_RECAST_DELAY
                self._access_item("spod_rod")
                sleep(1)
                self._resetting_stage()
                self.tackle.cast(update=False)
                pag.click()
                pag.press("0")
                sleep(ANIMATION_DELAY)

            self._refill_user_stats()
            self._harvesting_stage()
            if rod_count > 1:
                if self.cfg.SCRIPT.RANDOM_ROD_SELECTION:
                    rod_idx = (rod_idx + random.randint(1, rod_count - 1)) % rod_count
                else:  # sequential
                    rod_idx = (rod_idx + 1) % rod_count
            rod_key = self.cfg.KEY.RODS[rod_idx]
            logger.info("Checking rod %s", rod_idx + 1)
            pag.press(f"{rod_key}")
            sleep(1)  # wait for pick up animation

            if not self.detection.is_fish_hooked():
                self._put_tackle_back(check_miss_counts, rod_idx)
                self.cast_miss_count += 1
                continue

            check_miss_counts[rod_idx] = 0
            self._retrieving_stage()
            if self.detection.is_fish_hooked():
                self._drink_alcohol()
                self._pulling_stage()
            self._resetting_stage()
            self.tackle.cast()
            pag.click()

    def start_pirk_mode(self) -> None:
        """Main marine fishing loop."""
        self._trolling_stage()

        while True:
            if not self.cfg.ARGS.SKIP_CAST:
                self._refill_user_stats()
                self._resetting_stage()
                self.tackle.cast()
                self.tackle.sink()
            self.cfg.ARGS.SKIP_CAST = False

            if not self.detection.is_fish_hooked():
                self._pirking_stage()

            self._retrieving_stage()

            if self.detection.is_fish_hooked():
                self._drink_alcohol()
                self._pulling_stage()

    def start_elevator_mode(self) -> None:
        """Main marine fishing loop."""
        self._trolling_stage()

        while True:
            if not self.cfg.ARGS.SKIP_CAST:
                self._refill_user_stats()
                self._resetting_stage()
                self.tackle.cast()
                self.tackle.sink()
            self.cfg.ARGS.SKIP_CAST = False

            if not self.detection.is_fish_hooked():
                self._elevating_stage()

            self._retrieving_stage()

            if self.detection.is_fish_hooked():
                self._drink_alcohol()
                self._pulling_stage()

    def start_float_mode(self) -> None:
        """Main float fishing loop."""
        while True:
            self._refill_user_stats()
            self._harvesting_stage(pickup=True)
            self._resetting_stage()
            self.tackle.cast()

            logger.info("Checking float status")
            try:
                self._monitor_float_state()
            except TimeoutError:
                self.cast_miss_count += 1
                continue

            sleep(self.cfg.SELECTED.PULL_DELAY)
            utils.hold_mouse_button(PRE_RETRIEVAL_DURATION)
            if self.detection.is_fish_hooked():
                self._drink_alcohol()
                self._pulling_stage()

    def wakey_rig_fishing(self) -> None:
        """Main wakey rig fishing loop."""
        while True:
            if not self.cfg.ARGS.SKIP_CAST:
                self._refill_user_stats()
                self._resetting_stage()
                self.tackle.cast()
                self.tackle.sink(marine=False)
            self.cfg.ARGS.SKIP_CAST = False

            if self.cfg.SELECTED.PIRK_TIMEOUT > 0:
                self._pirking_stage()

            self._retrieving_stage()

            if self.detection.is_fish_hooked():
                self._drink_alcohol()
                self._pulling_stage()

    # this is not done yet :(
    # def trolling_fishing(self) -> None:
    #     # temp
    #     rod_idx = -1
    #     rod_count = len(self.bottom_rods_shortcuts) #!
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
    def _harvesting_stage(self, pickup=False) -> None:
        """Harvest the bait."""
        if not self.cfg.ARGS.HARVEST:
            return

        if not self.detection.is_energy_high():
            return

        logger.info("Harvesting baits")
        self._access_item("shovel_spoon")
        sleep(PULL_OUT_DELAY)
        pag.click()

        i = DIG_TIMEOUT
        while i > 0:
            i = utils.sleep_and_decrease(i, DIG_DELAY)
            if self.detection.is_harvest_success():
                # accept result and hide the tool
                pag.press("space")
                pag.press("backspace")
                sleep(ANIMATION_DELAY)
                self.harvest_count += 1
                break

        if pickup:
            self._access_item("main_rod")  # pick up again
            sleep(1)

        # when timed out, do not raise a TimeoutError but defer it to resetting stage

    def _refill_user_stats(self) -> None:
        """Refill player stats using tea and carrot."""
        if not self.cfg.ARGS.REFILL:
            return

        logger.info("Refilling player stats")
        # comfort is affected by weather, add a check to avoid over drink
        if self.detection.is_comfort_low() and self.timer.is_tea_drinkable():
            self._access_item("tea")
            self.tea_count += 1
            sleep(ANIMATION_DELAY)

        # refill food level
        if self.detection.is_hunger_low():
            self._access_item("carrot")
            self.carrot_count += 1
            sleep(ANIMATION_DELAY)

    def _drink_alcohol(self) -> None:
        """Drink alcohol with given quantity."""
        if not self.cfg.ARGS.ALCOHOL:
            return

        if not self.timer.is_alcohol_drinkable(self.cfg.STAT.ALCOHOL_DELAY):
            return

        logger.info("Drinking alcohol")
        for _ in range(self.cfg.STAT.ALCOHOL_PER_DRINK):
            self._access_item("alcohol")
            self.alcohol_count += 1
            sleep(ANIMATION_DELAY)

    def _drink_coffee(self) -> None:
        """Drink coffee."""
        if not self.cfg.ARGS.COFFEE:
            return

        if self.detection.is_energy_high():
            return

        if self.cur_coffee_count > self.cfg.STAT.COFFEE_LIMIT:
            pag.press("esc")  # back to control panel to reduce power usage
            self._handle_termination("Coffee limit reached", shutdown=False)

        logger.info("Drinking coffee")
        for _ in range(self.cfg.COFFEE_PER_DRINK):
            self._access_item("coffee")
            self.cur_coffee_count += 1
            self.total_coffee_count += 1
            sleep(ANIMATION_DELAY)


    def _access_item(self, item: str) -> None:
        """Access item by name using quick selection shortcut or menu.

        :param item: the name of the item
        :type item: str
        """
        # key = getattr(self.cfg, f"{item}_shortcut")
        key = self.cfg.KEY[item.upper()]
        if key != "-1":
            pag.press(key)
            return

        # key = 1, item is a food
        with pag.hold("t"):
            sleep(ANIMATION_DELAY)
            food_position = self.detection.get_food_position(item)
            pag.moveTo(food_position)
            pag.click()

    @utils.reset_friction_brake_after
    def _resetting_stage(self) -> None:
        """Reset the tackle till it's ready."""
        sleep(ANIMATION_DELAY)
        if self.detection.is_tackle_ready():
            return

        if self.detection.is_lure_broken():
            self._handle_broken_lure()
            return

        while True:
            try:
                self.tackle.reset()
                return
            except exceptions.FishHookedError:
                try:
                    self._pulling_stage()  # do a complete stage
                except TimeoutError:
                    pass
                return  # whether success or not, back to main fishing loop
            except exceptions.FishCapturedError:
                self._handle_fish()
                return
            except exceptions.GroundbaitNotChosenError:
                # trick to avoid invalid cast
                pag.press("0")
                return
            except TimeoutError:  # rare events
                self._handle_timeout()

    def _handle_timeout(self) -> None:
        """Handle common timeout events."""
        if self.detection.is_tackle_broken():
            self.general_quit("Tackle is broken")

        if self.detection.is_disconnected():
            self.disconnected_quit()

        if self.detection.is_ticket_expired():
            self._handle_expired_ticket()

        if self.cfg.SCRIPT.SNAG_DETECTION and self.detection.is_line_snagged():
            self.general_quit("Line is snagged")

    def _handle_broken_lure(self):
        """Handle the broken lure event according to the settings."""
        msg = "Lure is broken"
        logger.warning(msg)
        match self.cfg.SCRIPT.LURE_BROKEN_ACTION:
            case "alarm":
                self._handle_termination(msg, shutdown=False)
            case "replace":
                self._replace_broken_lures()
                return
            case "quit":
                self.general_quit(msg)
            case _:
                raise ValueError

    @utils.release_keys_after
    def _handle_termination(self, msg: str, shutdown: bool) -> None:
        """Send email and plot diagram, quit the game if necessary

        :param msg: quit message
        :type msg:
        :param shutdown: whether to shutdown the computer or not
        :type shutdown: bool
        """
        result = self.gen_result(msg)
        if self.cfg.ARGS.EMAIL:
            self.send_email(result)
        if self.cfg.ARGS.MIAOTIXING:
            self.send_miaotixing(result)
        if self.cfg.ARGS.PLOT:
            self.plot_and_save()
        if shutdown and self.cfg.ARGS.SHUTDOWN:
            os.system("shutdown /s /t 5")
        print(result)
        sys.exit()

    def _retrieving_stage(self) -> None:
        """Retrieve the line till it's fully retrieved with timeout handling."""
        if self.cfg.ARGS.BITE:
            # wait until the popup at bottom right corner becomes transparent
            sleep(SCREENSHOT_DELAY)
            self.window.save_screenshot(self.timer.get_cur_timestamp())
        if self.detection.is_retrieval_finished():
            return

        first = True
        gr_switched = False
        self.cur_coffee_count = 0
        while True:
            try:
                self.tackle.retrieve(first)
                break
            except exceptions.FishCapturedError:
                self._handle_fish()
                break
            except exceptions.LineAtEndError:
                self.general_quit("Fishing line is at its end")
            except TimeoutError:
                self._handle_timeout()
                first = False
                if self.cfg.ARGS.GEAR_RATIO and not gr_switched:
                    self.tackle.switch_gear_ratio()
                    gr_switched = True
                pag.keyUp("shift")
                self._drink_coffee()

        pag.keyUp("shift")
        if gr_switched:
            self.tackle.switch_gear_ratio()

    def _pirking_stage(self) -> None:
        """Perform pirking till a fish hooked with timeout handling."""
        ctrl_enabled = self.cfg.SELECTED.MODE == "wakey_rig"
        while True:
            try:
                self.tackle.pirk(ctrl_enabled)
                break
            except TimeoutError:
                self._handle_timeout()
                if self.cfg.PIRK_TIMEOUT_ACTION == "recast":
                    self._resetting_stage()
                    self.tackle.cast()
                    self.tackle.sink()
                elif self.cfg.PIRK_TIMEOUT_ACTION == "adjust":
                    # adjust lure depth if no fish is hooked
                    logger.info("Adjusting lure depth")
                    pag.press("enter")  # open reel
                    sleep(LURE_ADJUST_DELAY)
                    utils.hold_mouse_button(self.cfg.SELECTED_TIGHTEN_DURATION)
                # TODO: setting saturation
                # TODO: improve dedicated miss count for marine fishing
                self.cast_miss_count += 1

    def _elevating_stage(self) -> None:
        """Perform elevating till a fish hooked with timeout handling."""
        drop = False
        while True:
            try:
                drop = not drop
                self.tackle.elevate(drop)
                break
            except TimeoutError:
                self._handle_timeout()
                self.cast_miss_count += 1
                # lazy skip

    def _monitor_float_state(self) -> None:
        """Monitor the state of the float."""
        reference_img = pag.screenshot(region=self.detection.float_camera_rect)
        i = self.cfg.SELECTED.DRIFT_TIMEOUT
        while i > 0:
            i = utils.sleep_and_decrease(i, self.cfg.SELECTED.DRIFT_TIMEOUT)
            if self.detection.is_float_state_changed(reference_img):
                logger.info("Float status changed")
                return

        raise TimeoutError

    def _pulling_stage(self) -> None:
        """Pull the fish up, then handle it."""
        while True:
            try:
                self.tackle.pull()
                self._handle_fish()
                return
            except exceptions.FishGotAwayError:
                return
            except TimeoutError:
                self._handle_timeout()
                if self.cfg.SELECTED.MODE == "float":
                    continue
                self._retrieving_stage()

    def _handle_fish(self) -> None:
        """Keep or release the fish and record the fish count.

        !! a trophy ruffe will break the checking mechanism?
        """
        logger.info("Handling fish")

        if self.cfg.ARGS.SCREENSHOT:
            self.window.save_screenshot(self.timer.get_cur_timestamp())

        if self.detection.is_fish_marked():
            self.marked_count += 1
        else:
            self.unmarked_count += 1
            if self.cfg.ARGS.MARKED and not self._is_fish_whitelisted():
                pag.press("backspace")
                if (
                    self.cfg.ARGS.PAUSE
                    and time() - self.timer.last_pause > self.cfg.PAUSE.DELAY
                ):
                    pag.press("esc")
                    bound = self.cfg.PAUSE.DURATION // 20
                    offset = random.randint(-bound, bound)
                    self.cfg.PAUSE.DURATION = self.cfg.PAUSE.DURATION + offset
                    pag.press("esc")
                    self.timer.last_pause = time()
                return

        # fish is marked, unmarked release is disabled, or fish is in whitelist
        sleep(self.cfg.KEEPNET.DELAY)
        pag.press("space")

        self.keep_fish_count += 1
        if self.keep_fish_count == self.cfg.KEEPNET.CAPACITY - self.cfg.ARGS.FISHES_IN_KEEPNET:
            self._handle_full_keepnet()

        # avoid wrong cast hour
        if self.special_cast_miss:
            self.timer.update_cast_hour()
        self.timer.add_cast_hour()

        if (
            self.cfg.ARGS.PAUSE
            and time() - self.timer.last_pause > self.cfg.PAUSE.DELAY
        ):
            pag.press("esc")
            bound = self.cfg.PAUSE.DURATION // 20
            offset = random.randint(-bound, bound)
            self.cfg.PAUSE.DURATION = self.cfg.PAUSE.DURATION + offset
            pag.press("esc")
            self.timer.last_pause = time()

    def _handle_full_keepnet(self):
        msg = "Keepnet is full"
        match self.cfg.KEEPNET.FULL_ACTION:
            case "alarm":
                logger.warning(msg)
                playsound(str(Path(self.cfg.SCRIPT.ALARM_SOUND).resolve()))
            case "quit":
                self.general_quit(msg)
            case _:
                raise ValueError

    def _is_fish_whitelisted(self):
        if self.cfg.KEEPNET.RELEASE_WHITELIST[0] == "None":
            return False

        for species in self.cfg.KEEPNET.RELEASE_WHITELIST:
            if self.detection.is_fish_species_matched(species):
                return True
        return False

    # ---------------------------------------------------------------------------- #
    #                                     misc                                     #
    # ---------------------------------------------------------------------------- #

    def general_quit(self, msg: str) -> None:
        """Quit the game through control panel.

        :param msg: the cause of the termination
        :type msg: str
        """
        sleep(ANIMATION_DELAY)  # pre-delay
        pag.press("esc")
        pag.click()  # prevent possible stuck
        sleep(ANIMATION_DELAY)
        pag.moveTo(self.detection.get_quit_position())
        pag.click()
        sleep(ANIMATION_DELAY)
        pag.moveTo(self.detection.get_yes_position())
        pag.click()

        self._handle_termination(msg, shutdown=True)

    def disconnected_quit(self) -> None:
        """Quit the game through main menu."""
        pag.click()  # release possible clicklock
        pag.press("space")
        # sleep to bypass the black screen (experimental)
        sleep(DISCONNECTED_DELAY)

        pag.press("space")
        sleep(ANIMATION_DELAY)

        pag.moveTo(self.detection.get_exit_icon_position())
        pag.click()
        sleep(ANIMATION_DELAY)
        pag.moveTo(self.detection.get_confirm_exit_icon_position())
        pag.click()

        self._handle_termination("Game disconnected", shutdown=True)

    def gen_result(self, msg: str) -> PrettyTable:
        """Generate a PrettyTable object for display and email based on running results.

        :param msg: cause of termination
        :type msg: str
        :return: table consisting cause of termination and run-time records
        :rtype: PrettyTable
        """
        fish_count_total = self.marked_count + self.unmarked_count
        cast_count = self.cast_miss_count + fish_count_total

        if fish_count_total == 0:
            marked_ratio = 0
        else:
            marked_ratio = int(self.marked_count / fish_count_total * 100)
        mum_desc = f"{self.marked_count} / {self.unmarked_count} / {marked_ratio}%"

        bite_ratio = int(fish_count_total / cast_count * 100) if cast_count != 0 else 0
        hmb_desc = f"{fish_count_total} / {cast_count} / {bite_ratio}%"

        # display_running_results() not applicable for some of the records
        results = (
            ("Cause of termination", msg),
            ("Start time", self.timer.get_start_datetime()),
            ("Finish time", self.timer.get_cur_datetime()),
            ("Running time", self.timer.get_duration()),
            ("Fish caught", self.keep_fish_count),
            ("Marked / Unmarked / Mark ratio", mum_desc),
            ("Hit / Miss / Bite ratio", hmb_desc),
            ("Alcohol consumed", self.alcohol_count),
            ("Coffee consumed", self.total_coffee_count),
            ("Tea consumed", self.tea_count),
            ("Carrot consumed", self.carrot_count),
            ("Harvest baits count", self.harvest_count),
        )

        table = PrettyTable(header=False, align="l")
        table.title = "Running Results"
        for column_name, attribute_value in results:
            table.add_row([column_name, attribute_value])
        return table

    def send_email(self, table: PrettyTable) -> None:
        """Send a notification email to the user's email address.

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
        msg.attach(MIMEText(table.get_html_string(), "html"))

        # send email with SMTP
        with smtplib.SMTP_SSL(smtp_server_name, 465) as smtp_server:
            # smtp_server.ehlo()
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())
        print("A notification email has been sent to your email address")

    def send_miaotixing(self, table: PrettyTable) -> None:
        """Send a notification Message to the user's miaotixing service."""

        # Prepare the data to be sent as query parameters
        data_dict = {}
        for row in table.rows:
            column_name, attribute_value = row
            data_dict[column_name] = attribute_value

        load_dotenv()
        miao_code = os.getenv("MIAO_CODE")

        # Customizable Text Prompt Message
        text = (
            "Cause of termination:"
            + data_dict["Cause of termination"]
            + "\nStart time:"
            + data_dict["Start time"]
            + "\nFinish time:"
            + data_dict["Finish time"]
            + "\nRunning time:"
            + data_dict["Running time"]
            + "\nFish caught:"
            + str(data_dict["Fish caught"])
            + "\nMarked / Unmarked / Mark ratio:"
            + data_dict["Marked / Unmarked / Mark ratio"]
            + "\nHit / Miss / Bite ratio:"
            + data_dict["Hit / Miss / Bite ratio"]
            + "\nAlcohol consumed:"
            + str(data_dict["Alcohol consumed"])
            + "\nCoffee consumed:"
            + str(data_dict["Coffee consumed"])
            + "\nTea consumed:"
            + str(data_dict["Tea consumed"])
            + "\nCarrot consumed:"
            + str(data_dict["Carrot consumed"])
            + "\nHarvest baits count:"
            + str(data_dict["Harvest baits count"])
        )

        url = "http://miaotixing.com/trigger?" + parse.urlencode(
            {"id": miao_code, "text": text, "type": "json"}
        )

        with request.urlopen(url) as page:
            result = page.read()
            json_object = json.loads(result)
            if json_object["code"] == 0:
                print("A notification message to the user's miaotixing service.")
            else:
                print(
                    "Sending failed with error code:"
                    + str(json_object["code"])
                    + ", Deutilsion:"
                    + json_object["msg"]
                )

    def plot_and_save(self) -> None:
        """Plot and save an image using rhour and ghour list from timer object."""
        if self.keep_fish_count == 0:
            return

        cast_rhour_list, cast_ghour_list = self.timer.get_cast_hour_list()
        _, ax = plt.subplots(nrows=1, ncols=2)
        # _.canvas.manager.set_window_title('Record')
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

    def _handle_expired_ticket(self):
        """Select and use the ticket according to boat_ticket_duration argument."""
        if self.cfg.ARGS.BOAT_TICKET is None:
            pag.press("esc")
            sleep(TICKET_EXPIRE_DELAY)
            self.general_quit("Boat ticket expired")

        logger.info("Renewing boat ticket")
        ticket_loc = self.detection.get_ticket_position(self.cfg.ARGS.BOAT_TICKET)
        if ticket_loc is None:
            pag.press("esc")  # quit ticket menu
            sleep(ANIMATION_DELAY)
            self.general_quit("Boat ticket not found")
        pag.moveTo(ticket_loc)
        pag.click(clicks=2, interval=0.1)  # pag.doubleClick() not implemented
        sleep(ANIMATION_DELAY)

    def _replace_broken_lures(self):
        """Replace multiple broken items (lures)."""
        logger.info("Replacing broken lures")
        # open tackle menu
        pag.press("v")
        sleep(ANIMATION_DELAY)

        scrollbar_position = self.detection.get_scrollbar_position()
        if scrollbar_position is None:
            logger.info("Scroll bar not found, changing lures for normal rig")
            while self._open_broken_lure_menu():
                self._replace_selected_item()
            pag.press("v")
            return

        logger.info("Scroll bar found, changing lures for dropshot rig")
        pag.moveTo(scrollbar_position)
        for _ in range(5):
            sleep(1)
            pag.drag(xOffset=0, yOffset=125, duration=0.5, button="left")

            replaced = False
            while self._open_broken_lure_menu():
                self._replace_selected_item()
                replaced = True

            if replaced:
                pag.moveTo(self.detection.get_scrollbar_position())
        pag.press("v")
        sleep(ANIMATION_DELAY)

    def _open_broken_lure_menu(self) -> bool:
        """Search for text of broken item, open selection menu if found.

        :return: True if broken item is found, False otherwise
        :rtype: bool
        """
        logger.info("Searching for broken lure")
        broken_item_position = self.detection.get_100wear_position()
        if broken_item_position is None:
            logger.warning("Broken lure not found")
            return False

        # click item to open selection menu
        logger.info("Broken lure found")
        pag.moveTo(broken_item_position)
        sleep(ANIMATION_DELAY)
        pag.click()
        sleep(ANIMATION_DELAY)
        return True

    def _replace_selected_item(self) -> None:
        """Select a favorite item for replacement and replace the broken one."""
        logger.info("Search for favorite items")
        favorite_item_positions = self.detection.get_favorite_item_positions()
        while True:
            favorite_item_position = next(favorite_item_positions, None)

            if favorite_item_position is None:
                msg = "Lure for replacement not found"
                logger.warning(msg)
                pag.press("esc")
                sleep(ANIMATION_DELAY)
                pag.press("esc")
                sleep(ANIMATION_DELAY)
                self.general_quit(msg)

            # check if the lure for replacement is already broken
            x, y = utils.get_box_center(favorite_item_position)
            if pag.pixel(x - 75, y + 190) != (178, 59, 30):  # magic value
                logger.info("The broken lure has been replaced")
                pag.moveTo(x - 75, y + 190)
                pag.click(clicks=2, interval=0.1)
                sleep(WEAR_TEXT_UPDATE_DELAY)
                break

            logger.warning("Lure for replacement found but already broken")

    def _change_lure_randomly(self) -> None:
        """Open menu, select a random lure and replace the current one."""
        logger.info("Search for favorite items")
        with pag.hold("b"):
            sleep(ANIMATION_DELAY)
            favorite_item_positions = list(self.detection.get_favorite_item_positions())
            random.shuffle(favorite_item_positions)
            for favorite_item_position in favorite_item_positions:
                # check if the lure for replacement is already broken
                x, y = utils.get_box_center(favorite_item_position)
                if pag.pixel(x - 75, y + 190) != (178, 59, 30):  # magic value
                    logger.info("The lure has been replaced")
                    pag.moveTo(x - 75, y + 190)
                    pag.click()
                    break
                logger.warning("Lure for replacement found but already broken")
            logger.warning("Lure for replacement not found, stay unchanged")
        sleep(ANIMATION_DELAY)

    def _put_tackle_back(self, check_miss_counts: list[int], rod_idx: int) -> None:
        """Update counters, put down the tackle and wait for a while.

        :param check_miss_counts: miss counts of all rods
        :type check_miss_counts: list[int]
        :param rod_idx: current index of the rod
        :type rod_idx: int
        """
        check_miss_counts[rod_idx] += 1
        if check_miss_counts[rod_idx] >= self.cfg.SELECTED.CHECK_MISS_LIMIT:
            check_miss_counts[rod_idx] = 0
            self._resetting_stage()
            self.tackle.cast()
            pag.click()

        pag.press("0")
        random_offset = random.uniform(-BOUND, BOUND)
        sleep(self.cfg.SELECTED.CHECK_DELAY + random_offset)


    def _trolling_stage(self):
        """Start trolling and change moving direction based on trolling setting.

        Available options: never, forward, left, right.
        """
        if self.cfg.SELECTED.TROLLING == "never":
            return
        pag.press(TROLLING_KEY)
        if self.cfg.SELECTED.TROLLING not in ("left", "right"):
            return
        pag.keyDown(LEFT_KEY if self.cfg.SELECTED.TROLLING == "left" else RIGHT_KEY)

