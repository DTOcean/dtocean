import subprocess
from collections.abc import Callable
from pathlib import Path

ROOT_DIR = Path(__file__).parents[1]
GENERATED_DIR = ROOT_DIR / "src" / "dtocean_app" / "designer"


def _pyside6_rcc(*args):
    """Invoke pyside6-rcc with the given arguments."""
    subprocess.run(["pyside6-rcc", *list(args)], check=True)


def _pyside6_uic(*args):
    """Invoke pyside6-uic with the given arguments."""
    subprocess.run(["pyside6-uic", *list(args)], check=True)


def _cleanup():
    for root, dirs, files in GENERATED_DIR.walk(top_down=False):
        for name in files:
            (root / name).unlink()
        for name in dirs:
            (root / name).rmdir()


def build():
    """Build the project."""

    def _build_pyside6(
        search_path: Path,
        search_pattern: str,
        dst_dir: Path,
        suffix: str,
        command: Callable,
    ):
        dst_dir.mkdir(parents=True, exist_ok=True)

        for ui_path in search_path.glob(search_pattern):
            file_root = Path(ui_path).stem
            dst_str = str(dst_dir / file_root) + suffix

            # Convert the files
            print("create file: {}".format(dst_str))
            command(str(ui_path), "-o", str(dst_str))

    _cleanup()

    shared_ui_search_path = ROOT_DIR / "designer" / "shared"
    qrc_search_path = ROOT_DIR / "designer"

    # Low DPI
    dst_dir = GENERATED_DIR / "low"
    ui_search_path = ROOT_DIR / "designer" / "low"

    _build_pyside6(ui_search_path, "*.ui", dst_dir, ".py", _pyside6_uic)
    _build_pyside6(shared_ui_search_path, "*.ui", dst_dir, ".py", _pyside6_uic)
    _build_pyside6(qrc_search_path, "*.qrc", dst_dir, "_rc.py", _pyside6_rcc)

    # High DPI
    dst_dir = GENERATED_DIR / "high"
    ui_search_path = ROOT_DIR / "designer" / "high"

    _build_pyside6(ui_search_path, "*.ui", dst_dir, ".py", _pyside6_uic)
    _build_pyside6(shared_ui_search_path, "*.ui", dst_dir, ".py", _pyside6_uic)
    _build_pyside6(qrc_search_path, "*.qrc", dst_dir, "_rc.py", _pyside6_rcc)


if __name__ == "__main__":
    build()
