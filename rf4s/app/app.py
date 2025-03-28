"""Default App class for other tools.

This module provides a default App class for tools like item crafting and baits.
It initializes the configuration with a dummy profile and parses args.
#TODO

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""
from pathlib import Path

from rich.table import Table
from yacs.config import CfgNode as CN

from rf4s.config import config
from rf4s.controller.window import Window

ROOT = Path(__file__).resolve().parents[2]

class App:
    def __init__(self):
        self.cfg = config.setup_cfg()
        self.cfg.merge_from_file(ROOT / "config.yaml")
        args = self._parse_args()
        args_cfg = CN({"ARGS": config.dict_to_cfg(vars(args))})
        self.cfg.merge_from_other_cfg(args_cfg)
        self.cfg.merge_from_list(args.opts)

        # Dummy node
        dummy = CN({"SELECTED": config.dict_to_cfg({"MODE": "spin"})})
        self.cfg.merge_from_other_cfg(dummy)
        self.cfg.freeze()

        self.window = Window()

    def _parse_args(self):
        raise NotImplementedError("parse_args method must be implemented in subclass")

    def _start(self):
        raise NotImplementedError("_start method must be implemented in subclass")

    def start(self, results: tuple[tuple[str, str]]=()) -> None:
        """A wrapper for confirmation, window activation, and start.

        :param app: Main application class.
        :type app: object
        :param results: Counter lookup table.
        :type results: tuple[tuple[str, str]] | None
        """
        self.window.activate_game_window()
        try:
            self.start()
        except KeyboardInterrupt:
            pass
        if results:
            self._print_results(results)
        self.window.activate_script_window()

    def _print_results(self, results: tuple[tuple[str, str]]) -> None:
        """Display the running results of different apps.

        :param results: Attribute name - column name mapping.
        :type results: tuple[tuple[str, str]]
        """
        table = Table(
            "Results",
            title="Running Results",
            show_header=False,
            # min_width=20,
        )
        table.title = "Running Results"
        for field_name, attribute_name in results:
            table.add_row(field_name, getattr(self, attribute_name))
        print(table)