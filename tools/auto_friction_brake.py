sys.path.append(".")
import argparse
import sys
from multiprocessing import Lock

from pynput import keyboard

from rf4s import utils
from rf4s.component.friction_brake import FrictionBrake

ARGS = ()
EXIT = "'h'"
RESET = "'g'"

class App:
    """Main application class."""

    @utils.initialize_setting_and_monitor(ARGS)
    def __init__(self):
        self.setting.fishing_strategy = None
        if not utils.verify_window_size(self.setting):
            sys.exit()

        self.setting.set_absolute_coords()
        self.friction_brake_lock = Lock() # dummy lock
        self.friction_brake = FrictionBrake(
            self.setting, self.monitor, self.friction_brake_lock
        )

    def parse_args(self):
        parser = argparse.ArgumentParser(description="Automate the friction brake.")
        return parser.parse_args()

    def on_release(self, key: keyboard.KeyCode) -> None:
        """Callback for releasing button, including w key toggle control.

        :param key: key code used by OS
        :type key: keyboard.KeyCode
        """
        keystroke = str(key).lower()
        if keystroke == EXIT:
            self.friction_brake.monitor_process.terminate()
            sys.exit()
        if keystroke == RESET:
            self.friction_brake.reset(self.setting.initial_friction_brake)

    def start(self):
        self.friction_brake.monitor_process.start()
        with keyboard.Listener(on_release=self.on_release) as listener:
            listener.join()


if __name__ == "__main__":
    app = App()
    utils.start_app(app, None)