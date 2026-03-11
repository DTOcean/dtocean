import argparse
from pathlib import Path

from jinja2 import Template

ROOT_DIR = Path(__file__).parents[1]
TEMPLATE_PATH = ROOT_DIR / "docs" / "_assets" / "gh-pages-redirect.html.jinja"


def main(build_dir: str | Path, tag: str):
    build_dir = Path(build_dir)

    with open(TEMPLATE_PATH, "r") as f:
        template = Template(f.read())

    assert isinstance(template, Template)

    content = template.render(tag=tag)
    dst = build_dir / "index.html"

    with open(dst, "w") as f:
        f.write(content)


def entry_point():
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dir")
    parser.add_argument("tag")

    args = parser.parse_args()
    main(args.build_dir, args.tag)


if __name__ == "__main__":
    entry_point()
