import glob
import platform
import shutil
import subprocess
from pathlib import Path

BUILD_DIR = Path(__file__).parent.joinpath("build")
LIB_DIR = Path(__file__).parent.joinpath(
    "src",
    "dtocean_tidal",
    "submodel",
    "ParametricWake",
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
    subprocess.check_call(["meson", *list(args)])


def _cleanup():
    """Remove build artifacts."""
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    if _is_windows():
        files = (
            list(LIB_DIR.glob("*.pyd"))
            + list(LIB_DIR.glob("*.dll"))
            + list(LIB_DIR.glob("*.a"))
        )
    else:
        files = list(LIB_DIR.glob("*.so"))

    for file in files:
        file.unlink()


def build():
    """Build the project."""
    _cleanup()

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
            shutil.copy(file, LIB_DIR)


if __name__ == "__main__":
    build()
