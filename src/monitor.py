"""
Module for pyautogui.locateOnScreen wrappers.

Todo:
    Validate language option
    Implement snag detection
"""

# pylint: disable=missing-function-docstring
# docstring for every functions? u serious?

import logging
import sys

import pyautogui as pag
from pyscreeze import Box

from setting import Setting

logger = logging.getLogger(__name__)


class Monitor:
    """A class that holds different aliases of locateOnScreen(image)."""

    # pylint: disable=too-many-public-methods

    def __init__(self, setting: Setting):
        """Initialize setting.

        :param setting: general setting node
        :type setting: Setting
        """
        self.setting = setting

    def _locate_single_image_box(self, image: str, confidence: float) -> Box | None:
        """A wrapper for locateOnScreen method and path resolving.

        :param image: base name of the image
        :type image: str
        :param confidence: matching confidence for locateOnScreen
        :type confidence: float
        :return: image box, None if not found
        :rtype: Box
        """
        return pag.locateOnScreen(
            f"{self.setting.image_dir}/{image}.png", confidence=confidence
        )

    def _locate_multiple_image_boxes(self, image: str, confidence: float) -> Box | None:
        """A wrapper for locateAllOnScreen method and path resolving.

        This method is used for eliminating branching in ._locate_single_image_box(),
        which accelerates those frequently called upstreasm methods.
        It should only be invoked by get_favorite_items().

        :param image: base name of the image
        :type image: str
        :param confidence: matching confidence for locateOnScreen
        :type confidence: float
        :return: image box, None if not found
        :rtype: Box
        """
        return pag.locateAllOnScreen(
            f"{self.setting.image_dir}/{image}.png", confidence=confidence
        )

    # ---------------------------------------------------------------------------- #
    #                           icon and text recognition                          #
    # ---------------------------------------------------------------------------- #

    # ------------------------ unmarked release whitelist ------------------------ #
    def is_fish_species_matched(self, species: str) -> Box | None:
        """Check if the captured fish match the given species.

        :param species: mackerel, saithe, herring, squid, scallop, or mussel
        :type species: str
        :return: image box, None if not found
        :rtype: Box
        """
        return self._locate_single_image_box(species, 0.9)

    # ----------------------------- unmarked release ----------------------------- #
    def is_fish_marked(self):
        return self._locate_single_image_box("mark", 0.7)

    def is_fish_yellow_marked(self):
        return self._locate_single_image_box("trophy", 0.7)

    # -------------------------------- fish status ------------------------------- #
    def is_fish_hooked(self):
        return self._locate_single_image_box("get", 0.9)

    def is_fish_captured(self):
        return self._locate_single_image_box("keep", 0.9)

    # ---------------------------- retrieval detection --------------------------- #
    def _is_rainbow_line_0or5m(self):
        return self._locate_single_image_box(
            "5m", self.setting.retrieval_detect_confidence
        ) or self._locate_single_image_box(
            "0m", self.setting.retrieval_detect_confidence
        )

    def _is_spool_full(self):
        return self._locate_single_image_box(
            "wheel", self.setting.retrieval_detect_confidence
        )

    # ------------------------------ hint detection ------------------------------ #
    def is_tackle_ready(self):
        return self._locate_single_image_box("ready", 0.6)

    def is_tackle_broken(self):
        return self._locate_single_image_box("broke", 0.6)

    def is_lure_broken(self):
        return self._locate_single_image_box("lure_is_broken", 0.7)

    def is_moving_in_bottom_layer(self):
        return self._locate_single_image_box("movement", 0.7)

    # ------------------------------ hint detection ------------------------------ #
    def is_disconnected(self):
        return self._locate_single_image_box("disconnected", 0.9)

    def is_line_at_end(self):
        return self._locate_single_image_box("spooling", 0.98)

    def is_ticket_expired(self):
        return self._locate_single_image_box("ticket", 0.9)

    # ------------------------------- item crafting ------------------------------ #
    def is_operation_failed(self):
        return self._locate_single_image_box("warning", 0.8)

    def is_operation_success(self):
        return self._locate_single_image_box("ok", 0.8)

    # ---------------------- quiting game from control panel --------------------- #
    def get_quit_position(self):
        return self._locate_single_image_box("quit", 0.8)

    def get_yes_position(self):
        return self._locate_single_image_box("yes", 0.8)

    def get_make_position(self):
        return self._locate_single_image_box("make", 0.9)

    # ------------------------ quiting game from main menu ----------------------- #
    def get_exit_icon_position(self):
        return self._locate_single_image_box("exit", 0.8)

    def get_confirm_exit_icon_position(self):
        return self._locate_single_image_box("confirm_exit", 0.8)

    # ----------------------------- baits harvesting ----------------------------- #
    def is_harvest_success(self):
        return self._locate_single_image_box("harvest_confirm", 0.8)

    # ----------------------------- player stat icon ----------------------------- #
    def _get_energy_icon_position(self):
        box = self._locate_single_image_box("energy", 0.8)
        return box if box is None else pag.center(box)

    def _get_food_icon_position(self):
        box = self._locate_single_image_box("food", 0.8)
        return box if box is None else pag.center(box)

    def _get_comfort_icon_position(self):
        box = self._locate_single_image_box("comfort", 0.8)
        return box if box is None else pag.center(box)

    # -------------------------- player stat refill item ------------------------- #
    def get_food_position(self, food: str) -> Box | None:
        """Get the position of food in quick selection menu.

        :param food: carrot, tea, or coffee
        :type food: str
        :return: image box, None if not found
        :rtype: Box
        """
        return self._locate_single_image_box(food, 0.8)

    def get_ticket_position(self, duration: int) -> Box | None:
        """Locate the image of boat ticket according to the given duration.

        :param duration: duration of boat ticket
        :type duration: int
        :return: image box, None if not found
        :rtype: Box
        """
        return self._locate_single_image_box(f"ticket_{duration}", 0.95)

    # -------------------------- broken lure replacement ------------------------- #
    def get_scrollbar_position(self):
        return self._locate_single_image_box("scrollbar", 0.97)

    def get_100wear_position(self):
        return self._locate_single_image_box("100wear", 0.98)

    def get_favorite_item_positions(self):
        return self._locate_multiple_image_boxes("favorite", 0.95)

    # ---------------------------------------------------------------------------- #
    #                               image analyzation                              #
    # ---------------------------------------------------------------------------- #
    def is_energy_high(self) -> bool:
        """Check if the energy level is high enough to harvest baits

        :return: True if high enough, False otherwise
        :rtype: bool
        """
        pos = self._get_energy_icon_position()
        if not pos:
            return False
        x, y = int(pos.x), int(pos.y)
        # default threshold: 0.74,  well done FishSoft
        last_point = int(19 + 152 * self.setting.energy_threshold) - 1
        return pag.pixel(x + 19, y) == pag.pixel(x + last_point, y)

    def is_hunger_low(self) -> bool:
        """Check if hunger is low.

        :return: True if lower than 50%, False otherwise
        :rtype: bool
        """
        pos = self._get_food_icon_position()
        if not pos:
            return False
        x, y = int(pos.x), int(pos.y)
        last_point = int(18 + 152 * 0.5) - 1
        return not pag.pixel(x + 18, y) == pag.pixel(x + last_point, y)

    def is_comfort_low(self) -> bool:
        """Check if comfort is low.

        :return: True if lower than 51%, False otherwise
        :rtype: bool
        """
        pos = self._get_comfort_icon_position()
        if not pos:
            return False
        x, y = int(pos.x), int(pos.y)
        last_point = int(18 + 152 * 0.51) - 1
        return not pag.pixel(x + 18, y) == pag.pixel(x + last_point, y)

    def get_float_camera_region(self) -> tuple[int, int, int, int]:
        coord = self.setting.window_controller.get_window_coord()
        x_base, y_base, width, height = coord
        window_size = f"{width}x{height}"
        match window_size:
            case "2560x1440":
                x_base += 1200
                y_base += 1194
            case "1920x1080":
                x_base += 880
                y_base += 834
            case "1600x900":
                x_base += 720
                y_base += 654
            case _:
                logger.error(
                    "Invalid window size, must be 2560x1440, 1920x1080 or 1600x900"
                )
                sys.exit()
        return (x_base, y_base, 160, 160)
