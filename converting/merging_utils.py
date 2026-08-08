from datastructure.datastructure_utils import merged_tree_from_list
from global_utils import get_ordered_unique_elements


def get_list_trees_with_unique_white_black(original_list_trees):
    new_list_trees = []
    pairs = [(tree.headers['White'], tree.headers['Black']) for tree in original_list_trees]
    unique_pairs = get_ordered_unique_elements(pairs)

    for combination in unique_pairs:
        combination_list_trees = [t for t in original_list_trees if
                                  (t.headers['White'] == combination[0]) and (t.headers['Black'] == combination[1])]
        section_tree = merged_tree_from_list(combination_list_trees)
        new_list_trees.append(section_tree)
    return new_list_trees


# So that, for each chapter/White, there is one game for each section
# -> can be used for LaTeX generation, or simply to get denser PGN
def merge_subsections(list_trees):
    # Renaming Black
    renamed_list_trees = []
    for i_t, t in enumerate(list_trees):
        tree = t.get_copy()
        black = tree.headers['Black']
        new_black = black.split("#")[0].strip()
        tree.update_headers({'Black': new_black})
        renamed_list_trees.append(tree)
    # Now all subsections from the same section have the same name
    final_list_trees = get_list_trees_with_unique_white_black(renamed_list_trees)
    return final_list_trees


# So that there is one game for each chapter/White
# -> can be used to get training PGN
def merge_sections(list_trees):
    # Renaming Black
    renamed_list_trees = []
    for i_t, t in enumerate(list_trees):
        tree = t.get_copy()
        tree.update_headers({'Black': tree.headers['White']})
        renamed_list_trees.append(tree)
    # Now all subsections from the same section have the same name
    final_list_trees = get_list_trees_with_unique_white_black(renamed_list_trees)
    return final_list_trees


# The final util function
def get_grained_list_trees(list_trees, granularity):
    # We convert the list_trees into the correct granularity
    if granularity == "chapter":
        list_trees = merge_sections(list_trees)
    elif granularity == "section":
        list_trees = merge_subsections(list_trees)
    elif granularity == "single":
        list_trees = [merged_tree_from_list(list_trees)]
    elif granularity != "all":
        raise Exception(f"Unknown granularity '{granularity}'")
    return list_trees
