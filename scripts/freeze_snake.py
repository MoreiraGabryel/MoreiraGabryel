"""Make a static first-frame variant of each Platane/snk CSS-animated SVG."""

from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def freeze(source):
    ET.fromstring(source)
    # snk uses CSS keyframes. This also overrides its inline animation styles.
    style = '<style>* { animation: none !important; transition: none !important; }</style>'
    return source.replace("</svg>", f"{style}</svg>")


def adaptive(source):
    # Start from the dark SVG. The image inherits GitHub's color-scheme, so a
    # manual site theme works even when it differs from the operating system.
    style = '''<style>@media (prefers-color-scheme: light) {
      :root { --cs:#8C6200; --ce:#E6EFF9; --c0:#E6EFF9; --c1:#B4CEE6;
              --c2:#7BAED6; --c3:#3A8BC5; --c4:#0969B5; }
    }</style>'''
    return source.replace("</svg>", f"{style}</svg>")


def main():
    directory = Path(sys.argv[1])
    for name in ("github-contribution-grid-snake", "github-contribution-grid-snake-dark"):
        source = directory / f"{name}.svg"
        target = directory / f"{name}-static.svg"
        target.write_text(freeze(source.read_text(encoding="utf-8")), encoding="utf-8")
    source = (directory / "github-contribution-grid-snake-dark.svg").read_text(encoding="utf-8")
    themed = adaptive(source)
    (directory / "electric-snake.svg").write_text(themed, encoding="utf-8")
    (directory / "electric-snake-static.svg").write_text(freeze(themed), encoding="utf-8")


if __name__ == "__main__":
    main()
