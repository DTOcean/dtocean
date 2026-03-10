import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace, patch_docutils

PACKAGE_DIR = Path(__file__).parents[1].resolve()
DST_DIR = PACKAGE_DIR / "src" / "dtocean_docs" / "html"


def _build_docs(srcdir: Path, confdir: Path, outdir: Path):
    with (
        patch_docutils(confdir),
        docutils_namespace(),
        TemporaryDirectory() as doctreedir,
    ):
        app = Sphinx(srcdir, confdir, outdir, doctreedir, "html")
        app.build()


def _cleanup():
    if DST_DIR.exists():
        shutil.rmtree(DST_DIR)


def build():
    """Build the project."""
    _cleanup()

    DST_DIR.mkdir(parents=True)
    docs_dir = PACKAGE_DIR.parents[1] / "docs"

    _build_docs(docs_dir, docs_dir, DST_DIR)


if __name__ == "__main__":
    build()
