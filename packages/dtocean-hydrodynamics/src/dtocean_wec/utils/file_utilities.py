# -*- coding: utf-8 -*-
import os
import shutil
import sys
from typing import Any, Callable, Optional


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


def query_yes_no(question):
    # query the user on the terminal for a y or n answer
    sys.stdout.write("%s [y/n]\n" % question)
    while True:
        try:
            return strtobool(input().lower())
        except ValueError:
            sys.stdout.write("Please respond with 'y' or 'n'.\n")


def copy_result_to_project(source, destination, file_fl=False):
    src_st = os.path.join(source, "hydrostatic")
    src_dy = os.path.join(source, "hydrodynamic")
    dst_st = os.path.join(destination, "hydrostatic")
    dst_dy = os.path.join(destination, "hydrodynamic")

    try:
        shutil.copytree(src_st, dst_st)
        shutil.copytree(src_dy, dst_dy)
    except Exception as e:
        return (False, e)

    return (True, "")


def clean_prj_folder(path, exept=None):
    # remove all files and subfolders from the project folder
    folder_ls = os.listdir(path)
    if exept is not None:
        folder_ls = [el for el in folder_ls if el != exept]

    for el in folder_ls:
        el_path = os.path.join(path, el)
        try:
            if os.path.isfile(el_path):
                os.unlink(el_path)
            elif os.path.isdir(el_path):
                shutil.rmtree(el_path)
        except Exception as e:
            return (False, e)

    return (True, "")


def split_string_multilist(string, num_type=float, sep=",", sep_multi=";"):
    list_el = string.split(sep_multi)
    return [split_string(el, num_type=num_type, sep=sep) for el in list_el]


def split_string[T](
    string: str,
    num_type: Callable[[Any], T] = float,
    sep: Optional[str] = " ",
) -> list[T]:
    def convert(x: str):
        try:
            result = num_type(x)
        except Exception:
            result = None

        return result

    list_el = string.split(sep)
    result: list[T] = []

    for el in list_el:
        converted = convert(el)
        if converted is None:
            continue
        result.append(converted)

    return result


def load_file(path, file_name):
    """
    the method is case sensitive, it distinguishes from capital and lower size letters
    :param path:
    :param file_name:
    :return:
    """
    check_file_name = [el for el in os.listdir(path) if el == file_name]
    if not check_file_name:
        raise NameError(
            "The specified filename ({}) does not exist in the "
            "folder {}".format(file_name, path)
        )
    elif (
        len(check_file_name) > 1
    ):  # this cndition cannot exist, just keep it here in case the comparison is bugged
        raise ValueError(
            "The specified filename ({}) exists in multiple copies in the "
            "folder {}. ".format(file_name, path),
            "Remove the unused files",
        )

    with open(os.path.join(path, file_name)) as fid:
        lines = fid.readlines()

    return lines
