import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Union
from urllib.parse import urlparse
from urllib.request import urlopen
from zipfile import ZipFile

StrOrPath = Union[str, Path]


def extract_tar(src: StrOrPath, dst: StrOrPath):
    dst_path = Path(dst)
    dst_path.mkdir(exist_ok=True)

    with _resolve_src(src) as tg_path:
        tar = tarfile.open(tg_path)
        tar.extractall(path=dst_path, filter="tar")
        tar.close()


def extract_zip(src: StrOrPath, dst: StrOrPath):
    dst_path = Path(dst)
    dst_path.mkdir(exist_ok=True)

    with _resolve_src(src) as zip_path:
        zf = ZipFile(zip_path)
        zf.extractall(path=dst_path)
        zf.close()


@contextmanager
def _resolve_src(src: StrOrPath) -> Generator[Path, Any, None]:
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
        _download_archive(src_url, tmp_tg_path)
        yield tmp_tg_path


def _download_archive(archive_url: str, archive_path: Path):
    archive_req = urlopen(archive_url)

    with open(archive_path, "wb") as archive:
        archive.write(archive_req.read())
