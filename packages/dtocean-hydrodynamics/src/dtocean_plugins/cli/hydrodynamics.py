from dtocean_hydro.configure import get_data
from dtocean_wec import run


def init(args):
    get_data(args.force)


def subcommand(subparser):
    description = "Subcommands for the dtocean-hydrodynamics module"
    parser = subparser.add_parser(
        "hydrodynamics",
        description=description,
        help="dtocean-hydrodynamics commands",
    )
    sp = parser.add_subparsers(required=True)
    _setup_wec(sp)


def _setup_wec(subparser):
    """Command line interface for dtocean WEC pre-processor.

    Example:

        To get help::

            $ dtocean hydrodynamics wec -h

    """

    desStr = "Run the WEC pre-processor GUI."
    parser = subparser.add_parser("wec", description=desStr, help=desStr)
    parser.set_defaults(func=lambda _: run())
