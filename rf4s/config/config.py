"""
Configuration module for managing and manipulating configuration settings.

This module provides utilities for setting up, converting, and printing
configuration nodes using the YACS library.
"""

import sys
from pathlib import Path

from yacs.config import CfgNode as CN

from rf4s import config, utils
import re
import yaml

# Get the base path depending on runtime environment
if utils.is_compiled():
    OUTER_ROOT = Path(sys.executable).parent  # Running as .exe (Nuitka/PyInstaller)
else:
    OUTER_ROOT = Path(__file__).resolve().parents[2]


def setup_cfg() -> CN:
    """
    Set up and return a default configuration node.

    This function initializes a default configuration node and allows new keys
    to be added to the configuration.

    :return: A cloned configuration node with default settings.
    :rtype: CN
    """
    cfg = config.get_cfg_defaults()
    cfg.set_new_allowed(True)
    return cfg.clone()


def dict_to_cfg(args: dict) -> CN:
    """
    Convert a dictionary to a configuration node.

    This function recursively converts a dictionary into a configuration node,
    allowing nested dictionaries to be converted into nested configuration nodes.

    :param args: Dictionary to be converted into a configuration node.
    :type args: dict
    :return: Configuration node created from the dictionary.
    :rtype: CN
    """
    cfg = CN()
    for k, v in args.items():
        k = k.upper()
        if isinstance(v, dict):
            cfg[k] = dict_to_cfg(v)
        else:
            cfg[k] = v
    return cfg


def dump_cfg(cfg: CN, level: int = 0, result: list | None = None) -> str | None:
    """
    Print the configuration node in a readable format.

    This function recursively prints the configuration node, with indentation
    to represent nested levels.

    :param cfg: Configuration node to be printed.
    :type cfg: CN
    :param level: Current indentation level (used for recursion).
    :type level: int
    """
    # Two-space indentation style
    if result is None:
        result = []
    indent = "  " * level if level > 0 else ""
    for k, v in dict(cfg).items():
        if isinstance(v, CN):
            result.append(f"{indent}{k}:\n")
            dump_cfg(v, level + 1, result)
        else:
            result.append(f"{indent}{k}: {v}\n")
    if level == 0:
        return "".join(result)[:-1]
    return None

    # Two-Space separated style
    # Need to add a newline manually
    # for k, v in dict(cfg).items():
    #     if isinstance(v, CN):
    #         print(f"{k}:", end=" ")
    #         print_cfg(v, level + 1)
    #     else:
    #         print(f"{k}: {v}", end=" ")


def to_list(profile: dict) -> list:
    """
    Convert a dictionary into a flat list of key-value pairs.

    This function flattens a dictionary into a list where keys and values
    are alternated.

    :param profile: Dictionary to be converted into a list.
    :type profile: dict
    :return: List containing alternating keys and values from the dictionary.
    :rtype: list
    """
    pairs = []
    for k, v in profile.items():
        pairs.extend([k, v])
    return pairs


def load_cfg() -> CN:
    cfg = setup_cfg()
    # Load YAML ourselves so we can preprocess "value +- tol" annotations
    config_path = OUTER_ROOT / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    # Collect tolerances in a parallel dict structure
    tol_dict = {}

    def _process_raw(node: dict, tol_node: dict):
        for k, v in list(node.items()):
            if isinstance(v, dict):
                child_tol = {}
                _process_raw(v, child_tol)
                if child_tol:
                    tol_node[k] = child_tol
            elif isinstance(v, str):
                #strings matching the "+-N" pattern (e.g., "6.0 +-5s" or "4.0 +-2.5%")
                m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*\+\-\s*([0-9]+(?:\.[0-9]+)?)(%?)\s*$", v)
                if m:
                    base = float(m.group(1))
                    tol_raw = float(m.group(2))
                    is_percent = bool(m.group(3))
                    node[k] = base
                    # Store tolerance as a dict with TYPE and VALUE so consumers
                    # can distinguish absolute vs percent tolerances.
                    if is_percent:
                        tol_node[k] = {"TYPE": "pct", "VALUE": tol_raw}
                    else:
                        # Default: absolute seconds
                        tol_node[k] = {"TYPE": "abs", "VALUE": tol_raw}

    if isinstance(raw, dict):
        _process_raw(raw, tol_dict)

    # Convert the processed raw dict to a CfgNode and merge
    if isinstance(raw, dict):
        loaded_cfg = dict_to_cfg(raw)
        cfg.merge_from_other_cfg(loaded_cfg)

    # Merge tolerances (as CN) into cfg.TOLERANCE
    if tol_dict:
        cfg.TOLERANCE = dict_to_cfg(tol_dict)

    return cfg
