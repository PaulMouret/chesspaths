import os

from global_utils import is_trivial_pgn, formatted_text
from converting.merging_utils import get_grained_list_trees


def list_trees_to_pgn(list_trees, new_pgn_dir, new_pgn_name, granularity, verbosity=True):
    # The granularity level is used to process list_trees :
    # from there the LaTeX structure will be automatically parsed from White and Black field
    # White = chapter name ; Black = section name, possibly followed by # subsection index
    # Possible values for granularity are "chapter", "section" - if not, we let the list as it is

    # To avoid any problem when reading the pgn, we format the name :
    new_pgn_name = formatted_text(new_pgn_name)

    # We convert the list_trees into the correct granularity
    list_trees = get_grained_list_trees(list_trees, granularity)

    list_clean_pgns = []
    for tree in list_trees:
        try:
            tree_pgn = tree.pgn()
        except Exception as e:
            raise RuntimeError(f"Error while generating PGN from {tree.source_file}") from e
        if not is_trivial_pgn(tree_pgn):  # it is useless saving empty PGNs
            list_clean_pgns.append(tree_pgn)
    new_pgn = "\n\n".join(list_clean_pgns)
    # We store the PGN :
    if not os.path.exists(new_pgn_dir):
        os.makedirs(new_pgn_dir, exist_ok=True)
    # We write the PGN
    full_path = os.path.join(new_pgn_dir, f"{new_pgn_name}.pgn")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(new_pgn)
    if verbosity:
        print(f"\nPGN file successfully saved at {full_path}")
