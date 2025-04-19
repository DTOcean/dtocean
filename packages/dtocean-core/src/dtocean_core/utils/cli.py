import argparse
import datetime
import importlib
from inspect import getmembers, isfunction
from types import FunctionType, ModuleType

from mdo_engine.utilities.plugins import get_module_names_from_package

import dtocean_plugins.cli as cli


def main():
    now = datetime.datetime.now()
    epiStr = "The DTOcean Developers (c) {}.".format(now.year)

    parser = argparse.ArgumentParser(prog="dtocean", epilog=epiStr)
    subparser = parser.add_subparsers(required=True)
    setup_init(subparser)

    for subcommand in get_plugin_function("subcommand", cli):
        subcommand(subparser)

    args = parser.parse_args()
    args.func(args)


def setup_init(subparser):
    def run_inits(args):
        for f in get_plugin_function("init", cli):
            f(args)

    description = "initialize modules (requires internet connection)"
    parser = subparser.add_parser(
        "init",
        description=description,
        help=description,
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite existing files",
    )

    parser.set_defaults(func=run_inits)


def get_plugin_function(function_name: str, module: ModuleType):
    result: list[FunctionType] = []

    for name in get_module_names_from_package(module):
        mod = importlib.import_module(name)
        members = getmembers_dict(mod, isfunction)
        if function_name in members:
            result.append(members[function_name])

    return result


def getmembers_dict(mod: ModuleType, predicate=None):
    members = getmembers(mod, predicate=predicate)
    return {n: v for n, v in members}
