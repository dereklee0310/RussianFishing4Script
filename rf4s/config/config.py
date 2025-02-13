import argparse
import logging
import sys
from pathlib import Path

import yaml
from yacs.config import CfgNode as CN

from rf4s.config.defaults import get_cfg_defaults

logger = logging.getLogger("rich")

def setup_cfg() -> CN:
    cfg = get_cfg_defaults()
    cfg.set_new_allowed(True)
    return cfg.clone()

def dict_to_cfg(args):
    cfg = CN()
    for k, v in args.items():
        k = k.upper()
        if isinstance(v, dict):
            cfg[k] = dict_to_cfg(v)
        else:
            cfg[k] = v
    return cfg

def print_cfg(cfg, level: int=0):
    cfg = dict(cfg)
    indent = "  " * level if level > 0 else ""
    for k, v in cfg.items():
        if isinstance(v, CN):
            print(f"{indent}{k}:")
            print_cfg(v, level + 1)
        else:
            print(f"{indent}{k}: {v}")

def to_list(profile):
    pairs = []
    for k, v in profile.items():
        pairs.extend([k, v])
    return pairs