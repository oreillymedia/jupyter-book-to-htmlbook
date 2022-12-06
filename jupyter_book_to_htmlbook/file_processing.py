import logging
import re
from pathlib import Path
from bs4 import BeautifulSoup  # type: ignore
from .admonition_processing import process_admonitions
from .figure_processing import process_figures, process_informal_figs
from .footnote_processing import process_footnotes
from .math_processing import process_math
from .xref_processing import process_interal_refs, process_ids
from .code_processing import process_code


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
        chapter = base_soup.find_all('section')[0]
        chapter['xmlns'] = 'http://www.w3.org/1999/xhtml'  # type: ignore

    except IndexError:  # does not have a section class for top-level
        logging.warning("Looks like {toc_element.name} is malformed.")
        return None, None

    # promote headings
    chapter = promote_headings(chapter)

    # apply appropriate data-type (best guess)

    ch_stub = re.sub('[^a-zA-Z]', '', ch_name)

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
        except TypeError:
            # fun fact, this happens when there's not numbering on the toc
            pass  # like before, if it's not there that's OK.
        except KeyError:
            # fun fact, this happens when there is numbering on the toc
            pass  # like before, if it's not there that's OK.
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
    # note: must process figs before xrefs
    chapter = process_figures(chapter, build_dir)
    chapter = process_informal_figs(chapter, build_dir)
    chapter = process_interal_refs(chapter)
    chapter = process_footnotes(chapter)
    chapter = process_admonitions(chapter)
    chapter = process_math(chapter)
    chapter = process_code(chapter, skip_cell_numbering)
    chapter = move_span_ids_to_sections(chapter)
    chapter = process_subsections(chapter)
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
