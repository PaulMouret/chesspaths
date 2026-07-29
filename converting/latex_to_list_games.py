import re
from pathlib import Path
from global_utils import read_file
from converting.latex_to_tree_utils import find_matching_brace, cleaning_latex_comment


def parse_structural_command(text, match):
    """
    Parse a chapter, section, or subsection command.
    `match` is a regex match for the command itself.
    Returns:
        command_name, title, end_position
    """

    command_name = match.group("command")
    position = match.end()

    # Skip whitespace after the command
    while (
        position < len(text)
        and text[position].isspace()
    ):
        position += 1

    # Optional short title: [Short title]
    # This is not used for matching braces. We only skip it.
    if (
        position < len(text)
        and text[position] == "["
    ):
        closing_bracket = text.find(
            "]",
            position + 1,
        )

        if closing_bracket == -1:
            raise ValueError(
                f"Unmatched '[' after \\{command_name}"
            )

        position = closing_bracket + 1

        while (
            position < len(text)
            and text[position].isspace()
        ):
            position += 1

    # The actual title must start with {
    if (
        position >= len(text)
        or text[position] != "{"
    ):
        raise ValueError(
            f"Expected '{{...}}' after "
            f"\\{command_name}"
        )

    closing_brace = find_matching_brace(
        text,
        position,
    )

    title = text[
        position + 1:closing_brace
    ]

    return (
        command_name,
        title.strip(),
        closing_brace + 1,
    )


COMMAND_RE = re.compile(
    r"\\(?P<command>"
    r"chapter|section|subsection|newchessgame"
    r")\*?"
)
def parse_latex_file(
    full_file_text,
    chapter,
    full_file_path,
):
    """
    Extract all games from one .tex file.

    The current section/subsection is carried through
    the file and updated whenever a structural command is
    encountered.
    """

    list_games = []

    current_section = None
    current_subsection = None

    commands = list(
        COMMAND_RE.finditer(full_file_text)
    )

    for i_command, match in enumerate(commands):

        command = match.group("command")

        # -----------------------------------------------------
        # Structural command
        # -----------------------------------------------------

        if command in {
            "chapter",
            "section",
            "subsection",
        }:

            (
                command,
                title,
                command_end,
            ) = parse_structural_command(
                full_file_text,
                match,
            )

            if command == "chapter":
                # The chapter is already known from the
                # chapter directory. We do not need to update
                # it here.

                current_section = None
                current_subsection = None

            elif command == "section":
                current_section = title
                current_subsection = None

            elif command == "subsection":
                current_subsection = title

        # -----------------------------------------------------
        # Game
        # -----------------------------------------------------

        elif command == "newchessgame":

            game_start = match.end()

            # Find the next \newchessgame
            next_game = next(
                (
                    next_match
                    for next_match in commands[
                        i_command + 1:
                    ]
                    if next_match.group("command")
                    == "newchessgame"
                ),
                None,
            )

            if next_game is None:
                game_end = len(full_file_text)
            else:
                game_end = next_game.start()

            file_section = full_file_text[
                game_start:game_end
            ]

            list_games.append({
                "chapter": chapter,
                "section": current_section,
                "subsection": current_subsection,
                "file_path": full_file_path,
                "latex": file_section,
            })

    return list_games


def find_chapter(list_tex_files):
    chapter = None

    for full_file_path in list_tex_files:

        full_file_text = read_file(full_file_path)

        for match in COMMAND_RE.finditer(
            full_file_text
        ):

            if match.group("command") != "chapter":
                continue

            (
                _,
                title,
                _,
            ) = parse_structural_command(
                full_file_text,
                match,
            )

            if chapter is not None:
                raise Exception(
                    f"More than one \\chapter command found in {full_file_path}"
                )

            chapter = title

    if chapter is None:
        raise Exception(
            "No \\chapter command found"
        )

    return chapter


def latex_chapter_to_list_games(
    latex_chapter_path,
):

    latex_chapter_path = Path(
        latex_chapter_path
    )

    if not latex_chapter_path.is_dir():
        raise Exception(
            "latex_chapter_path should be a "
            "chapter directory"
        )

    list_tex_files = sorted(
        latex_chapter_path.rglob("*.tex")
    )

    chapter = find_chapter(
        list_tex_files
    )

    list_games = []

    for full_file_path in list_tex_files:

        full_file_text = read_file(
            full_file_path
        )

        list_games.extend(
            parse_latex_file(
                full_file_text,
                chapter,
                full_file_path,
            )
        )

    # We just need to clean the chapter, section and subsection fields, since they might contain \varref command
    clean_list_games = []
    for game in list_games:
        for k in ['chapter', 'section', 'subsection']:
            if isinstance(game[k], str):
                game[k] = cleaning_latex_comment(text_without_command(game[k], 'varref'))
        clean_list_games.append(game)

    return clean_list_games


def text_without_command(text, command):
    """
    Remove occurrences of \\command from `text`, preserving
    the content of its mandatory {...} argument.

    Handles:
        \\command{content}
        \\command[option]{content}
        nested braces inside content.
    """

    command_re = re.compile(
        rf"\\{re.escape(command)}\b"
    )

    while True:

        match = command_re.search(text)

        if match is None:
            break

        position = match.end()

        # Skip whitespace before the optional argument or {...}
        while (
            position < len(text)
            and text[position].isspace()
        ):
            position += 1

        # Skip optional argument [...]
        if (
            position < len(text)
            and text[position] == "["
        ):

            closing_bracket = text.find(
                "]",
                position + 1,
            )

            if closing_bracket == -1:
                raise ValueError(
                    f"Unmatched '[' after \\{command}"
                )

            position = closing_bracket + 1

            # Skip whitespace before {...}
            while (
                position < len(text)
                and text[position].isspace()
            ):
                position += 1

        # Mandatory argument {...}
        if (
            position >= len(text)
            or text[position] != "{"
        ):
            raise ValueError(
                f"Expected '{{...}}' after \\{command}"
            )

        closing_brace = find_matching_brace(
            text,
            position,
        )

        content = text[
            position + 1:closing_brace
        ]

        # Replace:
        #     \command[option]{content}
        #
        # with:
        #     content
        text = (
            text[:match.start()]
            + content
            + text[closing_brace + 1:]
        )

    return text