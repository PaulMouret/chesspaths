#!/usr/bin/env python3

import re
import sys
from pathlib import Path

PATTERN = re.compile(
    r'(\\xskakset\{level=2\})(.*?)(\\xskakset\{level=1\})',
    re.DOTALL
)

def process_file(path: Path) -> bool:
    """Replace \variation by \varref inside xskak level-2 blocks."""

    with path.open("r", encoding="utf-8") as f:
        text = f.read()

    def repl(match):
        begin = match.group(1)
        content = match.group(2).replace(r"\variation", r"\varref")
        end = match.group(3)
        return begin + content + end

    new_text = PATTERN.sub(repl, text)

    if new_text != text:
        with path.open("w", encoding="utf-8") as f:
            f.write(new_text)
        return True

    return False


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} DIRECTORY")
        sys.exit(1)

    root = Path(sys.argv[1])

    if not root.is_dir():
        print(f"Error: '{root}' is not a directory.")
        sys.exit(1)

    modified = 0
    for tex_file in root.rglob("*.tex"):
        if process_file(tex_file):
            print(f"Modified: {tex_file}")
            modified += 1

    print(f"\nDone. Modified {modified} file(s).")


if __name__ == "__main__":
    # This code should be run from command line using :
    # python replace_variation.py /path/to/your/directory
    # It goes recursively through all files of the directory and, for each of them :
    # For all blocks of text that are enclosed within \xskakset{level=2} and \xskakset{level=1}, it replaces
    # the \variation command with the \varref command
    # N.B. : it is recommended to use track_remaining_variations.py beforehand
    main()
