"""
Usage: main.py [-h] [-c FILE] ...

Main entry point.
"""

import argparse
import logging
import yaml
from yacs.config import CfgNode

from config.defaults import get_cfg_defaults

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_args() -> argparse.Namespace:
    """Parse command line arguments.

    :return: dict-like object
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="Foo."
    )
    parser.add_argument(
        "-c", "--config-file", metavar="FILE", help="path to config file"
    )
    parser.add_argument(
        "opts",
        help="Modify config options using the command-line",
        default=None,
        nargs=argparse.REMAINDER,
    )
    return parser.parse_args()


def setup_cfg(args: argparse.Namespace) -> CfgNode:
    """Merge args into cfg node.

    :param args: dict-like object
    :type args: argparse.Namespace
    :return: config
    :rtype: CfgNode
    """
    cfg = get_cfg_defaults()
    if args.config_file is not None:
        cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    return cfg.clone()


def main():
    """Main function."""
    c = setup_cfg(get_args())
    print(c)

if __name__ == "__main__":
    main()
