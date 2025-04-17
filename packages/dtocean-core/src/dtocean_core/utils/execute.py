# -*- coding: utf-8 -*-

#    Copyright (C) 2021-2024 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import time
import traceback
import warnings
from pathlib import Path
from typing import Union

from .. import start_logging
from ..core import Core
from ..extensions import StrategyManager
from ..menu import ModuleMenu

StrOrPath = Union[str, Path]


def warn_with_traceback(
    message, category, filename, lineno, logfile=None, line=None
):
    log = logfile if hasattr(logfile, "write") else sys.stderr
    traceback.print_stack(file=log)

    assert log is not None
    log.write(warnings.formatwarning(message, category, filename, lineno, line))


def main(
    fpath,
    save: Union[bool, StrOrPath] = True,
    full=False,
    warn=False,
    log=False,
):
    if full:
        action_str = "all scheduled modules"
    else:
        action_str = "next scheduled module"

    msg_str = "\n>>> Executing {} in project '{}'".format(action_str, fpath)
    extra_string = ""

    if warn:
        extra_string += "warning tracebacks"

    if log:
        if extra_string:
            extra_string += " and "
        extra_string += "logging"

    if extra_string:
        msg_str = "{} with {}".format(msg_str, extra_string)

    msg_str += "\n"
    print(msg_str)

    if warn:
        warnings.showwarning = warn_with_traceback

    if log:
        start_logging()

    my_core = Core()
    my_project = my_core.load_project(fpath)

    if full:
        strategy_manager = StrategyManager()
        basic_strategy = strategy_manager.get_strategy("Basic")

        start_time = time.time()
        basic_strategy.execute(my_core, my_project)

    else:
        my_menu = ModuleMenu()

        start_time = time.time()
        my_menu.execute_current(my_core, my_project)

    msg_str = "\n>>> Execution time: {}s".format(time.time() - start_time)
    print(msg_str)

    if not save:
        return

    if save is True:
        prepath, ext = os.path.splitext(fpath)
        save_path = "{}_complete{}".format(prepath, ext)
    else:
        save_path = save

    msg_str = "\n>>> Saving project to: {}".format(save_path)
    print(msg_str)

    my_core.dump_project(my_project, save_path)
