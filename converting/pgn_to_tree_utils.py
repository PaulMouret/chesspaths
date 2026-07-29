from pathlib import Path
import re


def read_pgn_games(path, encoding="utf-8"):
    """Return a list of games from a PGN file, preserving formatting."""
    text = Path(path).read_text(encoding=encoding)
    # Since the splitting into games relies on headers brackets, we need to remove noisy brackets :
    text = text.replace("[#]", "")
    # Moreover a special utf-8 character at the start of the file might interfere :
    text = text.removeprefix("\ufeff")

    games = []
    current = []

    for line in text.splitlines(keepends=True):
        # A new game starts when we encounter a header after we've already
        # accumulated a complete game.
        if line.startswith("[") and current and any(
            not l.startswith("[") and l.strip() for l in current
        ):
            games.append("".join(current).rstrip())
            current = []

        current.append(line)

    if current:
        games.append("".join(current).rstrip())



    return games


HEADER_RE = re.compile(r'^\[(\w+)\s+"(.*)"\]$')
RESULT_RE = re.compile(r'(?:\s+|^)(1-0|0-1|1/2-1/2|\*)\s*$')
def parse_game(game):
    """
    Parse a single PGN game.

    Returns:
        headers: dict[str, str]
        movetext: str   # without the trailing result
        result: str | None
    """
    headers = {}
    lines = game.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            break

        m = HEADER_RE.match(line)
        if m:
            headers[m.group(1)] = m.group(2)
        i += 1

    movetext = "\n".join(lines[i:]).strip()

    result = None
    m = RESULT_RE.search(movetext)
    if m:
        result = m.group(1)
        movetext = movetext[:m.start(1)].rstrip()

    return headers, movetext, result


MOVE_NUMBER_RE = re.compile(r'(\d+\.(?:\.\.)?)\s+')
def glue_move_numbers(movetext: str) -> str:
    return MOVE_NUMBER_RE.sub(r'\1', movetext)


def parse_movetext(movetext: str):

    tokens = []
    current = []

    i = 0
    n = len(movetext)

    while i < n:
        c = movetext[i]

        if c == '(':
            if current:
                tokens.append(("variation", "".join(current).strip()))
                current = []
            tokens.append(("parenthese", "("))
            i += 1

        elif c == ')':
            if current:
                tokens.append(("variation", "".join(current).strip()))
                current = []
            tokens.append(("parenthese", ")"))
            i += 1

        elif c == '{':
            if current:
                tokens.append(("variation", "".join(current).strip()))
                current = []

            j = movetext.index('}', i)
            comment = movetext[i + 1:j].strip()
            tokens.append(("comment", comment))
            i = j + 1

        else:
            current.append(c)
            i += 1

    if current:
        tokens.append(("variation", "".join(current).strip()))

    return tokens


def cleaning_pgn_comment(sequence):
    """
    Cleans comments coming from PGN files
    """
    # Out of security, we remove brackets that may cause an error in PGN generation
    sequence = sequence.replace("{", "").replace("}", "")
    # We remove PGN extensions such as colored arrows etc.
    sequence = re.sub(r'\[%[^\]]*]', '', sequence)
    # We remove embedded FEN
    sequence = re.sub(r'@@StartFEN@@.*?@@EndFEN@@', '', sequence)
    # We remove embedded diagram
    sequence = re.sub(r'@@StartDiagram@@.*?@@EndDiagram@@', '', sequence)
    # We remove embedded bracket
    sequence = re.sub(r'@@StartBracket@@.*?@@EndBracket@@', '', sequence)
    # We remove linebreaks
    sequence = sequence.replace("\n", " ")
    # We remove formatting :
    sequence = re.sub(r'<[^>]+>', '', sequence)
    # Some comments like in Shankland's may contain glued variations (also harming LaTeX generation) : we remove them
    sequence = re.sub(r'(?:\d+\.(?:\.\.)?[^\s]+){2,}', '', sequence)
    sequence = sequence.replace("•", " ")
    # After all these removals, we fix the multiple spacing the previous lines may have introduced
    sequence = " ".join(sequence.split())
    # We remove variation parentheses :
    sequence = sequence.lstrip(")").rstrip("(")
    # We remove punctuation that would not make sense in a PGN
    sequence = sequence.strip(",").strip(";").strip(":")
    if not any(c.isalpha() for c in sequence):
        return ""
    else:
        return sequence.strip()


def clean_pgn_sequence_list(pgn_sequence_list):
    final_list = []
    for i_chunk, chunk in enumerate(pgn_sequence_list):  # a chunk of successive moves
        sequence_type, sequence = chunk
        if sequence_type == "comment":
            if i_chunk != 0:  # there should be no comment at the beginning of the list
                cleaned_sequence = cleaning_pgn_comment(sequence)
                if cleaned_sequence != '':
                    final_list.append((sequence_type, cleaned_sequence))
        else:
            if sequence.strip():
                # Because parse_movetext may generate ('variation', '') if there is a whitespace between parentheses
                final_list.append(chunk)
    return final_list
