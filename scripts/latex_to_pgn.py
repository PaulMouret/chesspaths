from converting.latex_to_tree import latex_chapter_to_list_trees
from converting.tree_to_pgn import list_trees_to_pgn
from global_utils import basename
from constants import *

from pathlib import Path


def pgn_from_latex_chapter(latex_chapter_path, repertoire_color, new_pgn_dir, new_granularity, new_name=None,
                           verbosity=True):
    """
    From an latex chapter folder, creates the corresponding PGN
    :param latex_chapter_path: the directory corresponding to a latex chapter
    :param repertoire_color: boolean indicating the repertoire color (True for White, False for Black)
    :param new_pgn_dir: directory to save the new pgn
    :param new_granularity: indicates to which level we merge games from the list
    Possible values for granularity are "chapter", "section", "single", "all"
    :param new_name: optional new name of the new pgn : if None, same as the .tex file or dir it comes from
    :param verbosity: prints the path of the new generated pgn
    :return:
    """
    print(f"\n")  # for separating tasks well in the console
    new_pgn_name = new_name if new_name is not None else basename(latex_chapter_path)
    list_trees = latex_chapter_to_list_trees(latex_chapter_path=latex_chapter_path, repertoire_color=repertoire_color)
    list_trees_to_pgn(list_trees=list_trees, new_pgn_dir=new_pgn_dir, new_pgn_name=new_pgn_name,
                      granularity=new_granularity, verbosity=verbosity)


def pgns_from_latex_project(latex_project_path, repertoire_color, new_pgn_dir, new_granularity, verbosity=True):
    """
    From an latex project folder (ie. containing chapter folders), creates the corresponding PGNs (one per chapter)
    :param latex_project_path: the directory corresponding to a latex project
    :param repertoire_color: boolean indicating the repertoire color (True for White, False for Black)
    :param new_pgn_dir: directory to save the new pgns
    :param new_granularity: indicates to which level we merge games from the list
    Possible values for granularity are "chapter", "section", "single", "all"
    :param verbosity: prints the path of the new generated pgn
    :return:
    """
    print(f"\n")  # for separating tasks well in the console
    for latex_chapter_path in Path(latex_project_path).iterdir():
        if latex_chapter_path.is_dir() and latex_chapter_path.name not in ['Appendice']:
            pgn_from_latex_chapter(latex_chapter_path, repertoire_color=repertoire_color, new_pgn_dir=new_pgn_dir,
                                   new_granularity=new_granularity, new_name=None,
                                   verbosity=verbosity)
