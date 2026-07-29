from converting.pgn_to_tree import pgn_to_list_trees
from converting.tree_to_pgn import list_trees_to_pgn
from global_utils import list_files, basename


def clean_pgn(pgn_path, clean_dir, new_granularity, new_name=None, encoding="utf-8", verbosity=True):
    """
    From one or several existing PGNS, creates a single clean PGN that corrects formatting ambiguities
    (indeed, some PGNs cannot be read by all readers ; our PGN generation is universal)
    and performs the merging of games defined by new_granularity
    :param pgn_path: may be a directory containing .pgn files or a .pgn file
    :param clean_dir: directory to save the new pgn
    :param new_granularity: indicates to which level we merge games from the list
    Possible values for granularity are "chapter", "section", "single", "all"
    :param new_name: optional new name of the new pgn : if None, same as the original
    :param encoding: encoding used to open the original pgn
    :param verbosity: prints the path of the new generated pgn
    :return:
    """
    print(f"\n")  # for separating tasks well in the console
    new_pgn_name = new_name if new_name is not None else basename(pgn_path)
    list_trees = pgn_to_list_trees(pgn_path=pgn_path, encoding=encoding)
    list_trees_to_pgn(list_trees=list_trees, new_pgn_dir=clean_dir, new_pgn_name=new_pgn_name,
                      granularity=new_granularity, verbosity=verbosity)


def clean_pgns(global_pgn_path, clean_dir, new_granularity, encoding="utf-8", verbosity=True):
    """
    From existing PGNs, creates for each of them the corresponding clean PGN that corrects formatting ambiguities
    (indeed, some PGNs cannot be read by all readers ; our PGN generation is universal)
    and performs the merging of games defined by new_granularity
    :param global_pgn_path: a directory containing .pgn files
    :param clean_dir: directory to save the new pgn
    :param new_granularity: indicates to which level we merge games from the list
    Possible values for granularity are "chapter", "section", "single", "all"
    :param encoding: encoding used to open the original pgn
    :param verbosity: prints the path of the new generated pgn
    :return:
    """
    print(f"\n")  # for separating tasks well in the console
    for pgn_path in list_files(global_pgn_path, extension='.pgn'):
        clean_pgn(pgn_path=pgn_path, clean_dir=clean_dir, new_granularity=new_granularity,
                  new_name=None, encoding=encoding, verbosity=verbosity)
