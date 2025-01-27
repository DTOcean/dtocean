import argparse
from typing import TypeAlias

from .configure import get_data

SubParsers: TypeAlias = "argparse._SubParsersAction[argparse.ArgumentParser]"


def run():
    parser = argparse.ArgumentParser(prog="dtocean-hydro")
    subparsers = parser.add_subparsers(help="sub-command help", required=True)

    _setup_init(subparsers)

    args = parser.parse_args()
    args.func(args)


def _setup_init(subparsers: SubParsers):
    parser = subparsers.add_parser("init", help="download external files")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite files",
    )
    parser.set_defaults(func=lambda args: get_data(args.force))
