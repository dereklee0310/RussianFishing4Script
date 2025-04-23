"""Base application class for other tools.

Provides core functionality for:
- Configuration management
- Window control
- Result display

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import os
import signal
import sys
from pathlib import Path
from abc import ABC, abstractmethod

from pynput import keyboard
from rich import print
from rich.table import Table
from yacs.config import CfgNode as CN

from rf4s.config import config
from rf4s.controller.detection import Detection
from rf4s.controller.window import Window

ROOT = Path(__file__).resolve().parents[2]


class App(ABC):
    """A base application class.

    Attributes:
        cfg (yacs.config.CfgNode): Default + user's configuration file
        window (Window): Window controller
    """

    def __init__(self):
        """Initialize a mutable cfg node for further modification."""
        self.cfg = config.setup_cfg()
        self.cfg.merge_from_file(ROOT / "config.yaml")
        self.window = Window()

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Monitor user's keystrokes and convert a key press to a CTRL_C_EVENT.

        :param key: The key that was released.
        :type key: keyboard.KeyCode

        Exits the application when the configured quit key is pressed.
        """
        # Trigger CTRL_C_EVENT, which will be caught in start() to simulate pressing
        # CTRL-C to terminate the script.
        if key == keyboard.KeyCode.from_char(self.cfg.KEY.QUIT):
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            sys.exit()

    @abstractmethod
    def _start(self):
        raise NotImplementedError("_start() must be implemented in subclass")

    @abstractmethod
    def start(self):
        raise NotImplementedError("start() must be implemented in subclass")

    @abstractmethod
    def create_parser(self):
        raise NotImplementedError("create_parser() must be implemented in subclass")

    @abstractmethod
    def display_results(self) -> None:
        raise NotImplementedError("display_result() must be implemented in subclass")


class ToolApp(App):
    """General application class for other tools.

    Attributes:
        detection (Detection): Detection controller
        results (dict): Running results
    """

    def __init__(self):
        """Set up an immutable cfg node for further modification.

        1. Parse command-line arguments and merge them with the existing cfg node.
        2. Create a Window instance and a Detection instance.
        3. Create an empty dictionary for results
        """
        super().__init__()
        args = self.create_parser().parse_args()
        args_cfg = CN({"ARGS": config.dict_to_cfg(vars(args))})
        self.cfg.merge_from_other_cfg(args_cfg)
        self.cfg.merge_from_list(args.opts)

        # Dummy node
        dummy = CN({"SELECTED": config.dict_to_cfg({"MODE": "spin"})})
        self.cfg.merge_from_other_cfg(dummy)
        self.cfg.freeze()

        self.detection = Detection(self.cfg, self.window)
        self.results = {}  # This will be used in display_results()

    def display_results(self) -> None:
        """Display the running results in a table format."""
        table = Table("Results", title="Running Results", show_header=False)
        for name, value in self.results.items():
            table.add_row(name, str(value))
        print(table)

    def start(self) -> None:
        """Wrapper method that handle window activation and result display."""
        if self.cfg.KEY.QUIT != "CTRL-C":
            listener = keyboard.Listener(on_release=self._on_release)
            listener.start()

        self.window.activate_game_window()
        try:
            self._start()
        except KeyboardInterrupt:
            pass
        if self.results:
            self.display_results()
        self.window.activate_script_window()
