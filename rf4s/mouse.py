"""Human-like mouse movement using the WindMouse algorithm.

Simulates realistic mouse movement with random micro-deviations (wind)
and target attraction (gravity), producing natural S-shaped paths with
deceleration near the target.

"""

import ctypes
import math
import random
import time

import pyautogui as pag
from pyscreeze import Box

from rf4s import utils

# WindMouse parameters
GRAVITY = 9.0
WIND = 3.0
MIN_WAIT = 0.002  # 2ms
MAX_WAIT = 0.005  # 5ms
MAX_STEP = 10.0
TARGET_AREA = 8.0

# Short distance threshold — skip WindMouse for tiny moves
SHORT_DISTANCE = 30

# Overshoot probability and magnitude
OVERSHOOT_CHANCE = 0.15
OVERSHOOT_MIN = 3
OVERSHOOT_MAX = 8

# Click offset range (pixels)
CLICK_OFFSET = 3

# Click hold duration (seconds)
CLICK_HOLD_MIN = 0.05
CLICK_HOLD_MAX = 0.12


def _set_cursor_pos(x: int, y: int) -> None:
    """Move cursor using ctypes (no pyautogui PAUSE overhead)."""
    ctypes.windll.user32.SetCursorPos(int(x), int(y))


def _wind_mouse(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    gravity: float = GRAVITY,
    wind: float = WIND,
    max_step: float = MAX_STEP,
    target_area: float = TARGET_AREA,
) -> list[tuple[int, int]]:
    """Generate a list of points along a human-like path using WindMouse.

    :param start_x: Starting X coordinate.
    :param start_y: Starting Y coordinate.
    :param end_x: Target X coordinate.
    :param end_y: Target Y coordinate.
    :param gravity: Strength of attraction toward the target.
    :param wind: Strength of random deviations.
    :param max_step: Maximum pixel distance per step.
    :param target_area: Radius around target where movement decelerates.
    :return: List of (x, y) integer coordinate tuples.
    """
    points = []
    current_x, current_y = float(start_x), float(start_y)
    wind_x, wind_y = 0.0, 0.0

    while True:
        dx = end_x - current_x
        dy = end_y - current_y
        dist = math.hypot(dx, dy)

        if dist < 1:
            break

        # Wind: random force, stronger far from target, weaker near it
        wind_mag = min(wind, dist)
        if dist >= target_area:
            wind_x = wind_x / math.sqrt(3) + (random.random() * 2 - 1) * wind_mag / math.sqrt(5)
            wind_y = wind_y / math.sqrt(3) + (random.random() * 2 - 1) * wind_mag / math.sqrt(5)
        else:
            wind_x /= math.sqrt(3)
            wind_y /= math.sqrt(3)

        # Gravity: pull toward target
        grav_x = gravity * dx / dist
        grav_y = gravity * dy / dist

        # Velocity
        vx = grav_x + wind_x
        vy = grav_y + wind_y

        # Clamp step size
        speed = math.hypot(vx, vy)
        if speed > max_step:
            scale = max_step / speed
            vx *= scale
            vy *= scale

        # Near the target, reduce step size proportionally
        if dist < target_area:
            step_scale = dist / target_area
            vx *= step_scale
            vy *= step_scale

        current_x += vx
        current_y += vy

        ix, iy = int(round(current_x)), int(round(current_y))
        if not points or points[-1] != (ix, iy):
            points.append((ix, iy))

    # Ensure the final point is exactly the target
    final = (int(round(end_x)), int(round(end_y)))
    if not points or points[-1] != final:
        points.append(final)

    return points


def _apply_overshoot(end_x: int, end_y: int) -> tuple[int, int]:
    """With some probability, overshoot the target slightly.

    :return: The overshoot point (may equal the original target).
    """
    if random.random() < OVERSHOOT_CHANCE:
        angle = random.uniform(0, 2 * math.pi)
        magnitude = random.randint(OVERSHOOT_MIN, OVERSHOOT_MAX)
        return (
            end_x + int(magnitude * math.cos(angle)),
            end_y + int(magnitude * math.sin(angle)),
        )
    return end_x, end_y


def _add_click_offset(x: int, y: int) -> tuple[int, int]:
    """Add a small random offset to click coordinates."""
    return (
        x + random.randint(-CLICK_OFFSET, CLICK_OFFSET),
        y + random.randint(-CLICK_OFFSET, CLICK_OFFSET),
    )


def _resolve_coords(x=None, y=None) -> tuple[int, int]:
    """Resolve coordinates from (x, y), a Box, or current cursor position.

    Accepts:
    - human_move_to(box)        — Box object as first arg
    - human_move_to(x, y)       — explicit coordinates
    - human_move_to()           — current cursor position
    """
    if x is None and y is None:
        pos = pag.position()
        return int(pos[0]), int(pos[1])
    if isinstance(x, Box):
        return utils.get_box_center_integers(x)
    if isinstance(x, (tuple, list)) and len(x) >= 2:
        return int(x[0]), int(x[1])
    return int(x), int(y)


def human_move_to(x=None, y=None) -> None:
    """Move the mouse cursor to (x, y) along a human-like path.

    :param x: Target X coordinate, a Box, a tuple, or None for current pos.
    :param y: Target Y coordinate (ignored if x is a Box/tuple).
    """
    end_x, end_y = _resolve_coords(x, y)
    start = pag.position()
    start_x, start_y = int(start[0]), int(start[1])

    dist = math.hypot(end_x - start_x, end_y - start_y)

    if dist < 1:
        return

    # Short distance: simple linear interpolation
    if dist < SHORT_DISTANCE:
        steps = max(3, int(dist / 3))
        for i in range(1, steps + 1):
            t = i / steps
            ix = int(start_x + (end_x - start_x) * t)
            iy = int(start_y + (end_y - start_y) * t)
            _set_cursor_pos(ix, iy)
            time.sleep(random.uniform(MIN_WAIT, MAX_WAIT))
        return

    # Overshoot: move past the target, then correct
    overshoot_x, overshoot_y = _apply_overshoot(end_x, end_y)

    if (overshoot_x, overshoot_y) != (end_x, end_y):
        # Move to overshoot point
        points = _wind_mouse(start_x, start_y, overshoot_x, overshoot_y)
        for px, py in points:
            _set_cursor_pos(px, py)
            time.sleep(random.uniform(MIN_WAIT, MAX_WAIT))
        # Correct to actual target
        correction = _wind_mouse(overshoot_x, overshoot_y, end_x, end_y,
                                 gravity=GRAVITY * 1.5, wind=WIND * 0.3,
                                 max_step=MAX_STEP * 0.7)
        for px, py in correction:
            _set_cursor_pos(px, py)
            time.sleep(random.uniform(MIN_WAIT, MAX_WAIT))
    else:
        points = _wind_mouse(start_x, start_y, end_x, end_y)
        for px, py in points:
            _set_cursor_pos(px, py)
            time.sleep(random.uniform(MIN_WAIT, MAX_WAIT))


def human_click(x=None, y=None) -> None:
    """Move to (x, y) with human-like movement, then click realistically.

    Uses mouseDown/mouseUp with a random hold duration instead of instant click.

    :param x: Target X coordinate, a Box, a tuple, or None for current pos.
    :param y: Target Y coordinate (ignored if x is a Box/tuple).
    """
    end_x, end_y = _resolve_coords(x, y)
    click_x, click_y = _add_click_offset(end_x, end_y)

    human_move_to(click_x, click_y)

    # Realistic click: press, hold briefly, release
    pag.mouseDown()
    time.sleep(random.uniform(CLICK_HOLD_MIN, CLICK_HOLD_MAX))
    pag.mouseUp()
