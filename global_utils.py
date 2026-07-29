from pathlib import Path
import unicodedata
import re
import sys


# FILE MANAGEMENT

def list_files(directory, extension):
    return [str(path) for path in Path(directory).rglob(f"*{extension}") if path.is_file()]


def read_file(path, encoding="utf-8"):
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def basename(path):
    path = Path(path)
    return path.name if path.is_dir() else path.stem


def iter_depth(path, depth):
    path = Path(path)

    if depth == 1:
        yield from path.iterdir()
        return

    for child in path.iterdir():
        if child.is_dir():
            yield from iter_depth(child, depth - 1)


# A helper to load files even in a onefile executable
def resource_path(relative_path):

    if getattr(sys, "frozen", False):

        base_path = Path(sys._MEIPASS)

    else:

        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path


# HANDLING PGN

def is_trivial_pgn(pgn):
    # Remove PGN headers
    movetext = re.sub(r'(?m)^\[.*\]\s*$', '', pgn).strip()

    # Check whether the remaining movetext is just "1. -- *"
    return re.fullmatch(r'1\.\s*--\s*\*', movetext) is not None


# STRING MANIPULATION

def remove_accents(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def remove_spaces(text):
    return "_".join(text.split())


def remove_backslash(text):
    return text.replace("/", "").replace("\\", "")


INVALID_WINDOWS_CHARS = '<>:"/\\|?*'
def clean_windows_filename(text):
    return text.translate(
        str.maketrans({char: "_" for char in INVALID_WINDOWS_CHARS})
    )
# In particular, it avoids errors if if White is "?"


def formatted_text(text):  # used for creating files and folders names
    return clean_windows_filename(remove_backslash(remove_spaces(remove_accents(text))))


def unquote(s):
    return s.removeprefix('"').removesuffix('"')


def quote(s):
    return s if s.startswith('"') and s.endswith('"') else f'"{s}"'


# CHESS MOVES

# Simplified SAN
MOVE = (
    r'(?:'
    r'O-O-O|'
    r'O-O|'
    r'[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?'
    r')'
)

# A numbered move
NUMBERED = rf'\d+\.(?:\.\.)?\s*{MOVE}'
# A variation is one or more numbered moves, each optionally followed by
# one or more unnumbered moves.
CHESS_RE = re.compile(
    rf'{NUMBERED}(?:\s+{MOVE})*(?:\s+{NUMBERED}(?:\s+{MOVE})*)*'
)
def partition_chess(text):
    parts = []
    pos = 0

    for m in CHESS_RE.finditer(text):
        if pos < m.start():
            parts.append(("normal", text[pos:m.start()]))
        parts.append(("chess", m.group()))
        pos = m.end()

    if pos < len(text):
        parts.append(("normal", text[pos:]))

    return parts


MOVE_RE = re.compile(MOVE)
def partition_moves(text):
    parts = []
    pos = 0

    for m in MOVE_RE.finditer(text):
        if m.start() > pos:
            parts.append(("normal", text[pos:m.start()]))
        parts.append(("move", m.group()))
        pos = m.end()

    if pos < len(text):
        parts.append(("normal", text[pos:]))

    return parts


def clean_chess_in_text(text):  # for LaTeX
    parsed_text = partition_chess(text)
    clean_parsed_text = []
    for kind, content in parsed_text:
        if kind == "chess":
            clean_parsed_text.append(f"\\varref{{{content}}}")
        else:
            # In the rest of the text, there might still be chess moves. So :
            rest_parsed_text = partition_moves(content)
            cleaned_rest_parsed_text = [(f"\\wmove{{{content}}}" if kind == "move" else content) for kind, content in rest_parsed_text]
            clean_parsed_text.append("".join(cleaned_rest_parsed_text))
            #clean_parsed_text.append(content) is the easy way
    spaced_text = " ".join(clean_parsed_text)
    return " ".join(spaced_text.split())


# OTHER

def get_ordered_unique_elements(lst):
    return list(dict.fromkeys(lst))
    # If needed, an alternative :
    #seen = set()
    #unique = []
    #for x in lst:
    #    if x not in seen:
    #        seen.add(x)
    #        unique.append(x)
    #return unique
