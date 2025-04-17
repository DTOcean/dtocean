import os
from typing import Any

from dtocean_core.utils.database import (
    MIN_DB_VERSION,
    database_from_files,
    database_to_files,
    draw_map,
    filter_map,
    get_database,
    get_database_config,
    get_table_map,
)

from .shared import SmartFormatter


def subcommand(subparser):
    desStr = "Convert DTOcean database to and from structured files"
    parser = subparser.add_parser(
        "database",
        description=desStr,
        formatter_class=SmartFormatter,
    )
    _setup_database(parser)


def _setup_database(parser):
    parser.add_argument(
        "action",
        choices=["dump", "load", "list", "view", "dir"],
        help="R|Select an action, where\n"
        " dump = export database to files\n"
        " load = import files into database\n"
        " list = print stored credentials identifiers\n"
        " view = print stored credentials (using -i "
        "option)\n"
        "  dir = print table structure",
    )

    parser.add_argument(
        "-d",
        "--directory",
        help=("directory to add or read files from. " "Defaults to '.'"),
        type=str,
        default=".",
    )

    parser.add_argument(
        "-s",
        "--section",
        choices=["device", "site", "other"],
        help="R|Only operate on section from\n"
        " device = tables related to the OEC\n"
        " site = tables related to the deployment site\n"
        " other = tables related to the reference data",
    )

    parser.add_argument(
        "-i", "--identifier", help=("stored credentials identifier"), type=str
    )

    parser.add_argument("--host", help=("override database host"), type=str)

    parser.add_argument("--name", help=("override database name"), type=str)

    parser.add_argument("--user", help=("override database username"), type=str)

    parser.add_argument(
        "-p", "--pwd", help=("override database password"), type=str
    )

    parser.set_defaults(func=lambda args: _database(args))


def _database(args):
    """Command line interface for database_to_files and database_from_files.

    Example:

        To get help::

            $ dtocean-database -h

    """

    cred: dict[str, Any]
    _, config = get_database_config()

    request = {
        "action": args.action,
        "root_path": args.directory,
        "filter_table": args.section,
        "db_id": args.identifier,
        "db_host": args.host,
        "db_name": args.name,
        "db_user": args.user,
        "db_pwd": args.pwd,
    }

    # List the available database configurations
    if request["action"] == "list":
        id_str = ", ".join(config.keys())

        if id_str:
            msg_str = (
                "Available database configuration identifiers are: " "{}"
            ).format(id_str)
        else:
            msg_str = "No database configurations are stored"

        print(msg_str)

        return

    if request["action"] == "view":
        if request["db_id"] is None:
            err_msg = "Option '-i' must be specified with 'view' action"
            raise ValueError(err_msg)

        cred = config[request["db_id"]]

        for k, v in cred.items():
            print("{:>8} ::  {}".format(k, v))

        return

    table_list = get_table_map()

    # Filter the table if required
    if request["filter_table"] is not None:
        filtered_dict = filter_map(table_list, request["filter_table"])
        table_list = [filtered_dict]

    if request["action"] == "dir":
        print("\n" + draw_map(table_list))
        return

    # Set up the DB
    if request["db_id"] is not None:
        cred = config[request["db_id"]]
    else:
        cred = {"host": None, "dbname": None, "user": None, "pwd": None}

    if request["db_host"] is not None:
        cred["host"] = request["db_host"]

    if request["db_name"] is not None:
        cred["dbname"] = request["db_name"]

    if request["db_user"] is not None:
        cred["user"] = request["db_user"]

    if request["db_pwd"] is not None:
        cred["pwd"] = "postgres"

    db = get_database(cred, timeout=60, min_version=MIN_DB_VERSION)

    if request["action"] == "dump":
        # make a directory if required
        if not os.path.exists(request["root_path"]):
            os.makedirs(request["root_path"])

        database_to_files(
            request["root_path"],
            table_list,
            db,
            print_function=print,
        )

        return

    if request["action"] == "load":
        database_from_files(
            request["root_path"],
            table_list,
            db,
            print_function=print,
        )

        return

    raise RuntimeError("Highly illogical...")
