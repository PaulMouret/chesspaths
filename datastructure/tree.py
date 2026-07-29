from dataclasses import dataclass, field, asdict
from math import ceil

from constants import *
from datastructure.datastructure_utils import parse_moves, process_comment_for_latex, num_from_full_num
from global_utils import quote, unquote


@dataclass
class Node:
    """Node representing a chess move"""
    num: int  # the integer number of the move in standard notation (for instance 2 for the 2nd Black move)
    color: bool | None  # the color of the move, indicated as True for White or False for Black
    move: str  # the text move in SAN notation
    nag: str | None = None  # the NAG associated to a move, directly given as "$[i]" or "!"
    comment: str | None = None
    parent: "Node | None" = None  # the preceding move
    children: list["Node"] = field(default_factory=list, init=False)

    # the list of possible next moves (as many as alternatives, the first is the mainline)

    @property
    def symbolic_nag(self) -> str | None:
        if self.nag is not None and self.nag[0] == '$':
            return NAG_TO_SYMBOL[self.nag]
        else:
            return self.nag

    @property
    def dollar_nag(self) -> str | None:
        if self.nag is None or self.nag[0] == '$':
            return self.nag
        else:
            return SYMBOL_TO_NAG[self.nag]

    @property
    def full_num(self) -> int:
        # To generate the "actual" index of the move (ie. number of half-moves), to make it easier for comparison
        # (for instance 4 for the 2nd Black move)
        return 2 * (self.num - 1) + (1 if self.color == WHITE else 2)

    @property
    def key(self):
        # To easily get the "identifier" of the move
        # For our use, we do not need to include color in the key
        return self.num, self.move

    def add_child(self, child: "Node", repertoire_color=None) -> "Node":
        # If it is a repertoire, we first check that we provide no alternative for our repertoire side
        if repertoire_color is not None:
            if child.color == repertoire_color and len(self.children) > 0:
                raise Exception(f"{child} was given as an alternative to {self.children[0]} "
                                f"while we desire an unambiguous repertoire for "
                                f"{COLOR_TO_STRING[repertoire_color]}.")

        if child.color is None:
            child.color = not self.color  # we deduce the color of the move from its parent
        child.parent = self
        self.children.append(child)
        return child

    def add_sibling(self, sibling: "Node", repertoire_color=None) -> "Node":
        # N.B. : should not be applied to the root
        sibling = self.parent.add_child(sibling, repertoire_color=repertoire_color)
        return sibling

    @property
    def is_root(self):
        return self.parent is None

    def notation(self, no_preceding, with_nag=False, use_symbolic_nag=True):
        """
        Generates the notation of the move - this notation can be used for both LaTeX and PGN generation
        no_preceding is a boolean indicating that, from the sequence it belongs to, no move is immediately preceding it:
        this requires to indicate the index of the move (as 1. or 1..., depending on the side)
        """

        if self.color == WHITE:  # White moves always appear the same
            move_str = f"{self.num}. {self.move}"
        else:
            move_str = f"{self.num}... {self.move}" if no_preceding else f"{self.move}"
        if with_nag and self.nag is not None:
            return f"{move_str} {self.symbolic_nag if use_symbolic_nag else self.dollar_nag}"
        else:
            return move_str

    def __str__(self):
        return self.notation(no_preceding=True)


class Tree:
    """A tree representing a chess game"""

    def __init__(self, repertoire_color=None):
        self.root = Node(num=0, color=BLACK, move='')  # a dummy node
        self.repertoire_color = repertoire_color
        # In a repertoire, we require :
        # - there is no alternative for our side
        # - each variation ends with a move from our side
        self.source_file = None
        # We also add headers, initialized as default PGN :
        self.headers = {
            "Event": quote("?"), "Site": quote("?"), "Date": quote("????.??.??"), "Round": quote("?"),
            "White": quote("?"), "Black": quote("?"), "Result": quote("*"),
        }
        # Headers will be used for PGN generation, so they should be updated before PGN generation,
        # or passed as kwargs of pgn() method when called

    def update_headers(self, new_headers):
        clean_new_headers = {(k.capitalize() if k != 'FEN' else k): unquote(v) for k, v in new_headers.items()}
        # We forbig empty strings, that may cause an error in LaTeX :
        for k, v in clean_new_headers.items():
            if v.strip() == "":
                clean_new_headers[k] = "?"
        # Actual update
        self.headers.update(clean_new_headers)
        # If we update the headers with a FEN field, meaning the game starts from this FEN, we need to update the root
        if "FEN" in clean_new_headers.keys() and unquote(clean_new_headers['FEN']) != INITIAL_FEN:
            parsed_fen = unquote(clean_new_headers['FEN']).split()
            side_to_move = parsed_fen[1]
            next_num = int(parsed_fen[5])
            self.root.color = not (side_to_move == 'w')
            self.root.num = next_num if side_to_move == 'b' else (next_num - 1)

    def init_from_pgn_sequence_list(self, pgn_sequence_list, source_pgn_name):
        """
        Instantiates the Tree from a pgn_sequence_list, which is a list of tuples (sequence_type, sequence)
        It is extracted from a PGN, so the possible sequence_type are :
        - 'variation' : sequence is a sequence of consecutive moves, including their GANs, for instance "2...Nf6! 3.e5"
        - 'comment' : sequence is a comment referring to the preceding move, for instance " a strong prophylactic move"
        - 'parenthese' : sequence is either '(' or ')' ; it delimits variations in PGN notation
        source_pgn_name helps debugging
        """
        self.source_file = source_pgn_name

        if self.root.children:
            raise Exception("This tree already contains a game")

        current_node = self.root

        # Stack used when entering/leaving nested variations.
        # Each element is the node to return to when the variation ends.
        variation_stack = []

        # >0 means we are ignoring a malformed variation
        skip_depth = 0

        for sequence_type, sequence in pgn_sequence_list:

            # Ignore everything inside a skipped variation
            if skip_depth:
                if sequence_type == "parenthese":
                    if sequence == "(":
                        skip_depth += 1
                    elif sequence == ")":
                        skip_depth -= 1
                        if skip_depth == 0:
                            current_node = variation_stack.pop()  # we can go back to normal generation
                continue

            if sequence_type == "comment" and sequence != '':
                if not current_node.comment:
                    current_node.comment = sequence
                else:
                    current_node.comment += " " + sequence

            elif sequence_type == "variation":
                try:
                    parsed_moves_list = parse_moves(sequence)
                except Exception as e:
                    print(f"\nWARNING : in the current PGN, we failed at parsing '{sequence}'. "
                          f"We stop the Tree generation there. The PGN in question is :\n{source_pgn_name}\n")
                    variation_stack = []
                    break
                # So far, parsing has only failed if comments are not properly enclosed in brackets

                if len(parsed_moves_list) == 0:
                    print(f"\nWARNING : in the current PGN, we met the empty variation '{sequence}'. "
                          f"We stop the Tree generation there. The PGN in question is :\n{source_pgn_name}\n")
                    variation_stack = []
                    break

                # If a variation indicates a move as its own variation, it would break our code.
                # Since this case is rare, in this case we stop there and append a warning message
                move_number, color, move_san, nag = parsed_moves_list[0]
                # We enjoy the occasion to check the parsing of this move
                expected_move_number = ceil((current_node.full_num + 1) / 2)
                expected_color = not current_node.color
                first_node = Node(num=move_number if move_number is not None else expected_move_number,
                                  color=expected_color, move=move_san, nag=nag)

                if any(child.key == first_node.key for child in current_node.children):
                    #print(f"\nWARNING : in the current PGN, a move was indicated as its own variation "
                    #      f"({sequence} following {current_node})."
                    #      f"We ignore this variation. The PGN in question is :\n{source_pgn_name}\n")
                    skip_depth = 1
                    continue
                if first_node.full_num != (current_node.full_num + 1):
                    #print(f"\nWARNING : in the current PGN, a variation is incorrectly placed "
                    #      f"({sequence} following {current_node}). "
                    #      f"We ignore this variation. The PGN in question is :\n{source_pgn_name}\n")
                    skip_depth = 1
                    continue

                for i_move, move in enumerate(parsed_moves_list):
                    move_number, color, move_san, nag = move
                    expected_move_number = ceil((current_node.full_num + 1) / 2)
                    expected_color = not current_node.color
                    node = Node(num=expected_move_number, color=expected_color, move=move_san, nag=nag)
                    # we can not trust the color parsed from pgns ; luckily we do not need it
                    current_node = current_node.add_child(node)

            elif sequence_type == "parenthese":

                if sequence == "(":
                    # A variation starts from the parent of the move that
                    # has just been played.
                    if current_node.parent is None:
                        print(f"\nWARNING : in the current PGN, we met unexpected '(' at root level. "
                              f"We stop the Tree generation there. The PGN in question is :\n{source_pgn_name}\n")
                        variation_stack = []
                        break

                    variation_stack.append(current_node)
                    current_node = current_node.parent

                elif sequence == ")":
                    if not variation_stack:
                        raise ValueError(f"Unmatched ')' in {source_pgn_name}")

                    # Continue after the move preceding the variation.
                    current_node = variation_stack.pop()

                else:
                    raise ValueError(f"Unknown parenthesis in {source_pgn_name}: {sequence}")

            else:
                raise ValueError(f"Unknown chunk type in {source_pgn_name}: {sequence_type}")

        if variation_stack:
            raise ValueError(f"Unclosed variation(s) in {source_pgn_name}")

    def init_from_latex_sequence_list(self, latex_sequence_list, source_latex_name):
        """
        Instantiates the Tree from a latex_sequence_list, which is a list of tuples (sequence_type, sequence)
        It is extracted from a PGN, so the possible sequence_type are :
        - 'variation'/'mainline' : sequence is a sequence of consecutive moves, including their GANs,
        for instance "2...Nf6! 3.e5". The distinction 'variation'/'mainline' is not used in constructing the tree.
        - 'comment' : sequence is a comment referring to the preceding move, for instance " a strong prophylactic move"
        """

        self.source_file = source_latex_name

        assert self.repertoire_color is not None  # it is necessary to avoid ambiguity
        if len(self.root.children) > 0:
            raise Exception(f"This tree already contains a game")
        else:
            current_node = self.root  # the move we have just written in the file
            for chunk in latex_sequence_list:  # a chunk of successive moves
                sequence_type, sequence = chunk

                if sequence_type == "comment" and sequence != '':
                    if not current_node.comment:
                        current_node.comment = sequence
                    else:
                        current_node.comment += " " + sequence

                else:
                    parsed_moves_list = parse_moves(sequence)
                    for move in parsed_moves_list:
                        move_node = Node(*move)

                        if move_node.full_num == (current_node.full_num + 1):
                            current_node = current_node.add_child(move_node, repertoire_color=self.repertoire_color)
                            # as we expect variations to contain at least one reply, and end with a move from our side,
                            # and there is no alternative for our side
                            # - 2...g6 can be followed by 3.d4 only in 2...g6 3.d4 : 2...g6) 3.d4 is impossible
                            # - 3.d4 can be followed by 3...d5 only in 3.d4 d5 : 3.d4) 3...d5 is impossible

                        elif move_node.full_num < current_node.full_num:
                            # 3.d4) 2.g3 / 3.d4 ; 2...c5 / 3.d4 end of variation \n 2...d5
                            if current_node.color == self.repertoire_color:  # the only possible case
                                if move_node.color == current_node.color:
                                    # 3.d4) 2.g3 : we need to go out of the current variation to go back to the
                                    # corresponding "mainline"
                                    while current_node.full_num >= move_node.full_num:
                                        current_node = current_node.parent
                                    # we are back to 1...g5 the beginning of the variation, while the mainline is 1...c5
                                    current_node = current_node.parent.children[0]  # we are now in 1...c5
                                    current_node = current_node.add_child(move_node,
                                                                          repertoire_color=self.repertoire_color)

                                else:
                                    # 3.d4 ; 2...c5 / 3.d4 end of variation \n 2...c5
                                    # We need to go to the next variation among those with a common start
                                    while current_node.full_num > move_node.full_num:
                                        current_node = current_node.parent
                                    # we are back to 2...g5 the beginning of the variation
                                    current_node = current_node.parent  # we are now in the preceding of 2...g5
                                    current_node = current_node.add_child(move_node,
                                                                          repertoire_color=self.repertoire_color)
                            else:
                                raise Exception(f"There shouldn't be a valid case where {current_node} is "
                                                f"followed by {move_node}")

                        elif move_node.full_num == current_node.full_num:
                            if current_node.color == self.repertoire_color:
                                # we have reached the end of a one-move long alternative to the "main line" :
                                # for instance 4.d4) 4.g3 or 4.d4 \end of variation next main line
                                while current_node.full_num >= move_node.full_num:
                                    current_node = current_node.parent
                                # we are back to 3...g5 the beginning of the variation, while the mainline is 3...c5
                                current_node = current_node.parent.children[0]  # we are now in 3...c5
                                current_node = current_node.add_child(move_node, repertoire_color=self.repertoire_color)
                            else:
                                # we are reaching an alternative to the current node :
                                # for instance 4...c6 (4...g6 or 4...c6 end of mainline \n 4...g6
                                current_node = current_node.add_sibling(move_node,
                                                                        repertoire_color=self.repertoire_color)

                        else:  # move_node.full_num > (current_node.full_num + 1)
                            raise Exception(f"There shouldn't be a valid case where {current_node} is "
                                            f"followed by {move_node} "
                                            f"({move_node.full_num} > {current_node.full_num} + 1)")

    # For representing the tree :
    def __str__(self):
        """
        Represents the tree as an indented string.
        """
        return self._str_node(self.root)

    def _str_node(self, node, level=-1):
        lines = []
        for child in node.children:
            lines.append("    " * level + str(child))
            lines.append(self._str_node(child, level + 1))

        return "\n".join(line for line in lines if line)

    # For writing the PGN :
    def get_headers_str(self):
        return "\n".join([f"[{k} {quote(v)}]" for k, v in self.headers.items()])

    def pgn(self, with_comment=True, with_nag=True, use_symbolic_nag=False, **kwargs):
        """
        Generates the PGN corresponding to the tree, optionally with comments and NAGs.
        If they were not already, headers can be specified as kwargs.
        """
        # The headers
        new_headers = {**kwargs}
        self.update_headers(new_headers)
        headers_str = self.get_headers_str()

        # The actual moves
        pgn_moves = self._write_line_and_alternatives(self.root, first_in_sequence=True,
                                                      with_comment=with_comment, with_nag=with_nag,
                                                      use_symbolic_nag=use_symbolic_nag)

        return f"{headers_str}\n\n{pgn_moves} {unquote(self.headers['Result'])}"

    def _write_line_and_alternatives(self, parent, first_in_sequence=False,
                                     with_comment=False, with_nag=False,
                                     use_symbolic_nag=True):

        if not parent.children:  # when reaching a leaf
            return ""

        else:
            result = []
            mainline = parent.children[0]

            # We print the mainline move and its comment
            result.append(mainline.notation(no_preceding=first_in_sequence, with_nag=with_nag,
                                            use_symbolic_nag=use_symbolic_nag))
            if mainline.comment and with_comment:
                result.append("{" + mainline.comment + "}")
                mainline_commented = True
            else:
                mainline_commented = False

            # We print all alternatives as variations
            nb_variations = len(parent.children[1:])
            for variation in parent.children[1:]:
                result.append(
                    "(" + self._write_line_without_alternatives(variation, first_in_sequence=True,
                                                                with_comment=with_comment, with_nag=with_nag,
                                                                use_symbolic_nag=use_symbolic_nag) + ")"
                )

            # We print the rest of the mainline after the variations
            result.append(
                self._write_line_and_alternatives(parent=mainline,
                                                  first_in_sequence=(nb_variations > 0) or mainline_commented,
                                                  with_comment=with_comment, with_nag=with_nag,
                                                  use_symbolic_nag=use_symbolic_nag)
            )

            return " ".join(result)

    def _write_line_without_alternatives(self, node, first_in_sequence=False,
                                         with_comment=False, with_nag=False,
                                         use_symbolic_nag=True):
        if node.full_num == 0:
            return ""

        else:
            result = []
            current = node

            # We print the mainline move and its comment
            result.append(current.notation(no_preceding=first_in_sequence, with_nag=with_nag,
                                           use_symbolic_nag=use_symbolic_nag))
            if current.comment and with_comment:
                result.append("{" + current.comment + "}")
                mainline_commented = True
            else:
                mainline_commented = False

            # Since we print no alternatives, we can go on with printing the next move
            result.append(
                self._write_line_and_alternatives(parent=current, first_in_sequence=mainline_commented,
                                                  with_comment=with_comment, with_nag=with_nag,
                                                  use_symbolic_nag=use_symbolic_nag)
            )

            return " ".join(result)

    # For writing the LaTeX :
    def latex(self, with_comment=True, with_nag=True, use_symbolic_nag=False):
        last_level, latex_moves = self._write_latex_line_and_alternatives(parent=self.root, first_in_sequence=True,
                                                                          level=1, preceding_level=1,
                                                                          with_comment=with_comment,
                                                                          with_nag=with_nag,
                                                                          use_symbolic_nag=use_symbolic_nag)
        latex_moves = latex_moves.replace("(\n", "(")

        if "FEN" in self.headers.keys() and unquote(self.headers['FEN']) != INITIAL_FEN:
            fen_string = f"[setfen={unquote(self.headers['FEN'])}, " \
                         f"moveid={num_from_full_num(self.root.full_num)}{'b' if self.root.color == WHITE else 'w'}]"
            # And we also print the chessboard
            fen_string += f"\n\\chessboard\n\\medskip\n"
        else:
            fen_string = ""

        return f"\\xskakset{{level=1}}\n\\newchessgame{fen_string}\n{latex_moves}"

    def _write_latex_line_and_alternatives(self, parent, first_in_sequence=True, level=1, preceding_level=1,
                                           with_comment=False, with_nag=False,
                                           use_symbolic_nag=False):

        if not parent.children:  # when reaching a leaf
            # We first determine the str we will return :
            # if the line was already closed, for instance by a comment, we return "",
            # else it means we have reached the end of the variation so we return "}"
            returned_str = "" if first_in_sequence else "}"
            returned_level = preceding_level if level == 2 else level
            # because a "level 2 line" may actually end with a "level 3 line" -> we need to indicate it to use [outvar, outvar]
            return returned_level, returned_str
        elif level > 3:
            print(f"\nWarning: Latex only supports 3 levels of depth, so variation "
                  f"{parent.children[0]} (and possibly further variations) will not be included.")
            return level, ""
        else:
            output = ""
            mainline = parent.children[0]

            if first_in_sequence:
                variation_command = "\n\\mainline" if level == 1 else "\n\\variation"
                diff = int(level - preceding_level)
                potential_linebreak = '\n' if diff == (-2) else ''
                output += f"{potential_linebreak}{variation_command}{DIFF_TO_OPTION[diff]}{{"

            # We print the mainline move and its comment ; moreover, after a comment it's wiser to close the line
            output += mainline.notation(no_preceding=first_in_sequence, with_nag=with_nag,
                                        use_symbolic_nag=use_symbolic_nag)
            if mainline.comment and with_comment:
                # The formatting of the comment changes depending on the level :
                if level > 1:
                    output += f" \\xskakcomment{{ {process_comment_for_latex(mainline.comment)}}}}}"
                else:
                    output += f"}}\n\\xskakset{{level=2}}\n{process_comment_for_latex(mainline.comment)}\n\\xskakset{{level=1}}"
                mainline_commented = True
            else:
                mainline_commented = False

            # We print all alternatives as variations (they appear differently depending on the level) ,
            # only if level < 3 (else the deeper variations, even not appearing, may cause a problem)
            last_level = level
            nb_variations = len(parent.children[1:]) if level <= 2 else 0
            # we do as if there were no variations for level >=3

            # We close the mainline if necessary
            if (nb_variations > 0) and not mainline_commented:
                output += "}"

            list_variations = []
            for i in range(nb_variations):
                variation = parent.children[1:][i]
                last_level, variation_text = self._write_latex_line_without_alternatives(variation,
                                                                                         first_in_sequence=True,
                                                                                         level=level + 1,
                                                                                         preceding_level=last_level,
                                                                                         with_comment=with_comment,
                                                                                         with_nag=with_nag,
                                                                                         use_symbolic_nag=use_symbolic_nag)
                list_variations.append(variation_text)

            # We actually add the variations to the output
            if list_variations:
                if level == 1:
                    output += "\n" + "\n".join(list_variations) + "\n"
                elif level == 2:
                    output += "\n(" + " ;".join(list_variations) + ")"
                    # N.B. : depending on the case, after a level 3 in parentheses, either we go on on the same line,
                    # if we follow with level 2, or we break a line if we follow with level 1. Hence potential_linebreak
                elif level == 3:
                    print(
                        f"\nWarning: Latex only supports 3 levels of depth, so we cannot include deeper variations")

            # We can go to the next move
            final_level, end_mainline = self._write_latex_line_and_alternatives(parent=mainline,
                                                                                first_in_sequence=(
                                                                                                              nb_variations > 0) or mainline_commented,
                                                                                level=level,
                                                                                preceding_level=last_level,
                                                                                with_comment=with_comment,
                                                                                with_nag=with_nag,
                                                                                use_symbolic_nag=use_symbolic_nag)
            output += " " + end_mainline

            return final_level, output

    def _write_latex_line_without_alternatives(self, node, first_in_sequence=False, level=1, preceding_level=1,
                                               with_comment=False, with_nag=False,
                                               use_symbolic_nag=False):
        if node.full_num == 0:
            return level, ""  # we are at the root
        elif level > 3:
            print(f"\nWarning: Latex only supports 3 levels of depth, so variation "
                  f"{node} (and possibly further variations) will not be included.")
            return level, ""
        else:
            output = ""
            current = node

            if first_in_sequence:
                variation_command = "\n\\mainline" if level == 1 else "\n\\variation"
                diff = int(level - preceding_level)
                output += f"{variation_command}{DIFF_TO_OPTION[diff]}{{"

            # We print the mainline move and its comment
            output += current.notation(no_preceding=first_in_sequence, with_nag=with_nag,
                                       use_symbolic_nag=use_symbolic_nag)
            if current.comment and with_comment:
                # The formatting of the comment changes depending on the level :
                if level > 1:
                    output += f" \\xskakcomment{{ {process_comment_for_latex(current.comment)}}}}}"
                else:
                    output += f"}}\\xskakset{{level=2}}\n{process_comment_for_latex(current.comment)}\n\\xskakset{{level=1}}"
                mainline_commented = True
            else:
                mainline_commented = False

            # Since we print no alternatives, we can go on with printing the next move
            next_level, next_text = self._write_latex_line_and_alternatives(parent=current,
                                                                            first_in_sequence=mainline_commented,
                                                                            level=level, preceding_level=level,
                                                                            with_comment=with_comment,
                                                                            with_nag=with_nag,
                                                                            use_symbolic_nag=use_symbolic_nag)
            output += " " + next_text

            return next_level, output

    # For merging two trees
    def merge(self, other):
        """Merge another tree into this one."""
        self._merge_nodes(self.root, other.root)

    def multiple_merges(self, list_of_others):
        """Merge multiple trees into this one."""
        for other in list_of_others:
            self.merge(other)

    def _merge_nodes(self, node1, node2):
        """Merge node2 and its descendants into node1."""

        # For common nodes, we update comments
        if node2.comment:
            if not node1.comment:
                node1.comment = node2.comment
        # It is tempting to append node2.comment to node1.comment, if they are different, but this might lead to
        # undesired results after successive merges

        for child2 in node2.children:

            # Look for an identical child already present
            child1 = next(
                (child for child in node1.children if child.key == child2.key),
                None,
            )
            # Find the first child in node1.children whose key equals child2.key. If there isn't one, return None

            if child1 is None:
                # Entire branch is new
                node1.add_child(self._copy_subtree(child2))
            else:
                # Merge recursively
                self._merge_nodes(child1, child2)

    def _copy_subtree(self, node):
        """Deep-copy a subtree rooted at node."""
        copy = Node(
            num=node.num,
            color=node.color,
            move=node.move,
            comment=node.comment,
        )

        for child in node.children:
            copy.add_child(self._copy_subtree(child))

        return copy

    def get_copy(self):
        copy_tree = Tree()
        copy_tree.root = self._copy_subtree(self.root)
        copy_tree.repertoire_color = self.repertoire_color
        copy_tree.headers = self.headers
        copy_tree.source_file = self.source_file
        return copy_tree
