"""
Module for pyautogui.locateOnScreen wrappers.
"""

# pylint: disable=missing-function-docstring
# docstring for every functions? u serious?

import sys
import logging

import pyautogui as pag
from pyscreeze import Box

from setting import Setting

logger = logging.getLogger(__name__)

# FRICTION_BAR_COORDS = {
#     # ----------------------------- 16x9 - 1080p - 2k ---------------------------- #
#     "x_base": (480, 320, 0),
#     "y_base": (270, 180, 0),
#     "y": (1146, 1236, 1412),

#     # ------ left - red - yellow - center(left + 424) - yellow - red - right ----- #
#     # absolute coordinates, should subtract x_base from them according to window size
#     "x": (855, 960, 1066, 1279, 1491, 1598, 1702),
# }

# FRICTION_BAR_OFFSETS = {
#     # ------------ left - red - yellow - center - yellow - red - right ----------- #
#     "1600x900": {"x": (375, 480, 586, 799, 1011, 1118, 1222), "y": 876},
#     "1920x1080": {"x": (535, 640, 746, 959, 1171, 1278, 1382), "y": 1056},
#     "2560x1440": {"x": (855, 960, 1066, 1279, 1491, 1598, 1702), "y": 1412},
# }

# --------------------------- left - center - right -------------------------- #

# 70%: center + 297 (1279 + 297 = 1576)
# 80%: center + 340 (1279 + 340 = 1619)
# 90%: center + 382 (1279 + 382 = 1661)
# center = 1279

FRICTION_BRAKE_BAR_OFFSETS = {
    "1600x900": {
        "x": {
            0.7: (502, 799, 1096),
            0.8: (459, 799, 1139),
            0.9: (417, 799, 1181),
            0.95: (396, 799, 1202),
        },
        "y": 876,
    },
    "1920x1080": {
        "x": {
            0.7: (662, 959, 1256),
            0.8: (619, 959, 1299),
            0.9: (577, 959, 1341),
            0.95: (556, 959, 1362),
        },
        "y": 1056,
    },
    "2560x1440": {
        "x": {
            0.7: (982, 1279, 1576),
            0.8: (939, 1279, 1619),
            0.9: (897, 1279, 1661),
            0.95: (876, 1279, 1682),
        },
        "y": 1412,
    },
}

FISH_ICON_OFFSETS = {
    "1600x900": (389, 844),
    "1920x1080": (549, 1024),
    "2560x1440": (869, 1384)
}

# 1600x900
# 869, 1114, (480, 270)
# 1920x1080
# 869, 1204 (320, 180)
# 2560x1440
# 869, 1384, (0, 0)

FRICTION_BRAKE_OFFSET_NUM = 3
YELLOW_FRICTION = (200, 214, 63)
ORANGE_FRICTION = (229, 188, 0)
RED_FRICTION = (206, 56, 21)
SNAG_ICON_COLOR = (206, 56, 21)
FISH_ICON_COLOR = (234, 234, 234)


class Monitor:
    """A class that holds different aliases of locateOnScreen(image)."""

    # pylint: disable=too-many-public-methods

    def __init__(self, setting: Setting):
        """Initialize setting.

        :param setting: general setting node
        :type setting: Setting
        """
        self.setting = setting
        self.x_coords = None
        self.y_coord = None
        self._set_friction_brake_params()

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

    def is_line_snagged(self) -> bool:
        """Check the top of the snag icon to see if the line is snagged.

        :return: True if snagged, False otherwise
        :rtype: bool
        """
        return pag.pixel(*self.setting.snag_icon_position) == SNAG_ICON_COLOR

    def _set_friction_brake_params(self):
        if self.setting.friction_brake_threshold not in (0.7, 0.8, 0.9, 0.95):
            logger.error("Invalid friction threshold")
            sys.exit()

        if self.setting.friction_brake_threshold == 0.7:
            self.color_group = (ORANGE_FRICTION, RED_FRICTION)
        else:
            self.color_group = (RED_FRICTION, )

        offsets = FRICTION_BRAKE_BAR_OFFSETS[self.setting.window_size]
        x_offsets = offsets["x"][self.setting.friction_brake_threshold]
        y_offset = offsets["y"]
        self.x_coords = tuple(self.setting.x_base + offset for offset in x_offsets)
        self.y_coord = self.setting.y_base + y_offset

    def is_friction_brake_high(self) -> bool:
        """Check if the friction is too high based on left, mid, and right points.

        :return: True if pixels are the same and color is correct, False otherwise
        :rtype: bool
        """
        pixels = [pag.pixel(x, self.y_coord) for x in self.x_coords] # get pixel values
        if pixels.count(pixels[0]) != FRICTION_BRAKE_OFFSET_NUM: # check if pixels having same value
            return False
        return pixels[0] in self.color_group # check if pixel color is orange or red based on threshold

    def _set_fish_icon_params(self):
        offsets = FISH_ICON_OFFSETS[self.setting.window_size]
        self.fish_icon_x = self.setting.x_base + offsets[0]
        self.fish_icon_y = self.setting.y_base + offsets[1]

    def is_fish_hooked_pixel(self) -> bool:
        self._set_fish_icon_params()
        return all(c > 150 for c in pag.pixel(self.fish_icon_x, self.fish_icon_y))