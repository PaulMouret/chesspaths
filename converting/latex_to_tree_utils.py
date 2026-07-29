import os
from pathlib import Path
import unicodedata
import re


def remove_comments(text):
    return "\n".join(
        line.split("%", 1)[0]
        for line in text.splitlines()
    )


def remove_command(text, command):
    # N.B. : does not modify the initial text ; does support options in braces ;
    # does not support successive commands, so should use replace first
    while True:
        start = text.find(f"\\{command}")
        if start == -1:
            break

        # Find the opening brace
        i = text.find("{", start)
        if i == -1:
            break

        depth = 1
        j = i + 1
        while j < len(text) and depth:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1

        text = text[:start] + text[j:]

    return text


def replace_variation_in_xskakcomment(text):
    result = []
    i = 0

    while i < len(text):
        marker = r"\xskakcomment{"

        if text.startswith(marker, i):
            start = i + len(marker) - 1  # index of the opening {
            end = find_matching_brace(text, start)

            # Contents of the xskakcomment
            content = text[start + 1:end]

            # Replace only inside this content
            content = content.replace(r"\variation{", r"\varref{")

            result.append(marker)
            result.append(content)
            result.append("}")

            i = end + 1
        else:
            result.append(text[i])
            i += 1

    return "".join(result)


def find_matching_brace(s, opening_brace):
    """Return the index of the matching closing brace."""
    depth = 1
    i = opening_brace + 1

    while i < len(s):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1

    raise ValueError("Unmatched brace")


def extract_chess_commands(text):
    """
    Returns a list of tuples:
        ('comment', text)
        ('mainline', content)
        ('variation', content)

    Comments are everything outside of \\mainline{...} and \\variation{...}
    commands.
    """
    result = []

    cmd_pattern = re.compile(r'\\(mainline|variation)\b')
    matches = list(cmd_pattern.finditer(text))

    comment_start = 0

    for m in matches:
        # Emit preceding comment
        if m.start() > comment_start:
            result.append(("comment", text[comment_start:m.start()]))

        cmd = m.group(1)
        pos = m.end()

        # Skip whitespace
        while pos < len(text) and text[pos].isspace():
            pos += 1

        # Optional argument(s)
        while pos < len(text) and text[pos] == "[":
            depth = 1
            pos += 1
            while depth:
                if pos >= len(text):
                    raise ValueError(f"Unterminated optional argument in \\{cmd}")
                if text[pos] == "[":
                    depth += 1
                elif text[pos] == "]":
                    depth -= 1
                pos += 1

            # Allow whitespace after an optional argument
            while pos < len(text) and text[pos].isspace():
                pos += 1

        if pos >= len(text) or text[pos] != "{":
            raise ValueError(f"Expected '{{' after \\{cmd}")

        end = find_matching_brace(text, pos)

        result.append((cmd, text[pos + 1:end]))

        comment_start = end + 1

    # Trailing comment
    if comment_start < len(text):
        result.append(("comment", text[comment_start:]))

    return result


def move_chessboard_comments(commands_list):
    """
    Given a list of tuples:
        ('comment', text)
        ('mainline', content)
        ('variation', content)

    any comment containing '\\chessboard' is moved immediately after the
    preceding 'mainline' tuple.
    """
    result = []

    for token in commands_list:
        kind, content = token

        if kind == "comment" and r"\chessboard" in content:
            # Find the last mainline already emitted.
            for i in range(len(result) - 1, -1, -1):
                if result[i][0] == "mainline":
                    result.insert(i + 1, token)
                    break
            else:
                # No preceding mainline.
                result.append(token)
        else:
            result.append(token)

    return result


def split_xskakcomments(s, sequence_type):
    """
    Split a string into ordered (sequence_type, content) and ('comment', content)
    tuples, where comments are of the form \\xskakcomment{...}.

    Nested braces inside comments are supported.
    """
    result = []
    i = 0
    start = 0
    marker = r"\xskakcomment{"

    while i < len(s):
        if s.startswith(marker, i):
            # Add preceding text
            if i > start:
                result.append((sequence_type, s[start:i]))

            # Find the matching closing brace
            j = i + len(marker)
            depth = 1

            while j < len(s) and depth:
                if s[j] == "{":
                    depth += 1
                elif s[j] == "}":
                    depth -= 1
                j += 1

            if depth != 0:
                # Unclosed comment: treat the rest as text
                result.append((sequence_type, s[i:]))
                break

            # Extract comment content (without \xskakcomment{ })
            result.append(("comment", s[i + len(marker):j-1]))

            i = j
            start = j
        else:
            i += 1

    # Add remaining text
    if start < len(s):
        result.append((sequence_type, s[start:]))

    return result


def move_xskakcomments(commands_list):
    final_list = []
    for chunk in commands_list:  # a chunk of successive moves
        sequence_type, sequence = chunk
        if sequence_type == "comment":
            final_list.append(chunk)
        else:
            final_list += split_xskakcomments(sequence, sequence_type)
    return final_list


def cleaning_latex_comment(sequence):
    """
    Cleans comments coming from LaTeX files
    """
    # We clean href commands
    sequence = re.sub(r'\\href\{([^{}]*)\}\{([^{}]*)\}',
                      r'\2 (\1)',
                      sequence
                      )
    # Out of security, we remove brackets that may cause an error in PGN generation
    sequence = sequence.replace("{", "").replace("}", "")
    # We remove commands residuals, useless in comments
    for str_to_remove in ["\\xskaksetlevel=1", "\\xskaksetlevel=2", "\\symbolediag",
                          "\\chessboard[inverse]", "\\chessboard", "~", "\\medskip",
                          "\\newpage",
                          # Note we preserve the content of the following commands :
                          "\\textbf", "\\xskakcomment", "\\footnote", "\\href"]:
        sequence = sequence.replace(str_to_remove, "")
    # We clean the resulting \wmove, \bmove and \varref
    sequence = sequence.replace("\\wmove", "").replace("\\bmove", "...").replace("\\varref", "")
    # We remove linebreaks
    sequence = sequence.replace("\n", " ")
    sequence = " ".join(sequence.split())  # to fix the multiple spacing the previous line may have introduced
    # We remove variation parentheses :
    sequence = sequence.lstrip(")").rstrip("(")
    # We remove punctuation that would not make sense in a PGN
    sequence = sequence.strip(",").strip(";").strip(":")
    # We remove LaTeX linebreaks
    sequence = sequence.replace("\\\\", "")
    if not any(c.isalpha() for c in sequence):
        return ""
    else:
        return sequence.strip()


def clean_latex_sequence_list(latex_sequence_list):
    final_list = []
    for i_chunk, chunk in enumerate(latex_sequence_list):  # a chunk of successive moves
        sequence_type, sequence = chunk
        if sequence_type == "comment":
            if i_chunk != 0:  # there should be no comment at the beginning of the list
                cleaned_sequence = cleaning_latex_comment(sequence)
                if cleaned_sequence != '':
                    final_list.append((sequence_type, cleaned_sequence))
        else:
            final_list.append(chunk)
    return final_list
