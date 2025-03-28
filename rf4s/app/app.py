"""Base application class for other tools.

Provides core functionality for:
- Configuration management
- Window control
- Result display

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

from pathlib import Path

from rich import print
from rich.table import Table
from yacs.config import CfgNode as CN

from rf4s.config import config
from rf4s.controller.window import Window

ROOT = Path(__file__).resolve().parents[2]


class App:
    """Main application class providing configuration setup, window management,
    and result display functionality.

    This class serves as a base for specialized tools. Subclasses must implement
    `_parse_args()` and `_start()` methods.

    Attributes:
        cfg (yacs.config.CfgNode): Merged configuration from defaults, config file,
            CLI arguments, and runtime options (frozen after initialization).
        window (rf4s.controller.window.Window): Window management controller.
    """
    def __init__(self):
        """Initialize application configuration and window controller.

        Configuration is built from:
        1. Default configuration
        2. config.yaml file
        3. Command-line arguments (via subclass implementation)
        4. Runtime options

        Raises:
            NotImplementedError: If subclass does not implement `_parse_args()`
        """
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

    def start(self, results: tuple[tuple[str, str]] = ()) -> None:
        """Wrapper method for _start() that handle window activation and result display.

        :param results: (field name, attribute name) pairs
        :type results: tuple[tuple[str, str]], optional
        """
        self.window.activate_game_window()
        try:
            self._start()
        except KeyboardInterrupt:
            pass
        if results:
            self._print_results(results)
        self.window.activate_script_window()

    def _print_results(self, results: tuple[tuple[str, str]]) -> None:
        """Display the running results in a table format.

        :param results: (field name, attribute name) pairs
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
            table.add_row(field_name, str(getattr(self, attribute_name)))
        print(table)
