import os
import re
from pathlib import Path

from constants import *
from converting.merging_utils import merge_subsections, merge_sections
from global_utils import formatted_text, partition_chess
from datastructure.datastructure_utils import merged_tree_from_list


def get_title_command(repertoire_color, author, title, title_moves,
                      with_repertoire_line=True, with_title_line=True,
                      with_title_moves_line=True, with_author_line=True):
    repertoire_line = f"{{\\HUGE Répertoire {'blanc' if repertoire_color == WHITE else 'noir'} " \
                      f"\\{'pawn' if repertoire_color == WHITE else 'pawnB'}}}" \
                      f"\\\\[2\\baselineskip]\n" if with_repertoire_line else ""
    title_line = f"{{\\HUGE {title}}}\\\\[\\baselineskip]\n" if with_title_line else ""
    title_moves_line = f"{{\\HUGE (\\varref{{{title_moves}}})}}\\\\[\\baselineskip]\\par\n" if with_title_moves_line else ""
    author_line = f"{{\\large {author}}}\n" if with_author_line else ""

    # A insérer juste avant le begin document
    title_command = f"% Commands for my own title format\n" \
    f"\\newcommand*{{\\titlePP}}{{\\begingroup% Printing Poetry\n" \
    f"\\FSfont{{5jr}}% FontSite Jenson Recut (Centaur)\n" \
    f"\\drop=0.1\\textheight\n" \
    f"\\vspace*{{\\drop}}\n" \
    f"\\begin{{raggedleft}}\n{repertoire_line}{title_line}{title_moves_line}\\end{{raggedleft}}\n" \
    f"\\vfill\n" \
    f"\\begin{{center}}\n{author_line}\\end{{center}}\n" \
    f"\\vspace*{{\\drop}}\n" \
    f"%\\mbox{{}}\n" \
    f"\\endgroup}}"

    return title_command


def clean_title(section_title):
    cleaned_title = re.sub(r'^\d+\)', '', section_title)  # we remove manual index of the chapter
    parsed_title = partition_chess(cleaned_title)
    cleaned_parsed_title = [(f"\\varref{{{content}}}" if kind == "chess" else content) for kind, content in parsed_title]
    spaced_title = " ".join(cleaned_parsed_title)
    return " ".join(spaced_title.split())


def list_trees_to_latex(original_list_trees, granularity,
                        # FOR STORING
                        latex_dir, project_name,
                        # TITLE
                        repertoire_color, author, title, title_moves,
                        with_repertoire_line=True, with_title_line=True,
                        with_title_moves_line=True, with_author_line=True,
                        verbosity=True
                        ):
    # The granularity level is used to process list_trees :
    # from there the LaTeX structure will be automatically parsed from White and Black field
    # White = chapter name ; Black = section name, possibly followed by # subsection index
    # Possible values for granularity are "chapter", "section" - if not, we let the list as it is

    # We convert the list_trees into the correct granularity
    if granularity == "chapter":
        original_list_trees = merge_sections(original_list_trees)
    elif granularity == "section":
        original_list_trees = merge_subsections(original_list_trees)
    elif granularity == "single":
        original_list_trees = [merged_tree_from_list(original_list_trees)]
    elif granularity != "all":
        raise Exception(f"Unknown granularity '{granularity}'")

    # We load the Latex template
    BASE_DIR = Path(__file__).parent.parent
    template_path = BASE_DIR / "main_template.tex"
    with open(template_path, "r", encoding="utf-8") as f:
        latex_template = f.read()

    # We adapt the title
    my_title_command = get_title_command(repertoire_color=repertoire_color, author=author,
                                         title=title, title_moves=title_moves,
                                         with_repertoire_line=with_repertoire_line, with_title_line=with_title_line,
                                         with_title_moves_line=with_title_moves_line,
                                         with_author_line=with_author_line)
    latex_template = latex_template.replace("[INSERT_TITLE_COMMAND]", my_title_command)

    # We store the .tex files, organized as a project (with one .tex file per chapter) :
    # Because we append, and to avoid any undesired update, we raise an error if the project already exists
    project_dir = os.path.join(latex_dir, project_name)
    if os.path.exists(project_dir):
        raise Exception(f"The project {project_dir} already exists.\nRename it, or delete it.")
    else:
        os.makedirs(project_dir)

    # We build the list of sections, for each chapter :
    # We will know if a chapter contains only one section (in which case no "section" command is needed) or more
    sections_dict = dict()
    pairs = [(tree.headers['White'], tree.headers['Black']) for tree in original_list_trees]
    for pair in pairs:
        chap, sec = pair
        if chap not in sections_dict.keys():
            sections_dict[chap] = [sec]
        else:
            sections_dict[chap].append(sec)
    # From there we deduce the length of chapters (in terms of number of sections)
    chapter_len_dict = {chap: len(list_sec) for chap, list_sec in sections_dict.items()}

    # We write the chapters
    seen_chapters = set()
    chapters_inclusion_command = ''
    for tree in original_list_trees:
        chapter = tree.headers['White']
        section = tree.headers['Black']
        chapter_keyword = formatted_text(chapter)
        chapter_dir = os.path.join(project_dir, chapter_keyword)
        chapter_path = os.path.join(chapter_dir, f"{chapter_keyword}.tex")
        chapter_content = tree.latex(with_comment=True, with_nag=True, use_symbolic_nag=False)

        stuff_to_write = ''
        # We need to know if we print a chapter command and/or a section command
        if chapter not in seen_chapters:
            seen_chapters.add(chapter)
            os.makedirs(chapter_dir)
            print(f"Writing chapter {chapter_path}...")
            chapters_inclusion_command += f"\\input{{{chapter_keyword}/{chapter_keyword}}}\n"
            cleaned_chapter = clean_title(chapter)
            stuff_to_write += f"\\chapter{{{cleaned_chapter}}}\n"  # we remove the index of chapter
        if chapter_len_dict[chapter] > 1:
            cleaned_section = clean_title(section)
            stuff_to_write += f"\n\\section{{{cleaned_section}}}\n"  # we remove the index of section
        stuff_to_write += f"\n{chapter_content}\n"
        # We actually write files
        with open(chapter_path, "a", encoding="utf-8") as f:
            f.write(stuff_to_write)

    # Now we have finished writing chapters
    latex_template = latex_template.replace("[INSERT_CHAPTERS]", chapters_inclusion_command)
    main_path = os.path.join(project_dir, f"main.tex")
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(latex_template)

    if verbosity:
        print(f"LaTeX project successfully saved at {project_dir}")
