#!/usr/bin/env python3

import re
import sys
from pathlib import Path

# Matches everything between \xskakset{level=2} and the next \xskakset{level=1}
PATTERN = re.compile(
    r'\\xskakset\{level=2\}(.*?)\\xskakset\{level=1\}',
    re.DOTALL
)

def process_file(path: Path):
    with path.open("r", encoding="utf-8") as f:
        text = f.read()

    matches = []
    for match in PATTERN.finditer(text):
        content = match.group(1).strip()
        if r"\variation" in content:
            matches.append(content)

    if matches:
        print(f"{path}:")
        for content in matches:
            print(content)
        print()


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} DIRECTORY")
        sys.exit(1)

    root = Path(sys.argv[1])

    if not root.is_dir():
        print(f"Error: '{root}' is not a directory.")
        sys.exit(1)

    for tex_file in root.rglob("*.tex"):
        process_file(tex_file)


if __name__ == "__main__":
    # This code should be run from command line using :
    # python replace_variation.py /path/to/your/directory
    # It goes recursively through all files of the directory and, for each of them :
    # It prints all blocks of text that are enclosed within \xskakset{level=2} and \xskakset{level=1} that
    # still contain a \variation command (which should probably be replaced by a \varref command)
    main()
