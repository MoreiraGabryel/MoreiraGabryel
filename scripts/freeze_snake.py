"""Make a static first-frame variant of each Platane/snk CSS-animated SVG."""

from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def freeze(source):
    ET.fromstring(source)
    # snk uses CSS keyframes. This also overrides its inline animation styles.
    style = '<style>* { animation: none !important; transition: none !important; }</style>'
    return source.replace("</svg>", f"{style}</svg>")


def main():
    directory = Path(sys.argv[1])
    for name in ("github-contribution-grid-snake", "github-contribution-grid-snake-dark"):
        source = directory / f"{name}.svg"
        target = directory / f"{name}-static.svg"
        target.write_text(freeze(source.read_text(encoding="utf-8")), encoding="utf-8")


if __name__ == "__main__":
    main()
