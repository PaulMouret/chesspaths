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
# French and English piece initials:
#
# English: K Q R B N
# French:  R D T F C
#
# R is deliberately ambiguous: we keep it as R.
MOVE = (
    r'(?:'
    r'O-O-O|'
    r'O-O|'
    r'[KQRBNDFCT]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBNDFCT])?'
    r')'
)

# Convert French piece notation to English.
FRENCH_TO_ENGLISH = str.maketrans({
    "D": "Q",   # Dame -> Queen
    "F": "B",   # Fou -> Bishop
    "C": "N",   # Cavalier -> Knight
    "T": "R",   # Tour -> Rook
})
def normalize_move(move):
    """Convert French chess notation to English notation."""
    return move.translate(FRENCH_TO_ENGLISH)


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

# A sequence of moves, connected by "/" or "-".
MOVE_SEQUENCE_RE = re.compile(
    rf'{MOVE}(?:[/-]{MOVE})*'
)

# A black sequence: "..." followed immediately by a move sequence.
BLACK_MOVE_SEQUENCE_RE = re.compile(
    rf'\.\.\.{MOVE_SEQUENCE_RE.pattern}'
)


def partition_moves(text):
    parts = []
    pos = 0

    while pos < len(text):
        black_match = BLACK_MOVE_SEQUENCE_RE.search(text, pos)
        white_match = MOVE_SEQUENCE_RE.search(text, pos)

        matches = [
            m for m in (black_match, white_match)
            if m is not None
        ]

        if not matches:
            break

        m = min(matches, key=lambda m: m.start())

        if m.start() > pos:
            parts.append(("normal", text[pos:m.start()]))

        if m is black_match:
            # Remove the leading "..." before passing the sequence
            # to \bmove.
            parts.append(("bmove", m.group()[3:]))
        else:
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
            clean_parsed_text.append(f"\\varref{{{normalize_move(content)}}}")
        else:
            # In the rest of the text, there might still be chess moves. So :
            rest_parsed_text = partition_moves(content)
            cleaned_rest_parsed_text = []
            for skind, scontent in rest_parsed_text:
                if skind == "move":
                    cleaned_rest_parsed_text.append(f"\\wmove{{{normalize_move(scontent)}}}")
                elif skind == "bmove":
                    cleaned_rest_parsed_text.append(f"\\bmove{{{normalize_move(scontent)}}}")
                else:
                    cleaned_rest_parsed_text.append(normalize_move(scontent))
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
