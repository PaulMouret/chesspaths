import re
from math import ceil

from constants import *
from global_utils import clean_chess_in_text


# To update the list of allowed symbolic NAGs (I may need it in the future)
SYMBOLIC_NAGS = list(SYMBOL_TO_NAG.keys())
# Longest first so that "!!" is matched before "!"
SYMBOLIC_NAGS.sort(key=len, reverse=True)
NAG_PATTERN = "|".join(map(re.escape, SYMBOLIC_NAGS))
# If instead I want to allow combination of NAGs (for instance, 13.c4!=) :
# NAG_PATTERN = f"(?:{'|'.join(map(re.escape, SYMBOLIC_NAGS))})+"

TOKEN_RE = re.compile(
    rf"""
    \d+\.\.\.|      # 2...
    \d+\.|          # 2.
    \$\d+|          # $56
    {NAG_PATTERN}|  # symbolic NAGs
    \S+             # move
    """,
    re.VERBOSE,
)

GLUED_NAG_RE = re.compile(
    rf"^(.*?)(\$\d+|{NAG_PATTERN})$"
)

SEPARATE_NAG_RE = re.compile(
    rf"^(?:\$\d+|{NAG_PATTERN})$"
)


def parse_moves(san):
    """
    From a string representing a sequence of chess moves, generates the corresponding list of moves, where each move
    is represented by a tuple (num, color, move, nag) :
    - num is the index of the move, in standard chess notations
    - color is a boolean indicating whether it is a White or Black move
    - move is the actual move, written in SAN notation
    - nag is an optional annotation of the move, specified in symbolic form (for instance ?!) or NAG form ($6)
    """
    moves = []
    move_number = None
    color = None

    for token in TOKEN_RE.findall(san):

        if token.endswith("..."):
            move_number = int(token[:-3])
            color = BLACK
            continue

        if token.endswith("."):
            move_number = int(token[:-1])
            color = WHITE
            continue

        if SEPARATE_NAG_RE.fullmatch(token):
            if not moves:
                raise ValueError("NAG without preceding move")
            n, c, m, _ = moves[-1]
            moves[-1] = (n, c, m, token)
            continue

        m = GLUED_NAG_RE.match(token)
        if m:
            move, nag = m.groups()
        else:
            move, nag = token, None

        moves.append((move_number, color, move, nag))

        color = not color

    return moves


def merged_tree_from_list(list_trees):
    if list_trees:
        full_tree = list_trees[0].get_copy()
        full_tree.multiple_merges(list_trees[1:])
        return full_tree
    else:
        return list_trees


def process_comment_for_latex(comment):
    # We replace % that may be understood by LaTeX as a comment
    comment = comment.replace("%", "\\%")
    # We clean the chess moves it might contain
    return clean_chess_in_text(comment)


def num_from_full_num(full_num):
    return ceil(full_num/2)
