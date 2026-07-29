from pathlib import Path
import re

from converting.latex_to_tree_utils import remove_comments, remove_command, replace_variation_in_xskakcomment, \
    extract_chess_commands, move_chessboard_comments, move_xskakcomments, clean_latex_sequence_list
from datastructure.tree import Tree
from global_utils import read_file
from converting.latex_to_list_games import latex_chapter_to_list_games


def latex_chapter_to_list_trees(latex_chapter_path, repertoire_color):
    latex_chapter_path = Path(latex_chapter_path)
    if not latex_chapter_path.is_dir():
        raise Exception(f"latex_chapter_path should be a folder, but you specified "
                        f"'{latex_chapter_path}'")

    # We do not only want to retrieve games,
    # which would be easy going through files and performing full_file_text.split("\\newchessgame")
    # We also want to keep track of structural names (chapter, section, subsection) corresponding to each game
    # (they will be useful for future merging)
    list_games = latex_chapter_to_list_games(latex_chapter_path)
    # each game is a dict with the keys chapter, section, subsection, filepath, latex (with the actual latex content)

    list_trees = []  # will contain the Tree objects, one for each \newchessgame in .tex files

    for game in list_games:
        # We extract elements from the game
        white_header = game['chapter']
        black_header = f"{game['section'] if game['section'] is not None else ''} # {game['subsection'] if game['subsection'] is not None else ''}"
        latex_identifier = f"{game['file_path']} - {white_header} - {black_header}"
        file_section = game['latex']

        # We remove comments, since they might contain uncorrected text
        file_section = remove_comments(file_section)
        # We remove the \textcolor{bleufonce}{} commands and their content, since they correspond to
        # alternatives for my side
        file_section = file_section.replace("textcolor{bleufonce}", "textcolor_bleufonce")
        file_section = remove_command(file_section, "textcolor_bleufonce")
        # We expect the .tex files to be cleaned (manually, or using the cleaning_latex_files/ module) so that
        # (except possibly in the \textcolor{bleufonce}{} blocks, which have been previously removed)
        # the \variation{} commands only contain proper variations to store
        # (in opposition to references used to comment, that should use \varref{} instead)
        # We remove commands potentially containing noisy \variation{}
        file_section = replace_variation_in_xskakcomment(file_section)  # so we don't have to remove xskakcomment
        commands_to_remove = ["chapter", "section", "subsection", "subsubsection", "input"]
        for command in commands_to_remove:
            file_section = remove_command(file_section, command)
        # We force \footnote to be preceded by a space (as in my code I may glue them to a move, causing an error)
        file_section = re.sub(r'(?<!\s)\\footnote', r' \\footnote', file_section)
        # And, because they may be inside variations, the most secure is to remove footnotes :
        file_section = remove_command(file_section, 'footnote')

        # Now we retrieve all \mainline{} and \variation{} commands in the text as an ordered list of the form
        # [('mainline', '1.c4 e5 $1 \xskakcomment{ good}'), ('variation', '1...c5'), ('comment', ' is winning')]
        # N.B. : The notation is expected to be the SAN, same as PGN (for instance promotion is written as =)
        section_commands = extract_chess_commands(file_section)
        section_commands = move_chessboard_comments(section_commands)
        latex_sequence_list = move_xskakcomments(section_commands)  # now it is a proper 'sequence list'
        latex_sequence_list = clean_latex_sequence_list(latex_sequence_list)

        # Now latex_sequence_list is clean
        print(f"\n# {latex_identifier}...\n{latex_sequence_list}")  # enables to quickly identify location of fails
        # If it is an actual section (ie. if it contains a mainline), we build the corresponding tree object
        # If there are mistakes in the .tex files, they will raise an error here, or when opening the pgn,
        # so they will be easily identified and thus can be manually corrected
        if any(item[0] == 'mainline' for item in latex_sequence_list):
            # Important requirements :
            # - any variation should contain at least a reply
            # - any variation should end with a move from our side
            # - there is no alternative for our side
            # - the \variation command only correspond to actual variations
            # (and not references that serve as comment)
            # so that the order of variations is preserved (a reference to 1...c5 in the variation 5.c4 would break
            # this order)
            # - for the parsing to work, the first move of a sequence should be attached to the preceding dot
            section_tree = Tree(repertoire_color=repertoire_color)
            headers = {'White': white_header, 'Black': black_header}
            section_tree.update_headers(headers)
            section_tree.init_from_latex_sequence_list(latex_sequence_list, source_latex_name=latex_identifier)
            list_trees.append(section_tree)

    return list_trees


def latex_chapter_to_one_tree(latex_chapter_path, repertoire_color):
    list_trees = latex_chapter_to_list_trees(latex_chapter_path=latex_chapter_path, repertoire_color=repertoire_color)
    if len(list_trees) > 0:
        base_tree = list_trees[0].get_copy()
        base_tree.multiple_merges(list_trees[1:])
        return base_tree
    else:
        raise Exception(f"No tree was built from latex_chapter_path='{latex_chapter_path}', "
                        f"repertoire_color='{repertoire_color}'")


if __name__ == "__main__":
    # constants at opening level
    opening = 'Anglaise'
    latex_dir = f"C:/Users/paulm/Documents/LOISIRS/Echecs/01 Mes ouvertures/2021-aujourd'hui/LaTeX/{opening}"
    my_path = f"{latex_dir}/1.c4 c5/Closed system"

    my_list_trees = latex_chapter_to_list_trees(latex_chapter_path=my_path,
                                                repertoire_color=(opening == 'Anglaise'))
    my_tree = my_list_trees[0].get_copy()
    print(my_tree.pgn())
