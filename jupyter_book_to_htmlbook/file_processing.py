import logging
import re
from pathlib import Path
from typing import Union
from bs4 import BeautifulSoup  # type: ignore
from .admonition_processing import process_admonitions
from .figure_processing import process_figures, process_informal_figs
from .footnote_processing import process_footnotes
from .math_processing import process_math
from .reference_processing import (
        process_internal_refs,
        process_remaining_refs,
        process_ids,
        process_citations,
        add_glossary_datatypes
    )
from .code_processing import process_code, process_code_examples
from .text_processing import (
        clean_chapter,
        move_span_ids_to_sections,
        process_sidebars
    )


def process_part(part_path: Path, output_dir: Path):
    """
    create a file based on the placeholder path
    with the name designated in the placeholder path
    and the correct part numbering
    """
    info = re.search(r'_jb_part-([0-9]+)-(.+?).html', str(part_path))
    if info:
        part_number = info.group(1)
        # undo earlier space replacement and do a simple title case
        part_name = info.group(2).replace('-', ' ').title()

        with open(output_dir / f'part-{part_number}.html', 'wt') as f:
            f.write(f"""
<div xmlns="http://www.w3.org/1999/xhtml" data-type="part" id="part-1">
<h1>{part_name}</h1>
</div>""".lstrip())
        return f'part-{part_number}.html'
    else:
        logging.error("Unable to parse part information from " +
                      str(part_path))
        return


def process_subsections(chapter):
    """ add appropriate secX markers to subsections """
    # deal with subsections
    subsections = chapter.find_all('section')  # type: ignore
    for sub in subsections:
        if sub.select('section > h1'):
            sub['data-type'] = 'sect1'
        elif sub.select('section > h2'):
            sub['data-type'] = 'sect2'
            # parsing subsections within seems like the best strategy
        elif sub.select('section > h3'):
            sub['data-type'] = 'sect3'
        elif sub.select('section > h4'):
            sub['data-type'] = 'sect4'
        elif sub.select('section > h5'):
            sub['data-type'] = 'sect5'
    return chapter


def promote_headings(chapter):
    """
    we expect to have a single h1 and then a bunch of h2s
    in a single-file chapter, but we need to promote all the headings
    up on level for htmlbook to process them correctly
    """
    h2s = chapter.find_all('h2')
    for heading in h2s:
        heading.name = 'h1'
    h3s = chapter.find_all('h3')
    for heading in h3s:
        heading.name = 'h2'
    h4s = chapter.find_all('h4')
    for heading in h4s:
        heading.name = 'h3'
    h5s = chapter.find_all('h5')
    for heading in h5s:
        heading.name = 'h4'
    h6s = chapter.find_all('h6')
    for heading in h6s:
        heading.name = 'h5'

    return chapter


def apply_datatype(chapter, ch_name):
    """
    Does a best-guess application of a data-type based on file name.
    """
    ch_stub = re.sub('[^a-zA-Z]', '', ch_name)

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

    if ch_stub.lower() in front_matter or ch_name in front_matter:
        if ch_stub.lower() in allowed_data_types:
            chapter['data-type'] = ch_stub.lower()  # type: ignore
        else:
            chapter['data-type'] = "preface"  # type: ignore
    elif ch_stub.lower() in back_matter or ch_name in back_matter:
        if ch_stub.lower() in allowed_data_types:
            chapter['data-type'] = ch_stub.lower()  # type: ignore
        else:
            chapter['data-type'] = "afterword"  # type: ignore
    elif ch_stub.lower()[:4] == "appx" or ch_stub == "bibliography":
        chapter['data-type'] = "appendix"
    elif ch_stub.lower() == "glossary":
        chapter['data-type'] = "glossary"
    else:
        chapter['data-type'] = 'chapter'  # type: ignore
    del chapter['class']  # type: ignore

    return chapter


def get_main_section(soup):
    """
    Gets the main "section," or the main chapter text, and additionally
    checks to see if there is a separate bibliography section, returning
    that if it exists to be dealt with later.
    """
    sections = soup.find_all('section')
    try:
        main = sections[0]
    except IndexError:  # does not have a section class for top-level
        logging.warning("Looks like {toc_element.name} is malformed.")
        return None, None
    if len(sections) > 1:
        bibliography = soup.find('section', id="bibliography")
    else:
        bibliography = None
    return main, bibliography


def process_chapter_soup(toc_element: Union[Path, list[Path]]):
    """ unified file chapter processing """

    if isinstance(toc_element, list):  # i.e., an ordered list of chapter parts
        chapter_file = toc_element[0]
        chapter_parts = toc_element[1:]
    else:
        chapter_file = toc_element
        chapter_parts = None

    ch_name = chapter_file.stem

    with open(chapter_file, 'r') as f:
        base_soup = BeautifulSoup(f, 'lxml')

    # perform initial swapping and namespace designation
    chapter, bib = get_main_section(base_soup)

    if not chapter:
        return None, None

    else:
        chapter['xmlns'] = 'http://www.w3.org/1999/xhtml'  # type: ignore
        del chapter['class']

        # promote subheadings within "base" chapter
        chapter = promote_headings(chapter)

        if chapter_parts:
            for subfile in chapter_parts:
                subsection, sub_bib = process_chapter_subparts(subfile)
                chapter.append(subsection)
                if bib and sub_bib:
                    entries = sub_bib.find_all("dd")
                    bib.dl.extend(entries)
                elif sub_bib:
                    bib = sub_bib

        # apply appropriate data-type (best guess)
        chapter = apply_datatype(chapter, ch_name)

        # add bibliography, if present
        if bib:
            chapter.append(bib)

        return chapter, ch_name


def process_chapter_subparts(subfile):
    """ processing for chapters with "sections" """
    with open(subfile, 'r') as f:
        soup = BeautifulSoup(f, 'lxml')
        section, bib = get_main_section(soup)
        section['data-type'] = 'sect1'  # type: ignore
        del section['class']  # type: ignore
        # move id from empty span to section
        try:
            section['id'] = section.select_one('span')['id']  # type: ignore
        except TypeError:
            # fun fact, this happens when there's not numbering on the toc
            pass  # like before, if it's not there that's OK.
        except KeyError:
            # fun fact, this happens when there is numbering on the toc
            pass  # like before, if it's not there that's OK.
    return section, bib


def process_chapter(toc_element,
                    source_dir,
                    build_dir=Path('.'),
                    book_ids: list = [],
                    skip_cell_numbering: bool = False):
    """
    Takes a list of chapter files and chapter lists and then writes the chapter
    to the root directory in which the script is run. Note that this assumes
    that the files are in some /html/ directory or some such
    """

    chapter, ch_name = process_chapter_soup(toc_element)
    logging.info(f"Processing {ch_name}...")

    if not chapter:  # guard against malformed files
        logging.warning(f"Failed to process {toc_element}.")
        raise RuntimeError(
            f"Failed to process {toc_element}. Please check for error in " +
            "your source file(s). Contact the Tools team for additional " +
            "support.")

    # perform cleans and processing
    chapter = clean_chapter(chapter)
    # note: must process figs before xrefs
    chapter = process_figures(chapter, build_dir)
    chapter = process_informal_figs(chapter, build_dir)
    chapter = process_internal_refs(chapter)
    chapter = process_citations(chapter)
    chapter = process_footnotes(chapter)
    chapter = process_admonitions(chapter)
    chapter = process_math(chapter)
    # note: best to run examples before code processing
    chapter = process_code_examples(chapter)
    chapter = process_code(chapter, skip_cell_numbering)
    chapter = move_span_ids_to_sections(chapter)
    chapter = process_sidebars(chapter)
    chapter = process_subsections(chapter)
    # finally, process any remaining xrefs
    chapter = process_remaining_refs(chapter)

    if chapter.get("data-type") == "glossary":
        add_glossary_datatypes(chapter)

    # ensure we have unique IDs across the book
    chapter, ids = process_ids(chapter, book_ids)

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
    return str(out.relative_to(build_dir)), ids
