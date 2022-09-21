import logging
import re
from pathlib import Path
from bs4 import BeautifulSoup  # type: ignore
from .admonition_processing import process_admonitions
from .figure_processing import process_figures, process_informal_figs
from .footnote_processing import process_footnotes
from .math_processing import process_math
from .xref_processing import process_interal_refs


def process_chapter_single_file(toc_element):
    """ single-file chapter processing """
    ch_name = toc_element.stem

    # list of front and back matter guessed-at filenames
    front_matter = ['preface', 'notation', 'prereqs',
                    'titlepage', 'foreword', 'introduction']
    back_matter = ['colophon', 'author_bio', 'references',
                   "acknowledgments", "conclusion", "afterword"]
    # data-types
    allowed_data_types = ["colophon", "halftitlepage", "titlepage",
                          "copyright-page", "dedication", "acknowledgments",
                          "afterword", "conclusion", 'foreword',
                          'introduction', 'preface']

    with open(toc_element, 'r') as f:
        base_soup = BeautifulSoup(f, 'lxml')

    # perform initial swapping and namespace designation
    try:
        chapter = base_soup.find(class_='section')
        chapter.name = 'section'  # type: ignore
        chapter['xmlns'] = 'http://www.w3.org/1999/xhtml'  # type: ignore

    except AttributeError:  # does not have a section class for top-level
        if base_soup.main and base_soup.main.section:
            chapter = base_soup.main.section
            chapter['xmlns'] = 'http://www.w3.org/1999/xhtml'
        else:  # this is an edge case, and I'm going to leave it for now
            logging.warning("Looks like {toc_element.name} is malformed.")
            return None, None

    # apply appropriate data-type (best guess)
    if ch_name.lower() in front_matter:
        if ch_name.lower() in allowed_data_types:
            chapter['data-type'] = ch_name.lower()  # type: ignore
        else:
            chapter['data-type'] = "preface"  # type: ignore
    elif ch_name.lower() in back_matter:
        if ch_name.lower() in allowed_data_types:
            chapter['data-type'] = ch_name.lower()  # type: ignore
        else:
            chapter['data-type'] = "afterword"  # type: ignore
    else:
        chapter['data-type'] = 'chapter'  # type: ignore
    del chapter['class']  # type: ignore

    return chapter, ch_name


def process_chapter_subparts(subfile):
    """ processing for chapters with "sections" """
    with open(subfile, 'r') as f:
        soup = BeautifulSoup(f, 'lxml')
        section = soup.find_all('section')[0]
        section['data-type'] = 'sect1'  # type: ignore
        del section['class']  # type: ignore
        # move id from empty span to section
        try:
            section['id'] = section.select_one('span')['id']  # type: ignore
            # clean up empty spans
            del section.select_one('span')['id']  # type: ignore
        except TypeError:
            # fun fact, this happens when there's not numbering on the toc
            pass  # like before, if it's not there that's OK.
        except KeyError:
            # fun fact, this happens when there's numbering on the toc
            pass  # like before, if it's not there that's OK.
        # deal with subsections
        subsections = section.find_all(class_="section")  # type: ignore
        for sub in subsections:
            # remove duplicate sub-section summary ids
            # (do chapter-level stuff with post-processing scripts
            # b/c those handle in-chapter xrefs better)
            if sub['id'] == "summary":
                sub['id'] = f"{subfile.stem}_summary"
            if sub.select('div > h2'):
                sub.name = 'section'
                sub['data-type'] = 'sect2'
                # parsing subsections within seems like the best strategy
            elif sub.select('div > h3'):
                sub.name = 'section'
                sub['data-type'] = 'sect3'
            elif sub.select('div > h4'):
                sub.name = 'section'
                sub['data-type'] = 'sect4'
            elif sub.select('div > h5'):
                sub.name = 'section'
                sub['data-type'] = 'sect5'
    return section


def compile_chapter_parts(ordered_chapter_files_list):
    """
    Takes a list of chapter file URIs and returns a basic, sectioned
    chapter soup (i.e., with no other htmlbook optimizations)
    """
    # work with main file
    base_chapter_file = ordered_chapter_files_list[0]
    with open(base_chapter_file, 'r') as f:
        base_soup = BeautifulSoup(f, 'lxml')
    sections = base_soup.find_all('section')
    chapter = sections[0]  # first section is the "main" section
    chapter['data-type'] = 'chapter'  # type: ignore
    chapter['xmlns'] = 'http://www.w3.org/1999/xhtml'  # type: ignore
    del chapter['class']  # type: ignore
    # add class="pagenumrestart" if it's the first chapter
    # (will need to be changed for parts, but -- will handle that later)
    if base_chapter_file.as_posix().find('01') > -1 or \
       base_chapter_file.as_posix().find('/1/') > -1:
        chapter['class'] = "pagenumrestart"  # type: ignore
    # update chapter id to what is actually referred to (as far as I can tell)
    feel_better_msg = "It's possible there is no empty span here " + \
                      "and likely is not a problem."

    try:
        id_span = chapter.find('span')  # type: ignore
        chapter['id'] = id_span['id']  # type: ignore
        id_span.decompose()  # type: ignore

    except KeyError as e:
        logging.debug(f'{e} in {base_chapter_file.name}\n{feel_better_msg}')
        pass
    except TypeError as e:
        logging.debug(f'{e} in {base_chapter_file.name}\n{feel_better_msg}')
        pass

    # work with subfiles
    for subfile in ordered_chapter_files_list[1:]:
        subsection = process_chapter_subparts(subfile)
        chapter.append(subsection)  # type: ignore

    return chapter


def clean_chapter(chapter, rm_numbering=True):
    """
    "Cleans" the chapter from any script or style tags, removes table borders,
    removes any style attrs, and by default removes any section numbering.
    """
    remove_tags = ['style', 'script']
    all_tags = chapter.find_all()
    for tag in all_tags:
        if tag.name in remove_tags:
            tag.decompose()
        if tag.name == 'table':
            del tag['border']
    for tag in chapter.find_all(attrs={'style': True}):
        del tag['style']

    # (optionally) remove numbering
    if rm_numbering:
        for span in chapter.find_all(class_="section-number"):
            span.decompose()

    classes_to_remove = [
        # remove hidden cells. in the web version, these cells are hidden by
        # default and users can toggle them on/off. but they take up too much
        # space if rendered into the pdf.
        ".tag_hide-input > .cell_input",
        ".tag_hide-output > .cell_output",
        ".tag_hide-cell",
        ".toggle-details",

        # remove any heading links
        ".headerlink",
    ]

    for el in chapter.select(','.join(classes_to_remove)):
        el.decompose()
    return chapter


def move_span_ids_to_sections(chapter):
    """
    Takes span tags with "sec-" ids and moves the id to the parent section tag
    so Atlas can find the cross reference.
    """
    sec_spans = chapter.find_all("span", id=re.compile('sec-*'))
    for span in sec_spans:
        # get id
        span_id = span['id']
        # get next heading
        section = span.find_parent('section')
        # add span id to section
        section['id'] = span_id
        # remove span so no dup ids
        span.decompose()
    return chapter


def process_chapter(toc_element, source_dir, build_dir=Path('.')):
    """
    Takes a list of chapter files and chapter lists and then writes the chapter
    to the root directory in which the script is run. Note that this assumes
    that the files are in some /html/ directory or some such
    """

    if isinstance(toc_element, Path):  # single-file chapter
        chapter, ch_name = process_chapter_single_file(toc_element)

        # if the file happens to be bad, just return (logged elsewhere)
        if chapter is None or ch_name is None:
            return

    else:  # i.e., an ordered list of chapter parts
        chapter = compile_chapter_parts(toc_element)
        ch_name = toc_element[0].stem

    # see where we're at
    logging.info(f"Processing {ch_name}...")

    # perform cleans and processing
    chapter = clean_chapter(chapter)
    chapter = process_interal_refs(chapter)
    chapter = process_figures(chapter)
    chapter = process_informal_figs(chapter)
    chapter = process_footnotes(chapter)
    chapter = process_admonitions(chapter)
    chapter = process_math(chapter)
    chapter = move_span_ids_to_sections(chapter)

    # write the file, preserving any directory structure(s) from source
    if type(toc_element) == list:
        dir_structure = [p for p in toc_element[0].parts
                         if p not in source_dir.parts]
    else:
        dir_structure = [p for p in toc_element.parts
                         if p not in source_dir.parts]
    parents = '/'.join(dir_structure[:-1])  # don't double the file stem
    if parents:
        parent_path = build_dir / parents
        # required for the write step later
        parent_path.mkdir(parents=True, exist_ok=True)
        out = parent_path / (ch_name + '.html')
    else:
        out = build_dir / (ch_name + '.html')

    out.write_text(str(chapter))

    # return relative path of file as string for later use
    return str(out.relative_to(build_dir))
