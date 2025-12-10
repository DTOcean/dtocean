from pathlib import Path

THIS_DIR = Path(__file__).parent.resolve()


def get_index() -> str:
    return str(THIS_DIR / "html" / "index.html")
