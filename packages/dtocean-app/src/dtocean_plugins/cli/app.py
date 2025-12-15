from dtocean_app import main_
from dtocean_app.utils.config import init_config
from dtocean_plugins.cli.shared import SmartFormatter


def subcommand(subparser):
    description = "Subcommands for the dtocean-app module"
    parser = subparser.add_parser(
        "app",
        description=description,
        help="run or configure the DTOcean graphical application",
    )
    _setup_app(parser)

    sp = parser.add_subparsers()
    _setup_config(sp)


def _setup_app(subparser):
    """Command line interface for dtocean-app.

    Example:

        For help::

            $ dtocean app -h

    """

    subparser.add_argument(
        "--debug", help=("disable stream redirection"), action="store_true"
    )

    subparser.add_argument(
        "--trace-warnings",
        help=("add stack trace to warnings"),
        action="store_true",
    )

    subparser.add_argument(
        "--quit", help=("quit before interface opens"), action="store_true"
    )

    subparser.set_defaults(
        func=lambda args: main_(
            debug=args.debug,
            trace_warnings=args.trace_warnings,
            force_quit=args.quit,
        )
    )


def _setup_config(subparser):
    """Command line parser for init_config.

    Example:

        To get help::

            $ dtocean app config -h

    """

    desStr = (
        "Copy user modifiable configuration files to "
        r"<UserName>\AppData\Roaming\DTOcean\dtocean-app\config"
    )

    parser = subparser.add_parser(
        "config",
        description=desStr,
        help="copy config files",
        formatter_class=SmartFormatter,
    )

    parser.add_argument(
        "action",
        choices=["logging"],
        help="R|Select an action, where\n"
        " logging = copy logging configuration\n",
    )

    parser.add_argument(
        "--overwrite",
        help=("overwrite any existing configuration files"),
        action="store_true",
    )

    parser.set_defaults(func=lambda args: _config(args))


def _config(args):
    action = args.action
    overwrite = args.overwrite

    kwargs = {
        "logging": False,
        "overwrite": overwrite,
    }

    kwargs[action] = True
    dir_path = init_config(**kwargs)

    if dir_path is not None:
        print("Copying configuration files to {}".format(dir_path))
