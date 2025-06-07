"""Module for pyautogui.locateOnScreen and pag.pixel wrappers.

This module provides functionality for detecting in-game elements using image recognition
and pixel color analysis. It is used for automating tasks in Russian Fishing 4.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import time
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Generator

import cv2
import numpy as np
import pyautogui as pag
from PIL import Image
from pyscreeze import Box

from rf4s.controller.window import Window

CRITICAL_COLOR = (206, 56, 21)
WARNING_COLOR = (227, 149, 23)
WHITE = (255, 255, 255)

MIN_GRAY_SCALE_LEVEL = 150
YELLOW_FRICTION_BRAKE = (200, 214, 63)
ORANGE_FRICTION_BRAKE = (229, 188, 0)
RED_FRICTION_BRAKE = (206, 56, 21)
COLOR_TOLERANCE = 32
CAMERA_OFFSET = 40
SIDE_LENGTH = 160
SIDE_LENGTH_HALF = 80
ORANGE_REEL = (227, 149, 23)

ROOT = Path(__file__).resolve().parents[2]


class TagColor(Enum):
    GREEN = "green_tag"
    YELLOW = "yellow_tag"
    PINK = "pink_tag"
    BLUE = "blue_tag"
    PURPLE = "purple_tag"


COORD_OFFSETS = {
    "1600x900": {
        "friction_brake_very_high": (502, 872),  # Left point only
        "friction_brake_high": (459, 872),
        "friction_brake_medium": (417, 872),
        "friction_brake_low": (396, 872),
        "fish_icon": (389, 844),
        "clip_icon": (1042, 844),
        "spool_icon": (1077, 844),  # x + 15, y + 15
        "reel_burning_icon": (1112, 842),
        "snag_icon": (1147, 829),  # x + 15, y
        "float_camera": (720, 654),
        "bait_icon": (35, 31),
    },
    "1920x1080": {
        "friction_brake_very_high": (662, 1052),
        "friction_brake_high": (619, 1052),
        "friction_brake_medium": (577, 1052),
        "friction_brake_low": (556, 1052),
        "fish_icon": (549, 1024),
        "clip_icon": (1202, 1024),
        "spool_icon": (1237, 1024),
        "reel_burning_icon": (1271, 1023),
        "snag_icon": (1307, 1009),
        "float_camera": (880, 834),
        "bait_icon": (35, 31),
    },
    "2560x1440": {
        "friction_brake_very_high": (982, 1412),
        "friction_brake_high": (939, 1412),
        "friction_brake_medium": (897, 1412),
        "friction_brake_low": (876, 1412),
        "fish_icon": (869, 1384),
        "clip_icon": (1522, 1384),
        "spool_icon": (1557, 1384),
        "reel_burning_icon": (1593, 1383),
        "snag_icon": (1627, 1369),
        "float_camera": (1200, 1194),
        "bait_icon": (35, 31),
    },
}

# ------------------------ Friction brake coordinates ------------------------ #
# ----------------------------- 900p - 1080p - 2k ---------------------------- #
# ------ left - red - yellow - center(left + 424) - yellow - red - right ----- #
# "bases": ((480, 270), (320, 180), (0, 0))
# "absolute": {"x": (855, 960, 1066, 1279, 1491, 1598, 1702, "y": (1146, 1236, 1412)}
# "1600x900": {"x": (375, 480, 586, 799, 1011, 1118, 1222), "y": 876},
# "1920x1080": {"x": (535, 640, 746, 959, 1171, 1278, 1382), "y": 1056},
# "2560x1440": {"x": (855, 960, 1066, 1279, 1491, 1598, 1702), "y": 1412},


class Detection:
    """A class that holds different aliases of locateOnScreen(image).

    This class provides methods for detecting various in-game elements such as fish,
    icons, and UI components using image recognition and pixel color analysis.

    Attributes:
        cfg (CfgNode): Configuration node for the detection settings.
        window (Window): Game window controller instance.
        image_dir (Path): Directory containing reference images for detection.
        coord_offsets (dict): Dictionary of coordinate offsets for different window sizes.
        bait_icon_reference_img (Image): Reference image for bait icon detection.
    """

    def __init__(self, cfg, window: Window):
        """Initialize the Detection class with configuration and window settings.

        :param cfg: Configuration node for detection settings.
        :type cfg: CfgNode
        :param window: Game window controller instance.
        :type window: Window
        """
        self.cfg = cfg
        self.window = window
        self.image_dir = ROOT / "static" / cfg.SCRIPT.LANGUAGE

        if window.is_size_supported():
            self._set_absolute_coords()
            self.is_fish_hooked = self.is_fish_hooked_pixel
        else:
            self.is_fish_hooked = partial(
                self._get_image_box,
                image="fish_icon",
                confidence="0.9",
            )

        self.bait_icon_reference_img = Image.open(self.image_dir / "bait_icon.png")

    def _get_image_box(
        self, image: str, confidence: float, multiple: bool = False
    ) -> Box | Generator[Box, None, None] | None:
        """A wrapper for locateOnScreen method and path resolving.

        :param image: Base name of the image.
        :type image: str
        :param confidence: Matching confidence for locateOnScreen.
        :type confidence: float
        :param multiple: Whether to locate all matching images, defaults to False.
        :type multiple: bool, optional
        :return: Image box, None if not found.
        :rtype: Box | None
        """
        image_path = str(self.image_dir / f"{image}.png")
        if multiple:
            return pag.locateAllOnScreen(image_path, confidence=confidence)
        return pag.locateOnScreen(image_path, confidence=confidence)

    def _set_absolute_coords(self) -> None:
        """Add offsets to the base coordinates to get absolute ones."""
        self.coord_offsets = COORD_OFFSETS[self.window.get_resolution_str()]

        for key in self.coord_offsets:
            setattr(self, f"{key}_coord", self._get_absolute_coord(key))

        self.bait_icon_coord = self._get_absolute_coord("bait_icon") + [44, 52]
        friction_brake_key = f"friction_brake_{self.cfg.FRICTION_BRAKE.SENSITIVITY}"
        self.friction_brake_coord = self._get_absolute_coord(friction_brake_key)

        bases = self._get_absolute_coord("float_camera")
        if self.cfg.SELECTED.MODE in ("telescopic", "bolognese"):
            match self.cfg.SELECTED.CAMERA_SHAPE:
                case "tall":
                    bases[0] += CAMERA_OFFSET
                    width, height = SIDE_LENGTH_HALF, SIDE_LENGTH
                case "wide":
                    bases[1] += CAMERA_OFFSET
                    width, height = SIDE_LENGTH, SIDE_LENGTH_HALF
                case "square":
                    width, height = SIDE_LENGTH, SIDE_LENGTH
                case _:
                    raise ValueError(self.cfg.SELECTED.CAMERA_SHAPE)
            self.float_camera_rect = (*bases, width, height)  # (left, top, w, h)

    def _get_absolute_coord(self, offset_key: str) -> list[int]:
        """Calculate absolute coordinate based on given key.

        :param offset_key: A key in the offset dictionary.
        :type offset_key: str
        :return: Converted absolute coordinate.
        :rtype: list[int]
        """
        box = self.window.get_box()
        return [box[i] + self.coord_offsets[offset_key][i] for i in range(2)]

    # ----------------------------- Untagged release ----------------------------- #
    def is_tag_exist(self, color: TagColor):
        match color:
            case TagColor.GREEN:
                lower = np.array([30, 128, 128])
                upper = np.array([36, 255, 255])
            case TagColor.YELLOW:
                lower = np.array([22, 128, 128])
                upper = np.array([28, 255, 255])
            case TagColor.PINK:
                lower = np.array([142, 64, 128])
                upper = np.array([148, 255, 255])
            case TagColor.BLUE:
                lower = np.array([101, 64, 128])
                upper = np.array([107, 255, 255])
            case TagColor.PURPLE:
                lower = np.array([127, 64, 128])
                upper = np.array([133, 255, 255])
            case _:
                raise ValueError("Invalid tag color")
        hsv_img = cv2.cvtColor(np.array(pag.screenshot()), cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv_img, lower, upper)
        haystack_img = Image.fromarray(mask)
        needle_img = Image.open(self.image_dir / f"{color.value}.png")
        return pag.locate(needle_img, haystack_img, grayscale=True, confidence=0.9)

    def is_fish_species_matched(self, species: str):
        return self._get_image_box(species, 0.9)

    # -------------------------------- Fish status ------------------------------- #
    def is_fish_hooked(self):
        pass  # It's initialized in the constructor

    def is_fish_hooked_pixel(self) -> bool:
        return all(c > MIN_GRAY_SCALE_LEVEL for c in pag.pixel(*self.fish_icon_coord))

    def is_fish_hooked_twice(self) -> bool:
        if not self.is_fish_hooked():
            return False

        # check if the fish got away after a short delay
        time.sleep(self.cfg.SELECTED.HOOK_DELAY)
        if self.is_fish_hooked():
            return True
        return False

    def is_fish_captured(self):
        return self._get_image_box("keep", 0.9)

    def is_fish_whitelisted(self) -> bool:
        """Check if the fish is in the whitelist.

        :return: True if the fish is in the whitelist, False otherwise.
        :rtype: bool
        """
        return self._is_fish_in_list(self.cfg.KEEPNET.WHITELIST)

    def is_fish_blacklisted(self) -> bool:
        """Check if the fish is in the blacklist.

        :return:  True if the fish is in the blacklist, False otherwise
        :rtype: bool
        """
        return self._is_fish_in_list(self.cfg.KEEPNET.BLACKLIST)

    def _is_fish_in_list(self, fish_species_list: tuple | list) -> bool:
        """Check if the fish species matches any in the table.

        :param fish_species_list: fish species list
        :type fish_species_list: tuple | list
        :return: True if the fish species matches, False otherwise
        :rtype: bool
        """
        for species in fish_species_list:
            if self.is_fish_species_matched(species):
                return True
        return False

    # ---------------------------- Retrieval detection --------------------------- #
    def is_retrieval_finished(self):
        ready = self.is_tackle_ready()
        if self.cfg.ARGS.RAINBOW:
            return ready or self._is_rainbow_line_0or5m()
        return ready or self._is_spool_full()

    def _is_rainbow_line_0or5m(self):
        return self._get_image_box(
            "5m", self.cfg.SCRIPT.SPOOL_CONFIDENCE
        ) or self._get_image_box("0m", self.cfg.SCRIPT.SPOOL_CONFIDENCE)

    def _is_spool_full(self):
        return self._get_image_box("wheel", self.cfg.SCRIPT.SPOOL_CONFIDENCE)

    def is_line_snagged(self) -> bool:
        return pag.pixel(*self.snag_icon_coord) == CRITICAL_COLOR

    def is_line_at_end(self) -> bool:
        return pag.pixel(*self.spool_icon_coord) in (WARNING_COLOR, CRITICAL_COLOR)

    def is_clip_open(self) -> bool:
        return not all(
            c > MIN_GRAY_SCALE_LEVEL for c in pag.pixel(*self.clip_icon_coord)
        )

    # ------------------------------ Text detection ------------------------------ #
    def is_tackle_ready(self):
        return self._get_image_box("ready", 0.6)

    def is_tackle_broken(self):
        return self._get_image_box("broke", 0.8)

    def is_lure_broken(self):
        return self._get_image_box("lure_is_broken", 0.8)

    def is_moving_in_bottom_layer(self):
        return self._get_image_box("movement", 0.7)

    # ------------------------------ Hint detection ------------------------------ #
    def is_disconnected(self):
        return self._get_image_box("disconnected", 0.9)

    def is_ticket_expired(self):
        return self._get_image_box("ticket", 0.9)

    # ------------------------------- Item crafting ------------------------------ #
    def is_operation_failed(self):
        return self._get_image_box("warning", 0.8)

    def is_operation_success(self):
        return self._get_image_box("ok_black", 0.8) or self._get_image_box(
            "ok_white", 0.8
        )

    def is_material_complete(self):
        return not self._get_image_box("material_slot", 0.7)

    # ---------------------- Quiting game from control panel --------------------- #
    def get_quit_position(self):
        return self._get_image_box("quit", 0.8)

    def get_yes_position(self):
        return self._get_image_box("yes", 0.8)

    def get_make_button_position(self):
        return self._get_image_box("make", 0.9)

    # ------------------------ Quiting game from main menu ----------------------- #
    def get_exit_icon_position(self):
        return self._get_image_box("exit", 0.8)

    def get_confirm_button_position(self):
        return self._get_image_box("confirm", 0.8)

    # ------------------------------- Player stats ------------------------------- #
    def _get_energy_icon_position(self):
        box = self._get_image_box("energy", 0.8)
        return box if box is None else pag.center(box)

    def _get_food_icon_position(self):
        box = self._get_image_box("food", 0.8)
        return box if box is None else pag.center(box)

    def _get_comfort_icon_position(self):
        box = self._get_image_box("comfort", 0.8)
        return box if box is None else pag.center(box)

    def get_food_position(self, food: str):
        return self._get_image_box(food, 0.9)

    def is_energy_high(self) -> bool:
        pos = self._get_energy_icon_position()
        if not pos:
            return False
        x, y = int(pos.x), int(pos.y)
        # default threshold: 0.74,  well done FishSoft
        last_point = int(19 + 152 * self.cfg.STAT.ENERGY_THRESHOLD) - 1
        return pag.pixel(x + 19, y) == pag.pixel(x + last_point, y)

    def is_hunger_low(self) -> bool:
        pos = self._get_food_icon_position()
        if not pos:
            return False
        x, y = int(pos.x), int(pos.y)
        last_point = int(18 + 152 * self.cfg.STAT.HUNGER_THRESHOLD) - 1
        return not pag.pixel(x + 18, y) == pag.pixel(x + last_point, y)

    def is_comfort_low(self) -> bool:
        pos = self._get_comfort_icon_position()
        if not pos:
            return False
        x, y = int(pos.x), int(pos.y)
        last_point = int(18 + 152 * self.cfg.STAT.COMFORT_THRESHOLD) - 1
        return not pag.pixel(x + 18, y) == pag.pixel(x + last_point, y)

    # ----------------------------- Item replacement ----------------------------- #
    def get_scrollbar_position(self):
        return self._get_image_box("scrollbar", 0.97)

    def get_100wear_position(self):
        return self._get_image_box("100wear", 0.98)

    def get_favorite_item_positions(self):
        return self._get_image_box("favorite", 0.95, multiple=True)

    def is_pva_chosen(self):
        return self._get_image_box("pva_icon", 0.6) is None

    def is_bait_chosen(self):
        if self.cfg.SELECTED.MODE in ("pirk", "elevator"):
            return True

        # Two bait slots, check only the first one
        if self.cfg.SELECTED.MODE in ("telescopic", "bolognese"):
            return (
                pag.locate(
                    pag.screenshot(region=self.bait_icon_coord),
                    self.bait_icon_reference_img,
                    confidence=0.6,
                )
                is None
            )
        return self._get_image_box("bait_icon", 0.6) is None

    def is_groundbait_chosen(self):
        return self._get_image_box("groundbait_icon", 0.6) is None

    def get_groundbait_position(self):
        return self._get_image_box("classic_feed_mix", 0.95)

    def get_dry_mix_position(self):
        return self._get_image_box("dry_feed_mix", 0.95)

    def get_pva_position(self):
        return self._get_image_box("pva_stick_or_pva_stringer", 0.95)

    # ------------------------------ Friction brake ------------------------------ #
    def is_friction_brake_high(self) -> bool:
        return pag.pixelMatchesColor(
            *self.friction_brake_coord, RED_FRICTION_BRAKE, COLOR_TOLERANCE
        )

    def is_reel_burning(self) -> bool:
        return pag.pixel(*self.reel_burning_icon_coord) == ORANGE_REEL

    def is_float_state_changed(self, reference_img):
        current_img = pag.screenshot(region=self.float_camera_rect)
        return not pag.locate(
            current_img,
            reference_img,
            grayscale=True,
            confidence=self.cfg.SELECTED.FLOAT_SENSITIVITY,
        )

    def get_ticket_position(self, duration: int):
        return self._get_image_box(f"ticket_{duration}", 0.95)

    def is_harvest_success(self):
        return self._get_image_box("harvest_confirm", 0.8)

    def is_gift_receieved(self):
        return self._get_image_box("gift", 0.8)
