from converting.pgn_to_tree import pgn_to_list_trees
from converting.tree_to_latex import list_trees_to_latex
from constants import *
from global_utils import basename


def latex_from_pgn(
        # PGN
        pgn_path,
        # MERGING
        granularity,
        # FOR STORING
        latex_dir,
        # TITLE
        repertoire_color=None, author=None, title=None, title_moves=None,
        # PGN (default)
        encoding="utf-8",
        # FOR STORING (default)
        project_name=None, ):
    """
    From one or several existing PGNS, creates the corresponding latex project
    :param pgn_path: may be a directory containing .pgn files or a .pgn file
    :param repertoire_color: boolean indicating the repertoire color (True for White, False for Black)
    :param author: name of the author
    :param title: title
    :param title_moves: string representing the base moves of the repertoire (will be enclosed in \varref{})
    :param latex_dir: directory to save the latex project
    :param granularity: indicates to which level we merge games from the list
    Possible values for granularity are "chapter", "section", "single", "all"
    :param project_name: optional new name of the latex project : if None, same as pgn_path it is created from
    :return:
    """
    print(f"\n")  # for separating tasks well in the console
    # We deduce the title lines from the titles that are given :
    with_repertoire_line = (repertoire_color is not None)
    with_title_line = (title is not None)
    with_title_moves_line = (title_moves is not None)
    with_author_line = (author is not None)

    new_project_name = project_name if project_name is not None else basename(pgn_path)
    original_list_trees = pgn_to_list_trees(pgn_path=pgn_path, encoding=encoding)
    list_trees_to_latex(
        original_list_trees=original_list_trees,
        granularity=granularity,
        # FOR STORING
        latex_dir=latex_dir, project_name=new_project_name,
        # TITLE
        repertoire_color=repertoire_color, author=author,
        title=title, title_moves=title_moves,
        with_repertoire_line=with_repertoire_line, with_title_line=with_title_line,
        with_title_moves_line=with_title_moves_line, with_author_line=with_author_line
    )
