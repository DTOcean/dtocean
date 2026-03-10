import tarfile
import tempfile
import time
from contextlib import contextmanager
from http.client import HTTPException
from pathlib import Path
from typing import Any, Callable, Generator, Optional, Sequence, Union
from urllib.parse import urlparse
from urllib.request import urlopen
from zipfile import ZipFile

StrOrPath = Union[str, Path]


def extract_tar(
    src: StrOrPath,
    dst: StrOrPath,
    seconds_before_retry: Optional[Sequence[int]] = None,
    logger: Callable[[str], None] = print,
):
    dst_path = Path(dst)

    with (
        _resolve_src(src, seconds_before_retry, logger) as tg_path,
        tarfile.open(tg_path) as tar,
    ):
        dst_path.mkdir(exist_ok=True, parents=True)
        tar.extractall(path=dst_path, filter="tar")


def extract_zip(
    src: StrOrPath,
    dst: StrOrPath,
    seconds_before_retry: Optional[Sequence[int]] = None,
    logger: Callable[[str], None] = print,
):
    dst_path = Path(dst)

    with (
        _resolve_src(src, seconds_before_retry, logger) as zip_path,
        ZipFile(zip_path) as zf,
    ):
        dst_path.mkdir(exist_ok=True, parents=True)
        zf.extractall(path=dst_path)


@contextmanager
def _resolve_src(
    src: StrOrPath,
    seconds_before_retry: Optional[Sequence[int]] = None,
    logger: Callable[[str], None] = print,
) -> Generator[Path, Any, None]:
    parsed = urlparse(str(src))

    if not (parsed.scheme and parsed.netloc):
        src_path = Path(src)
        if not src_path.is_file():
            raise ValueError("Source is neither a file or a URL")

        yield Path(src)
        return

    src_url = str(src)

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_dir_path = Path(tmpdirname)
        tmp_tg_path = tmp_dir_path / "tempfile.tar.gz"
        _download_archive(src_url, tmp_tg_path, seconds_before_retry, logger)
        yield tmp_tg_path


def _download_archive(
    archive_url: str,
    archive_path: Path,
    seconds_before_retry: Optional[Sequence[int]] = None,
    logger: Callable[[str], None] = print,
):
    if seconds_before_retry is None:
        seconds_before_retry = [10, 20, 30]
    else:
        seconds_before_retry = list(seconds_before_retry)

    exp = None

    while True:
        try:
            archive_req = urlopen(archive_url)
            exp = None
            break
        except HTTPException as e:
            exp = e
            if not seconds_before_retry:
                break

            sleep_seconds = seconds_before_retry.pop(0)

            msg = f"Retrying connection in {sleep_seconds} second"
            if sleep_seconds != 1:
                msg += "s"
            msg += "..."

            logger(f"Caught: {e}")
            logger(msg)
            time.sleep(sleep_seconds)

    if exp is not None:
        raise exp

    with open(archive_path, "wb") as archive:
        archive.write(archive_req.read())
