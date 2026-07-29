#!/usr/bin/env python3

import re
import sys
from pathlib import Path

# Matches \part, \chapter, \section, or \subsection
SECTION_CMD_RE = re.compile(r'\\(?:part|chapter|section|subsection|subsubsection|addcontentsline)\b')

def process_file(path: Path) -> bool:
    """Process one .tex file. Returns True if the file was modified."""
    modified = False
    new_lines = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if SECTION_CMD_RE.search(line):
                new_line = line.replace(r"\variation", r"\varref")
                if new_line != line:
                    modified = True
                new_lines.append(new_line)
            else:
                new_lines.append(line)

    if modified:
        with path.open("w", encoding="utf-8", newline="") as f:
            f.writelines(new_lines)

    return modified


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} DIRECTORY")
        sys.exit(1)

    root = Path(sys.argv[1])

    if not root.is_dir():
        print(f"Error: '{root}' is not a directory.")
        sys.exit(1)

    modified_count = 0

    for tex_file in root.rglob("*.tex"):
        if process_file(tex_file):
            print(f"Modified: {tex_file}")
            modified_count += 1

    print(f"\nDone. Modified {modified_count} file(s).")


if __name__ == "__main__":
    # This code should be run from command line using :
    # python replace_variation.py /path/to/your/directory
    # It goes recursively through all files of the directory and, for each of them :
    # If a line contains the command \part, \chapter, \section, \subsection, \subsubsection, \addcontentsline,
    # every \variation command on this line is replaced with \varref
    main()
