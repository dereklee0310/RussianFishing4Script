"""Standalone test for BotApp._mouse_wiggle behavior.

This script runs three quick scenarios without requiring pytest:
- Wiggle should NOT run while paused.
- Wiggle SHOULD run when the game window is foreground and not paused.
- Wiggle should NOT run when the game window is not the foreground window.

It patches win32gui and HumanMouse.move_in_radius to avoid moving the real mouse and to count invocations.
Run with:
    python -u rf4s/tests/wiggle_test.py
"""
import threading
import time
import types
import sys
from pathlib import Path
from yacs.config import CfgNode as CN

# Ensure project root is on sys.path so this test can be executed as
# a standalone script (python rf4s/tests/wiggle_test.py) as well as a module
# (python -m rf4s.tests.wiggle_test).
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from rf4s.app.app import BotApp, HumanMouse
import win32gui
import pydirectinput as pdi


def make_bot(interval=0.05):
    bot = BotApp.__new__(BotApp)
    bot.paused = False
    bot._stop_event = threading.Event()
    cfg = CN()
    cfg.BOT = CN()
    cfg.BOT.MOUSE_WIGGLE = CN()
    cfg.BOT.MOUSE_WIGGLE.ENABLED = True
    cfg.BOT.MOUSE_WIGGLE.INTERVAL = interval
    cfg.BOT.MOUSE_WIGGLE.RADIUS = 80
    cfg.BOT.MOUSE_WIGGLE.MIN_DURATION = 0.01
    cfg.BOT.MOUSE_WIGGLE.MAX_DURATION = 0.5
    bot.cfg = cfg
    bot.window = types.SimpleNamespace(game_title="TestGame")
    return bot


def run_thread_and_wait(bot, run_time=0.25):
    t = threading.Thread(target=bot._mouse_wiggle, daemon=True)
    t.start()
    # wait a bit while the wiggle thread runs
    time.sleep(run_time)
    bot._stop_event.set()
    t.join(timeout=1)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Wiggle test")
    parser.add_argument("--visual", action="store_true", help="Allow real mouse movement for visual verification")
    parser.add_argument("--run", action="store_true", help="Run the wiggle loop like the main app (for duration seconds)")
    parser.add_argument("--duration", type=float, default=10.0, help="Duration in seconds to run in --run mode (default: 10)")
    args = parser.parse_args()

    original_find = win32gui.FindWindow
    original_fg = win32gui.GetForegroundWindow
    original_move = HumanMouse.move_in_radius

    results = []

    try:
        # Scenario 1: paused -> no moves
        bot = make_bot(interval=0.02)
        bot.paused = True

        # make FindWindow/GetForegroundWindow return same hwnd
        win32gui.FindWindow = lambda a, b: 123
        win32gui.GetForegroundWindow = lambda: 123

        called = []

        def fake_move(self, *args, **kwargs):
            print("[TEST] fake_move called")
            called.append(1)

        HumanMouse.move_in_radius = fake_move

        run_thread_and_wait(bot, run_time=0.15)
        results.append(("paused", len(called) == 0, len(called)))

        # Scenario 2: active & foreground -> moves occur
        bot = make_bot(interval=0.02)
        bot.paused = False
        called = []

        if args.visual:
            # wrap original move to print status and perform actual moves
            def visual_wrapper(self, *a, **k):
                print("[TEST] visual move start")
                original_move(self, *a, **k)
                print("[TEST] visual move end")

            HumanMouse.move_in_radius = visual_wrapper
        else:
            HumanMouse.move_in_radius = fake_move

        win32gui.FindWindow = lambda a, b: 123
        win32gui.GetForegroundWindow = lambda: 123

        run_thread_and_wait(bot, run_time=0.25)
        results.append(("foreground_match", len(called) > 0 or args.visual, len(called)))

        # Scenario 3: foreground mismatch -> no moves
        bot = make_bot(interval=0.02)
        bot.paused = False
        called = []
        HumanMouse.move_in_radius = fake_move
        win32gui.FindWindow = lambda a, b: 123
        win32gui.GetForegroundWindow = lambda: 456

        run_thread_and_wait(bot, run_time=0.15)
        results.append(("foreground_mismatch", len(called) == 0, len(called)))

    finally:
        # restore
        win32gui.FindWindow = original_find
        win32gui.GetForegroundWindow = original_fg
        HumanMouse.move_in_radius = original_move

    # Print results
    all_ok = True
    for name, ok, calls in results:
        status = "PASS" if ok else "FAIL"
        print(f"{name}: {status} (calls={calls})")
        if not ok:
            all_ok = False

    if not all_ok:
        sys.exit(2)


if __name__ == '__main__':
    # If run mode requested, run a single wiggle loop similar to the bot main loop
    import argparse as _arg
    _parser = _arg.ArgumentParser(add_help=False)
    _parser.add_argument("--run", action="store_true")
    _parser.add_argument("--duration", type=float, default=10.0)
    _parser.add_argument("--visual", action="store_true")
    _args, _rest = _parser.parse_known_args()
    if _args.run:
        print(f"Running wiggle loop for {_args.duration} seconds (visual={_args.visual})")
        # prepare a bot and run the wiggle loop
        bot = make_bot(interval=0.05)
        bot.paused = False

        original_find = win32gui.FindWindow
        original_fg = win32gui.GetForegroundWindow
        original_move = HumanMouse.move_in_radius

        try:
            win32gui.FindWindow = lambda a, b: 123
            win32gui.GetForegroundWindow = lambda: 123
            if _args.visual:
                # use real movement but wrap to print before/after positions for visibility
                def visual_wrapper(self, *a, **k):
                    pre = pdi.position()
                    print(f"[TEST] visual move start, pre_pos={pre}")
                    original_move(self, *a, **k)
                    post = pdi.position()
                    print(f"[TEST] visual move end, post_pos={post}")

                HumanMouse.move_in_radius = visual_wrapper
            else:
                # fake move prints a notice instead of moving
                def fake_move(self, *a, **k):
                    print("[TEST] fake_move called")
                HumanMouse.move_in_radius = fake_move

            # stop after duration seconds
            stopper = threading.Timer(_args.duration, lambda: bot._stop_event.set())
            stopper.start()
            try:
                bot._mouse_wiggle()
            except KeyboardInterrupt:
                bot._stop_event.set()
            stopper.cancel()
        finally:
            win32gui.FindWindow = original_find
            win32gui.GetForegroundWindow = original_fg
            HumanMouse.move_in_radius = original_move
        print("Wiggle run finished")
    else:
        main()
