import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parents[1]
UI_DIR = ROOT_DIR.joinpath("src", "dtocean_qt", "pandas", "views", "_ui")
QRC_PATH = UI_DIR / "icons.qrc"
RC_PATH = UI_DIR / "icons_rc.py"


def _pyside6_rcc(*args):
    """Invoke pyside6-rcc with the given arguments."""
    subprocess.run(["pyside6-rcc", *list(args)], check=True)


def _cleanup():
    # qt icon rc file
    if RC_PATH.is_file():
        RC_PATH.unlink()


def build():
    """Build the project."""
    _cleanup()

    # qt icons
    _pyside6_rcc(str(QRC_PATH), "-o", str(RC_PATH))


if __name__ == "__main__":
    build()
