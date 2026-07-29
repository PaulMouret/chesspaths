from pathlib import Path

from converting.pgn_to_tree_utils import read_pgn_games, parse_game, glue_move_numbers, parse_movetext, \
    clean_pgn_sequence_list
from datastructure.tree import Tree
from global_utils import list_files, is_trivial_pgn


def pgn_to_list_trees(pgn_path, encoding="utf-8"):

    # We list the .pgn files from which we will build the trees
    pgn_path = Path(pgn_path)
    if pgn_path.is_file() and pgn_path.suffix.upper() == ".PGN":
        list_pgn_files = [pgn_path]
    elif pgn_path.is_dir():
        list_pgn_files = list_files(pgn_path, extension='.pgn')  # all .pgn files in the path (recursively)
    else:
        raise Exception(f"pgn_path should be a folder or a .pgn file, but you speicified "
                        f"'{pgn_path}'")

    list_trees = []  # will contain the Tree objects, one for each game in .pgn files

    for i_file, full_file_path in enumerate(list_pgn_files):
        try:
            pgn_list = read_pgn_games(full_file_path, encoding=encoding)
        except:
            pgn_list = read_pgn_games(full_file_path, encoding="latin-1" if encoding == "utf-8" else "utf-8")
        # a .pgn file itself may contain several games
        for i_pgn, pgn_game in enumerate(pgn_list):
            pgn_tree = Tree()
            headers, movetext, result = parse_game(pgn_game)
            # We update headers
            if result:
                headers.update({"Result": result})
            pgn_tree.update_headers(headers)
            # We create an identifier name for the PGN to easily debug it :
            short_headers = f"{pgn_tree.headers['White']} - {pgn_tree.headers['Black']}"
            pgn_identifier = f"{full_file_path} - game {i_pgn + 1} - {short_headers}"
            # We prepare the movetext
            movetext = movetext.replace("\n", " ")  # linebreaks are useless in PGNs
            movetext = glue_move_numbers(movetext)  # for our parsing of moves to work
            # We parse the movetext
            try:
                pgn_sequence_list = parse_movetext(movetext)
            except Exception as e:
                print(f"\nWARNING : Error when parsing movetext for {pgn_identifier}")
                continue
            pgn_sequence_list = clean_pgn_sequence_list(pgn_sequence_list)
            # We create the actual game tree ; if an error is raised it indicates the problematic PGN
            try:
                pgn_tree.init_from_pgn_sequence_list(pgn_sequence_list, source_pgn_name=pgn_identifier)
            except Exception as e:
                raise RuntimeError(f"Error while creating Tree from {pgn_identifier}") from e

            list_trees.append(pgn_tree)

    # Because some files may originally contain nothing but comments, which thus have been ignored by our code
    # (which only considers comments following a move), we clean the list of trees by getting rid of empty trees
    clean_list_trees = [t for t in list_trees if not is_trivial_pgn(t.pgn())]

    return clean_list_trees


def pgn_to_one_tree(pgn_path, encoding="utf-8"):
    list_trees = pgn_to_list_trees(pgn_path=pgn_path, encoding=encoding)
    if len(list_trees) > 0:
        base_tree = list_trees[0].get_copy()
        base_tree.multiple_merges(list_trees[1:])
        return base_tree
    else:
        raise Exception(f"No tree was built from pgn_path='{pgn_path}', "
                        f"encoding='{encoding}'")
