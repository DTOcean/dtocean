import glob
import os
import platform
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parents[1]
BUILD_DIR = ROOT_DIR.joinpath("build")
BUILD_ENV = {
    **os.environ.copy(),
    "FC": "gfortran",
    "CC": "gcc",
}
GENERATED_DIR = ROOT_DIR.joinpath(
    "src",
    "dtocean_wec",
    "generated",
)
LIB_DIR = ROOT_DIR.joinpath(
    "src",
    "dtocean_tidal",
    "submodel",
    "ParametricWake",
)
UI_DIR = ROOT_DIR.joinpath(
    "src",
    "dtocean_wec",
    "designer",
)
WINDOWS_DLLS = [
    "libquadmath-*.dll",
    "libwinpthread-*.dll",
    "libgcc_s_seh-*.dll",
    "libgfortran-*.dll",
]


def _is_windows():
    """Return True if the current platform is Windows."""
    return platform.system() == "Windows"


def _meson(*args):
    """Invoke meson with the given arguments."""
    subprocess.run(["meson", *list(args)], check=True, env=BUILD_ENV)


def _pyside6_uic(*args):
    """Invoke pyside6-uic with the given arguments."""
    subprocess.run(["pyside6-uic", *list(args)], check=True)


def _cleanup():
    """Remove build artifacts."""
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    # qt widgets
    files = list(GENERATED_DIR.glob("ui_*.py"))

    # fortran module
    if _is_windows():
        files += (
            list(LIB_DIR.glob("*.pyd"))
            + list(LIB_DIR.glob("*.dll"))
            + list(LIB_DIR.glob("*.a"))
        )
    else:
        files += list(LIB_DIR.glob("*.so"))

    for file in files:
        file.unlink()


def build():
    """Build the project."""
    _cleanup()

    # qt widgets
    for ui_path in UI_DIR.glob("*.ui"):
        dst = GENERATED_DIR / f"ui_{ui_path.stem}.py"
        _pyside6_uic(str(ui_path), "-o", str(dst))

    # fortran module
    _meson("setup", BUILD_DIR.as_posix())
    _meson("compile", "-C", BUILD_DIR.as_posix())
    _meson("install", "-C", BUILD_DIR.as_posix())

    if not _is_windows():
        return

    find_gfortran = shutil.which("gfortran")
    assert find_gfortran is not None
    gfortran_path = Path(find_gfortran).parent

    for dll_name in WINDOWS_DLLS:
        dll_path = gfortran_path / dll_name
        for file in glob.glob(str(dll_path)):
            print(f"Installing {Path(file).name} to {LIB_DIR.as_posix()}")
            shutil.copy(file, LIB_DIR)


if __name__ == "__main__":
    build()
