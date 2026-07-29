from converting.latex_to_tree import latex_chapter_to_list_trees
from converting.tree_to_latex import list_trees_to_latex
from global_utils import basename

from pathlib import Path


def clean_latex_project(latex_project_path, clean_dir, new_granularity,
                repertoire_color, author=None, title=None, title_moves=None,
                new_name=None, verbosity=True):
    """
    From an existing latex project, creates a clean version (ie. corresponding to our simplified Tree structure)
    :param latex_project_path: the directory corresponding to a latex project
    :param repertoire_color: boolean indicating the repertoire color (True for White, False for Black)
    :param author: name of the author
    :param title: title
    :param title_moves: string representing the base moves of the repertoire (will be enclosed in \varref{})
    :param clean_dir: directory to save the new latex
    :param new_granularity: indicates to which level we merge games from the list
    Possible values for granularity are "chapter", "section", "single", "all"
    :param new_name: optional new name of the new latex project : if None, same as the original
    :param verbosity: prints the path of the new generated latex project
    :return:
    """
    print(f"\n")  # for separating tasks well in the console
    new_latex_name = new_name if new_name is not None else basename(latex_project_path)
    list_trees = []
    for latex_chapter_path in Path(latex_project_path).iterdir():
        if latex_chapter_path.is_dir() and latex_chapter_path.name not in ['Appendice']:
            list_trees += latex_chapter_to_list_trees(latex_chapter_path=latex_chapter_path,
                                                      repertoire_color=repertoire_color)
    list_trees_to_latex(original_list_trees=list_trees, granularity=new_granularity,
                        # FOR STORING
                        latex_dir=clean_dir, project_name=new_latex_name,
                        # TITLE
                        repertoire_color=repertoire_color, author=author, title=title, title_moves=title_moves,
                        with_repertoire_line=(repertoire_color is not None), with_title_line=(title is not None),
                        with_title_moves_line=(title_moves is not None), with_author_line=(author is not None),
                        verbosity=verbosity)
